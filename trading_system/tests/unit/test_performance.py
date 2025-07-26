#!/usr/bin/env python3
"""
Performance Tests - Test system performance and benchmarks
"""
import sys
import time
import unittest
import statistics
import threading
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path
sys.path.insert(0, '.')

import config
import signal_engine
import confidence_scoring
from paper_trading_engine import get_paper_engine
from okx_market_data import get_okx_engine

class TestSystemPerformance(unittest.TestCase):
    
    def setUp(self):
        """Set up performance test environment"""
        # Ensure paper trading mode
        config.MODE = "paper"
        config.PAPER_TRADING = True
        config.LIVE_TRADING = False
        
        self.process = psutil.Process(os.getpid())
        
    def test_signal_generation_speed(self):
        """Test signal generation speed and consistency"""
        print("🧪 Testing signal generation speed...")
        
        iterations = 50
        times = []
        
        shared_data = {
            "timestamp": time.time(),
            "mode": "paper",
            "iteration": 100
        }
        
        # Warm up
        for _ in range(5):
            signal_engine.generate_signal(shared_data)
        
        # Actual test
        for i in range(iterations):
            start_time = time.perf_counter()
            signal = signal_engine.generate_signal(shared_data)
            end_time = time.perf_counter()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
            
            # Verify signal is valid
            self.assertIsInstance(signal, dict)
            self.assertIn("confidence", signal)
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        max_time = max(times)
        min_time = min(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"✅ Signal Generation Performance ({iterations} iterations):")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Median:  {median_time:.2f}ms")
        print(f"   Min:     {min_time:.2f}ms")
        print(f"   Max:     {max_time:.2f}ms")
        print(f"   Std Dev: {std_dev:.2f}ms")
        
        # Performance assertions
        self.assertLess(avg_time, 100, "Average signal generation too slow")
        self.assertLess(max_time, 500, "Worst case signal generation too slow")
        
        # Consistency check
        self.assertLess(std_dev, avg_time * 0.5, "Signal generation time too inconsistent")
    
    def test_confidence_scoring_speed(self):
        """Test confidence scoring performance"""
        print("🧪 Testing confidence scoring speed...")
        
        # Create test signals
        def create_test_signal(i):
            return {
                "confidence": 0.7 + (i % 3) * 0.1,
                "source": f"test_module_{i}",
                "production_validated": True,
                "rsi_drop": 20.0 + i * 2,
                "entropy": 0.3 + i * 0.05,
                "volume_acceleration": 1.5 + i * 0.2,
                "btc_dominance": 0.5 + i * 0.05,
                "signal_data": {
                    "asset": "BTC",
                    "entry_price": 67500.0 + i,
                    "stop_loss": 68500.0 + i,
                    "take_profit_1": 66500.0 + i,
                    "signal_type": "SHORT",
                    "reason": f"test_signal_{i}"
                },
                "timestamp": time.time()
            }
        
        iterations = 30
        times = []
        
        # Test with varying numbers of signals
        for num_signals in [1, 3, 5]:
            for i in range(iterations // 3):
                signals = [create_test_signal(j) for j in range(num_signals)]
                
                start_time = time.perf_counter()
                result = confidence_scoring.softmax_weighted_scoring(signals)
                end_time = time.perf_counter()
                
                times.append((end_time - start_time) * 1000)  # Convert to ms
                
                # Verify result
                self.assertIsInstance(result, dict)
                self.assertIn("confidence", result)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        print(f"✅ Confidence Scoring Performance ({iterations} iterations):")
        print(f"   Average: {avg_time:.2f}ms")
        print(f"   Max:     {max_time:.2f}ms")
        
        # Performance assertions
        self.assertLess(avg_time, 50, "Average confidence scoring too slow")
        self.assertLess(max_time, 200, "Worst case confidence scoring too slow")
    
    def test_paper_trading_speed(self):
        """Test paper trading execution speed"""
        print("🧪 Testing paper trading speed...")
        
        paper_engine = get_paper_engine()
        paper_engine.positions.clear()
        
        iterations = 20
        times = []
        
        for i in range(iterations):
            signal = {
                "confidence": 0.85,
                "signal_data": {
                    "asset": f"TEST{i}",  # Use unique assets
                    "entry_price": 1000.0 + i,
                    "stop_loss": 1020.0 + i,
                    "take_profit_1": 980.0 + i,
                    "signal_type": "SHORT"
                }
            }
            
            start_time = time.perf_counter()
            result = paper_engine.open_position(signal)
            end_time = time.perf_counter()
            
            if result:  # Only count successful executions
                times.append((end_time - start_time) * 1000)
        
        if times:
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            print(f"✅ Paper Trading Performance ({len(times)} executions):")
            print(f"   Average: {avg_time:.2f}ms")
            print(f"   Max:     {max_time:.2f}ms")
            
            # Performance assertions
            self.assertLess(avg_time, 10, "Paper trading execution too slow")
        else:
            print("⚠️ No successful paper trades executed")
    
    def test_concurrent_signal_processing(self):
        """Test concurrent signal processing performance"""
        print("🧪 Testing concurrent signal processing...")
        
        def generate_and_score():
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper",
                "iteration": 100
            }
            
            signal = signal_engine.generate_signal(shared_data)
            result = confidence_scoring.merge_signals([signal])
            return result
        
        iterations = 20
        start_time = time.perf_counter()
        
        # Test concurrent execution
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_and_score) for _ in range(iterations)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1000
        avg_time_per_signal = total_time / iterations
        
        print(f"✅ Concurrent Processing Performance:")
        print(f"   Total time: {total_time:.2f}ms")
        print(f"   Avg per signal: {avg_time_per_signal:.2f}ms")
        print(f"   Successful signals: {len(results)}")
        
        # Verify all results are valid
        self.assertEqual(len(results), iterations)
        for result in results:
            self.assertIsInstance(result, dict)
            self.assertIn("confidence", result)
    
    def test_memory_usage(self):
        """Test memory usage during operation"""
        print("🧪 Testing memory usage...")
        
        # Get initial memory usage
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Run a bunch of operations
        paper_engine = get_paper_engine()
        
        for i in range(100):
            shared_data = {
                "timestamp": time.time(),
                "mode": "paper", 
                "iteration": i
            }
            
            # Generate signal
            signal = signal_engine.generate_signal(shared_data)
            
            # Score signal
            merged = confidence_scoring.merge_signals([signal])
            
            # Execute trade (some will fail due to limits)
            if i < 3:  # Only first few to avoid limits
                signal["signal_data"]["asset"] = f"TEST{i}"
                paper_engine.open_position(merged)
        
        # Get final memory usage
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"✅ Memory Usage Test:")
        print(f"   Initial: {initial_memory:.1f} MB")
        print(f"   Final:   {final_memory:.1f} MB")
        print(f"   Increase: {memory_increase:.1f} MB")
        
        # Memory usage should be reasonable
        self.assertLess(memory_increase, 100, "Memory usage increased too much")
    
    def test_cpu_usage_during_load(self):
        """Test CPU usage during high load"""
        print("🧪 Testing CPU usage during load...")
        
        def cpu_intensive_work():
            for _ in range(50):
                shared_data = {
                    "timestamp": time.time(),
                    "mode": "paper",
                    "iteration": 100
                }
                signal = signal_engine.generate_signal(shared_data)
                confidence_scoring.merge_signals([signal])
        
        # Measure CPU usage during work
        cpu_percentages = []
        
        def monitor_cpu():
            for _ in range(10):  # Monitor for 5 seconds
                cpu_percentages.append(self.process.cpu_percent())
                time.sleep(0.5)
        
        # Start monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Do CPU intensive work
        start_time = time.time()
        cpu_intensive_work()
        end_time = time.time()
        
        monitor_thread.join()
        
        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)
            
            print(f"✅ CPU Usage Test:")
            print(f"   Duration: {(end_time - start_time):.1f}s")
            print(f"   Avg CPU: {avg_cpu:.1f}%")
            print(f"   Max CPU: {max_cpu:.1f}%")
            
            # CPU usage should be reasonable (not maxing out single core)
            self.assertLess(avg_cpu, 90, "Average CPU usage too high")
    
    def test_market_data_latency(self):
        """Test market data retrieval latency"""
        print("🧪 Testing market data latency...")
        
        market_engine = get_okx_engine()
        
        latencies = []
        successful_requests = 0
        
        for i in range(10):
            start_time = time.perf_counter()
            
            try:
                price_data = market_engine.get_live_price("BTC")
                end_time = time.perf_counter()
                
                if price_data and price_data.get('price', 0) > 0:
                    latency = (end_time - start_time) * 1000  # ms
                    latencies.append(latency)
                    successful_requests += 1
                    
            except Exception as e:
                print(f"   Request {i} failed: {e}")
            
            time.sleep(0.1)  # Small delay between requests
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            min_latency = min(latencies)
            
            print(f"✅ Market Data Latency ({successful_requests}/10 successful):")
            print(f"   Average: {avg_latency:.1f}ms")
            print(f"   Min:     {min_latency:.1f}ms") 
            print(f"   Max:     {max_latency:.1f}ms")
            
            # Latency should be reasonable for trading
            self.assertLess(avg_latency, 1000, "Market data latency too high")
        else:
            print("⚠️ No successful market data requests")
    
    def test_throughput_benchmark(self):
        """Test overall system throughput"""
        print("🧪 Testing system throughput...")
        
        paper_engine = get_paper_engine()
        paper_engine.positions.clear()
        
        num_signals = 100
        start_time = time.time()
        
        successful_signals = 0
        successful_trades = 0
        
        for i in range(num_signals):
            try:
                # Generate signal
                shared_data = {
                    "timestamp": time.time(),
                    "mode": "paper",
                    "iteration": i + 100
                }
                
                signal = signal_engine.generate_signal(shared_data)
                successful_signals += 1
                
                # Process signal
                merged = confidence_scoring.merge_signals([signal])
                
                # Attempt trade (will fail after position limits)
                if i < config.MAX_OPEN_POSITIONS:
                    signal["signal_data"]["asset"] = f"TEST{i}"
                    result = paper_engine.open_position(merged)
                    if result:
                        successful_trades += 1
                        
            except Exception as e:
                print(f"   Error in iteration {i}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        signals_per_second = successful_signals / total_time
        
        print(f"✅ System Throughput Benchmark:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful signals: {successful_signals}/{num_signals}")
        print(f"   Successful trades: {successful_trades}")
        print(f"   Signals per second: {signals_per_second:.1f}")
        
        # Should process at least 10 signals per second
        self.assertGreater(signals_per_second, 10, "System throughput too low")


def run_performance_tests():
    """Run performance test suite"""
    print("🔥 RUNNING PERFORMANCE TESTS")
    print("="*60)
    print("⚡ Testing system speed and efficiency")
    print("📊 Measuring latency, throughput, and resource usage")
    print("="*60)
    
    # Ensure paper trading mode
    config.MODE = "paper"
    config.PAPER_TRADING = True
    config.LIVE_TRADING = False
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSystemPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("🔥 PERFORMANCE TEST RESULTS")
    print("="*60)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ PERFORMANCE FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n💥 PERFORMANCE ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n🎉 ALL PERFORMANCE TESTS PASSED!")
        print("✅ Signal generation is fast and consistent")
        print("✅ Confidence scoring is efficient")
        print("✅ Paper trading executes quickly")
        print("✅ System handles concurrent operations well")
        print("✅ Memory and CPU usage are reasonable")
        print("✅ Market data latency is acceptable")
        print("✅ Overall throughput meets requirements")
    else:
        print("\n❌ SOME PERFORMANCE TESTS FAILED")
        print("🔧 Review performance issues and optimize")
    
    return success


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)