import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()

import logging
from typing import Dict, List
import torch
import signal_engine
import config

def calculate_rsi_short_term(prices: List[float], period: int = ) -> float:
    if len(prices) < :
        return .
    
    prices_tensor = torch.tensor(prices, dtype=torch.float, device=config.DVIC)
    deltas = torch.diff(prices_tensor)
    gains = torch.clamp(deltas, min=)
    losses = torch.clamp(-deltas, min=)
    
    avg_gain = torch.mean(gains) if len(gains) >  else torch.tensor(.)
    avg_loss = torch.mean(losses) if len(losses) >  else torch.tensor(.)
    
    rs = avg_gain / (avg_loss + e-)
    rsi =  - ( / ( + rs))
    return float(rsi)

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == :
        return prices[-] if prices else 
    
    total_pv = sum(p * v for p, v in zip(prices, volumes))
    total_v = sum(volumes)
    return total_pv / (total_v + e-)

def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < :
        return .
    
    current_vol = volumes[-]
    avg_vol = sum(volumes[:-]) / len(volumes[:-])
    return current_vol / (avg_vol + e-)

def detect_relief_trap(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("TC", )
        if not btc_data["valid"] or len(btc_data["prices"]) < :
            return 
                "confidence": .,
                "source": "relief_trap",
                "priority": ,
                "entropy": .
            
        
        prices = btc_data["prices"]
        volumes = btc_data["volumes"]
        current_price = btc_data["current_price"]
        
        vwap = calculate_vwap(prices, volumes)
        
        confidence = .
        reason = []
        
        # Relief trap detection logic
        if len(prices) >= :
            price_min_ago = prices[-]
            price_bounce = (current_price - price_min_ago) / price_min_ago
            
            if price_bounce > .:  # .% bounce
                rsi_m = calculate_rsi_short_term(prices[-:])
                rsi_m = calculate_rsi_short_term(prices[-:])
                
                rsi_divergence = abs(rsi_m - rsi_m)
                fails_vwap_reclaim = current_price < vwap
                
                if rsi_divergence > :
                    confidence += .
                    reason.append("rsi_divergence")
                
                if fails_vwap_reclaim:
                    confidence += .
                    reason.append("failed_vwap_reclaim")
                
                volume_ratio = calculate_volume_ratio(volumes)
                if volume_ratio > .:
                    confidence += .
                    reason.append("elevated_volume")
                
                if confidence > .:
                    return 
                        "confidence": min(confidence, .),
                        "source": "relief_trap",
                        "priority": ,
                        "entropy": .,
                        "signal_data": 
                            "asset": "TC",
                            "entry_price": current_price,
                            "stop_loss": current_price * .,
                            "take_profit_": current_price * .9,
                            "price_bounce_min": price_bounce * ,
                            "rsi_m": rsi_m,
                            "rsi_m": rsi_m,
                            "rsi_divergence": rsi_divergence,
                            "vwap": vwap,
                            "failed_vwap_reclaim": fails_vwap_reclaim,
                            "volume_ratio": volume_ratio,
                            "reason": " + ".join(reason)
                        
                    
        
        return 
            "confidence": .,
            "source": "relief_trap",
            "priority": ,
            "entropy": .
        
        
    ecept ception as e:
        logging.error(f"Relief trap detector error: e")
        return 
            "confidence": .,
            "source": "relief_trap",
            "priority": ,
            "entropy": .
        
