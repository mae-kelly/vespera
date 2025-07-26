import torch
import warnings
import platform
import os
import sys

warnings.filterwarnings("ignore", category=UserWarning)

# FORCE MPS ENVIRONMENT VARIABLES
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'

# Declare DEVICE as global at module level
DEVICE = None

def get_optimal_device():
    """MANDATORY GPU DETECTION - NO CPU FALLBACK ALLOWED"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"🔍 MANDATORY GPU Detection on {system} {machine}")
    
    # PRIORITY 1: A100 GPUs (HIGHEST PERFORMANCE)
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            if "A100" in device_name:
                test_tensor = torch.randn(10, device='cuda')
                result = torch.sum(test_tensor)
                print(f"🏆 A100 GPU ACTIVATED: {device_name}")
                
                # Enable A100 optimizations
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                torch.backends.cudnn.benchmark = True
                torch.cuda.empty_cache()
                
                return 'cuda'
        except Exception as e:
            print(f"⚠️ A100 test failed: {e}")
    
    # PRIORITY 2: Apple Silicon M1/M2/M3/M4
    if system == "Darwin" and machine == "arm64":
        try:
            cpu_info = os.popen("sysctl -n machdep.cpu.brand_string").read().strip()
            if any(chip in cpu_info for chip in ['M1', 'M2', 'M3', 'M4']):
                print(f"🍎 APPLE SILICON DETECTED: {cpu_info}")
                
                # Force MPS activation
                if hasattr(torch.backends, 'mps'):
                    try:
                        test_tensor = torch.randn(5, device='mps')
                        result = torch.sum(test_tensor)
                        print(f"🎉 MPS ACTIVATED SUCCESSFULLY: {result}")
                        return 'mps'
                    except Exception as e:
                        print(f"❌ MPS activation failed: {e}")
                        # Try environment override
                        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                        try:
                            test_tensor = torch.randn(3, device='mps')
                            result = torch.sum(test_tensor)
                            print(f"🎉 MPS FORCED ACTIVATION: {result}")
                            return 'mps'
                        except Exception as e2:
                            print(f"❌ MPS force failed: {e2}")
        except Exception as e:
            print(f"❌ Apple Silicon detection failed: {e}")
    
    # PRIORITY 3: Other NVIDIA GPUs
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            test_tensor = torch.randn(5, device='cuda')
            result = torch.sum(test_tensor)
            print(f"⚡ NVIDIA GPU ACTIVATED: {device_name}")
            torch.backends.cudnn.benchmark = True
            return 'cuda'
        except Exception as e:
            print(f"❌ NVIDIA GPU test failed: {e}")
    
    # PRIORITY 4: AMD ROCm (if available)
    try:
        import torch_directml
        test_tensor = torch.randn(5, device='dml')
        result = torch.sum(test_tensor)
        print(f"🔴 AMD GPU ACTIVATED via DirectML")
        return 'dml'
    except:
        pass
    
    # ABSOLUTE FAILURE - NO CPU FALLBACK
    print("❌ CRITICAL SYSTEM FAILURE: NO GPU DETECTED")
    print("=" * 60)
    print("MANDATORY GPU REQUIREMENTS NOT MET")
    print("This system requires GPU acceleration. Available options:")
    print("  🏆 NVIDIA A100 (Preferred)")
    print("  🍎 Apple Silicon M1/M2/M3/M4")
    print("  ⚡ Other NVIDIA GPUs with CUDA")
    print("  🔴 AMD GPUs with ROCm")
    print("")
    print("Please install appropriate GPU drivers and try again.")
    print("CPU fallback is NOT ALLOWED for this Stanford PhD-level system.")
    sys.exit(1)

# Initialize DEVICE at module level
DEVICE = get_optimal_device()

def array(data, dtype=None):
    """Create tensor on optimal device - MANDATORY GPU"""
    global DEVICE
    try:
        if isinstance(data, (list, tuple)):
            tensor_data = torch.tensor(data, dtype=torch.float32 if dtype is None else dtype)
        else:
            tensor_data = torch.as_tensor(data, dtype=torch.float32 if dtype is None else dtype)
        
        # MANDATORY GPU - no CPU fallback
        return tensor_data.to(DEVICE)
    except Exception as e:
        print(f"❌ CRITICAL: GPU tensor creation failed: {e}")
        print("System requires GPU acceleration. Cannot continue.")
        sys.exit(1)

def zeros(shape, dtype=torch.float32):
    """Create zeros tensor on GPU - MANDATORY"""
    try:
        return torch.zeros(shape, dtype=dtype, device=DEVICE)
    except Exception as e:
        print(f"❌ CRITICAL: GPU zeros creation failed: {e}")
        sys.exit(1)

def ones(shape, dtype=torch.float32):
    """Create ones tensor on GPU - MANDATORY"""
    try:
        return torch.ones(shape, dtype=dtype, device=DEVICE)
    except Exception as e:
        print(f"❌ CRITICAL: GPU ones creation failed: {e}")
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
        except Exception as e:
            print(f"❌ CRITICAL: GPU random generation failed: {e}")
            sys.exit(1)
    
    @staticmethod
    def exponential(scale=1.0, size=None):
        try:
            if size is None:
                return torch.exponential(torch.tensor([scale], device=DEVICE)).item()
            else:
                return torch.exponential(torch.full(size, scale, device=DEVICE))
        except Exception as e:
            print(f"❌ CRITICAL: GPU exponential generation failed: {e}")
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

print(f"🚀 MANDATORY GPU ACTIVATED: {device_names.get(DEVICE, DEVICE)}")
print(f"✅ System will use {DEVICE} for all computations")
