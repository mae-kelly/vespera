import sys
import time
import json
sys.path.append('.')

def test_gpu():
    try:
        import config
        device = config.DEVICE
        
        print(f"Testing GPU on device: {device}")
        
        # Import torch after config
        import torch
        
        operations_completed = 0
        errors = []
        
        start_time = time.time()
        
        # Test 10 GPU operations
        for i in range(10):
            try:
                # Create tensors on GPU
                x = torch.randn(1000, 1000, device=device, dtype=torch.float32)
                y = torch.randn(1000, 1000, device=device, dtype=torch.float32)
                
                # Perform operations
                z1 = torch.matmul(x, y)
                z2 = torch.sigmoid(z1)
                z3 = torch.softmax(z2, dim=1)
                result = torch.sum(z3)
                
                # Synchronize
                if device == 'cuda':
                    torch.cuda.synchronize()
                elif device == 'mps':
                    torch.mps.synchronize()
                
                operations_completed += 1
                print(f"  GPU operation {i+1}: OK (result: {result.item():.3f})")
                
                # Cleanup
                del x, y, z1, z2, z3, result
                
            except Exception as e:
                errors.append(f"Operation {i}: {str(e)}")
                print(f"  GPU operation {i+1}: ERROR - {e}")
        
        total_time = (time.time() - start_time) * 1000
        
        results = {
            'device': device,
            'operations_completed': operations_completed,
            'total_operations': 10,
            'total_time_ms': round(total_time, 2),
            'avg_time_per_op': round(total_time / 10, 2),
            'errors': errors
        }
        
        print(f"\nGPU Test Summary:")
        print(f"  Device: {device}")
        print(f"  Operations completed: {operations_completed}/10")
        print(f"  Total time: {results['total_time_ms']:.1f}ms")
        print(f"  Average per operation: {results['avg_time_per_op']:.1f}ms")
        
        return results
        
    except Exception as e:
        return {'error': str(e), 'operations_completed': 0}

if __name__ == "__main__":
    result = test_gpu()
    print(f"\nFINAL_RESULT: {json.dumps(result)}")
