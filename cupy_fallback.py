import torch
import platform
import os
import sys

# Detect optimal device for Apple Silicon
def get_optimal_device():
    system = platform.system()
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        # Enable MPS fallback for unsupported operations
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        return 'mps'
    elif torch.cuda.is_available():
        return 'cuda'
    else:
        return 'cpu'

DEVICE = get_optimal_device()
print(f"🚀 Optimized device: {DEVICE}")

class AppleOptimizedCompute:
    """Apple Silicon optimized compute using PyTorch MPS"""
    
    def __init__(self):
        self.device = DEVICE
        # Pre-warm MPS if available
        if self.device == 'mps':
            try:
                torch.zeros(1, device='mps')
                print("✅ Apple Metal Performance Shaders (MPS) ready")
            except Exception as e:
                print(f"⚠️ MPS fallback to CPU: {e}")
                self.device = 'cpu'
    
    def array(self, data, dtype=None):
        """Create optimized tensor array"""
        try:
            tensor = torch.tensor(data, dtype=dtype or torch.float32)
            if self.device != 'cpu':
                return tensor.to(self.device)
            return tensor
        except Exception:
            # Fallback to CPU if device fails
            return torch.tensor(data, dtype=dtype or torch.float32)
    
    def sum(self, x, axis=None):
        if axis is None:
            return torch.sum(x)
        return torch.sum(x, dim=axis)
    
    def mean(self, x, axis=None):
        if axis is None:
            return torch.mean(x)
        return torch.mean(x, dim=axis)
    
    def diff(self, x, n=1):
        return torch.diff(x, n=n)
    
    def log(self, x):
        # Add small epsilon to avoid log(0)
        return torch.log(x + 1e-10)
    
    def min(self, x, axis=None):
        if axis is None:
            return torch.min(x)
        return torch.min(x, dim=axis)[0]
    
    def max(self, x, axis=None):
        if axis is None:
            return torch.max(x)
        return torch.max(x, dim=axis)[0]
    
    def sqrt(self, x):
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
    
    @property
    def float64(self):
        return torch.float64

# Global optimized compute instance
cp = AppleOptimizedCompute()

# Compatibility exports
def zeros(shape, dtype=None):
    return torch.zeros(shape, dtype=dtype or torch.float32, device=DEVICE)

def ones(shape, dtype=None):
    return torch.ones(shape, dtype=dtype or torch.float32, device=DEVICE)

def arange(start, stop=None, step=1, dtype=None):
    if stop is None:
        stop = start
        start = 0
    return torch.arange(start, stop, step, dtype=dtype or torch.float32, device=DEVICE)

# GPU memory management for Apple Silicon
def empty_cache():
    """Clear GPU cache - Apple Silicon compatible"""
    if DEVICE == 'mps':
        try:
            torch.mps.empty_cache()
        except:
            pass
    elif DEVICE == 'cuda':
        torch.cuda.empty_cache()

def memory_allocated():
    """Get allocated GPU memory"""
    if DEVICE == 'mps':
        try:
            return torch.mps.current_allocated_memory()
        except:
            return 0
    elif DEVICE == 'cuda':
        return torch.cuda.memory_allocated()
    return 0

# Export all compatibility functions
__all__ = ['cp', 'DEVICE', 'zeros', 'ones', 'arange', 'empty_cache', 'memory_allocated']

print(f"✅ Apple optimized compute ready on {DEVICE}")
