import time
import logging
from typing import Dict, List
from collections import deque
import torch
import cupy as cp
import signal_engine
import config

class EntropyTracker:
    def __init__(self):
        self.entropy_history = deque(maxlen=10)
        self.last_calculation = 0
        
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0.0
        
        try:
            prices_cp = cp.array(prices, dtype=cp.float32)
            log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-1] + 1e-10)
            
            if cp.all(log_returns == log_returns[0]):
                return 0.0
            
            p = (log_returns - log_returns.min()) / (log_returns.max() - log_returns.min() + 1e-10)
            p = p / cp.sum(p)
            
            entropy = -cp.sum(p * cp.log(p + 1e-10))
            return float(entropy)
            
        except Exception as e:
            logging.error(f"Entropy calculation error: {e}")
            return 0.0

entropy_tracker = EntropyTracker()

def calculate_entropy_signal(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BTC", 60)
        
        if not btc_data["valid"]:
            return {
                "confidence": 0.0,
                "source": "entropy_meter",
                "priority": 2,
                "entropy": 0.0
            }
        
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["prices"])
        entropy_tracker.entropy_history.append(entropy)
        
        confidence = min(entropy / 2.0, 0.3) if entropy > 0 else 0.0
        
        return {
            "confidence": confidence,
            "source": "entropy_meter", 
            "priority": 2,
            "entropy": entropy
        }
        
    except Exception as e:
        logging.error(f"Entropy meter error: {e}")
        return {
            "confidence": 0.0,
            "source": "entropy_meter",
            "priority": 2,
            "entropy": 0.0
        }
