import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import torch
import sys
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
def detect_laggard_opportunity(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", 30)
        eth_data = signal_engine.feed.get_recent_data("ETH", 30)
        sol_data = signal_engine.feed.get_recent_data("SOL", 30)
        if not all([btc_data["valid"], eth_data["valid"], sol_data["valid"]]):
            return {
                "confidence": 0.0,
                "source": "laggard_sniper",
                "priority": 3,
                "entropy": 0.0
            }
        btc_rsi = calculate_rsi_torch_tensor(btc_data["prices"])
        eth_rsi = calculate_rsi_torch_tensor(eth_data["prices"])
        sol_rsi = calculate_rsi_torch_tensor(sol_data["prices"])
        btc_vol_ratio = calculate_volume_ratio(btc_data["volumes"])
        eth_vol_ratio = calculate_volume_ratio(eth_data["volumes"])
        sol_vol_ratio = calculate_volume_ratio(sol_data["volumes"])
        confidence = 0.0
        target_asset = None
        reason = []
        if btc_rsi < 30:
            if eth_rsi < 40 and eth_rsi < 28:
                if eth_vol_ratio > 2.0 and btc_vol_ratio < 1.0:
                    confidence += 0.4
                    target_asset = "ETH"
                    reason.append("eth_laggard_rsi_volume")
            if sol_rsi < 40 and sol_rsi < 28:
                if sol_vol_ratio > 2.0 and btc_vol_ratio < 1.0:
                    vol_conf = 0.35
                    if not target_asset or confidence < vol_conf:
                        confidence = vol_conf
                        target_asset = "SOL"
                        reason = ["sol_laggard_rsi_volume"]
            btc_eth_correlation = calculate_correlation_torch(btc_data["prices"], eth_data["prices"])
            btc_sol_correlation = calculate_correlation_torch(btc_data["prices"], sol_data["prices"])
            if btc_eth_correlation < 0.5 and target_asset == "ETH":
                confidence += 0.15
                reason.append("correlation_breakdown")
            elif btc_sol_correlation < 0.5 and target_asset == "SOL":
                confidence += 0.15
                reason.append("correlation_breakdown")
        if target_asset and confidence > 0.1:
            current_price = eth_data["current_price"] if target_asset == "ETH" else sol_data["current_price"]
            return {
                "confidence": min(confidence, 1.0),
                "source": "laggard_sniper",
                "priority": 3,
                "entropy": 0.0,
                "signal_data": {
                    "asset": target_asset,
                    "entry_price": current_price,
                    "stop_loss": current_price * 1.015,
                    "take_profit_1": current_price * 0.985,
                    "rsi": eth_rsi if target_asset == "ETH" else sol_rsi,
                    "btc_rsi": btc_rsi,
                    "volume_ratio": eth_vol_ratio if target_asset == "ETH" else sol_vol_ratio,
                    "reason": " + ".join(reason)
                }
            }
        return {
            "confidence": 0.0,
            "source": "laggard_sniper",
            "priority": 3,
            "entropy": 0.0
        }
        return {
            "confidence": 0.0,
            "source": "laggard_sniper",
            "priority": 3,
            "entropy": 0.0
        }
def calculate_rsi_torch_tensor(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    if torch.cuda.is_available():
        prices_tensor = torch.tensor(prices, dtype=torch.float32, device='cuda')
    else:
        prices_tensor = torch.tensor(prices, dtype=torch.float32)
    deltas = torch.diff(prices_tensor)
    gains = torch.clamp(deltas, min=0)
    losses = torch.clamp(-deltas, min=0)
    if len(gains) >= period:
        avg_gain = torch.mean(gains[-period:])
        avg_loss = torch.mean(losses[-period:])
        rs = avg_gain / (avg_loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    return 50.0
def calculate_volume_ratio(volumes: List[float]) -> float:
    if len(volumes) < 3:
        return 1.0
    current_vol = volumes[-1]
    mean_vol = sum(volumes[:-1]) / len(volumes[:-1])
    return current_vol / (mean_vol + 1e-8)
def calculate_correlation_torch(prices1: List[float], prices2: List[float]) -> float:
    if len(prices1) != len(prices2) or len(prices1) < 10:
        return 0.0
    min_len = min(len(prices1), len(prices2))
    prices1 = prices1[-min_len:]
    prices2 = prices2[-min_len:]
    if torch.cuda.is_available():
        p1 = torch.tensor(prices1, dtype=torch.float32, device='cuda')
        p2 = torch.tensor(prices2, dtype=torch.float32, device='cuda')
    else:
        p1 = torch.tensor(prices1, dtype=torch.float32)
        p2 = torch.tensor(prices2, dtype=torch.float32)
    p1_mean = torch.mean(p1)
    p2_mean = torch.mean(p2)
    numerator = torch.sum((p1 - p1_mean) * (p2 - p2_mean))
    denominator = torch.sqrt(torch.sum((p1 - p1_mean) ** 2) * torch.sum((p2 - p2_mean) ** 2))
    correlation = numerator / (denominator + 1e-8)
    return float(correlation)