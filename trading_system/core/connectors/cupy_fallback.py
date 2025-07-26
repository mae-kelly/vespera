import torch
import platform
import sys

def get_optimal_device():
    system = platform.system()
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    elif torch.cuda.is_available():
        return 'cuda'
    else:
        raise RuntimeError("PRODUCTION TERMINATED: No GPU acceleration available")

DEVICE = get_optimal_device()

class ProductionCompute:
    def __init__(self):
        self.device = DEVICE
        try:
            test_tensor = torch.zeros(1, device=self.device)
            print(f"✅ Production GPU validated: {self.device}")
        except Exception as e:
            raise RuntimeError(f"GPU validation failed: {e}")
    
    def array(self, data, dtype=None):
        if not data:
            raise RuntimeError("Cannot create array from empty data")
        return torch.tensor(data, dtype=dtype or torch.float32, device=self.device)
    
    def sum(self, x, axis=None):
        if x.numel() == 0:
            raise RuntimeError("Cannot sum empty tensor")
        return torch.sum(x, dim=axis) if axis is not None else torch.sum(x)
    
    def mean(self, x, axis=None):
        if x.numel() == 0:
            raise RuntimeError("Cannot mean empty tensor")
        return torch.mean(x, dim=axis) if axis is not None else torch.mean(x)
    
    def diff(self, x, n=1):
        if x.numel() <= n:
            raise RuntimeError(f"Insufficient data for diff: {x.numel()} <= {n}")
        return torch.diff(x, n=n)
    
    def log(self, x):
        if torch.any(x <= 0):
            raise RuntimeError("Log of non-positive values")
        return torch.log(x)
    
    def min(self, x, axis=None):
        if x.numel() == 0:
            raise RuntimeError("Cannot find min of empty tensor")
        return torch.min(x, dim=axis)[0] if axis is not None else torch.min(x)
    
    def max(self, x, axis=None):
        if x.numel() == 0:
            raise RuntimeError("Cannot find max of empty tensor")
        return torch.max(x, dim=axis)[0] if axis is not None else torch.max(x)
    
    def sqrt(self, x):
        if torch.any(x < 0):
            raise RuntimeError("Square root of negative values")
        return torch.sqrt(x)
    
    def abs(self, x):
        return torch.abs(x)
    
    def exp(self, x):
        return torch.exp(x)
    
    def clamp(self, x, min_val=None, max_val=None):
        return torch.clamp(x, min=min_val, max=max_val)
    
    @property
    def float32(self):
        return torch.float32

cp = ProductionCompute()
__all__ = ['cp', 'DEVICE']
