import torch
import numpy as np
import logging
from typing import Dict, List, Optional
import cupy_fallback as cp

def softmax_weighted_scoring(signals: List[Dict]) -> Dict:
    """
    Implement softmax-weighted signal combination as specified
    """
    if not signals:
        return {"confidence": 0.0, "error": "NO_SIGNALS"}
    
    # Extract signal components
    signal_data = []
    for signal in signals:
        if signal.get("confidence", 0) > 0.1:
            signal_data.append({
                "confidence": signal.get("confidence", 0),
                "source": signal.get("source", "unknown"),
                "rsi_drop": signal.get("rsi_drop", 0),
                "entropy": signal.get("entropy", 0.5),
                "volume_acceleration": signal.get("volume_acceleration", 1.0),
                "btc_dominance": signal.get("btc_dominance", 0.5),
                "signal_data": signal.get("signal_data", {})
            })
    
    if not signal_data:
        return {"confidence": 0.0, "error": "NO_VALID_SIGNALS"}
    
    # Convert to tensors for GPU computation
    confidences = torch.tensor([s["confidence"] for s in signal_data], device=cp.DEVICE)
    rsi_drops = torch.tensor([s["rsi_drop"] for s in signal_data], device=cp.DEVICE)
    entropies = torch.tensor([s["entropy"] for s in signal_data], device=cp.DEVICE)
    volume_accel = torch.tensor([s["volume_acceleration"] for s in signal_data], device=cp.DEVICE)
    btc_dom = torch.tensor([s["btc_dominance"] for s in signal_data], device=cp.DEVICE)
    
    # Normalize components to [0,1] range
    norm_rsi = torch.clamp(rsi_drops / 50.0, 0, 1)  # RSI drops up to 50 points
    norm_entropy = torch.clamp(1.0 - entropies, 0, 1)  # Lower entropy = higher signal
    norm_volume = torch.clamp(volume_accel / 3.0, 0, 1)  # Volume acceleration up to 3x
    norm_btc_dom = torch.clamp(btc_dom, 0, 1)  # BTC dominance correlation
    
    # Feature matrix for softmax weighting
    features = torch.stack([
        confidences,
        norm_rsi,
        norm_entropy,
        norm_volume,
        norm_btc_dom
    ], dim=1)  # Shape: [num_signals, 5]
    
    # Learned weights for each feature (can be trained over time)
    feature_weights = torch.tensor([
        0.4,  # Base confidence
        0.25, # RSI drop importance  
        0.15, # Entropy decay importance
        0.15, # Volume acceleration
        0.05  # BTC dominance correlation
    ], device=cp.DEVICE)
    
    # Calculate weighted scores
    weighted_scores = torch.matmul(features, feature_weights)
    
    # Apply softmax to get signal weights
    signal_weights = torch.softmax(weighted_scores, dim=0)
    
    # Calculate final confidence as weighted average
    final_confidence = torch.sum(signal_weights * confidences).item()
    
    # Find best signal (highest weighted score)
    best_signal_idx = torch.argmax(weighted_scores).item()
    best_signal = signal_data[best_signal_idx]
    
    # Apply confidence enhancement for strong multi-signal agreement
    if len(signal_data) >= 3:
        # Multi-signal bonus
        agreement_factor = 1.0 + (len(signal_data) - 2) * 0.05  # 5% bonus per extra signal
        final_confidence = min(final_confidence * agreement_factor, 0.95)
    
    # Apply entropy-based confidence adjustment
    entropy_factor = best_signal["entropy"]
    if entropy_factor < 0.3:  # Low entropy = high certainty
        final_confidence = min(final_confidence * 1.1, 0.95)
    
    # Volume confirmation boost
    if best_signal["volume_acceleration"] > 2.0:
        final_confidence = min(final_confidence * 1.05, 0.95)
    
    # Create enhanced result
    result = {
        "confidence": final_confidence,
        "source": "softmax_weighted",
        "best_signal": best_signal["signal_data"],
        "signal_weights": signal_weights.cpu().tolist(),
        "weighted_scores": weighted_scores.cpu().tolist(),
        "num_signals": len(signal_data),
        "signals_used": [s["source"] for s in signal_data],
        "timestamp": signal_data[0].get("timestamp", 0),
        "production_validated": final_confidence > 0.75,
        "enhancement_applied": True
    }
    
    # Add technical details
    if best_signal["signal_data"]:
        result["signal_data"] = best_signal["signal_data"]
        result["signal_data"]["confidence_components"] = {
            "base_confidence": confidences[best_signal_idx].item(),
            "rsi_component": norm_rsi[best_signal_idx].item(),
            "entropy_component": norm_entropy[best_signal_idx].item(),
            "volume_component": norm_volume[best_signal_idx].item(),
            "btc_dominance": norm_btc_dom[best_signal_idx].item()
        }
    
    return result

def merge_signals(signals: List[Dict]) -> Dict:
    """
    Enhanced signal merging with softmax weighting
    """
    try:
        # Use softmax weighted scoring
        result = softmax_weighted_scoring(signals)
        
        # Validate result
        confidence = result.get("confidence", 0)
        if confidence < 0.75:
            logging.info(f"Signal confidence {confidence:.3f} below production threshold")
            result["error"] = f"BELOW_PRODUCTION_THRESHOLD_0.75"
        
        return result
        
    except Exception as e:
        logging.error(f"Enhanced confidence scoring error: {e}")
        # Fallback to simple max confidence
        if signals:
            best = max(signals, key=lambda s: s.get("confidence", 0))
            return {
                "confidence": best.get("confidence", 0),
                "best_signal": best.get("signal_data", {}),
                "source": "fallback_scoring",
                "error": f"SOFTMAX_ERROR_{str(e)}"
            }
        return {"confidence": 0.0, "error": "CRITICAL_SCORING_ERROR"}

# Additional utility functions
def calculate_rsi_drop_normalized(current_rsi: float, previous_rsi: float) -> float:
    """Calculate normalized RSI drop for scoring"""
    if previous_rsi > current_rsi:
        return min((previous_rsi - current_rsi) / 30.0, 1.0)  # Normalize to 30-point drop = 1.0
    return 0.0

def calculate_entropy_decay_rate(entropy_history: List[float]) -> float:
    """Calculate entropy decay rate (dS/dt)"""
    if len(entropy_history) < 3:
        return 0.0
    
    # Simple linear regression slope
    n = len(entropy_history)
    x = list(range(n))
    y = entropy_history
    
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0.0
    
    slope = numerator / denominator
    return max(-slope, 0.0)  # Negative slope = entropy decay = positive signal

def get_btc_dominance_correlation() -> float:
    """
    Calculate BTC dominance correlation (placeholder for TradingView API)
    In production, this would fetch from TradingView API
    """
    # Simulated BTC dominance calculation
    # In real implementation, fetch from TradingView API
    import time
    dominance_sim = 0.45 + 0.1 * np.sin(time.time() / 3600)  # Simulate daily cycle
    return np.clip(dominance_sim, 0.4, 0.6)
