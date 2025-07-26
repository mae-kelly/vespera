import sys
import time
import threading
import json
import statistics
sys.path.append('.')

def single_signal_test():
    try:
        import signal_engine
        start = time.time()
        shared_data = {'timestamp': time.time(), 'mode': 'dry', 'iteration': 1}
        signal = signal_engine.generate_signal(shared_data)
        end = time.time()
        return (end - start) * 1000, signal.get('confidence', 0)
    except Exception as e:
        return None, str(e)

def concurrent_signal_test(num_threads=10, iterations_per_thread=5):
    results = []
    errors = []
    
    def worker():
        for _ in range(iterations_per_thread):
            time_ms, confidence = single_signal_test()
            if time_ms is not None:
                results.append({'time_ms': time_ms, 'confidence': confidence})
            else:
                errors.append(confidence)  # confidence contains error message
    
    threads = []
    start_time = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    return {
        'total_time': (end_time - start_time) * 1000,
        'results': results,
        'errors': errors,
        'num_threads': num_threads,
        'iterations_per_thread': iterations_per_thread
    }

def memory_stress_test(duration_seconds=30):
    import signal_engine
    import gc
    
    start_time = time.time()
    iteration_count = 0
    memory_samples = []
    
    while time.time() - start_time < duration_seconds:
        try:
            shared_data = {'timestamp': time.time(), 'mode': 'dry', 'iteration': iteration_count}
            signal = signal_engine.generate_signal(shared_data)
            iteration_count += 1
            
            if iteration_count % 100 == 0:
                gc.collect()
                # Try to get memory usage if psutil available
                try:
                    import psutil
                    memory_samples.append(psutil.Process().memory_info().rss / 1024 / 1024)  # MB
                except ImportError:
                    memory_samples.append(0)  # Fallback if psutil not available
                    
        except Exception as e:
            print(f"Memory stress error: {e}")
            break
    
    return {
        'duration': time.time() - start_time,
        'iterations': iteration_count,
        'memory_samples': memory_samples,
        'avg_memory_mb': statistics.mean(memory_samples) if memory_samples else 0
    }

if __name__ == "__main__":
    import json
    
    print("Running performance tests...")
    
    # Test 1: Single threaded performance
    times = []
    confidences = []
    for i in range(20):
        time_ms, confidence = single_signal_test()
        if time_ms is not None:
            times.append(time_ms)
            confidences.append(confidence)
    
    single_thread_results = {
        'avg_time_ms': statistics.mean(times) if times else 0,
        'min_time_ms': min(times) if times else 0,
        'max_time_ms': max(times) if times else 0,
        'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0,
        'avg_confidence': statistics.mean(confidences) if confidences else 0,
        'successful_runs': len(times)
    }
    
    # Test 2: Concurrent performance
    concurrent_results = concurrent_signal_test()
    
    # Test 3: Memory stress test
    memory_results = memory_stress_test(10)  # 10 second test
    
    results = {
        'single_thread': single_thread_results,
        'concurrent': concurrent_results,
        'memory_stress': memory_results
    }
    
    print(json.dumps(results, indent=2))
