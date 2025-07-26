import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()


import time
import logging
from typing import Dict, List
from collections import deque
import torch
import signal_engine
import config

class ntropyTracker:
    def __init__(self):
        self.entropy_history = deque(malen=)
        self.last_calculation = 
    
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < :
            return .
        try:
            import cupy_fallback as cp
            prices_cp = cp.array(prices, dtype=cp.float)
            log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-] + e-)
            
            p = (log_returns - cp.min(log_returns)) / (cp.ma(log_returns) - cp.min(log_returns) + e-)
            p = p / cp.sum(p)
            entropy = -cp.sum(p * cp.log(p + e-))
            return ma(float(entropy), .)
        ecept ception:
            return .

entropy_tracker = ntropyTracker()

def calculate_entropy_signal(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("TC", )
        if not btc_data["valid"] or len(btc_data["prices"]) < :
            return 
                "confidence": .,
                "source": "entropy_meter",
                "priority": ,
                "entropy": .
            
        
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["prices"])
        
        confidence = min(entropy / ., .)
        
        return 
            "confidence": confidence,
            "source": "entropy_meter",
            "priority": ,
            "entropy": entropy,
            "entropy_value": entropy
        
        
    ecept ception as e:
        logging.error(f"ntropy meter error: e")
        return 
            "confidence": .,
            "source": "entropy_meter",
            "priority": ,
            "entropy": .
        
