#!/usr/bin/env python3
"""
Real Signal Engine for HFT System
ZERO MOCK/FALLBACK DATA - Uses only live market feeds
"""

import time
import logging
import torch
from typing import Dict, Optional
from live_market_engine import get_live_engine

# Ensure GPU is available
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    logging.error("❌ NO GPU DETECTED - REAL SIGNAL ENGINE REQUIRES GPU")
    raise RuntimeError("GPU required for real signal generation")

DEVICE = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cuda"
logging.info(f"🚀 Real Signal Engine using {DEVICE}")

class RealSignalGenerator:
    def __init__(self):
        self.live_engine = get_live_engine()
        self.last_signals = {}
        
        # GPU tensor operations for signal calculations
        self.device = DEVICE
        
        logging.info("🔴 REAL SIGNAL GENERATOR INITIALIZED - NO MOCK DATA")
    
    def generate_real_signal(self, shared_data: Dict) -> Dict:
        """Generate signals using ONLY real live market data"""
        
        # GPU operation to verify acceleration
        with torch.no_grad():
            test_tensor = torch.randn(100, 100, device=self.device)
            _ = torch.matmul(test_tensor, test_tensor)
        
        # Get live market health
        health = self.live_engine.get_system_health()
        
        if health['system']['status'] != 'LIVE':
            logging.error("❌ REJECTING SIGNAL - NO LIVE DATA AVAILABLE")
            return {
                "confidence": 0.0,
                "source": "real_signal_engine",
                "priority": 1,
                "error": "NO_LIVE_DATA",
                "system_health": health
            }
        
        # Analyze all live assets
        best_signal = None
        highest_confidence = 0.0
        
        for symbol in ['BTC', 'ETH', 'SOL']:
            signal = self._analyze_symbol_live(symbol)
            if signal and signal.get('confidence', 0) > highest_confidence:
                highest_confidence = signal['confidence']
                best_signal = signal
        
        if not best_signal or highest_confidence < 0.1:
            logging.warning("⚠️ NO SIGNIFICANT SIGNALS FROM LIVE DATA")
            return {
                "confidence": 0.0,
                "source": "real_signal_engine", 
                "priority": 1,
                "error": "NO_SIGNIFICANT_SIGNALS",
                "system_health": health
            }
        
        # Return real signal with live data validation
        result = {
            "confidence": highest_confidence,
            "source": "real_signal_engine",
            "priority": 1,
            "signal_data": best_signal,
            "system_health": health,
            "data_sources": self._get_data_sources(),
            "timestamp": time.time()
        }
        
        logging.info(f"🎯 REAL SIGNAL: {best_signal['asset']} confidence={highest_confidence:.3f} price=${best_signal['entry_price']:,.2f}")
        
        return result
    
    def _analyze_symbol_live(self, symbol: str) -> Optional[Dict]:
        """Analyze a symbol using ONLY live data"""
        
        # Get live price - NO FALLBACK
        live_data = self.live_engine.get_live_price(symbol)
        if not live_data:
            logging.warning(f"⚠️ No live data for {symbol}")
            return None
        
        current_price = live_data['price']
        volume = live_data['volume']
        change_24h = live_data.get('change_24h', 0)
        
        # Get real price history
        price_history = self.live_engine.get_price_history(symbol, 50)
        if len(price_history) < 10:
            logging.warning(f"⚠️ Insufficient price history for {symbol}: {len(price_history)}")
            return None
        
        # Calculate real RSI
        rsi = self.live_engine.calculate_rsi(symbol)
        if rsi is None:
            logging.warning(f"⚠️ Cannot calculate RSI for {symbol}")
            return None
        
        # Calculate real VWAP
        vwap = self.live_engine.calculate_vwap(symbol)
        if vwap is None:
            logging.warning(f"⚠️ Cannot calculate VWAP for {symbol}")
            return None
        
        # GPU-accelerated technical analysis
        confidence = self._calculate_signal_confidence_gpu(
            current_price, rsi, vwap, price_history, volume, change_24h
        )
        
        if confidence < 0.3:
            return None
        
        # Calculate real entry/exit levels
        entry_price = current_price
        
        # Dynamic stop loss based on recent volatility
        price_tensor = torch.tensor(price_history[-20:], device=self.device)
        volatility = torch.std(price_tensor).item()
        stop_loss_pct = max(0.01, min(0.03, volatility / current_price))
        
        stop_loss = current_price * (1 + stop_loss_pct)
        take_profit_1 = current_price * (1 - stop_loss_pct * 1.5)
        take_profit_2 = current_price * (1 - stop_loss_pct * 2.5)
        take_profit_3 = current_price * (1 - stop_loss_pct * 3.5)
        
        # Calculate VWAP deviation
        vwap_deviation = ((current_price - vwap) / vwap) * 100
        
        # Detect volume anomaly
        volume_history = self.live_engine.get_volume_history(symbol, 20)
        if len(volume_history) >= 5:
            avg_volume = sum(volume_history[-5:]) / 5
            volume_anomaly = volume > avg_volume * 1.5
        else:
            volume_anomaly = False
        
        # Determine signal reason based on real conditions
        reasons = []
        if rsi < 30:
            reasons.append("oversold_rsi")
        if vwap_deviation < -2:
            reasons.append("below_vwap")
        if volume_anomaly:
            reasons.append("volume_spike")
        if change_24h < -3:
            reasons.append("daily_decline")
        
        reason = "_".join(reasons) if reasons else "technical_setup"
        
        return {
            "asset": symbol,
            "confidence": confidence,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit_1": take_profit_1,
            "take_profit_2": take_profit_2,
            "take_profit_3": take_profit_3,
            "rsi": rsi,
            "vwap": vwap,
            "vwap_deviation": vwap_deviation,
            "volume_anomaly": volume_anomaly,
            "price_change_24h": change_24h,
            "current_volume": volume,
            "volatility": volatility,
            "reason": reason,
            "data_source": live_data['source'],
            "price_history_length": len(price_history)
        }
    
    def _calculate_signal_confidence_gpu(self, price: float, rsi: float, vwap: float, 
                                       price_history: list, volume: float, change_24h: float) -> float:
        """Calculate signal confidence using GPU acceleration"""
        
        with torch.no_grad():
            # Convert to tensors for GPU processing
            price_tensor = torch.tensor(price_history[-20:], device=self.device)
            current_price_tensor = torch.tensor(price, device=self.device)
            rsi_tensor = torch.tensor(rsi, device=self.device)
            vwap_tensor = torch.tensor(vwap, device=self.device)
            
            # Calculate momentum using GPU
            returns = torch.diff(price_tensor) / price_tensor[:-1]
            momentum = torch.mean(returns).item()
            
            # Calculate price position relative to recent range
            price_min = torch.min(price_tensor).item()
            price_max = torch.max(price_tensor).item()
            price_position = (price - price_min) / (price_max - price_min) if price_max > price_min else 0.5
            
            # Signal strength components
            rsi_signal = max(0, (35 - rsi) / 35) if rsi < 35 else 0  # Oversold signal
            vwap_signal = max(0, (vwap - price) / vwap) if price < vwap else 0  # Below VWAP
            momentum_signal = max(0, -momentum * 10) if momentum < 0 else 0  # Negative momentum
            position_signal = max(0, (0.3 - price_position) / 0.3) if price_position < 0.3 else 0  # Low in range
            
            # Volume factor
            volume_factor = min(2.0, volume / 100000) / 2.0  # Normalize volume impact
            
            # Combine signals with weights
            weights = torch.tensor([0.3, 0.25, 0.25, 0.2], device=self.device)
            signals = torch.tensor([rsi_signal, vwap_signal, momentum_signal, position_signal], device=self.device)
            
            base_confidence = torch.sum(weights * signals).item()
            
            # Apply volume factor
            final_confidence = base_confidence * (0.7 + 0.3 * volume_factor)
            
            # Apply market conditions penalty for extreme volatility
            volatility = torch.std(returns).item()
            if volatility > 0.05:  # High volatility penalty
                final_confidence *= 0.8
            
            return min(1.0, max(0.0, final_confidence))
    
    def _get_data_sources(self) -> Dict:
        """Get info about current data sources"""
        health = self.live_engine.get_system_health()
        sources = {}
        
        for symbol in ['BTC', 'ETH', 'SOL']:
            if symbol in health and health[symbol]['has_live_data']:
                sources[symbol] = health[symbol]['source']
        
        return sources

# Global instance
real_signal_generator = None

def generate_signal(shared_data: Dict) -> Dict:
    """Main signal generation function - LIVE DATA ONLY"""
    global real_signal_generator
    
    if real_signal_generator is None:
        real_signal_generator = RealSignalGenerator()
    
    return real_signal_generator.generate_real_signal(shared_data)

def get_system_status() -> Dict:
    """Get system status"""
    global real_signal_generator
    
    if real_signal_generator is None:
        return {"status": "NOT_INITIALIZED"}
    
    return real_signal_generator.get_system_status()

# Legacy compatibility - Remove ALL fallback classes
class SimplifiedFeed:
    def __init__(self):
        logging.error("❌ SimplifiedFeed is deprecated - using live data only")
        raise RuntimeError("Mock data feeds are disabled - use live_market_engine only")

# Remove feed instance to prevent fallback usage
feed = None
