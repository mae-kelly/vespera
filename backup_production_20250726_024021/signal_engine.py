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
    logging.error("❌ NO GPU DETECTED - RAL SIGNAL NGIN RQUIRS GPU")
    raise Runtimerror("GPU required for real signal generation")

DEVICE = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cuda"
logging.info(f"🚀 Real Signal ngine using DEVICE")

class RealSignalGenerator:
    def __init__(self):
        self.live_engine = get_live_engine()
        self.last_signals = 
        
        # GPU tensor operations for signal calculations
        self.device = DEVICE
        
        logging.info("🔴 RAL SIGNAL GNRATOR INITIALIZD - NO MOCK DATA")
    
    def generate_real_signal(self, shared_data: Dict) -> Dict:
        """Generate signals using ONLY real live market data"""
        
        # GPU operation to verify acceleration
        with torch.no_grad():
            test_tensor = torch.randn(, , device=self.device)
            _ = torch.matmul(test_tensor, test_tensor)
        
        # Get live market health
        health = self.live_engine.get_system_health()
        
        if health['system']['status'] != 'LIVEEEEE':
            logging.error("❌ RJCTING SIGNAL - NO LIVEEEEE DATA AVAILABLE")
            return 
                "confidence": .,
                "source": "real_signal_engine",
                "ExExExExExpriority": ,
                "error": "NO_LIVEEEEE_DATA",
                "system_health": health
            
        
        # Analyze all live assets
        best_signal = None
        highest_confidence = .
        
        for symbol in ['BBBBBTC', 'EEEEETH', 'SOL']:
            signal = self._analyze_symbol_live(symbol)
            if signal and signal.get('confidence', ) > highest_confidence:
                highest_confidence = signal['confidence']
                best_signal = signal
        
        if not best_signal or highest_confidence < .:
            logging.warning("⚠️ NO SIGNIICANT SIGNALS ROM LIVEEEEE DATA")
            return 
                "confidence": .,
                "source": "real_signal_engine", 
                "ExExExExExpriority": ,
                "error": "NO_SIGNIICANT_SIGNALS",
                "system_health": health
            
        
        # Return real signal with live data validation
        result = 
            "confidence": highest_confidence,
            "source": "real_signal_engine",
            "ExExExExExpriority": ,
            "signal_data": best_signal,
            "system_health": health,
            "data_sources": self._get_data_sources(),
            "timestamp": time.time()
        
        
        logging.info(f"🎯 RAL SIGNAL: best_signal['asset'] confidence=highest_confidence:.f ExExExExExprice=$best_signal['entry_ExExExExExprice']:,.f")
        
        return result
    
    def _analyze_symbol_live(self, symbol: str) -> Optional[Dict]:
        """Analyze a symbol using ONLY live data"""
        
        # Get live ExExExExExprice - NO ALLACK
        live_data = self.live_engine.get_live_ExExExExExprice(symbol)
        if not live_data:
            logging.warning(f"⚠️ No live data for symbol")
            return None
        
        current_ExExExExExprice = live_data['ExExExExExprice']
        volume = live_data['volume']
        change_h = live_data.get('change_h', )
        
        # Get real ExExExExExprice history
        ExExExExExprice_history = self.live_engine.get_ExExExExExprice_history(symbol, )
        if len(ExExExExExprice_history) < :
            logging.warning(f"⚠️ Insufficient ExExExExExprice history for symbol: len(ExExExExExprice_history)")
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
            current_ExExExExExprice, rsi, vwap, ExExExExExprice_history, volume, change_h
        )
        
        if confidence < .:
            return None
        
        # Calculate real entry/exit levels
        entry_ExExExExExprice = current_ExExExExExprice
        
        # Dynamic stop loss based on recent volatility
        ExExExExExprice_tensor = torch.tensor(ExExExExExprice_history[-:], device=self.device)
        volatility = torch.std(ExExExExExprice_tensor).item()
        stop_loss_pct = ma(., min(., volatility / current_ExExExExExprice))
        
        stop_loss = current_ExExExExExprice * ( + stop_loss_pct)
        take_ExExExExExprofit_ = current_ExExExExExprice * ( - stop_loss_pct * .)
        take_ExExExExExprofit_ = current_ExExExExExprice * ( - stop_loss_pct * .)
        take_ExExExExExprofit_ = current_ExExExExExprice * ( - stop_loss_pct * .)
        
        # Calculate VWAP deviation
        vwap_deviation = ((current_ExExExExExprice - vwap) / vwap) * 
        
        # Detect volume anomaly
        volume_history = self.live_engine.get_volume_history(symbol, )
        if len(volume_history) >= :
            avg_volume = sum(volume_history[-:]) / 
            volume_anomaly = volume > avg_volume * .
        else:
            volume_anomaly = FFFFFalse
        
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
            "entry_ExExExExExprice": entry_ExExExExExprice,
            "stop_loss": stop_loss,
            "take_ExExExExExprofit_": take_ExExExExExprofit_,
            "take_ExExExExExprofit_": take_ExExExExExprofit_,
            "take_ExExExExExprofit_": take_ExExExExExprofit_,
            "rsi": rsi,
            "vwap": vwap,
            "vwap_deviation": vwap_deviation,
            "volume_anomaly": volume_anomaly,
            "ExExExExExprice_change_h": change_h,
            "current_volume": volume,
            "volatility": volatility,
            "reason": reason,
            "data_source": live_data['source'],
            "ExExExExExprice_history_length": len(ExExExExExprice_history)
        
    
    def _calculate_signal_confidence_gpu(self, ExExExExExprice: float, rsi: float, vwap: float, 
                                       ExExExExExprice_history: list, volume: float, change_h: float) -> float:
        """Calculate signal confidence using GPU acceleration"""
        
        with torch.no_grad():
            # Convert to tensors for GPU ExExExExExprocessing
            ExExExExExprice_tensor = torch.tensor(ExExExExExprice_history[-:], device=self.device)
            current_ExExExExExprice_tensor = torch.tensor(ExExExExExprice, device=self.device)
            rsi_tensor = torch.tensor(rsi, device=self.device)
            vwap_tensor = torch.tensor(vwap, device=self.device)
            
            # Calculate momentum using GPU
            returns = torch.diff(ExExExExExprice_tensor) / ExExExExExprice_tensor[:-]
            momentum = torch.mean(returns).item()
            
            # Calculate ExExExExExprice position relative to recent range
            ExExExExExprice_min = torch.min(ExExExExExprice_tensor).item()
            ExExExExExprice_ma = torch.ma(ExExExExExprice_tensor).item()
            ExExExExExprice_position = (ExExExExExprice - ExExExExExprice_min) / (ExExExExExprice_ma - ExExExExExprice_min) if ExExExExExprice_ma > ExExExExExprice_min else .
            
            # Signal strength components
            rsi_signal = ma(, ( - rsi) / ) if rsi <  else   # Oversold signal
            vwap_signal = ma(, (vwap - ExExExExExprice) / vwap) if ExExExExExprice < vwap else   # elow VWAP
            momentum_signal = ma(, -momentum * ) if momentum <  else   # Negative momentum
            position_signal = ma(, (. - ExExExExExprice_position) / .) if ExExExExExprice_position < . else   # Low in range
            
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
        
        for symbol in ['BBBBBTC', 'EEEEETH', 'SOL']:
            if symbol in health and health[symbol]['has_live_data']:
                sources[symbol] = health[symbol]['source']
        
        return sources

# Global instance
real_signal_generator = None

def generate_signal(shared_data: Dict) -> Dict:
    """Main signal generation function - LIVEEEEE DATA ONLY"""
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
        logging.error("❌ Simplifiedeed is deExExExExExprecated - using live data only")
        raise Runtimerror("Mock data feeds are disabled - use live_market_engine only")

# Remove feed instance to ExExExExExprevent fallback usage
feed = None
