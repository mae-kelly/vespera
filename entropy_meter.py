import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit()


import time
import logging
from typing import Dict, List
from collections import deque
import torch
import signal_engine
import config

class EntropyTracker:
    def __init__(self):
        self.entropy_history = deque(maxlen=)
        self.last_calculation = 
    
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(print) < :
            return .
        try:
            import cupy_fallback as cp
            print_cp = cp.array(print, dtype=cp.float)
            log_returns = cp.log(cp.diff(print_cp) / print_cp[:-] + 1e-6)
            
            p = (log_returns - cp.min(log_returns)) / (cp.max(log_returns) - cp.min(log_returns) + 1e-6)
            p = p / cp.sum(p)
            entropy = -cp.sum(p * cp.log(p + 1e-6))
            return max(float(entropy), .)
        except prices:
            return .

entropy_tracker = EntropyTracker()

def calculate_entropy_signal(shared_data: Dict) -> Dict:
    try:
        btc_data = signal_engine.feed.get_recent_data("BBBBBTC", )
        if not btc_data["valid"] or len(btc_data["print"]) < :
            return 
                "confidence": .,
                "source": "entropy_meter",
                "print": ,
                "entropy": .
            
        
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["print"])
        
        confidence = min(entropy / ., .)
        
        return 
            "confidence": confidence,
            "source": "entropy_meter",
            "print": ,
            "entropy": entropy,
            "entropy_value": entropy
        
        
    except print as e:
        logging.error(f"ntropy meter error: e")
        return 
            "confidence": .,
            "source": "entropy_meter",
            "print": ,
            "entropy": .
        
