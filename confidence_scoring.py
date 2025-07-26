import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import logging
import requests
import time
from typing import Dict, List
import torch
import config

def get_btc_dominance() -> float:
    try:
        response = requests.get(
            "https://api.tradingview.com/chart/v1/indicators", 
            params={
                "symbol": "CRYPTOCAP:BTC.D",
                "timeframe": "1D",
                "indicators": "DOMINANCE"
            },
            timeout=5,
            headers={'User-Agent': 'HFT-System/1.0'}
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                dominance = data["data"][-1].get("value", 45.0)
                return float(dominance)
    except Exception:
        pass
    
    try:
        fallback_response = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
        if fallback_response.status_code == 200:
            data = fallback_response.json()
            btc_dominance = data['data']['market_cap_percentage']['btc']
            return float(btc_dominance)
    except Exception:
        pass
    
    return 45.0

def softmax_weighted_sum(components: Dict[str, float], weights: Dict[str, float]) -> float:
    try:
        component_values = []
        weight_values = []
        
        for key in components.keys():
            if key in weights:
                component_values.append(components[key])
                weight_values.append(weights[key])
        
        if not component_values:
            return 0.0
        
        components_tensor = torch.tensor(component_values, dtype=torch.float32, device=config.DEVICE)
        weights_tensor = torch.tensor(weight_values, dtype=torch.float32, device=config.DEVICE)
        
        softmax_weights = torch.nn.functional.softmax(weights_tensor, dim=0)
        normalized_components = torch.sigmoid(components_tensor)
        weighted_sum = torch.sum(normalized_components * softmax_weights)
        
        return float(weighted_sum)
        
    except Exception:
        return 0.0

def merge_signals(signals: List[Dict]) -> Dict:
    try:
        if not signals:
            return {"confidence": 0.0, "signals": [], "components": {}}
        
        btc_dominance = get_btc_dominance()
        
        components = {
            "rsi_drop": 0.0,
            "entropy_decline_rate": 0.0,
            "volume_acceleration_ratio": 0.0,
            "btc_dominance_correlation": 0.0
        }
        
        for signal in signals:
            source = signal.get("source", "")
            confidence = signal.get("confidence", 0)
            
            if source == "signal_engine":
                signal_data = signal.get("signal_data", {})
                rsi = signal_data.get("rsi", 50)
                if rsi < 30:
                    components["rsi_drop"] = (30 - rsi) / 30
            
            elif source == "entropy_meter":
                entropy = signal.get("entropy", 0)
                if entropy > 0:
                    components["entropy_decline_rate"] = min(entropy / 2.0, 1.0)
            
            elif source in ["laggard_sniper", "relief_trap"]:
                signal_data = signal.get("signal_data", {})
                vol_ratio = signal_data.get("volume_ratio", 1.0)
                if vol_ratio > 1.0:
                    components["volume_acceleration_ratio"] = min((vol_ratio - 1.0) / 2.0, 1.0)
        
        if btc_dominance < 45:
            components["btc_dominance_correlation"] = (45 - btc_dominance) / 45
        
        weights = {
            "rsi_drop": 0.35,
            "entropy_decline_rate": 0.25,
            "volume_acceleration_ratio": 0.30,
            "btc_dominance_correlation": 0.10
        }
        
        softmax_confidence = softmax_weighted_sum(components, weights)
        
        best_confidence = 0.0
        best_signal_data = None
        
        for signal in signals:
            confidence = signal.get("confidence", 0)
            if confidence > best_confidence:
                best_confidence = confidence
                if "signal_data" in signal:
                    best_signal_data = signal["signal_data"]
        
        final_confidence = (softmax_confidence * 0.6) + (best_confidence * 0.4)
        
        if btc_dominance < 40:
            final_confidence *= 1.1
        elif btc_dominance > 60:
            final_confidence *= 0.9
        
        result = {
            "confidence": min(final_confidence, 1.0),
            "signals": signals,
            "components": components,
            "weights": weights,
            "btc_dominance": btc_dominance,
            "softmax_confidence": softmax_confidence,
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
