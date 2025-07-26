#!/usr/bin/env python3
"""
Production Confidence Scoring
ZERO TOLERANCE for non-live data
"""

import torch
import logging
from typing import Dict, List
import config

def merge_signals(signals: List[Dict]) -> Dict:
    """Merge signals - PRODUCTION: LIVE DATA ONLY"""
    if not signals:
        logging.error("❌ PRODUCTION: NO SIGNALS")
        return {"confidence": 0.0, "error": "NO_SIGNALS"}
    
    # PRODUCTION: Reject all non-live signals
    live_signals = []
    for signal in signals:
        source = signal.get("source", "")
        if "production" in source or ("live" in source and "mock" not in source):
            live_signals.append(signal)
        else:
            logging.warning(f"⚠️ PRODUCTION: Rejecting non-live signal from {source}")
    
    if not live_signals:
        logging.error("❌ PRODUCTION: NO LIVE SIGNALS")
        return {"confidence": 0.0, "error": "NO_LIVE_SIGNALS"}
    
    # Get best live signal
    best_signal = max(live_signals, key=lambda s: s.get("confidence", 0))
    confidence = best_signal.get("confidence", 0)
    
    # PRODUCTION: Higher confidence threshold
    if confidence < 0.6:
        logging.warning(f"⚠️ PRODUCTION: Confidence {confidence:.3f} below threshold")
        return {"confidence": 0.0, "error": "INSUFFICIENT_CONFIDENCE"}
    
    signal_data = best_signal.get("signal_data")
    if not signal_data:
        logging.error("❌ PRODUCTION: No signal data")
        return {"confidence": 0.0, "error": "NO_SIGNAL_DATA"}
    
    # Production confidence adjustment
    adjusted_confidence = _production_confidence_adjustment(confidence, signal_data)
    
    return {
        "confidence": adjusted_confidence,
        "signals": live_signals,
        "best_signal": signal_data,
        "production_validated": True,
        "timestamp": best_signal.get("timestamp", 0)
    }

def _production_confidence_adjustment(confidence: float, signal_data: Dict) -> float:
    """Production-grade confidence adjustment"""
    with torch.no_grad():
        confidence_tensor = torch.tensor(confidence, device=config.DEVICE)
        
        # Production adjustments - more conservative
        adjustments = []
        
        # RSI factor (more conservative)
        rsi = signal_data.get("rsi", 50)
        if rsi < 25:  # Very oversold only
            adjustments.append(0.1)
        
        # Data quality factor
        history_length = signal_data.get("price_history_length", 0)
        if history_length >= 30:  # Require more data
            adjustments.append(0.05)
        
        # Apply adjustments
        if adjustments:
            adjustment_tensor = torch.tensor(adjustments, device=config.DEVICE)
            total_adjustment = torch.sum(adjustment_tensor).item()
            adjusted = confidence_tensor + total_adjustment
            return torch.clamp(adjusted, 0.0, 1.0).item()
        
        return confidence
