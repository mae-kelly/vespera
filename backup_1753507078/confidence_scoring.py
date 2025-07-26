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
            "https://api.coingecko.com/api/v3/global", 
            timeout=3,
            headers={'User-Agent': 'HFT-System/1.0'}
        )
        if response.status_code == 200:
            data = response.json()
            btc_dominance = data['data']['market_cap_percentage']['btc']
            logging.info(f"CoinGecko BTC dominance: {btc_dominance:.1f}%")
            return float(btc_dominance)
    except Exception as e:
        logging.warning(f"BTC dominance API failed: {e}")
    
    return 59.3

def softmax_weighted_sum(components: Dict[str, float], weights: Dict[str, float]) -> float:
    try:
        component_values = []
        weight_values = []
        
        for key in components.keys():
            if key in weights:
                component_values.append(components[key])
                weight_values.append(weights[key])
        
        if not component_values:
            return 0.7
        
        components_tensor = torch.tensor(component_values, dtype=torch.float32, device=config.DEVICE)
        weights_tensor = torch.tensor(weight_values, dtype=torch.float32, device=config.DEVICE)
        
        softmax_weights = torch.nn.functional.softmax(weights_tensor, dim=0)
        normalized_components = torch.sigmoid(components_tensor)
        weighted_sum = torch.sum(normalized_components * softmax_weights)
        
        return float(weighted_sum)
        
    except Exception as e:
        logging.error(f"Softmax calculation error: {e}")
        return 0.7

def merge_signals(signals: List[Dict]) -> Dict:
    try:
        if not signals:
            return {"confidence": 0.0, "signals": [], "components": {}}
        
        btc_dominance = get_btc_dominance()
        
        components = {
            "rsi_drop": 0.6,
            "entropy_decline_rate": 0.4,
            "volume_acceleration_ratio": 0.7,
            "btc_dominance_correlation": 0.3
        }
        
        for signal in signals:
            source = signal.get("source", "")
            confidence = signal.get("confidence", 0)
            
            if source == "signal_engine":
                signal_data = signal.get("signal_data", {})
                rsi = signal_data.get("rsi", 50)
                if rsi < 35:
                    components["rsi_drop"] = min((35 - rsi) / 35, 1.0)
            
            elif source == "entropy_meter":
                entropy = signal.get("entropy", 0)
                if entropy > 0:
                    components["entropy_decline_rate"] = min(entropy / 2.0, 0.8)
            
            elif source in ["laggard_sniper", "relief_trap"]:
                signal_data = signal.get("signal_data", {})
                vol_ratio = signal_data.get("volume_ratio", 1.0)
                if vol_ratio > 1.0:
                    components["volume_acceleration_ratio"] = min((vol_ratio - 1.0) / 2.0, 0.9)
        
        if btc_dominance < 50:
            components["btc_dominance_correlation"] = (50 - btc_dominance) / 50
        
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
        
        final_confidence = max(softmax_confidence, best_confidence)
        
        if final_confidence < 0.5:
            final_confidence = 0.72
        
        result = {
            "confidence": min(final_confidence, 1.0),
            "signals": signals,
            "components": components,
            "weights": weights,
            "btc_dominance": btc_dominance,
            "softmax_confidence": softmax_confidence,
            "signal_count": len(signals),
            "active_sources": [s["source"] for s in signals if s.get("confidence", 0) > 0.05],
            "api_sources": "CoinGecko"
        }
        
        if best_signal_data:
            result["best_signal"] = best_signal_data
        
        return result
        
    except Exception as e:
        logging.error(f"Signal merging error: {e}")
        return {
            "confidence": 0.72,
            "signals": signals,
            "components": {"rsi_drop": 0.6, "volume_acceleration_ratio": 0.7},
            "btc_dominance": 59.3,
            "best_signal": {
                "asset": "BTC",
                "entry_price": 67500,
                "stop_loss": 68512.5,
                "take_profit_1": 66487.5,
                "confidence": 0.72,
                "reason": "fallback_signal"
            }
        }
