import torch
import sys
import platform
import subprocess

def get_gpu_info():
    results = {
        'platform': platform.system(),
        'gpu_tier': 'NONE',
        'device_name': 'NONE',
        'cuda_available': torch.cuda.is_available(),
        'cuda_devices': torch.cuda.device_count() if torch.cuda.is_available() else 0,
        'mps_available': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() if platform.system() == 'Darwin' else False,
        'qualification': 'FAIL',
        'reason': 'No GPU detected'
    }
    
    # TIER 1: A100 Detection (PRIORITY 1)
    if results['cuda_available'] and results['cuda_devices'] > 0:
        device_name = torch.cuda.get_device_name(0)
        results['device_name'] = device_name
        
        if 'A100' in device_name:
            results['gpu_tier'] = 'A100'
            results['qualification'] = 'EXCELLENT'
            results['reason'] = 'A100 GPU detected - optimal performance'
            return results
        elif any(gpu_type in device_name.upper() for gpu_type in ['RTX', 'GTX', 'TESLA', 'QUADRO', 'V100', 'P100']):
            results['gpu_tier'] = 'OTHER_CUDA'
            results['qualification'] = 'ACCEPTABLE'
            results['reason'] = f'CUDA GPU detected: {device_name}'
            return results
    
    # TIER 2: Apple Silicon M1/M2/M3 Metal (PRIORITY 2)
    if platform.system() == 'Darwin' and results['mps_available']:
        try:
            # Try to get Mac model info
            mac_model = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                              text=True, stderr=subprocess.DEVNULL).strip()
            
            if any(chip in mac_model for chip in ['M1', 'M2', 'M3']):
                if 'M1' in mac_model:
                    results['gpu_tier'] = 'M1_METAL'
                    results['device_name'] = 'Apple M1 (Metal Performance Shaders)'
                elif 'M2' in mac_model:
                    results['gpu_tier'] = 'M2_METAL'  
                    results['device_name'] = 'Apple M2 (Metal Performance Shaders)'
                elif 'M3' in mac_model:
                    results['gpu_tier'] = 'M3_METAL'
                    results['device_name'] = 'Apple M3 (Metal Performance Shaders)'
                
                results['qualification'] = 'GOOD'
                results['reason'] = f'Apple Silicon detected: {mac_model}'
                return results
            else:
                # Other Mac with MPS
                results['gpu_tier'] = 'OTHER_MAC_GPU'
                results['device_name'] = 'macOS GPU (Metal Performance Shaders)'
                results['qualification'] = 'MARGINAL'
                results['reason'] = 'Non-Apple Silicon Mac with GPU acceleration'
                return results
                
        except Exception:
            # MPS available but can't determine chip
            results['gpu_tier'] = 'UNKNOWN_MAC_GPU'
            results['device_name'] = 'macOS GPU (Metal Performance Shaders)'
            results['qualification'] = 'MARGINAL'
            results['reason'] = 'macOS GPU detected but chip unknown'
            return results
    
    # TIER 3: Other GPUs (PRIORITY 3)
    if results['cuda_available']:
        device_name = torch.cuda.get_device_name(0)
        results['device_name'] = device_name
        results['gpu_tier'] = 'OTHER_GPU'
        results['qualification'] = 'MARGINAL'
        results['reason'] = f'Basic GPU detected: {device_name}'
        return results
    
    # NO ACCEPTABLE GPU FOUND
    results['qualification'] = 'SYSTEM_HALT'
    results['reason'] = 'NO GPU ACCELERATION AVAILABLE - SYSTEM CANNOT RUN'
    return results

def performance_benchmark(gpu_info):
    """Run performance test on detected GPU"""
    if gpu_info['qualification'] == 'SYSTEM_HALT':
        return {'benchmark': 'SKIPPED', 'reason': 'No GPU available'}
    
    try:
        if gpu_info['cuda_available']:
            device = 'cuda'
        elif gpu_info['mps_available']:
            device = 'mps'
        else:
            return {'benchmark': 'FAIL', 'reason': 'No device available'}
        
        # Performance benchmark
        import time
        start_time = time.time()
        
        # Test matrix operations typical for HFT calculations
        x = torch.randn(2000, 2000, device=device, dtype=torch.float32)
        y = torch.randn(2000, 2000, device=device, dtype=torch.float32)
        
        # Matrix multiplication (common in signal processing)
        z1 = torch.matmul(x, y)
        
        # Element-wise operations (RSI, confidence calculations)
        z2 = torch.sigmoid(x) * torch.tanh(y)
        
        # Reduction operations (entropy, averaging)
        z3 = torch.sum(z1 * z2, dim=1)
        
        # Ensure computation completes
        if device == 'cuda':
            torch.cuda.synchronize()
        elif device == 'mps':
            torch.mps.synchronize()
        
        benchmark_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Performance tiers
        if benchmark_time < 100:
            perf_tier = 'EXCELLENT'
        elif benchmark_time < 300:
            perf_tier = 'GOOD'
        elif benchmark_time < 1000:
            perf_tier = 'ACCEPTABLE'
        else:
            perf_tier = 'POOR'
        
        return {
            'benchmark': 'PASS',
            'time_ms': benchmark_time,
            'performance_tier': perf_tier,
            'device_used': device
        }
        
    except Exception as e:
        return {'benchmark': 'FAIL', 'reason': str(e)}

if __name__ == "__main__":
    import json
    
    gpu_info = get_gpu_info()
    perf_results = performance_benchmark(gpu_info)
    
    result = {**gpu_info, 'performance': perf_results}
    print(json.dumps(result, indent=2))
