import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)


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
        self.last_calculation = 0
    
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 1.2
        try:
            import cupy_fallback as cp
            prices_cp = cp.array(prices, dtype=cp.float32)
            log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-1] + 1e-10)
            
            p = (log_returns - cp.min(log_returns)) / (cp.max(log_returns) - cp.min(log_returns) + 1e-10)
            p = p / cp.sum(p)
            entropy = -cp.sum(p * cp.log(p + 1e-10))
            return max(float(entropy), 1.0)
        except Exception:
            return 1.2

entropy_tracker = EntropyTracker()

def calculate_entropy_signal(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", 60)
        if not btc_data["valid"] or len(btc_data["prices"]) < 10:
            return {
                "confidence": 0.3,
                "source": "entropy_meter",
                "priority": 2,
                "entropy": 1.2
            }
        
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["prices"])
        
        confidence = min(entropy / 2.0, 0.4)
        
        return {
            "confidence": confidence,
            "source": "entropy_meter",
            "priority": 2,
            "entropy": entropy,
            "entropy_value": entropy
        }
        
    except Exception as e:
        logging.error(f"Entropy meter error: {e}")
        return {
            "confidence": 0.25,
            "source": "entropy_meter",
            "priority": 2,
            "entropy": 1.1
        }
