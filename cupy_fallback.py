# macOS-compatible CuPy fallback using pure PyTorch
import torch
import warnings

# Suppress compatibility warnings
warnings.filterwarnings("ignore", category=UserWarning)

def array(data, dtype=None):
    """Create tensor from data"""
    if isinstance(data, (list, tuple)):
        tensor_data = torch.tensor(data, dtype=torch.float32 if dtype is None else dtype)
    else:
        tensor_data = torch.as_tensor(data, dtype=torch.float32 if dtype is None else dtype)
    
    # Use MPS on Apple Silicon if available, otherwise CPU
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return tensor_data.to('mps')
    elif torch.cuda.is_available():
        return tensor_data.cuda()
    else:
        return tensor_data

def zeros(shape, dtype=torch.float32):
    """Create zero tensor"""
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return torch.zeros(shape, dtype=dtype, device='mps')
    elif torch.cuda.is_available():
        return torch.zeros(shape, dtype=dtype, device='cuda')
    else:
        return torch.zeros(shape, dtype=dtype)

def ones(shape, dtype=torch.float32):
    """Create ones tensor"""
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return torch.ones(shape, dtype=dtype, device='mps')
    elif torch.cuda.is_available():
        return torch.ones(shape, dtype=dtype, device='cuda')
    else:
        return torch.ones(shape, dtype=dtype)

# Math operations
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
            device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else ('cuda' if torch.cuda.is_available() else 'cpu')
            return torch.normal(mean, std, size=(1,), device=device).item()
        else:
            device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else ('cuda' if torch.cuda.is_available() else 'cpu')
            return torch.normal(mean, std, size=size, device=device)
    
    @staticmethod
    def exponential(scale=1.0, size=None):
        if size is None:
            device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else ('cuda' if torch.cuda.is_available() else 'cpu')
            return torch.exponential(torch.tensor([scale], device=device)).item()
        else:
            device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else ('cuda' if torch.cuda.is_available() else 'cpu')
            return torch.exponential(torch.full(size, scale, device=device))

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
            elif torch.backends.mps.is_available():
                pass  # MPS doesn't need explicit device setting

# Kernel fusion decorator (uses torch operations)
def fuse():
    def decorator(func):
        return func
    return decorator

print("✅ macOS-compatible PyTorch/CuPy fallback loaded")
