import torch
import sys
import platform
import os

DEVICE = None

def get_optimal_device():
    system = platform.system()
    if torch.cuda.is_available():
        return 'cuda'
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        return 'mps'
    print("❌ No GPU available")
    sys.exit(1)

DEVICE = get_optimal_device()

def array(data, dtype=None):
    return torch.tensor(data, dtype=torch.float32 if dtype is None else dtype).to(DEVICE)

def sum(x, axis=None):
    return torch.sum(x) if axis is None else torch.sum(x, dim=axis)

def mean(x, axis=None):
    return torch.mean(x) if axis is None else torch.mean(x, dim=axis)

def diff(x, n=1):
    return torch.diff(x, n=n)

def log(x):
    return torch.log(x)

def min(x, axis=None):
    return torch.min(x) if axis is None else torch.min(x, dim=axis)[0]

def max(x, axis=None):
    return torch.max(x) if axis is None else torch.max(x, dim=axis)[0]

# Additional functions for compatibility
def float32():
    return torch.float32
