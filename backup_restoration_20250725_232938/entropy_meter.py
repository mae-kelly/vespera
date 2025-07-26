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
import time
import logging
from typing import Dict, List
from collections import deque
import torch
import signal_engine
import config
class EntropyTracker:
    def __init__(self):
        self.entropy_history = deque(maxlen=60)
        self.entropy_slopes = deque(maxlen=10)
        self.last_calculation = 0
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0.0
        try:
            if torch.cuda.is_available():
                prices_cp = cp.array(prices, dtype=cp.float32)
                log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-1] + 1e-10)
                if cp.all(log_returns == log_returns[0]):
                    return 0.0
                p = (log_returns - log_returns.min()) / (log_returns.max() - log_returns.min() + 1e-10)
                p = p / cp.sum(p)
                entropy = -cp.sum(p * cp.log(p + 1e-10))
                return float(entropy)
            else:
                    return 0.0
                p = (log_returns - log_returns.min()) / (log_returns.max() - log_returns.min() + 1e-10)
                return float(entropy)
            return 0.0
    def update_entropy_slope(self, entropy: float) -> bool:
        self.entropy_history.append(entropy)
        if len(self.entropy_history) >= 4:
            recent_entropies = list(self.entropy_history)[-4:]
            if torch.cuda.is_available():
                entropies_tensor = torch.tensor(recent_entropies, dtype=torch.float32)
                time_points = torch.arange(len(recent_entropies), dtype=torch.float32)
                n = len(recent_entropies)
                sum_x = torch.sum(time_points)
                sum_y = torch.sum(entropies_tensor)
                sum_xy = torch.sum(time_points * entropies_tensor)
                sum_x2 = torch.sum(time_points ** 2)
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2 + 1e-8)
                slope = float(slope)
            else:
            self.entropy_slopes.append(slope)
            if len(self.entropy_slopes) >= 3:
                recent_slopes = list(self.entropy_slopes)[-3:]
                return all(s < 0 for s in recent_slopes)
        return False
entropy_tracker = EntropyTracker()
def calculate_entropy_signal(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", 60)
        if not btc_data["valid"] or len(btc_data["prices"]) < 10:
            return {
                "confidence": 0.0,
                "source": "entropy_meter",
                "priority": 2,
                "entropy": 0.0
            }
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["prices"])
        slope_alert = entropy_tracker.update_entropy_slope(entropy)
        base_confidence = min(entropy / 3.0, 0.3) if entropy > 0 else 0.0
        confidence = base_confidence
        if slope_alert:
            confidence += 0.2
            logging.warning("Entropy slope negative for 3+ minutes - market instability detected")
        return {
            "confidence": min(confidence, 1.0),
            "source": "entropy_meter",
            "priority": 2,
            "entropy": entropy,
            "entropy_slope_alert": slope_alert,
            "entropy_value": entropy
        }
        return {
            "confidence": 0.0,
            "source": "entropy_meter",
            "priority": 2,
            "entropy": 0.0
        }