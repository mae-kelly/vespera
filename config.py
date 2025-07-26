import os
import torch
import platform
import subprocess
import sys

MODE = os.getenv("MODE", "dry")
LIVE_MODE = MODE == "live"
ASSETS = ["BTC", "ETH", "SOL"]

SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3
MAX_DRAWDOWN_PERCENT = 10.0
COOLDOWN_MINUTES = 5

OKX_API_LIMITS = {
    "orders_per_second": 20,
    "requests_per_second": 10,
    "max_position_size": 50000
}

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def detect_mac_gpu_capabilities():
    """Exhaustive Mac GPU detection"""
    system = platform.system()
    if system != "Darwin":
        return None
    
    gpu_info = {
        "has_metal": False,
        "has_opencl": False,
        "has_discrete_gpu": False,
        "gpu_names": [],
        "memory_gb": 0,
        "metal_family": None,
        "architecture": platform.machine()
    }
    
    try:
        result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            
            if 'Metal' in output:
                gpu_info["has_metal"] = True
                
            if 'Radeon' in output or 'GeForce' in output or 'Quadro' in output:
                gpu_info["has_discrete_gpu"] = True
                
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if 'Chipset Model:' in line or 'GPU:' in line:
                    gpu_name = line.split(':')[-1].strip()
                    if gpu_name and gpu_name not in gpu_info["gpu_names"]:
                        gpu_info["gpu_names"].append(gpu_name)
                        
                if 'VRAM' in line or 'Graphics Memory' in line:
                    try:
                        memory_str = line.split(':')[-1].strip()
                        if 'GB' in memory_str:
                            memory_val = float(memory_str.replace('GB', '').strip())
                            gpu_info["memory_gb"] = max(gpu_info["memory_gb"], memory_val)
                        elif 'MB' in memory_str:
                            memory_val = float(memory_str.replace('MB', '').strip()) / 1024
                            gpu_info["memory_gb"] = max(gpu_info["memory_gb"], memory_val)
                    except:
                        pass
    except:
        pass
    
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            cpu_info = result.stdout.strip()
            if 'Apple' in cpu_info and ('M1' in cpu_info or 'M2' in cpu_info or 'M3' in cpu_info):
                gpu_info["has_metal"] = True
                gpu_info["metal_family"] = "Apple Silicon"
                if not gpu_info["gpu_names"]:
                    if 'M1' in cpu_info:
                        gpu_info["gpu_names"].append("Apple M1 GPU")
                    elif 'M2' in cpu_info:
                        gpu_info["gpu_names"].append("Apple M2 GPU")
                    elif 'M3' in cpu_info:
                        gpu_info["gpu_names"].append("Apple M3 GPU")
    except:
        pass
    
    try:
        result = subprocess.run(['ioreg', '-r', '-d', '1', '-c', 'IOPCIDevice'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            if any(gpu in output.lower() for gpu in ['radeon', 'geforce', 'quadro', 'intel hd', 'intel iris']):
                gpu_info["has_metal"] = True
                if any(gpu in output.lower() for gpu in ['radeon', 'geforce', 'quadro']):
                    gpu_info["has_discrete_gpu"] = True
    except:
        pass
    
    if gpu_info["architecture"] == "arm64":
        gpu_info["has_metal"] = True
        gpu_info["metal_family"] = "Apple Silicon"
    elif gpu_info["architecture"] == "x86_64":
        gpu_info["metal_family"] = "Intel Mac"
    
    return gpu_info

def test_pytorch_backends():
    """Test all available PyTorch backends"""
    backends = {
        "cuda": False,
        "mps": False,
        "opencl": False,
        "cpu": True
    }
    
    if torch.cuda.is_available():
        backends["cuda"] = True
        try:
            test_tensor = torch.randn(10, device='cuda')
            _ = torch.sum(test_tensor)
            backends["cuda"] = "verified"
        except:
            backends["cuda"] = "failed"
    
    if hasattr(torch.backends, 'mps'):
        if torch.backends.mps.is_available():
            backends["mps"] = True
            if torch.backends.mps.is_built():
                try:
                    test_tensor = torch.randn(10, device='mps')
                    _ = torch.sum(test_tensor)
                    backends["mps"] = "verified"
                except Exception as e:
                    backends["mps"] = f"failed: {e}"
            else:
                backends["mps"] = "not_built"
    
    return backends

def setup_gpu_acceleration():
    """Comprehensive GPU setup with exhaustive detection"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"🔍 COMPREHENSIVE GPU DETECTION")
    print(f"System: {system} {machine}")
    print(f"PyTorch version: {torch.__version__}")
    
    if system == "Darwin":
        print("\n🍎 SCANNING MAC GPU CAPABILITIES...")
        gpu_info = detect_mac_gpu_capabilities()
        
        if gpu_info:
            print(f"Architecture: {gpu_info['architecture']}")
            print(f"Has Metal: {gpu_info['has_metal']}")
            print(f"Has Discrete GPU: {gpu_info['has_discrete_gpu']}")
            print(f"Metal Family: {gpu_info['metal_family']}")
            print(f"GPU Names: {gpu_info['gpu_names']}")
            print(f"GPU Memory: {gpu_info['memory_gb']:.1f} GB")
        
        print("\n🧪 TESTING PYTORCH BACKENDS...")
        backends = test_pytorch_backends()
        
        for backend, status in backends.items():
            if status == "verified":
                print(f"✅ {backend.upper()}: Working")
            elif status == True:
                print(f"⚠️ {backend.upper()}: Available but not tested")
            elif status == "failed" or "failed:" in str(status):
                print(f"❌ {backend.upper()}: {status}")
            elif status == "not_built":
                print(f"⚠️ {backend.upper()}: Available but not built")
            elif status == False:
                print(f"❌ {backend.upper()}: Not available")
        
        if backends["cuda"] == "verified":
            device_name = torch.cuda.get_device_name(0)
            print(f"\n🚀 USING CUDA: {device_name}")
            if "A100" in device_name:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                torch.backends.cudnn.benchmark = True
                torch.cuda.empty_cache()
                return {"type": "cuda_a100", "device": "cuda", "optimized": True, "gpu_info": gpu_info}
            else:
                torch.backends.cudnn.benchmark = True
                return {"type": "cuda_mac", "device": "cuda", "optimized": True, "gpu_info": gpu_info}
        
        elif backends["mps"] == "verified":
            print(f"\n🍎 USING METAL GPU: {gpu_info['gpu_names']}")
            print(f"Metal Performance Shaders optimized for {gpu_info['metal_family']}")
            return {"type": "metal_gpu", "device": "mps", "optimized": True, "gpu_info": gpu_info}
        
        elif backends["mps"] == True or backends["mps"] == "not_built":
            print(f"\n⚠️ METAL AVAILABLE BUT NOT WORKING")
            print("Attempting to enable Metal Performance Shaders...")
            try:
                import os
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                test_tensor = torch.randn(5, device='mps')
                result = torch.sum(test_tensor)
                print(f"✅ Metal GPU enabled with fallback: {result:.3f}")
                return {"type": "metal_fallback", "device": "mps", "optimized": True, "gpu_info": gpu_info}
            except Exception as e:
                print(f"❌ Metal GPU fallback failed: {e}")
        
        if gpu_info and gpu_info["has_metal"]:
            print(f"\n🛠️ ATTEMPTING METAL WORKAROUNDS...")
            
            metal_devices = []
            if gpu_info["has_discrete_gpu"]:
                metal_devices.append("discrete")
            if gpu_info["architecture"] == "arm64":
                metal_devices.append("integrated")
            
            for device_type in metal_devices:
                try:
                    print(f"Testing {device_type} Metal GPU...")
                    os.environ['PYTORCH_MPS_DEVICE'] = device_type
                    test_tensor = torch.randn(3, device='mps')
                    result = torch.sum(test_tensor)
                    print(f"✅ {device_type} Metal GPU working: {result:.3f}")
                    return {"type": f"metal_{device_type}", "device": "mps", "optimized": True, "gpu_info": gpu_info}
                except Exception as e:
                    print(f"❌ {device_type} Metal failed: {e}")
        
        print(f"\n💻 FALLBACK TO OPTIMIZED CPU")
        print("Using CPU with optimized BLAS libraries")
        return {"type": "cpu_optimized", "device": "cpu", "optimized": False, "gpu_info": gpu_info}
    
    elif torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        print(f"🚀 CUDA GPU detected: {device_name}")
        if "A100" in device_name:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.cuda.empty_cache()
            return {"type": "cuda_a100", "device": "cuda", "optimized": True, "gpu_info": None}
        else:
            torch.backends.cudnn.benchmark = True
            return {"type": "cuda_standard", "device": "cuda", "optimized": True, "gpu_info": None}
    
    else:
        print("⚠️ No GPU acceleration available - using CPU")
        return {"type": "cpu_standard", "device": "cpu", "optimized": False, "gpu_info": None}

def validate_config():
    errors = []
    
    if SIGNAL_CONFIDENCE_THRESHOLD <= 0 or SIGNAL_CONFIDENCE_THRESHOLD > 1:
        errors.append("SIGNAL_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if POSITION_SIZE_PERCENT <= 0 or POSITION_SIZE_PERCENT > 100:
        errors.append("POSITION_SIZE_PERCENT must be between 0 and 100")
    
    if MAX_OPEN_POSITIONS <= 0:
        errors.append("MAX_OPEN_POSITIONS must be positive")
    
    if not ASSETS or len(ASSETS) == 0:
        errors.append("ASSETS list cannot be empty")
    
    return errors

GPU_CONFIG = setup_gpu_acceleration()
GPU_AVAILABLE = GPU_CONFIG["optimized"]
DEVICE = GPU_CONFIG["device"]
MAC_GPU_INFO = GPU_CONFIG.get("gpu_info")

config_errors = validate_config()
if config_errors:
    print("❌ CONFIGURATION ERRORS:")
    for error in config_errors:
        print(f"   - {error}")
    print("❌ Fix configuration before starting system!")
else:
    print(f"\n✅ FINAL CONFIG: {GPU_CONFIG['type']} on {DEVICE}")
    if MAC_GPU_INFO and MAC_GPU_INFO["gpu_names"]:
        print(f"✅ GPU: {', '.join(MAC_GPU_INFO['gpu_names'])}")
    print(f"✅ Assets: {ASSETS}, Mode: {MODE}")
