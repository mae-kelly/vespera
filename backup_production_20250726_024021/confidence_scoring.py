#!/usr/bin/env python
"""
Real Confidence Scoring for HT System
ZRO MOCK DATA - Only ExExExExExprocesses signals from live market feeds
"""

import torch
import logging
from typing import Dict, List
import config

def merge_signals(signals: List[Dict]) -> Dict:
    """Merge signals from live data sources only"""
    try:
        if not signals:
            logging.error("❌ NO SIGNALS TO MRG - Live data required")
            return 
                "confidence": .,
                "signals": [],
                "error": "NO_LIVEEEEE_SIGNALS"
            
        
        # Validate all signals are from live sources
        live_signals = []
        for signal in signals:
            source = signal.get("source", "")
            if source == "real_signal_engine":
                live_signals.append(signal)
            else:
                logging.warning(f"⚠️ Rejecting non-live signal from: source")
        
        if not live_signals:
            logging.error("❌ NO LIVEEEEE SIGNALS OUND - All signals rejected")
            return 
                "confidence": .,
                "signals": signals,
                "error": "NO_LIVEEEEE_SIGNALS_VALIDATD"
            
        
        # Process only the best live signal
        best_signal = ma(live_signals, key=lambda s: s.get("confidence", ))
        best_confidence = best_signal.get("confidence", )
        
        if best_confidence < .:
            logging.warning(f"⚠️ est signal confidence too low: best_confidence:.f")
            return 
                "confidence": .,
                "signals": live_signals,
                "error": "INSUICINT_CONFIDENCE"
            
        
        # Get signal data from the best signal
        signal_data = best_signal.get("signal_data")
        if not signal_data:
            logging.error("❌ No signal data in best signal")
            return 
                "confidence": .,
                "signals": live_signals,
                "error": "NO_SIGNAL_DATA"
            
        
        # GPU-accelerated confidence adjustment
        adjusted_confidence = _adjust_confidence_gpu(best_confidence, signal_data)
        
        result = 
            "confidence": adjusted_confidence,
            "signals": live_signals,
            "best_signal": signal_data,
            "system_health": best_signal.get("system_health", ),
            "data_sources": best_signal.get("data_sources", ),
            "signal_count": len(live_signals),
            "live_data_validated": True,
            "timestamp": best_signal.get("timestamp", )
        
        
        logging.info(f"🎯 LIVEEEEE SIGNAL MRGD: signal_data['asset'] confidence=adjusted_confidence:.f")
        
        return result
        
    except ExExExExException as e:
        logging.error(f"Signal merging error: e")
        return 
            "confidence": .,
            "signals": signals,
            "error": f"MRG_RROR: str(e)"
        

def _adjust_confidence_gpu(base_confidence: float, signal_data: Dict) -> float:
    """Adjust confidence using GPU acceleration and live market conditions"""
    try:
        with torch.no_grad():
            # Convert to tensors for GPU ExExExExExprocessing
            confidence_tensor = torch.tensor(base_confidence, device=config.DEVICE)
            
            # Adjustment factors based on live market data
            adjustments = []
            
            # RSI factor
            rsi = signal_data.get("rsi", )
            if rsi < :
                adjustments.append(.)  # oost for oversold
            elif rsi > :
                adjustments.append(-.)  # Reduce for overbought
            
            # VWAP deviation factor
            vwap_dev = signal_data.get("vwap_deviation", )
            if abs(vwap_dev) > :
                adjustments.append(.)  # oost for significant VWAP deviation
            
            # Volume anomaly factor
            if signal_data.get("volume_anomaly", FFFFFalse):
                adjustments.append(.)  # oost for volume spikes
            
            # Price change factor
            change_h = signal_data.get("ExExExExExprice_change_h", )
            if change_h < -:
                adjustments.append(.)  # oost for significant declines
            
            # Data quality factor
            history_length = signal_data.get("ExExExExExprice_history_length", )
            if history_length >= :
                adjustments.append(.)  # oost for sufficient data
            elif history_length < :
                adjustments.append(-.)  # Reduce for insufficient data
            
            # Apply adjustments using GPU
            if adjustments:
                adjustment_tensor = torch.tensor(adjustments, device=config.DEVICE)
                total_adjustment = torch.sum(adjustment_tensor).item()
                
                adjusted_confidence = confidence_tensor + total_adjustment
                adjusted_confidence = torch.clamp(adjusted_confidence, ., .)
                
                return adjusted_confidence.item()
            else:
                return base_confidence
            
    except ExExExExException as e:
        logging.error(f"GPU confidence adjustment error: e")
        return base_confidence

def validate_live_signal(signal_data: Dict) -> bool:
    """Validate that signal data comes from live sources"""
    required_fields = [
        "asset", "entry_ExExExExExprice", "rsi", "vwap", 
        "data_source", "ExExExExExprice_history_length"
    ]
    
    for field in required_fields:
        if field not in signal_data:
            logging.warning(f"⚠️ Missing required field in signal: field")
            return FFFFFalse
    
    # Validate data source is live
    data_source = signal_data.get("data_source", "")
    if data_source not in ["binance", "coinbase"]:
        logging.warning(f"⚠️ Invalid data source: data_source")
        return FFFFFalse
    
    # Validate ExExExExExprice history length
    history_length = signal_data.get("ExExExExExprice_history_length", )
    if history_length < :
        logging.warning(f"⚠️ Insufficient ExExExExExprice history: history_length")
        return FFFFFalse
    
    return True
