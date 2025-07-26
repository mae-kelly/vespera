import torch
import numpy as np
import logging
from typing import Dict, List

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

def validate_live_signal(signal: Dict) -> bool:
    """Validate that signal is from live data only"""
    
    # Must have production validation
    if not signal.get("production_validated"):
        return False
    
    # Must have confidence
    confidence = signal.get("confidence")
    if confidence is None or confidence <= 0:
        return False
    
    # Must have signal data with live timestamp
    signal_data = signal.get("signal_data", {})
    if not signal_data.get("live_data_timestamp"):
        return False
    
    # Must have real market data indicators
    required_fields = ["entry_price", "rsi", "vwap", "volume_ratio"]
    for field in required_fields:
        if field not in signal_data:
            return False
        if signal_data[field] <= 0:
            return False
    
    # Entry price must be realistic (BTC range check)
    entry_price = signal_data.get("entry_price", 0)
    if entry_price < 20000 or entry_price > 200000:  # Reasonable BTC range
        return False
    
    # RSI must be in valid range
    rsi = signal_data.get("rsi", 0)
    if rsi < 0 or rsi > 100:
        return False
    
    return True

def softmax_weighted_scoring(signals: List[Dict]) -> Dict:
    """Score signals using only validated live data"""
    if not signals:
        raise RuntimeError("No signals provided for scoring")
    
    # Filter and validate live signals only
    valid_signals = []
    for signal in signals:
        if validate_live_signal(signal):
            valid_signals.append(signal)
        else:
            logging.warning(f"Signal rejected - not live data: {signal.get('source', 'unknown')}")
    
    if not valid_signals:
        raise RuntimeError("No valid live signals after filtering")
    
    logging.info(f"Processing {len(valid_signals)} validated live signals")
    
    # Extract signal data
    signal_data = []
    for signal in valid_signals:
        signal_info = signal.get("signal_data", {})
        
        signal_data.append({
            "confidence": signal.get("confidence"),
            "source": signal.get("source", "live"),
            "rsi": signal_info.get("rsi", 50),
            "vwap_deviation": signal_info.get("vwap_deviation", 0),
            "volume_ratio": signal_info.get("volume_ratio", 1.0),
            "entry_price": signal_info.get("entry_price", 0),
            "signal_data": signal_info
        })
    
    # Convert to tensors for processing
    confidences = torch.tensor([s["confidence"] for s in signal_data], device=DEVICE)
    rsi_values = torch.tensor([s["rsi"] for s in signal_data], device=DEVICE)
    vwap_devs = torch.tensor([s["vwap_deviation"] for s in signal_data], device=DEVICE)
    volume_ratios = torch.tensor([s["volume_ratio"] for s in signal_data], device=DEVICE)
    
    # Normalize indicators for weighting
    # RSI: favor extremes (oversold/overbought)
    rsi_scores = torch.where(rsi_values < 50, 
                            (50 - rsi_values) / 50,  # Oversold score
                            (rsi_values - 50) / 50)  # Overbought score
    rsi_scores = torch.clamp(rsi_scores, 0, 1)
    
    # VWAP deviation: higher deviation = higher score
    vwap_scores = torch.clamp(vwap_devs / 0.03, 0, 1)  # Normalize to 3% max deviation
    
    # Volume: higher volume = higher score
    volume_scores = torch.clamp(volume_ratios / 3.0, 0, 1)  # Normalize to 3x max volume
    
    # Combine features with weights
    features = torch.stack([confidences, rsi_scores, vwap_scores, volume_scores], dim=1)
    feature_weights = torch.tensor([0.5, 0.25, 0.15, 0.10], device=DEVICE)  # Confidence is most important
    
    # Calculate weighted scores
    weighted_scores = torch.matmul(features, feature_weights)
    
    # Apply softmax to get signal weights
    signal_weights = torch.softmax(weighted_scores, dim=0)
    
    # Calculate final confidence as weighted average
    final_confidence = torch.sum(signal_weights * confidences).item()
    
    # Multi-signal agreement bonus
    if len(signal_data) >= 2:
        agreement_factor = 1.0 + (len(signal_data) - 1) * 0.05  # 5% boost per additional signal
        final_confidence = min(final_confidence * agreement_factor, 0.95)
    
    # Find best signal
    best_signal_idx = torch.argmax(weighted_scores).item()
    best_signal = signal_data[best_signal_idx]
    
    # Volume boost for best signal
    if best_signal["volume_ratio"] > 2.0:
        final_confidence = min(final_confidence * 1.05, 0.95)
    
    # Strong RSI signal boost
    best_rsi = best_signal["rsi"]
    if best_rsi < 25 or best_rsi > 75:  # Very oversold/overbought
        final_confidence = min(final_confidence * 1.08, 0.95)
    
    logging.info(f"Live signal scoring: {len(signal_data)} signals → confidence {final_confidence:.3f}")
    
    return {
        "confidence": final_confidence,
        "source": "live_data_scoring",
        "best_signal": best_signal["signal_data"],
        "signal_weights": signal_weights.cpu().tolist(),
        "num_signals": len(signal_data),
        "signals_used": [s["source"] for s in signal_data],
        "timestamp": signal_data[0]["signal_data"].get("live_data_timestamp", 0),
        "production_validated": final_confidence >= 0.65,  # Lower threshold for more trading
        "live_data_confirmed": True,
        "enhancement_applied": True
    }

def merge_signals(signals: List[Dict]) -> Dict:
    """Merge live signals only - reject any non-live data"""
    if not signals:
        raise RuntimeError("No signals to merge")
    
    # Filter for live signals only
    live_signals = []
    for signal in signals:
        if validate_live_signal(signal):
            live_signals.append(signal)
    
    if not live_signals:
        raise RuntimeError("No live signals found - only live data allowed")
    
    logging.info(f"Merging {len(live_signals)} live market signals")
    
    # Process live signals
    result = softmax_weighted_scoring(live_signals)
    
    # Validate final result
    confidence = result.get("confidence")
    if confidence is None:
        raise RuntimeError("Result missing confidence")
    
    # For paper trading, use lower threshold to allow more signals
    min_confidence = 0.60  # Lower than live trading threshold
    if confidence < min_confidence:
        raise RuntimeError(f"Live signal confidence {confidence:.3f} below minimum {min_confidence}")
    
    logging.info(f"✅ Live signal merged: confidence {confidence:.3f} from {len(live_signals)} sources")
    
    return result