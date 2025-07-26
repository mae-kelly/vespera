import torch
import sys
import platform

def test_gpu():
    results = {
        'cuda_available': torch.cuda.is_available(),
        'cuda_devices': torch.cuda.device_count() if torch.cuda.is_available() else 0,
        'mps_available': hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() if platform.system() == 'Darwin' else False,
        'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU',
        'platform': platform.system()
    }
    
    # Performance test
    if results['cuda_available'] or results['mps_available']:
        device = 'cuda' if results['cuda_available'] else 'mps'
        try:
            x = torch.randn(1000, 1000, device=device)
            y = torch.matmul(x, x)
            results['gpu_performance_test'] = 'PASS'
        except Exception as e:
            results['gpu_performance_test'] = f'FAIL: {e}'
    else:
        results['gpu_performance_test'] = 'SKIP'
    
    return results

if __name__ == "__main__":
    import json
    results = test_gpu()
    print(json.dumps(results, indent=2))
