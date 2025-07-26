import time
import logging
import torch
from typing import Dict, Optional

try:
    from live_data_engine import get_live_engine
except ImportError:
    from live_market_engine import get_live_engine

if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    raise RuntimeError("GPU required for production")

DEVICE = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cuda"

class ProductionSignalGenerator:
    def __init__(self):
        self.live_engine = get_live_engine()
        if not self.live_engine:
            raise RuntimeError("Live engine initialization failed")
        
        logging.info("Production signal generator - LIVE DATA ONLY")
    
    def generate_signal(self, shared_data: Dict) -> Dict:
        health = self.live_engine.get_system_health()
        if health['system']['status'] != 'LIVE':
            return {
                "confidence": 0.0,
                "source": "production_engine",
                "error": "NO_LIVE_DATA"
            }
        
        best_signal = None
        highest_confidence = 0.0
        
        for symbol in ['BTC', 'ETH', 'SOL']:
            signal = self._analyze_symbol_live(symbol)
            if signal and signal.get('confidence', 0) > highest_confidence:
                highest_confidence = signal['confidence']
                best_signal = signal
        
        if not best_signal or highest_confidence < 0.75:
            return {
                "confidence": 0.0,
                "source": "production_engine",
                "error": "NO_PRODUCTION_SIGNALS"
            }
        
        return {
            "confidence": highest_confidence,
            "source": "production_engine",
            "signal_data": best_signal,
            "production_validated": True,
            "timestamp": time.time()
        }
    
    def _analyze_symbol_live(self, symbol: str) -> Optional[Dict]:
        live_data = self.live_engine.get_live_price(symbol)
        if not live_data:
            return None
        
        current_price = live_data['price']
        price_history = self.live_engine.get_price_history(symbol, 50)
        if len(price_history) < 20:
            return None
        
        rsi = self.live_engine.calculate_rsi(symbol)
        vwap = self.live_engine.calculate_vwap(symbol)
        
        if rsi is None or vwap is None:
            return None
        
        confidence = self._calculate_production_confidence(current_price, rsi, vwap, price_history)
        
        if confidence < 0.75:
            return None
        
        return {
            "asset": symbol,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * 1.008,
            "take_profit_1": current_price * 0.992,
            "rsi": rsi,
            "vwap": vwap,
            "reason": "live_production_signal",
            "data_source": live_data.get('source', 'unknown'),
            "price_history_length": len(price_history)
        }
    
    def _calculate_production_confidence(self, price: float, rsi: float, vwap: float, history: list) -> float:
        with torch.no_grad():
            price_tensor = torch.tensor(history[-20:], device=DEVICE)
            momentum = torch.mean(torch.diff(price_tensor) / price_tensor[:-1]).item()
            
            rsi_signal = max(0, (25 - rsi) / 25) if rsi < 25 else 0
            vwap_signal = max(0, (vwap - price) / vwap) if price < vwap else 0
            momentum_signal = max(0, -momentum * 30) if momentum < -0.015 else 0
            
            confidence = (rsi_signal * 0.6 + vwap_signal * 0.25 + momentum_signal * 0.15)
            return min(1.0, confidence)

production_generator = None

def generate_signal(shared_data: Dict) -> Dict:
    global production_generator
    if production_generator is None:
        production_generator = ProductionSignalGenerator()
    return production_generator.generate_signal(shared_data)

def get_system_status() -> Dict:
    global production_generator
    if production_generator is None:
        return {"status": "NOT_INITIALIZED"}
    return {"status": "PRODUCTION_READY"}

feed = type('Feed', (), {
    'get_recent_data': lambda self, symbol, length: {
        'valid': False,
        'prices': [],
        'volumes': [],
        'current_price': 0
    }
})()
