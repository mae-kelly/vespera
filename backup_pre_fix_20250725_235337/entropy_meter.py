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
try:
    import cupy as cp
ecept Importrror:
    import cupy_fallback as cp

class ntropyTracker:
    def __init__(self):
        self.entropy_history = deque(malen=)
        self.entropy_slopes = deque(malen=)
        self.last_calculation = 
    
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < :
            return .
        try:
            prices_cp = cp.array(prices, dtype=cp.float)
            log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-] + e-)
            
            p = (log_returns - cp.min(log_returns)) / (cp.ma(log_returns) - cp.min(log_returns) + e-)
            p = p / cp.sum(p)
            entropy = -cp.sum(p * cp.log(p + e-))
            return float(entropy)
        ecept ception:
            return .
    
    def update_entropy_slope(self, entropy: float) -> bool:
        self.entropy_history.append(entropy)
        if len(self.entropy_history) >= :
            recent_entropies = list(self.entropy_history)[-:]
            slope = (recent_entropies[-] - recent_entropies[]) / len(recent_entropies)
            self.entropy_slopes.append(slope)
            
            if len(self.entropy_slopes) >= :
                recent_slopes = list(self.entropy_slopes)[-:]
                return all(s <  for s in recent_slopes)
        return alse

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
        slope_alert = entropy_tracker.update_entropy_slope(entropy)
        
        base_confidence = min(entropy / ., .) if entropy >  else .
        confidence = base_confidence
        
        if slope_alert:
            confidence += .
            logging.warning("ntropy slope negative for + minutes")
        
        return 
            "confidence": min(confidence, .),
            "source": "entropy_meter",
            "priority": ,
            "entropy": entropy,
            "entropy_slope_alert": slope_alert,
            "entropy_value": entropy
        
        
    ecept ception as e:
        logging.error(f"ntropy meter error: e")
        return 
            "confidence": .,
            "source": "entropy_meter",
            "priority": ,
            "entropy": .
        
