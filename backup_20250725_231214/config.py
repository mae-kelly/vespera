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

def setup_mandatory_gpu_acceleration():
    """MANDATORY GPU HIERARCHY: A100 → M1 → Other GPU → FAIL"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"🎯 MANDATORY GPU DETECTION")
    print(f"System: {system} {machine}")
    print(f"PyTorch version: {torch.__version__}")
    
    # PRIORITY 1: A100 GPUs (HIGHEST PERFORMANCE)
    print("\n🏆 PRIORITY 1: A100 GPU DETECTION")
    print("=" * 50)
    
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA GPU found: {device_name}")
            
            if "A100" in device_name:
                print("🏆 A100 DETECTED - MAXIMUM PERFORMANCE MODE")
                test_tensor = torch.randn(100, device='cuda')
                result = torch.sum(test_tensor)
                print(f"✅ A100 GPU validated: {result:.3f}")
                
                # Enable A100 optimizations
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                torch.backends.cudnn.benchmark = True
                torch.cuda.empty_cache()
                
                return {
                    "type": "cuda_a100",
                    "device": "cuda",
                    "optimized": True,
                    "gpu_info": {"name": device_name, "a100": True},
                    "priority": 1
                }
        except Exception as e:
            print(f"⚠️ A100 validation failed: {e}")
    else:
        print("❌ No CUDA GPUs available")
    
    # PRIORITY 2: APPLE SILICON (M1/M2/M3/M4)
    if system == "Darwin":
        print("\n🍎 PRIORITY 2: APPLE SILICON DETECTION")
        print("=" * 50)
        
        try:
            cpu_info = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                    capture_output=True, text=True, timeout=5)
            if cpu_info.returncode == 0:
                cpu_brand = cpu_info.stdout.strip()
                print(f"CPU: {cpu_brand}")
                
                if any(chip in cpu_brand for chip in ['M1', 'M2', 'M3', 'M4']):
                    print(f"✅ Apple Silicon confirmed: {cpu_brand}")
                    
                    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                        try:
                            print("🧪 Testing Apple Silicon GPU...")
                            test_tensor = torch.randn(100, device='mps')
                            result = torch.sum(test_tensor)
                            print(f"✅ APPLE SILICON GPU ACTIVE: {result:.3f}")
                            
                            return {
                                "type": "apple_silicon",
                                "device": "mps",
                                "optimized": True,
                                "gpu_info": {"name": cpu_brand, "apple_silicon": True},
                                "priority": 2
                            }
                        except Exception as e:
                            print(f"⚠️ Apple Silicon GPU test failed: {e}")
                            # Try with fallback
                            try:
                                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
                                test_tensor = torch.randn(10, device='mps')
                                result = torch.sum(test_tensor)
                                print(f"✅ Apple Silicon GPU with fallback: {result:.3f}")
                                return {
                                    "type": "apple_silicon_fallback",
                                    "device": "mps", 
                                    "optimized": True, 
                                    "gpu_info": {"name": cpu_brand, "apple_silicon": True},
                                    "priority": 2
                                }
                            except Exception as e2:
                                print(f"❌ Apple Silicon GPU fallback failed: {e2}")
                    else:
                        print("❌ MPS not available for Apple Silicon")
        except Exception as e:
            print(f"❌ Apple Silicon detection failed: {e}")
    
    # PRIORITY 3: OTHER CUDA GPUs
    print("\n⚡ PRIORITY 3: OTHER CUDA GPU DETECTION")
    print("=" * 50)
    
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ Other CUDA GPU found: {device_name}")
            
            test_tensor = torch.randn(10, device='cuda')
            result = torch.sum(test_tensor)
            print(f"✅ CUDA GPU validated: {result:.3f}")
            
            torch.backends.cudnn.benchmark = True
            return {
                "type": "cuda_standard",
                "device": "cuda",
                "optimized": True,
                "gpu_info": {"name": device_name},
                "priority": 3
            }
        except Exception as e:
            print(f"❌ CUDA GPU validation failed: {e}")
    
    # PRIORITY 4: AMD ROCm (experimental)
    print("\n🔴 PRIORITY 4: AMD GPU DETECTION")
    print("=" * 50)
    
    try:
        # Check for ROCm
        rocm_result = subprocess.run(['rocm-smi', '--showproductname'], 
                                   capture_output=True, text=True, timeout=5)
        if rocm_result.returncode == 0 and rocm_result.stdout.strip():
            print(f"✅ AMD GPU detected: {rocm_result.stdout.strip()}")
            return {
                "type": "amd_rocm",
                "device": "cuda",  # ROCm can use CUDA-like interface
                "optimized": False,
                "gpu_info": {"name": rocm_result.stdout.strip()},
                "priority": 4
            }
    except:
        pass
    
    # COMPLETE FAILURE - NO CPU FALLBACK ALLOWED
    print("\n❌ CRITICAL SYSTEM FAILURE")
    print("=" * 50)
    print("🚨 NO GPU ACCELERATION DETECTED")
    print("")
    print("MANDATORY GPU REQUIREMENTS:")
    print("  🏆 NVIDIA A100 (Preferred)")
    print("  🍎 Apple Silicon M1/M2/M3/M4")
    print("  ⚡ Other NVIDIA GPUs with CUDA")
    print("  🔴 AMD GPUs with ROCm")
    print("")
    print("SYSTEM REQUIREMENTS NOT MET")
    print("This Stanford PhD-level system requires GPU acceleration.")
    print("CPU fallback is NOT ALLOWED.")
    print("")
    print("Please install appropriate GPU drivers and try again.")
    sys.exit(1)

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

# Initialize MANDATORY GPU 
GPU_CONFIG = setup_mandatory_gpu_acceleration()
GPU_AVAILABLE = True  # Always true since we exit if no GPU
DEVICE = GPU_CONFIG["device"]

# Validate configuration
config_errors = validate_config()
if config_errors:
    print("❌ CONFIGURATION ERRORS:")
    for error in config_errors:
        print(f"   - {error}")
    print("❌ Fix configuration before starting system!")
    sys.exit(1)
else:
    print(f"\n✅ MANDATORY GPU CONFIGURATION:")
    print(f"   Type: {GPU_CONFIG['type']}")
    print(f"   Device: {DEVICE}")
    print(f"   Priority: {GPU_CONFIG.get('priority', 'Unknown')}")
    
    if GPU_CONFIG.get("gpu_info", {}).get("name"):
        print(f"   GPU: {GPU_CONFIG['gpu_info']['name']}")
    
    print(f"   Assets: {ASSETS}")
    print(f"   Mode: {MODE}")
    
    # Show priority hierarchy
    priority_messages = {
        1: "🏆 USING A100 GPU (Maximum Performance)",
        2: "🍎 USING APPLE SILICON GPU (Excellent Performance)", 
        3: "⚡ USING NVIDIA GPU (Good Performance)",
        4: "🔴 USING AMD GPU (Basic Performance)"
    }
    print(f"\n{priority_messages.get(GPU_CONFIG['priority'], '❓ Unknown GPU Type')}")
    print(f"✅ System ready for Stanford PhD-level performance")
