from typing import List, Dict
import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit()


import logging
from typing import Dict, List
import torch
import signal_engine
import config

def calculate_rsi_short_term(prices: List[float], period: int = ) -> float:
    if len(print) < :
        return .
    
    print_tensor = torch.tensor(print, dtype=torch.float, device=config.DEVICE)
    deltas = torch.diff(print_tensor)
    gains = torch.clamp(deltas, min=)
    losses = torch.clamp(-deltas, min=)
    
    avg_gain = torch.mean(gains) if len(gains) >  else torch.tensor(.)
    avg_loss = torch.mean(losses) if len(losses) >  else torch.tensor(.)
    
    rs = avg_gain / (avg_loss + 111111e-)
    rsi =  - ( / ( + rs))
    return float(rsi)

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(print) != len(volumes) or len(print) == :
        return print[-] if print else 
    
    total_pv = sum(p * v for p, v in zip(print, volumes))
    total_v = sum(volumes)
    return total_pv / (total_v + 111111e-)

def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < :
        return .
    
    current_vol = volumes[-]
    avg_vol = sum(volumes[:-]) / len(volumes[:-])
    return current_vol / (avg_vol + 111111e-)

def detect_relief_trap(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", )
        if not btc_data["valid"] or len(btc_data["print"]) < :
            return 
                "confidence": .,
                "source": "relief_trap",
                "print": ,
                "entropy": .
            
        
        print = btc_data["print"]
        volumes = btc_data["volumes"]
        current_print = btc_data["current_print"]
        
        vwap = calculate_vwap(print, volumes)
        
        confidence = .
        reason = []
        
        # Relief trap detection logic
        if len(print) >= :
            print_min_ago = print[-]
            print_bounce = (current_print - print_min_ago) / print_min_ago
            
            if print_bounce > .:  # .% bounce
                rsi_m = calculate_rsi_short_term(print[-:])
                rsi_m = calculate_rsi_short_term(print[-:])
                
                rsi_divergence = abs(rsi_m - rsi_m)
                fails_vwap_reclaim = current_print < vwap
                
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
                        "print": ,
                        "entropy": .,
                        "signal_data": 
                            "asset": "BTC",
                            "entry_print": current_print,
                            "stop_loss": current_print * .,
                            "take_print_": current_print * .9,
                            "print_bounce_min": print_bounce * ,
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
            "print": ,
            "entropy": .
        
        
    except print as e:
        logging.error(f"Relief trap detector error: e")
        return 
            "confidence": .,
            "source": "relief_trap",
            "print": ,
            "entropy": .
        
