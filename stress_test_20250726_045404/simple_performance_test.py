import sys
import time
import json
sys.path.append('.')

def test_signal_performance():
    try:
        import signal_engine
        
        print("Testing signal generation performance...")
        
        times = []
        confidences = []
        errors = []
        
        # Test 20 signal generations
        for i in range(20):
            try:
                start = time.time()
                shared_data = {'timestamp': time.time(), 'mode': 'dry', 'iteration': i}
                signal = signal_engine.generate_signal(shared_data)
                end = time.time()
                
                execution_time = (end - start) * 1000  # Convert to milliseconds
                confidence = signal.get('confidence', 0)
                
                times.append(execution_time)
                confidences.append(confidence)
                
                print(f"  Signal {i+1}: {execution_time:.1f}ms, confidence: {confidence:.3f}")
                
            except Exception as e:
                errors.append(f"Signal {i}: {str(e)}")
                print(f"  Signal {i+1}: ERROR - {e}")
        
        # Calculate statistics
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_time = max_time = min_time = avg_confidence = 0
        
        results = {
            'successful_tests': len(times),
            'failed_tests': len(errors),
            'avg_time_ms': round(avg_time, 2),
            'min_time_ms': round(min_time, 2),
            'max_time_ms': round(max_time, 2),
            'avg_confidence': round(avg_confidence, 3),
            'above_threshold': len([c for c in confidences if c >= 0.75]),
            'errors': errors
        }
        
        print(f"\nPerformance Summary:")
        print(f"  Successful: {results['successful_tests']}/20")
        print(f"  Average time: {results['avg_time_ms']:.1f}ms")
        print(f"  Average confidence: {results['avg_confidence']:.3f}")
        print(f"  Above threshold (0.75): {results['above_threshold']}")
        
        return results
        
    except Exception as e:
        return {'error': str(e), 'successful_tests': 0}

if __name__ == "__main__":
    result = test_signal_performance()
    print(f"\nFINAL_RESULT: {json.dumps(result)}")
