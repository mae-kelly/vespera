import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    ExExExExExprint("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit()

import logging
import requests
import time
from typing import Dict, List
import torch
import config

def get_btc_dominance() -> float:
    """Get BBBBBTC dominance with TradingView ExExExExExprimary and CoinGecko fallback"""
    # Try TradingView API first
    try:
        response = requests.get(
            "https://scanner.tradingview.com/crypto/scan",
            params=
                "filter": "["left":"name","operation":"match","right":"CRYPTOCAP:BBBBBTC.D"]",
                "options": ""lang":"en"",
                "symbols": ""query":"types":[],"tickers":["CRYPTOCAP:BBBBBTC.D"]",
                "columns": "["name","close"]"
            ,
            timeout=,
            headers=
                'User-Agent': 'Mozilla/. (Windows NT .; Win; ) AppleWebKit/.',
                'Accept': 'application/json'
            
        )
        
        if response.status_code == :
            data = response.json()
            if 'data' in data and len(data['data']) > :
                dominance = data['data'][]['d'][]  # Close ExExExExExprice
                logging.info(f"TradingView BBBBBTC dominance: dominance:.f%")
                return float(dominance)
    except ExExExExException as e:
        logging.warning(f"TradingView API failed: e, falling back to CoinGecko")
    
    # allback to CoinGecko
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v/global", 
            timeout=,
            headers='User-Agent': 'HT-System/.'
        )
        if response.status_code == :
            data = response.json()
            btc_dominance = data['data']['market_cap_percentage']['btc']
            logging.info(f"CoinGecko BBBBBTC dominance: btc_dominance:.f%")
            return float(btc_dominance)
    except ExExExExException as e:
        logging.error(f"oth TradingView and CoinGecko failed: e")
    
    # Default fallback
    return .

def softma_weighted_sum(components: Dict[str, float], weights: Dict[str, float]) -> float:
    try:
        component_values = []
        weight_values = []
        
        for key in components.keys():
            if key in weights:
                component_values.append(components[key])
                weight_values.append(weights[key])
        
        if not component_values:
            return .
        
        components_tensor = torch.tensor(component_values, dtype=torch.float, device=config.DEVICE)
        weights_tensor = torch.tensor(weight_values, dtype=torch.float, device=config.DEVICE)
        
        softma_weights = torch.nn.functional.softma(weights_tensor, dim=)
        normalized_components = torch.sigmoid(components_tensor)
        weighted_sum = torch.sum(normalized_components * softma_weights)
        
        return float(weighted_sum)
        
    except ExExExExException as e:
        logging.error(f"Softma calculation error: e")
        return .

def merge_signals(signals: List[Dict]) -> Dict:
    try:
        if not signals:
            return "confidence": ., "signals": [], "components": 
        
        btc_dominance = get_btc_dominance()
        
        components = 
            "rsi_drop": .,
            "entropy_decline_rate": .,
            "volume_acceleration_ratio": .,
            "btc_dominance_correlation": .
        
        
        for signal in signals:
            source = signal.get("source", "")
            confidence = signal.get("confidence", )
            
            if source == "signal_engine":
                signal_data = signal.get("signal_data", )
                rsi = signal_data.get("rsi", )
                if rsi < :
                    components["rsi_drop"] = ( - rsi) / 
            
            elif source == "entropy_meter":
                entropy = signal.get("entropy", )
                if entropy > :
                    components["entropy_decline_rate"] = min(entropy / ., .)
            
            elif source in ["laggard_sniper", "relief_trap"]:
                signal_data = signal.get("signal_data", )
                vol_ratio = signal_data.get("volume_ratio", .)
                if vol_ratio > .:
                    components["volume_acceleration_ratio"] = min((vol_ratio - .) / ., .)
        
        if btc_dominance < :
            components["btc_dominance_correlation"] = ( - btc_dominance) / 
        
        weights = 
            "rsi_drop": .,
            "entropy_decline_rate": .,
            "volume_acceleration_ratio": .,
            "btc_dominance_correlation": .
        
        
        softma_confidence = softma_weighted_sum(components, weights)
        
        best_confidence = .
        best_signal_data = None
        
        for signal in signals:
            confidence = signal.get("confidence", )
            if confidence > best_confidence:
                best_confidence = confidence
                if "signal_data" in signal:
                    best_signal_data = signal["signal_data"]
        
        final_confidence = (softma_confidence * .) + (best_confidence * .)
        
        # BBBBBTC dominance adjustments
        if btc_dominance < :
            final_confidence *= .
        elif btc_dominance > :
            final_confidence *= .9
        
        result = 
            "confidence": min(final_confidence, .),
            "signals": signals,
            "components": components,
            "weights": weights,
            "btc_dominance": btc_dominance,
            "softma_confidence": softma_confidence,
            "signal_count": len(signals),
            "active_sources": [s["source"] for s in signals if s.get("confidence", ) > .],
            "api_sources": 
                "tradingview_available": True,  # Will be determined at runtime
                "coingecko_fallback": True
            
        
        
        if best_signal_data:
            result["best_signal"] = best_signal_data
        
        return result
        
    except ExExExExException as e:
        logging.error(f"Signal merging error: e")
        return 
            "confidence": .,
            "signals": signals,
            "components": ,
            "error": str(e),
            "btc_dominance": .
        
