#!/usr/bin/env python3
"""
PRODUCTION Signal Engine - LIVE DATA ONLY
NO MOCK DATA - ZERO FALLBACKS
"""

import time
import logging
import torch
from typing import Dict, Optional

# Import live data engine
try:
    from live_data_engine import get_live_engine
except ImportError:
    from live_market_engine import get_live_engine

# Ensure GPU is available
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    logging.error("❌ NO GPU DETECTED - PRODUCTION REQUIRES GPU")
    raise RuntimeError("GPU required for production")

DEVICE = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cuda"

class ProductionSignalGenerator:
    def __init__(self):
        self.live_engine = get_live_engine()
        if not self.live_engine:
            raise RuntimeError("CRITICAL: Live engine initialization failed")
        
        logging.info("🔴 PRODUCTION SIGNAL GENERATOR - LIVE DATA ONLY")
    
    def generate_signal(self, shared_data: Dict) -> Dict:
        """Generate signals using ONLY live market data - NO FALLBACKS"""
        
        # Verify live data is available
        health = self.live_engine.get_system_health()
        if health['system']['status'] != 'LIVE':
            logging.error("❌ PRODUCTION HALT - NO LIVE DATA")
            return {
                "confidence": 0.0,
                "source": "production_engine",
                "error": "NO_LIVE_DATA_PRODUCTION_HALT"
            }
        
        # Analyze live assets
        best_signal = None
        highest_confidence = 0.0
        
        for symbol in ['BTC', 'ETH', 'SOL']:
            signal = self._analyze_symbol_live(symbol)
            if signal and signal.get('confidence', 0) > highest_confidence:
                highest_confidence = signal['confidence']
                best_signal = signal
        
        if not best_signal or highest_confidence < 0.6:  # Higher threshold for production
            return {
                "confidence": 0.0,
                "source": "production_engine",
                "error": "NO_PRODUCTION_SIGNALS"
            }
        
        return {
            "confidence": highest_confidence,
            "source": "production_engine",
            "signal_data": best_signal,
            "system_health": health,
            "production_validated": True,
            "timestamp": time.time()
        }
    
    def _analyze_symbol_live(self, symbol: str) -> Optional[Dict]:
        """Analyze symbol using ONLY live data - NO FALLBACKS"""
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
        
        # Production signal logic - more conservative
        confidence = self._calculate_production_confidence(current_price, rsi, vwap, price_history)
        
        if confidence < 0.6:  # Production threshold
            return None
        
        return {
            "asset": symbol,
            "confidence": confidence,
            "entry_price": current_price,
            "stop_loss": current_price * 1.01,  # Tighter stops for production
            "take_profit_1": current_price * 0.99,
            "rsi": rsi,
            "vwap": vwap,
            "reason": "live_production_signal",
            "data_source": live_data.get('source', 'unknown'),
            "price_history_length": len(price_history)
        }
    
    def _calculate_production_confidence(self, price: float, rsi: float, vwap: float, history: list) -> float:
        """Calculate confidence using production-grade logic"""
        with torch.no_grad():
            price_tensor = torch.tensor(history[-20:], device=DEVICE)
            momentum = torch.mean(torch.diff(price_tensor) / price_tensor[:-1]).item()
            
            # Production signal criteria - more conservative
            rsi_signal = max(0, (30 - rsi) / 30) if rsi < 30 else 0  # Only very oversold
            vwap_signal = max(0, (vwap - price) / vwap) if price < vwap else 0
            momentum_signal = max(0, -momentum * 25) if momentum < -0.01 else 0  # Stronger downtrend required
            
            # Higher weights for production
            confidence = (rsi_signal * 0.5 + vwap_signal * 0.3 + momentum_signal * 0.2)
            return min(1.0, confidence)

# Global production instance
production_generator = None

def generate_signal(shared_data: Dict) -> Dict:
    """Production signal generation - LIVE ONLY"""
    global production_generator
    if production_generator is None:
        production_generator = ProductionSignalGenerator()
    return production_generator.generate_signal(shared_data)

def get_system_status() -> Dict:
    """Get system status"""
    global production_generator
    if production_generator is None:
        return {"status": "NOT_INITIALIZED"}
    return {"status": "PRODUCTION_READY"}
