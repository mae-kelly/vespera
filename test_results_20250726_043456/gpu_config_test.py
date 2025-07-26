import sys
sys.path.append('.')

def test_gpu_configuration():
    try:
        import config
        
        # Check if config properly detects and configures GPU
        gpu_config = getattr(config, 'GPU_CONFIG', None)
        device = getattr(config, 'DEVICE', None)
        gpu_available = getattr(config, 'GPU_AVAILABLE', None)
        
        if not gpu_config:
            return {'success': False, 'error': 'GPU_CONFIG not found in config'}
        
        if not device or device == 'cpu':
            return {'success': False, 'error': f'Invalid device configuration: {device}'}
        
        if not gpu_available:
            return {'success': False, 'error': 'GPU_AVAILABLE is False'}
        
        return {
            'success': True,
            'gpu_config': gpu_config,
            'device': device,
            'gpu_available': gpu_available
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    import json
    result = test_gpu_configuration()
    print(json.dumps(result))
