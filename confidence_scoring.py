#!/usr/bin/env python3
"""
Real Confidence Scoring for HFT System
ZERO MOCK DATA - Only processes signals from live market feeds
"""

import torch
import logging
from typing import Dict, List
import config

def merge_signals(signals: List[Dict]) -> Dict:
    """Merge signals from live data sources only"""
    try:
        if not signals:
            logging.error("❌ NO SIGNALS TO MERGE - Live data required")
            return {
                "confidence": 0.0,
                "signals": [],
                "error": "NO_LIVE_SIGNALS"
            }
        
        # Validate all signals are from live sources
        live_signals = []
        for signal in signals:
            source = signal.get("source", "")
            if source == "real_signal_engine":
                live_signals.append(signal)
            else:
                logging.warning(f"⚠️ Rejecting non-live signal from: {source}")
        
        if not live_signals:
            logging.error("❌ NO LIVE SIGNALS FOUND - All signals rejected")
            return {
                "confidence": 0.0,
                "signals": signals,
                "error": "NO_LIVE_SIGNALS_VALIDATED"
            }
        
        # Process only the best live signal
        best_signal = max(live_signals, key=lambda s: s.get("confidence", 0))
        best_confidence = best_signal.get("confidence", 0)
        
        if best_confidence < 0.3:
            logging.warning(f"⚠️ Best signal confidence too low: {best_confidence:.3f}")
            return {
                "confidence": 0.0,
                "signals": live_signals,
                "error": "INSUFFICIENT_CONFIDENCE"
            }
        
        # Get signal data from the best signal
        signal_data = best_signal.get("signal_data")
        if not signal_data:
            logging.error("❌ No signal data in best signal")
            return {
                "confidence": 0.0,
                "signals": live_signals,
                "error": "NO_SIGNAL_DATA"
            }
        
        # GPU-accelerated confidence adjustment
        adjusted_confidence = _adjust_confidence_gpu(best_confidence, signal_data)
        
        result = {
            "confidence": adjusted_confidence,
            "signals": live_signals,
            "best_signal": signal_data,
            "system_health": best_signal.get("system_health", {}),
            "data_sources": best_signal.get("data_sources", {}),
            "signal_count": len(live_signals),
            "live_data_validated": True,
            "timestamp": best_signal.get("timestamp", 0)
        }
        
        logging.info(f"🎯 LIVE SIGNAL MERGED: {signal_data['asset']} confidence={adjusted_confidence:.3f}")
        
        return result
        
    except Exception as e:
        logging.error(f"Signal merging error: {e}")
        return {
            "confidence": 0.0,
            "signals": signals,
            "error": f"MERGE_ERROR: {str(e)}"
        }

def _adjust_confidence_gpu(base_confidence: float, signal_data: Dict) -> float:
    """Adjust confidence using GPU acceleration and live market conditions"""
    try:
        with torch.no_grad():
            # Convert to tensors for GPU processing
            confidence_tensor = torch.tensor(base_confidence, device=config.DEVICE)
            
            # Adjustment factors based on live market data
            adjustments = []
            
            # RSI factor
            rsi = signal_data.get("rsi", 50)
            if rsi < 30:
                adjustments.append(0.1)  # Boost for oversold
            elif rsi > 70:
                adjustments.append(-0.1)  # Reduce for overbought
            
            # VWAP deviation factor
            vwap_dev = signal_data.get("vwap_deviation", 0)
            if abs(vwap_dev) > 2:
                adjustments.append(0.05)  # Boost for significant VWAP deviation
            
            # Volume anomaly factor
            if signal_data.get("volume_anomaly", False):
                adjustments.append(0.08)  # Boost for volume spikes
            
            # Price change factor
            change_24h = signal_data.get("price_change_24h", 0)
            if change_24h < -5:
                adjustments.append(0.12)  # Boost for significant declines
            
            # Data quality factor
            history_length = signal_data.get("price_history_length", 0)
            if history_length >= 50:
                adjustments.append(0.03)  # Boost for sufficient data
            elif history_length < 20:
                adjustments.append(-0.05)  # Reduce for insufficient data
            
            # Apply adjustments using GPU
            if adjustments:
                adjustment_tensor = torch.tensor(adjustments, device=config.DEVICE)
                total_adjustment = torch.sum(adjustment_tensor).item()
                
                adjusted_confidence = confidence_tensor + total_adjustment
                adjusted_confidence = torch.clamp(adjusted_confidence, 0.0, 1.0)
                
                return adjusted_confidence.item()
            else:
                return base_confidence
            
    except Exception as e:
        logging.error(f"GPU confidence adjustment error: {e}")
        return base_confidence

def validate_live_signal(signal_data: Dict) -> bool:
    """Validate that signal data comes from live sources"""
    required_fields = [
        "asset", "entry_price", "rsi", "vwap", 
        "data_source", "price_history_length"
    ]
    
    for field in required_fields:
        if field not in signal_data:
            logging.warning(f"⚠️ Missing required field in signal: {field}")
            return False
    
    # Validate data source is live
    data_source = signal_data.get("data_source", "")
    if data_source not in ["binance", "coinbase"]:
        logging.warning(f"⚠️ Invalid data source: {data_source}")
        return False
    
    # Validate price history length
    history_length = signal_data.get("price_history_length", 0)
    if history_length < 10:
        logging.warning(f"⚠️ Insufficient price history: {history_length}")
        return False
    
    return True
