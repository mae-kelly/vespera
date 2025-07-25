# Pure CuPy/Torch fallback - NO NUMPY USAGE
import torch

# CuPy API using pure torch operations
def array(data, dtype=None):
    if torch.cuda.is_available():
        return torch.tensor(data, dtype=torch.float32 if dtype is None else dtype, device='cuda')
    else:
        return torch.tensor(data, dtype=torch.float32 if dtype is None else dtype)

def zeros(shape, dtype=torch.float32):
    if torch.cuda.is_available():
        return torch.zeros(shape, dtype=dtype, device='cuda')
    else:
        return torch.zeros(shape, dtype=dtype)

def ones(shape, dtype=torch.float32):
    if torch.cuda.is_available():
        return torch.ones(shape, dtype=dtype, device='cuda')
    else:
        return torch.ones(shape, dtype=dtype)

def log(x):
    return torch.log(x)

def diff(x, n=1):
    return torch.diff(x, n=n)

def sum(x, axis=None):
    if axis is None:
        return torch.sum(x)
    else:
        return torch.sum(x, dim=axis)

def min(x, axis=None):
    if axis is None:
        return torch.min(x)
    else:
        return torch.min(x, dim=axis)[0]

def max(x, axis=None):
    if axis is None:
        return torch.max(x)
    else:
        return torch.max(x, dim=axis)[0]

def mean(x, axis=None):
    if axis is None:
        return torch.mean(x)
    else:
        return torch.mean(x, dim=axis)

def where(condition, x, y):
    return torch.where(condition, x, y)

def all(x):
    return torch.all(x)

def any(x):
    return torch.any(x)

# Random module using torch
class RandomModule:
    @staticmethod
    def normal(mean=0.0, std=1.0, size=None):
        if size is None:
            if torch.cuda.is_available():
                return torch.normal(mean, std, size=(1,), device='cuda').item()
            else:
                return torch.normal(mean, std, size=(1,)).item()
        else:
            if torch.cuda.is_available():
                return torch.normal(mean, std, size=size, device='cuda')
            else:
                return torch.normal(mean, std, size=size)
    
    @staticmethod
    def exponential(scale=1.0, size=None):
        if size is None:
            if torch.cuda.is_available():
                return torch.exponential(torch.tensor([scale], device='cuda')).item()
            else:
                return torch.exponential(torch.tensor([scale])).item()
        else:
            if torch.cuda.is_available():
                return torch.exponential(torch.full(size, scale, device='cuda'))
            else:
                return torch.exponential(torch.full(size, scale))

random = RandomModule()

# Memory management (dummy implementations for compatibility)
def get_default_memory_pool():
    class DummyMemoryPool:
        def set_limit(self, size):
            pass
        def free_all_blocks(self):
            pass
    return DummyMemoryPool()

# CUDA module
class cuda:
    class Device:
        def __init__(self, device_id=0):
            self.device_id = device_id
        
        def use(self):
            if torch.cuda.is_available():
                torch.cuda.set_device(self.device_id)

# Kernel fusion decorator (uses torch operations)
def fuse():
    def decorator(func):
        return func
    return decorator

print("✅ Pure Torch/CuPy fallback loaded (NO NumPy)")
