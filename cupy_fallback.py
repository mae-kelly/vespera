import torch
import sys
import platform
import os
DEVICE = None
def get_optimal_device():
    system = platform.system()
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.cuda.empty_cache()
        return 'cuda'
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        return 'mps'
    print("❌ SYSTEM TERMINATED: NO GPU DETECTED")
    sys.exit(1)
DEVICE = get_optimal_device()
def array(data, dtype=None):
    return torch.tensor(data, dtype=torch.float32 if dtype is None else dtype).to(DEVICE)
def zeros(shape, dtype=torch.float32):
    return torch.zeros(shape, dtype=dtype, device=DEVICE)
def ones(shape, dtype=torch.float32):
    return torch.ones(shape, dtype=dtype, device=DEVICE)
def log(x):
    return torch.log(x)
def diff(x, n=1):
    return torch.diff(x, n=n)
def sum(x, axis=None):
    return torch.sum(x) if axis is None else torch.sum(x, dim=axis)
def min(x, axis=None):
    return torch.min(x) if axis is None else torch.min(x, dim=axis)[0]
def max(x, axis=None):
    return torch.max(x) if axis is None else torch.max(x, dim=axis)[0]
def mean(x, axis=None):
    return torch.mean(x) if axis is None else torch.mean(x, dim=axis)
def where(condition, x, y):
    return torch.where(condition, x, y)
def all(x):
    return torch.all(x)
def any(x):
    return torch.any(x)
class RandomModule:
    @staticmethod
    def normal(mean=0.0, std=1.0, size=None):
        if size is None:
            return torch.normal(mean, std, size=(1,), device=DEVICE).item()
        return torch.normal(mean, std, size=size, device=DEVICE)
    @staticmethod
    def exponential(scale=1.0, size=None):
        if size is None:
            return torch.exponential(torch.tensor([scale], device=DEVICE)).item()
        return torch.exponential(torch.full(size, scale, device=DEVICE))
random = RandomModule()
def get_default_memory_pool():
    class GPUMemoryPool:
        def set_limit(self, size): pass
        def free_all_blocks(self):
            if DEVICE == 'cuda': torch.cuda.empty_cache()
            elif DEVICE == 'mps': torch.mps.empty_cache()
    return GPUMemoryPool()
class cuda:
    class Device:
        def __init__(self, device_id=0): self.device_id = device_id
        def use(self):
            if DEVICE == 'cuda': torch.cuda.set_device(self.device_id)
def fuse():
    return lambda func: func
