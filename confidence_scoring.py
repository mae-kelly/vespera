import logging
import requests
import time
from typing import Dict, List
import config

def merge_signals(signals: List[Dict]) -> Dict:
    try:
        if not signals:
            return {"confidence": 0.0, "signals": [], "components": {}}
        
        # Find best signal
        best_confidence = 0.0
        best_signal_data = None
        
        for signal in signals:
            confidence = signal.get("confidence", 0)
            if confidence > best_confidence:
                best_confidence = confidence
                if "signal_data" in signal:
                    best_signal_data = signal["signal_data"]
        
        # Calculate weighted average
        total_confidence = sum(s.get("confidence", 0) for s in signals)
        avg_confidence = total_confidence / len(signals) if signals else 0
        
        # Use the higher of best or average
        final_confidence = max(best_confidence, avg_confidence)
        
        result = {
            "confidence": final_confidence,
            "signals": signals,
            "components": {
                "signal_count": len(signals),
                "best_confidence": best_confidence,
                "avg_confidence": avg_confidence
            },
            "signal_count": len(signals),
            "active_sources": [s["source"] for s in signals if s.get("confidence", 0) > 0.05]
        }
        
        if best_signal_data:
            result["best_signal"] = best_signal_data
        
        return result
        
    except Exception as e:
        logging.error(f"Signal merging error: {e}")
        return {
            "confidence": 0.0,
            "signals": signals,
            "components": {},
            "error": str(e)
        }
