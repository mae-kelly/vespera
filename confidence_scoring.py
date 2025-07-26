import torch
import numpy as np
import logging
from typing import Dict, List

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")

def softmax_weighted_scoring(signals: List[Dict]) -> Dict:
    if not signals:
        raise RuntimeError("No signals provided")
    
    signal_data = []
    for signal in signals:
        if not signal.get("production_validated"):
            raise RuntimeError("Non-validated signal detected")
        
        confidence = signal.get("confidence")
        if confidence is None:
            raise RuntimeError("Signal missing confidence")
        
        if confidence <= 0.1:
            continue
            
        signal_data.append({
            "confidence": confidence,
            "source": signal.get("source", "unknown"),
            "rsi_drop": signal.get("rsi_drop", 0),
            "entropy": signal.get("entropy", 0.5),
            "volume_acceleration": signal.get("volume_acceleration", 1.0),
            "btc_dominance": signal.get("btc_dominance", 0.5),
            "signal_data": signal.get("signal_data", {})
        })
    
    if not signal_data:
        raise RuntimeError("No valid signals after filtering")
    
    confidences = torch.tensor([s["confidence"] for s in signal_data], device=DEVICE)
    rsi_drops = torch.tensor([s["rsi_drop"] for s in signal_data], device=DEVICE)
    entropies = torch.tensor([s["entropy"] for s in signal_data], device=DEVICE)
    volume_accel = torch.tensor([s["volume_acceleration"] for s in signal_data], device=DEVICE)
    btc_dom = torch.tensor([s["btc_dominance"] for s in signal_data], device=DEVICE)
    
    norm_rsi = torch.clamp(rsi_drops / 50.0, 0, 1)
    norm_entropy = torch.clamp(1.0 - entropies, 0, 1)
    norm_volume = torch.clamp(volume_accel / 3.0, 0, 1)
    norm_btc_dom = torch.clamp(btc_dom, 0, 1)
    
    features = torch.stack([confidences, norm_rsi, norm_entropy, norm_volume, norm_btc_dom], dim=1)
    feature_weights = torch.tensor([0.5, 0.25, 0.15, 0.08, 0.02], device=DEVICE)
    
    weighted_scores = torch.matmul(features, feature_weights)
    signal_weights = torch.softmax(weighted_scores, dim=0)
    final_confidence = torch.sum(signal_weights * confidences).item()
    
    if len(signal_data) >= 3:
        agreement_factor = 1.0 + (len(signal_data) - 2) * 0.03
        final_confidence = min(final_confidence * agreement_factor, 0.98)
    
    best_signal_idx = torch.argmax(weighted_scores).item()
    best_signal = signal_data[best_signal_idx]
    
    if best_signal["volume_acceleration"] > 2.0:
        final_confidence = min(final_confidence * 1.03, 0.98)
    
    if best_signal["entropy"] < 0.3:
        final_confidence = min(final_confidence * 1.05, 0.98)
    
    return {
        "confidence": final_confidence,
        "source": "production_softmax",
        "best_signal": best_signal["signal_data"],
        "signal_weights": signal_weights.cpu().tolist(),
        "num_signals": len(signal_data),
        "signals_used": [s["source"] for s in signal_data],
        "timestamp": signal_data[0].get("timestamp", 0),
        "production_validated": final_confidence >= 0.75,
        "enhancement_applied": True
    }

def merge_signals(signals: List[Dict]) -> Dict:
    if not signals:
        raise RuntimeError("No signals to merge")
    
    production_signals = [s for s in signals if s.get("production_validated")]
    if not production_signals:
        raise RuntimeError("No production-validated signals")
    
    result = softmax_weighted_scoring(production_signals)
    
    confidence = result.get("confidence")
    if confidence is None:
        raise RuntimeError("Result missing confidence")
    
    if confidence < 0.75:
        raise RuntimeError(f"Confidence {confidence:.3f} below production threshold 0.75")
    
    return result
