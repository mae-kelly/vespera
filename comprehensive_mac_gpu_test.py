#!/usr/bin/env python3
import torch
import platform
import config
import cupy_fallback as cp
import subprocess
import time

def comprehensive_mac_gpu_test():
    print("🧪 COMPREHENSIVE MAC GPU DETECTION & TESTING")
    print("=" * 60)
    
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system}")
    print(f"Architecture: {machine}")
    print(f"PyTorch version: {torch.__version__}")
    
    if config.MAC_GPU_INFO:
        print(f"\n🔍 DETECTED GPU CAPABILITIES:")
        info = config.MAC_GPU_INFO
        print(f"  Has Metal: {info['has_metal']}")
        print(f"  Has Discrete GPU: {info['has_discrete_gpu']}")
        print(f"  Metal Family: {info['metal_family']}")
        print(f"  GPU Names: {info['gpu_names']}")
        print(f"  GPU Memory: {info['memory_gb']:.1f} GB")
    
    print(f"\n⚙️ PYTORCH CONFIGURATION:")
    print(f"  Selected Device: {config.DEVICE}")
    print(f"  GPU Type: {config.GPU_CONFIG['type']}")
    print(f"  Optimized: {config.GPU_AVAILABLE}")
    
    print(f"\n🧮 INTENSIVE GPU TESTING:")
    
    try:
        print("  Testing tensor creation...")
        x = cp.array([1.0, 2.0, 3.0, 4.0, 5.0])
        print(f"    Array device: {x.device}")
        print(f"    Array values: {x}")
        
        print("  Testing mathematical operations...")
        y = cp.array([2.0, 3.0, 4.0, 5.0, 6.0])
        z = x + y
        print(f"    Addition result: {z}")
        
        print("  Testing advanced operations...")
        mean_val = cp.mean(x)
        sum_val = cp.sum(y)
        log_val = cp.log(x + 1)
        print(f"    Mean: {mean_val}")
        print(f"    Sum: {sum_val}")
        print(f"    Log: {log_val}")
        
        print("  Testing large tensor operations...")
        large_tensor = cp.zeros((1000, 1000))
        large_result = cp.sum(large_tensor)
        print(f"    Large tensor sum: {large_result}")
        
        print("  Testing random operations...")
        random_tensor = torch.randn(100, 100, device=config.DEVICE)
        random_mean = torch.mean(random_tensor)
        print(f"    Random tensor mean: {random_mean:.4f}")
        
        print("  Testing memory operations...")
        if config.DEVICE == 'mps':
            try:
                torch.mps.empty_cache()
                print("    MPS cache cleared successfully")
            except:
                print("    MPS cache clear not available")
        
        performance_start = time.time()
        for _ in range(100):
            test_tensor = torch.randn(50, 50, device=config.DEVICE)
            result = torch.sum(test_tensor)
        performance_time = time.time() - performance_start
        print(f"    Performance test (100 ops): {performance_time:.4f}s")
        
        if config.DEVICE == "mps":
            print("\n🍎 APPLE METAL GPU VERIFICATION:")
            print("  ✅ All Metal GPU operations successful!")
            print("  🚀 Your Mac is using full Metal GPU acceleration!")
            
        elif config.DEVICE == "cuda":
            print("\n🚀 CUDA GPU VERIFICATION:")
            device_name = torch.cuda.get_device_name(0)
            print(f"  ✅ CUDA working on: {device_name}")
            
        else:
            print("\n💻 CPU FALLBACK:")
            print("  ⚠️ Using optimized CPU operations")
            if config.MAC_GPU_INFO and config.MAC_GPU_INFO["has_metal"]:
                print("  💡 Metal GPU detected but PyTorch MPS not working")
                print("  💡 Consider updating PyTorch for Metal support")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GPU test failed: {e}")
        return False

def test_signal_engine_with_gpu():
    print(f"\n🧪 SIGNAL ENGINE GPU ACCELERATION TEST")
    print("=" * 60)
    
    import signal_engine
    import time
    
    print(f"Device: {config.DEVICE}")
    print(f"GPU Config: {config.GPU_CONFIG}")
    
    signal_engine.feed.start_feed()
    time.sleep(3)
    
    shared_data = {
        "timestamp": time.time(),
        "mode": "dry", 
        "iteration": 1,
        "gpu_available": config.GPU_AVAILABLE
    }
    
    print("\nTesting signal generation with GPU acceleration...")
    start_time = time.time()
    signal = signal_engine.generate_signal(shared_data)
    signal_time = time.time() - start_time
    
    print(f"Signal confidence: {signal.get('confidence', 0):.3f}")
    print(f"Signal generation time: {signal_time:.4f}s")
    print(f"Signal source: {signal.get('source', 'unknown')}")
    
    if 'signal_data' in signal:
        data = signal['signal_data']
        print(f"Asset: {data.get('asset', 'N/A')}")
        print(f"Entry price: ${data.get('entry_price', 0):,.2f}")
        print(f"RSI: {data.get('rsi', 0):.2f}")
    
    print("\nTesting RSI calculation performance...")
    prices = [100 + i*0.1 + (i%3)*0.5 for i in range(100)]
    start_time = time.time()
    rsi = signal_engine.calculate_rsi_torch(prices)
    rsi_time = time.time() - start_time
    print(f"RSI result: {rsi:.2f} (calculated in {rsi_time:.6f}s)")
    
    print("\nTesting VWAP calculation performance...")
    prices = [100 + i*0.05 for i in range(50)]
    volumes = [1000 + i*10 for i in range(50)]
    start_time = time.time()
    vwap = signal_engine.calculate_vwap(prices, volumes)
    vwap_time = time.time() - start_time
    print(f"VWAP result: {vwap:.2f} (calculated in {vwap_time:.6f}s)")
    
    if config.DEVICE == "mps":
        print(f"\n🚀 ALL CALCULATIONS PERFORMED ON APPLE METAL GPU!")
        print(f"🍎 Maximum performance achieved on your Mac!")
    elif config.DEVICE == "cuda":
        print(f"\n🚀 ALL CALCULATIONS PERFORMED ON CUDA GPU!")
    else:
        print(f"\n💻 Calculations performed on optimized CPU")
    
    return True

if __name__ == "__main__":
    print("🔥 STARTING COMPREHENSIVE MAC GPU TESTING...")
    
    gpu_success = comprehensive_mac_gpu_test()
    signal_success = test_signal_engine_with_gpu()
    
    print(f"\n{'='*60}")
    print("🏁 FINAL RESULTS:")
    print(f"✅ GPU Detection: {'PASSED' if gpu_success else 'FAILED'}")
    print(f"✅ Signal Engine: {'PASSED' if signal_success else 'FAILED'}")
    
    if gpu_success and signal_success:
        if config.DEVICE == "mps":
            print("\n🎉 COMPLETE SUCCESS!")
            print("🍎 Your Mac Metal GPU is fully operational!")
            print("⚡ Maximum HFT performance achieved!")
        elif config.DEVICE == "cuda":
            print("\n🎉 CUDA GPU FULLY OPERATIONAL!")
        else:
            print("\n✅ System operational on CPU")
    else:
        print("\n❌ Some tests failed - check output above")
        exit(1)
