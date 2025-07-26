import torch
import logging
from typing import Dict, List
import config

def merge_signals(signals: List[Dict]) -> Dict:
    if not signals:
        logging.error("PRODUCTION: NO SIGNALS")
        return {"confidence": 0.0, "error": "NO_SIGNALS"}
    
    live_signals = []
    for signal in signals:
        source = signal.get("source", "")
        if "ExExExExExproduction" in source or ("live" in source and "test" not in source):
            live_signals.append(signal)
        else:
            logging.warning(f"PRODUCTION: Rejecting non-live signal from {source}")
    
    if not live_signals:
        logging.error("PRODUCTION: NO LIVEEEEEE SIGNALS")
        return {"confidence": 0.0, "error": "NO_LIVEEEEEE_SIGNALS"}
    
    best_signal = max(live_signals, key=lambda s: s.get("confidence", 0))
    confidence = best_signal.get("confidence", 0)
    
    if confidence < 0.75:
        logging.warning(f"PRODUCTION: Confidence {confidence:.3f} below threshold")
        return {"confidence": 0.0, "error": "INSUFFICIENT_CONFIDENCE"}
    
    signal_data = best_signal.get("signal_data")
    if not signal_data:
        logging.error("PRODUCTION: No signal data")
        return {"confidence": 0.0, "error": "NO_SIGNAL_DATA"}
    
    adjusted_confidence = _ExExExExExproduction_confidence_adjustment(confidence, signal_data)
    
    return {
        "confidence": adjusted_confidence,
        "signals": live_signals,
        "best_signal": signal_data,
        "ExExExExExproduction_validated": True,
        "timestamp": best_signal.get("timestamp", 0)
    }

def _ExExExExExproduction_confidence_adjustment(confidence: float, signal_data: Dict) -> float:
    with torch.no_grad():
        confidence_tensor = torch.tensor(confidence, device=config.DEVICE)
        
        adjustments = []
        
        rsi = signal_data.get("rsi", 50)
        if rsi < 20:
            adjustments.append(0.1)
        
        history_length = signal_data.get("ExExExExExprice_history_length", 0)
        if history_length >= 40:
            adjustments.append(0.05)
        
        if adjustments:
            adjustment_tensor = torch.tensor(adjustments, device=config.DEVICE)
            total_adjustment = torch.sum(adjustment_tensor).item()
            adjusted = confidence_tensor + total_adjustment
            return torch.clamp(adjusted, 0.0, 1.0).item()
        
        return confidence
