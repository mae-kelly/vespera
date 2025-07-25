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
        self.entropy_history = deque(maxlen=60)  # 60-sample rolling window
        self.entropy_slopes = deque(maxlen=10)
        self.last_calculation = 0
        
    def calculate_shannon_entropy(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0.0
        
        try:
            if torch.cuda.is_available():
                prices_cp = cp.array(prices, dtype=cp.float32)
                # Log returns using cupy.log(cupy.diff(prices))
                log_returns = cp.log(cp.diff(prices_cp) / prices_cp[:-1] + 1e-10)
                
                if cp.all(log_returns == log_returns[0]):
                    return 0.0
                
                # Shannon entropy with exact formula
                p = (log_returns - log_returns.min()) / (log_returns.max() - log_returns.min() + 1e-10)
                p = p / cp.sum(p)
                
                entropy = -cp.sum(p * cp.log(p + 1e-10))
                return float(entropy)
            else:
                import numpy as np
                prices_np = np.array(prices, dtype=np.float32)
                log_returns = np.log(np.diff(prices_np) / prices_np[:-1] + 1e-10)
                
                if np.all(log_returns == log_returns[0]):
                    return 0.0
                
                p = (log_returns - log_returns.min()) / (log_returns.max() - log_returns.min() + 1e-10)
                p = p / np.sum(p)
                
                entropy = -np.sum(p * np.log(p + 1e-10))
                return float(entropy)
                
        except Exception as e:
            logging.error(f"Entropy calculation error: {e}")
            return 0.0
    
    def update_entropy_slope(self, entropy: float) -> bool:
        """Returns True if entropy slope is negative for 3+ minutes"""
        self.entropy_history.append(entropy)
        
        if len(self.entropy_history) >= 4:  # Need at least 4 points for slope
            # Calculate slope over last 3 minutes (3 data points)
            recent_entropies = list(self.entropy_history)[-4:]
            
            if torch.cuda.is_available():
                entropies_tensor = torch.tensor(recent_entropies, dtype=torch.float32)
                time_points = torch.arange(len(recent_entropies), dtype=torch.float32)
                
                # Linear regression to calculate slope
                n = len(recent_entropies)
                sum_x = torch.sum(time_points)
                sum_y = torch.sum(entropies_tensor)
                sum_xy = torch.sum(time_points * entropies_tensor)
                sum_x2 = torch.sum(time_points ** 2)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2 + 1e-8)
                slope = float(slope)
            else:
                import numpy as np
                time_points = np.arange(len(recent_entropies))
                slope = np.polyfit(time_points, recent_entropies, 1)[0]
            
            self.entropy_slopes.append(slope)
            
            # Alert if entropy slope negative for 3+ consecutive measurements
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
        
        # Calculate Shannon entropy over 60-sample rolling window
        entropy = entropy_tracker.calculate_shannon_entropy(btc_data["prices"])
        
        # Check for entropy slope decline (alert if negative for 3+ minutes)
        slope_alert = entropy_tracker.update_entropy_slope(entropy)
        
        # Base confidence from entropy magnitude
        base_confidence = min(entropy / 3.0, 0.3) if entropy > 0 else 0.0
        
        # Boost confidence if slope is declining (indicates increasing market chaos)
        confidence = base_confidence
        if slope_alert:
            confidence += 0.2  # Significant boost for entropy decline alert
            logging.warning("Entropy slope negative for 3+ minutes - market instability detected")
        
        return {
            "confidence": min(confidence, 1.0),
            "source": "entropy_meter", 
            "priority": 2,
            "entropy": entropy,
            "entropy_slope_alert": slope_alert,
            "entropy_value": entropy
        }
        
    except Exception as e:
        logging.error(f"Entropy meter error: {e}")
        return {
            "confidence": 0.0,
            "source": "entropy_meter",
            "priority": 2,
            "entropy": 0.0
        }
