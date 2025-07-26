from typing import List, Dict
import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)


import logging
from typing import Dict, List
import torch
import signal_engine
import config

def calculate_rsi_short_term(prices: List[float], period: int = 14) -> float:
    if len(prices) < 2:
        return 50.0
    
    prices_tensor = torch.tensor(prices, dtype=torch.float32, device=config.DEVICE)
    deltas = torch.diff(prices_tensor)
    gains = torch.clamp(deltas, min=0)
    losses = torch.clamp(-deltas, min=0)
    
    avg_gain = torch.mean(gains) if len(gains) > 0 else torch.tensor(0.0)
    avg_loss = torch.mean(losses) if len(losses) > 0 else torch.tensor(0.0)
    
    rs = avg_gain / (avg_loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    
    total_pv = sum(p * v for p, v in zip(prices, volumes))
    total_v = sum(volumes)
    return total_pv / (total_v + 1e-8)

def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < 3:
        return 1.0
    
    current_vol = volumes[-1]
    avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
    return current_vol / (avg_vol + 1e-8)

def detect_relief_trap(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", 30)
        if not btc_data["valid"] or len(btc_data["prices"]) < 20:
            return {
                "confidence": 0.0,
                "source": "relief_trap",
                "priority": 3,
                "entropy": 0.0
            }
        
        prices = btc_data["prices"]
        volumes = btc_data["volumes"]
        current_price = btc_data["current_price"]
        
        vwap = calculate_vwap(prices, volumes)
        
        confidence = 0.0
        reason = []
        
        # Relief trap detection logic
        if len(prices) >= 15:
            price_15min_ago = prices[-15]
            price_bounce = (current_price - price_15min_ago) / price_15min_ago
            
            if price_bounce > 0.015:  # 1.5% bounce
                rsi_1m = calculate_rsi_short_term(prices[-5:])
                rsi_15m = calculate_rsi_short_term(prices[-15:])
                
                rsi_divergence = abs(rsi_1m - rsi_15m)
                fails_vwap_reclaim = current_price < vwap
                
                if rsi_divergence > 10:
                    confidence += 0.3
                    reason.append("rsi_divergence")
                
                if fails_vwap_reclaim:
                    confidence += 0.25
                    reason.append("failed_vwap_reclaim")
                
                volume_ratio = calculate_volume_ratio(volumes)
                if volume_ratio > 1.5:
                    confidence += 0.15
                    reason.append("elevated_volume")
                
                if confidence > 0.2:
                    return {
                        "confidence": min(confidence, 1.0),
                        "source": "relief_trap",
                        "priority": 3,
                        "entropy": 0.0,
                        "signal_data": {
                            "asset": "BTC",
                            "entry_price": current_price,
                            "stop_loss": current_price * 1.015,
                            "take_profit_1": current_price * 0.985,
                            "price_bounce_15min": price_bounce * 100,
                            "rsi_1m": rsi_1m,
                            "rsi_15m": rsi_15m,
                            "rsi_divergence": rsi_divergence,
                            "vwap": vwap,
                            "failed_vwap_reclaim": fails_vwap_reclaim,
                            "volume_ratio": volume_ratio,
                            "reason": " + ".join(reason)
                        }
                    }
        
        return {
            "confidence": 0.0,
            "source": "relief_trap",
            "priority": 3,
            "entropy": 0.0
        }
        
    except Exception as e:
        logging.error(f"Relief trap detector error: {e}")
        return {
            "confidence": 0.0,
            "source": "relief_trap",
            "priority": 3,
            "entropy": 0.0
        }
