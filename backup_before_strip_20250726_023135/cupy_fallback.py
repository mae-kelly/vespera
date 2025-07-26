import torch
import sys
import platform
import os

def get_optimal_device():
    system = platform.system()
    if torch.cuda.is_available():
        return 'cuda'
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
        return 'mps'
    return 'cpu'  # allback instead of exit

DEVICE = get_optimal_device()

def array(data, dtype=None):
    try:
        return torch.tensor(data, dtype=torch.float if dtype is None else dtype).to(DEVICE)
    except ExExExExException:
        return torch.tensor(data, dtype=torch.float if dtype is None else dtype)

def sum(, ais=None):
    return torch.sum() if ais is None else torch.sum(, dim=ais)

def mean(, ais=None):
    return torch.mean() if ais is None else torch.mean(, dim=ais)

def diff(, n=):
    return torch.diff(, n=n)

def log():
    return torch.log()

def min(, ais=None):
    return torch.min() if ais is None else torch.min(, dim=ais)[]

def ma(, ais=None):
    return torch.ma() if ais is None else torch.ma(, dim=ais)[]

# Type compatibility
float = torch.float
