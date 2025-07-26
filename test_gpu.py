#!/usr/bin/env python3
import torch
import platform
import logging

logging.basicConfig(level=logging.INFO)

def test_all_gpu_options():
    """Test multiple ways to detect and use GPU on M1 Mac"""
    
    print("🔍 Testing GPU detection methods...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"PyTorch version: {torch.__version__}")
    
    # Method 1: Standard CUDA check
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        print(f"✅ Method 1 - CUDA: {gpu_name}")
        return device
    
    # Method 2: Standard MPS check
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        try:
            device = torch.device("mps")
            test_tensor = torch.zeros(1, device=device)
            print("✅ Method 2 - MPS available and functional")
            return device
        except Exception as e:
            print(f"❌ Method 2 - MPS failed: {e}")
    
    # Method 3: Direct MPS device creation
    try:
        device = torch.device("mps")
        test_tensor = torch.zeros(1, device=device)
        test_result = test_tensor + 1
        print("✅ Method 3 - Direct MPS creation successful")
        return device
    except Exception as e:
        print(f"❌ Method 3 - Direct MPS failed: {e}")
    
    # Method 4: Check torch.has_mps (newer PyTorch)
    try:
        if torch.has_mps:
            device = torch.device("mps")
            test_tensor = torch.randn(10, 10, device=device)
            print("✅ Method 4 - torch.has_mps successful")
            return device
    except Exception as e:
        print(f"❌ Method 4 - torch.has_mps failed: {e}")
    
    # Method 5: Force MPS on macOS
    if platform.system() == "Darwin":
        try:
            import subprocess
            result = subprocess.run(['sysctl', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            if 'Apple' in result.stdout:
                device = torch.device("mps")
                torch.zeros(1, device=device)
                print("✅ Method 5 - Forced MPS on Apple Silicon")
                return device
        except Exception as e:
            print(f"❌ Method 5 - Force MPS failed: {e}")
    
    # Method 6: Environment variable override
    try:
        import os
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        device = torch.device("mps")
        test_tensor = torch.zeros(1, device=device)
        print("✅ Method 6 - MPS with fallback enabled")
        return device
    except Exception as e:
        print(f"❌ Method 6 - MPS fallback failed: {e}")
    
    print("❌ ALL GPU METHODS FAILED - NO GPU AVAILABLE")
    raise RuntimeError("No GPU detected - CPU not allowed")

def benchmark_gpu(device):
    """Benchmark the detected GPU"""
    print(f"\n🏃 Benchmarking {device}...")
    
    # Matrix multiplication benchmark
    sizes = [100, 500, 1000, 2000]
    
    for size in sizes:
        try:
            # Create test tensors
            a = torch.randn(size, size, device=device)
            b = torch.randn(size, size, device=device)
            
            # Warm up
            for _ in range(10):
                c = torch.mm(a, b)
            
            # Benchmark
            import time
            start_time = time.time()
            for _ in range(100):
                c = torch.mm(a, b)
            if device.type == "mps":
                torch.mps.synchronize()
            elif device.type == "cuda":
                torch.cuda.synchronize()
            
            elapsed = time.time() - start_time
            ops_per_sec = 100 / elapsed
            
            print(f"  {size}x{size} matrix mult: {ops_per_sec:.1f} ops/sec")
            
        except Exception as e:
            print(f"  {size}x{size} failed: {e}")
            break

if __name__ == "__main__":
    try:
        device = test_all_gpu_options()
        benchmark_gpu(device)
        print(f"\n✅ GPU READY: {device}")
        print("🚀 ML training can proceed")
    except Exception as e:
        print(f"\n❌ GPU TEST FAILED: {e}")
        print("🛑 Cannot proceed with ML training")
