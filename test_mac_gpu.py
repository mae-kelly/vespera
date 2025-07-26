#!/usr/bin/env python3
import torch
import platform
import config
import cupy_fallback as cp

def test_mac_gpu_detection():
    print("🧪 MAC GPU DETECTION TEST")
    print("=" * 30)
    
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system}")
    print(f"Architecture: {machine}")
    print(f"PyTorch version: {torch.__version__}")
    
    print(f"\nGPU Configuration: {config.GPU_CONFIG}")
    print(f"Device: {config.DEVICE}")
    print(f"GPU Available: {config.GPU_AVAILABLE}")
    
    if system == "Darwin":
        print(f"\n🍎 macOS Detection:")
        if machine == "arm64":
            print("  - Apple Silicon detected")
        else:
            print("  - Intel Mac detected")
        
        if torch.backends.mps.is_available():
            print("  ✅ Metal Performance Shaders available")
            if torch.backends.mps.is_built():
                print("  ✅ Metal Performance Shaders built and ready")
                
                # Test actual Metal GPU functionality
                try:
                    test_tensor = torch.randn(10, device='mps')
                    test_result = torch.sum(test_tensor)
                    print(f"  ✅ Metal GPU computation test: {test_result:.3f}")
                except Exception as e:
                    print(f"  ❌ Metal GPU test failed: {e}")
            else:
                print("  ❌ Metal Performance Shaders not built")
        else:
            print("  ❌ Metal Performance Shaders not available")
            print("  💡 This Mac may not support Metal GPU acceleration")
    
    print(f"\n🧮 Testing tensor operations on {config.DEVICE}:")
    try:
        x = cp.array([1, 2, 3, 4, 5])
        y = cp.sum(x)
        z = cp.mean(x)
        
        print(f"  Array: {x}")
        print(f"  Sum: {y}")
        print(f"  Mean: {z}")
        print(f"  Device: {x.device}")
        
        computation_test = cp.array([10.0]) * cp.array([5.0])
        print(f"  Computation test: {computation_test}")
        
        if config.DEVICE == "mps":
            print("  ✅ Apple GPU acceleration working!")
        elif config.DEVICE == "cuda":
            print("  ✅ CUDA GPU acceleration working!")
        else:
            print("  ⚠️ Using CPU (no GPU acceleration)")
            
        return True
        
    except Exception as e:
        print(f"  ❌ GPU test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_mac_gpu_detection()
    if success:
        print("\n🎉 Mac Metal GPU detection working correctly!")
        if config.DEVICE == "mps":
            print("🚀 Your Mac is using Metal GPU acceleration for maximum performance!")
        else:
            print("ℹ️ Metal GPU not available - check PyTorch MPS support for your Mac model")
    else:
        print("\n❌ Mac Metal GPU detection failed")
        exit(1)
