import torch
import sys
if not torch.cuda.is_available():
    print("❌ CRITICAL ERROR: NO GPU DETECTED")
    print("This system requires GPU acceleration. gpu operation is FORBIDDEN.")
    sys.exit(1)
device_name = torch.cuda.get_device_name(0)
if "A100" not in device_name:
    print(f"⚠️ WARNING: Non-A100 GPU detected: {device_name}")
    print("Optimal performance requires A100. Continuing with reduced performance.")

import logging
from typing import Dict, List
import torch
import signal_engine
import config
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
        bounce_threshold = 0.015
        lookback_minutes = 15
        if len(prices) >= lookback_minutes:
            price_15min_ago = prices[-lookback_minutes]
            price_bounce = (current_price - price_15min_ago) / price_15min_ago
            if price_bounce > bounce_threshold:
                rsi_1m = calculate_rsi_short_term(prices[-5:])
                rsi_15m = calculate_rsi_short_term(prices[-15:])
                if torch.cuda.is_available():
                    rsi_divergence = float(torch.abs(torch.tensor(rsi_1m) - torch.tensor(rsi_15m)))
                else:
                    rsi_divergence = abs(rsi_1m - rsi_15m)
                fails_vwap_reclaim = current_price < vwap
                confidence = 0.0
                reason = []
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
                if len(prices) >= 30:
                    trend_start = prices[-30]
                    overall_trend = (current_price - trend_start) / trend_start
                    if overall_trend < -0.02:
                        confidence += 0.1
                        reason.append("downtrend_context")
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
        return {
            "confidence": 0.0,
            "source": "relief_trap",
            "priority": 3,
            "entropy": 0.0
        }
def calculate_rsi_short_term(prices: List[float], period: int = 14) -> float:
    if len(prices) < 2:
        return 50.0
    if torch.cuda.is_available():
        prices_tensor = torch.tensor(prices, dtype=torch.float32, device='cuda')
        deltas = torch.diff(prices_tensor)
        gains = torch.clamp(deltas, min=0)
        losses = torch.clamp(-deltas, min=0)
        avg_gain = torch.mean(gains) if len(gains) > 0 else torch.tensor(0.0)
        avg_loss = torch.mean(losses) if len(losses) > 0 else torch.tensor(0.0)
        rs = avg_gain / (avg_loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    else:
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, d) for d in deltas]
        losses = [max(0, -d) for d in deltas]
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    if torch.cuda.is_available():
        prices_cp = cp.array(prices)
        volumes_cp = cp.array(volumes)
        total_pv = cp.sum(prices_cp * volumes_cp)
        total_v = cp.sum(volumes_cp)
        return float(total_pv / (total_v + 1e-8))
    else:
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_v = sum(volumes)
        return total_pv / (total_v + 1e-8)
def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < 3:
        return 1.0
    current_vol = volumes[-1]
    avg_vol = sum(volumes[:-1]) / len(volumes[:-1])
    return current_vol / (avg_vol + 1e-8)