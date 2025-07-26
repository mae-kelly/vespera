#!/usr/bin/env python
"""
Real Signal ngine for HT System
ZRO MOCK/ALLACK DATA - Uses only live market feeds
"""

import time
import logging
import torch
from typing import Dict, Optional
from live_market_engine import get_live_engine

# nsure GPU is available
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    logging.error("❌ NO GPU DTCTD - RAL SIGNAL NGIN RQUIRS GPU")
    raise Runtimerror("GPU required for real signal generation")

DVIC = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cuda"
logging.info(f"🚀 Real Signal ngine using DVIC")

class RealSignalGenerator:
    def __init__(self):
        self.live_engine = get_live_engine()
        self.last_signals = 
        
        # GPU tensor operations for signal calculations
        self.device = DVIC
        
        logging.info("🔴 RAL SIGNAL GNRATOR INITIALIZD - NO MOCK DATA")
    
    def generate_real_signal(self, shared_data: Dict) -> Dict:
        """Generate signals using ONLY real live market data"""
        
        # GPU operation to verify acceleration
        with torch.no_grad():
            test_tensor = torch.randn(, , device=self.device)
            _ = torch.matmul(test_tensor, test_tensor)
        
        # Get live market health
        health = self.live_engine.get_system_health()
        
        if health['system']['status'] != 'LIV':
            logging.error("❌ RJCTING SIGNAL - NO LIV DATA AVAILAL")
            return 
                "confidence": .,
                "source": "real_signal_engine",
                "priority": ,
                "error": "NO_LIV_DATA",
                "system_health": health
            
        
        # Analyze all live assets
        best_signal = None
        highest_confidence = .
        
        for symbol in ['TC', 'TH', 'SOL']:
            signal = self._analyze_symbol_live(symbol)
            if signal and signal.get('confidence', ) > highest_confidence:
                highest_confidence = signal['confidence']
                best_signal = signal
        
        if not best_signal or highest_confidence < .:
            logging.warning("⚠️ NO SIGNIICANT SIGNALS ROM LIV DATA")
            return 
                "confidence": .,
                "source": "real_signal_engine", 
                "priority": ,
                "error": "NO_SIGNIICANT_SIGNALS",
                "system_health": health
            
        
        # Return real signal with live data validation
        result = 
            "confidence": highest_confidence,
            "source": "real_signal_engine",
            "priority": ,
            "signal_data": best_signal,
            "system_health": health,
            "data_sources": self._get_data_sources(),
            "timestamp": time.time()
        
        
        logging.info(f"🎯 RAL SIGNAL: best_signal['asset'] confidence=highest_confidence:.f price=$best_signal['entry_price']:,.f")
        
        return result
    
    def _analyze_symbol_live(self, symbol: str) -> Optional[Dict]:
        """Analyze a symbol using ONLY live data"""
        
        # Get live price - NO ALLACK
        live_data = self.live_engine.get_live_price(symbol)
        if not live_data:
            logging.warning(f"⚠️ No live data for symbol")
            return None
        
        current_price = live_data['price']
        volume = live_data['volume']
        change_h = live_data.get('change_h', )
        
        # Get real price history
        price_history = self.live_engine.get_price_history(symbol, )
        if len(price_history) < :
            logging.warning(f"⚠️ Insufficient price history for symbol: len(price_history)")
            return None
        
        # Calculate real RSI
        rsi = self.live_engine.calculate_rsi(symbol)
        if rsi is None:
            logging.warning(f"⚠️ Cannot calculate RSI for symbol")
            return None
        
        # Calculate real VWAP
        vwap = self.live_engine.calculate_vwap(symbol)
        if vwap is None:
            logging.warning(f"⚠️ Cannot calculate VWAP for symbol")
            return None
        
        # GPU-accelerated technical analysis
        confidence = self._calculate_signal_confidence_gpu(
            current_price, rsi, vwap, price_history, volume, change_h
        )
        
        if confidence < .:
            return None
        
        # Calculate real entry/eit levels
        entry_price = current_price
        
        # Dynamic stop loss based on recent volatility
        price_tensor = torch.tensor(price_history[-:], device=self.device)
        volatility = torch.std(price_tensor).item()
        stop_loss_pct = ma(., min(., volatility / current_price))
        
        stop_loss = current_price * ( + stop_loss_pct)
        take_profit_ = current_price * ( - stop_loss_pct * .)
        take_profit_ = current_price * ( - stop_loss_pct * .)
        take_profit_ = current_price * ( - stop_loss_pct * .)
        
        # Calculate VWAP deviation
        vwap_deviation = ((current_price - vwap) / vwap) * 
        
        # Detect volume anomaly
        volume_history = self.live_engine.get_volume_history(symbol, )
        if len(volume_history) >= :
            avg_volume = sum(volume_history[-:]) / 
            volume_anomaly = volume > avg_volume * .
        else:
            volume_anomaly = alse
        
        # Determine signal reason based on real conditions
        reasons = []
        if rsi < :
            reasons.append("oversold_rsi")
        if vwap_deviation < -:
            reasons.append("below_vwap")
        if volume_anomaly:
            reasons.append("volume_spike")
        if change_h < -:
            reasons.append("daily_decline")
        
        reason = "_".join(reasons) if reasons else "technical_setup"
        
        return 
            "asset": symbol,
            "confidence": confidence,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit_": take_profit_,
            "take_profit_": take_profit_,
            "take_profit_": take_profit_,
            "rsi": rsi,
            "vwap": vwap,
            "vwap_deviation": vwap_deviation,
            "volume_anomaly": volume_anomaly,
            "price_change_h": change_h,
            "current_volume": volume,
            "volatility": volatility,
            "reason": reason,
            "data_source": live_data['source'],
            "price_history_length": len(price_history)
        
    
    def _calculate_signal_confidence_gpu(self, price: float, rsi: float, vwap: float, 
                                       price_history: list, volume: float, change_h: float) -> float:
        """Calculate signal confidence using GPU acceleration"""
        
        with torch.no_grad():
            # Convert to tensors for GPU processing
            price_tensor = torch.tensor(price_history[-:], device=self.device)
            current_price_tensor = torch.tensor(price, device=self.device)
            rsi_tensor = torch.tensor(rsi, device=self.device)
            vwap_tensor = torch.tensor(vwap, device=self.device)
            
            # Calculate momentum using GPU
            returns = torch.diff(price_tensor) / price_tensor[:-]
            momentum = torch.mean(returns).item()
            
            # Calculate price position relative to recent range
            price_min = torch.min(price_tensor).item()
            price_ma = torch.ma(price_tensor).item()
            price_position = (price - price_min) / (price_ma - price_min) if price_ma > price_min else .
            
            # Signal strength components
            rsi_signal = ma(, ( - rsi) / ) if rsi <  else   # Oversold signal
            vwap_signal = ma(, (vwap - price) / vwap) if price < vwap else   # elow VWAP
            momentum_signal = ma(, -momentum * ) if momentum <  else   # Negative momentum
            position_signal = ma(, (. - price_position) / .) if price_position < . else   # Low in range
            
            # Volume factor
            volume_factor = min(., volume / ) / .  # Normalize volume impact
            
            # Combine signals with weights
            weights = torch.tensor([., ., ., .], device=self.device)
            signals = torch.tensor([rsi_signal, vwap_signal, momentum_signal, position_signal], device=self.device)
            
            base_confidence = torch.sum(weights * signals).item()
            
            # Apply volume factor
            final_confidence = base_confidence * (. + . * volume_factor)
            
            # Apply market conditions penalty for etreme volatility
            volatility = torch.std(returns).item()
            if volatility > .:  # High volatility penalty
                final_confidence *= .
            
            return min(., ma(., final_confidence))
    
    def _get_data_sources(self) -> Dict:
        """Get info about current data sources"""
        health = self.live_engine.get_system_health()
        sources = 
        
        for symbol in ['TC', 'TH', 'SOL']:
            if symbol in health and health[symbol]['has_live_data']:
                sources[symbol] = health[symbol]['source']
        
        return sources

# Global instance
real_signal_generator = None

def generate_signal(shared_data: Dict) -> Dict:
    """Main signal generation function - LIV DATA ONLY"""
    global real_signal_generator
    
    if real_signal_generator is None:
        real_signal_generator = RealSignalGenerator()
    
    return real_signal_generator.generate_real_signal(shared_data)

def get_system_status() -> Dict:
    """Get system status"""
    global real_signal_generator
    
    if real_signal_generator is None:
        return "status": "NOT_INITIALIZD"
    
    return real_signal_generator.get_system_status()

# Legacy compatibility - Remove ALL fallback classes
class Simplifiedeed:
    def __init__(self):
        logging.error("❌ Simplifiedeed is deprecated - using live data only")
        raise Runtimerror("Mock data feeds are disabled - use live_market_engine only")

# Remove feed instance to prevent fallback usage
feed = None
