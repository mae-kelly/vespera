import torch
import sys
import platform
import os
DEVICE = None
def get_optimal_device():
    system = platform.system()
    machine = platform.machine()
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            if "A100" in device_name:
                test_tensor = torch.randn(10, device='cuda')
                result = torch.sum(test_tensor)
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                torch.backends.cudnn.benchmark = True
                torch.cuda.empty_cache()
                return 'cuda'
    if system == "Darwin" and machine == "arm64":
        try:
            gpu_info = os.popen("sysctl -n machdep.gpu.brand_string").read().strip()
            if any(chip in gpu_info for chip in ['M1', 'M2', 'M3', 'M4']):
                if hasattr(torch.backends, 'mps'):
                    try:
                        test_tensor = torch.randn(5, device='mps')
                        result = torch.sum(test_tensor)
                        return 'mps'
                        try:
                            test_tensor = torch.randn(3, device='mps')
                            result = torch.sum(test_tensor)
                            return 'mps'
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            test_tensor = torch.randn(5, device='cuda')
            result = torch.sum(test_tensor)
            torch.backends.cudnn.benchmark = True
            return 'cuda'
    print("❌ CRITICAL SYSTEM FAILURE: NO GPU DETECTED")
    print("MANDATORY GPU REQUIREMENTS NOT MET")
    print("This system requires GPU acceleration.")
    sys.exit(1)
DEVICE = get_optimal_device()
def array(data, dtype=None):
    global DEVICE
    try:
        if isinstance(data, (list, tuple)):
            tensor_data = torch.tensor(data, dtype=torch.float32 if dtype is None else dtype)
        else:
            tensor_data = torch.as_tensor(data, dtype=torch.float32 if dtype is None else dtype)
        return tensor_data.to(DEVICE)
        sys.exit(1)
def zeros(shape, dtype=torch.float32):
    try:
        return torch.zeros(shape, dtype=dtype, device=DEVICE)
        sys.exit(1)
def ones(shape, dtype=torch.float32):
    try:
        return torch.ones(shape, dtype=dtype, device=DEVICE)
        sys.exit(1)
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
class RandomModule:
    @staticmethod
    def normal(mean=0.0, std=1.0, size=None):
        try:
            if size is None:
                return torch.normal(mean, std, size=(1,), device=DEVICE).item()
            else:
                return torch.normal(mean, std, size=size, device=DEVICE)
            sys.exit(1)
    @staticmethod
    def exponential(scale=1.0, size=None):
        try:
            if size is None:
                return torch.exponential(torch.tensor([scale], device=DEVICE)).item()
            else:
                return torch.exponential(torch.full(size, scale, device=DEVICE))
            sys.exit(1)
random = RandomModule()
def get_default_memory_pool():
    class MandatoryGPUMemoryPool:
        def set_limit(self, size):
            pass
        def free_all_blocks(self):
            if DEVICE == 'cuda':
                torch.cuda.empty_cache()
            elif DEVICE == 'mps':
                torch.mps.empty_cache()
    return MandatoryGPUMemoryPool()
class cuda:
    class Device:
        def __init__(self, device_id=0):
            self.device_id = device_id
        def use(self):
            if DEVICE == 'cuda':
                torch.cuda.set_device(self.device_id)
def fuse():
    def decorator(func):
        return func
    return decorator
device_names = {
    'cuda': 'CUDA GPU (Mandatory)',
    'mps': 'Apple Silicon Metal GPU (Mandatory)', 
    'dml': 'DirectML GPU (Mandatory)'
}
