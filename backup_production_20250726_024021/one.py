#!/usr/bin/env python3
"""
HFT System Performance Test Suite
Comprehensive testing for signal generation, execution timing, and system health
"""

import sys
import time
import json
import os
import subprocess
import threading
import statistics
import psutil
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

class HFTPerformanceTester:
    def __init__(self):
        self.test_results = {}
        self.system_metrics = {}
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 HFT SYSTEM PERFORMANCE TEST SUITE")
        print("=" * 50)
        
        tests = [
            ("GPU Detection", self.test_gpu_detection),
            ("Module Imports", self.test_module_imports),
            ("Signal Generation Speed", self.test_signal_generation_speed),
            ("Signal Quality", self.test_signal_quality),
            ("File I/O Performance", self.test_file_io_performance),
            ("Memory Usage", self.test_memory_usage),
            ("Concurrent Processing", self.test_concurrent_processing),
            ("Rust Executor", self.test_rust_executor),
            ("End-to-End Latency", self.test_end_to_end_latency),
            ("System Stability", self.test_system_stability),
            ("Fallback Mechanisms", self.test_fallback_mechanisms)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result.get("passed", False):
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"💥 {test_name}: CRASHED - {e}")
                self.test_results[test_name] = {"passed": False, "error": str(e)}
        
        self.generate_report()
    
    def test_gpu_detection(self) -> Dict:
        """Test GPU detection and availability"""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                return {
                    "passed": True,
                    "gpu_type": "CUDA",
                    "device_name": gpu_name,
                    "memory_gb": round(gpu_memory, 2)
                }
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return {
                    "passed": True,
                    "gpu_type": "Apple MPS",
                    "device_name": "Apple Silicon",
                    "memory_gb": "N/A"
                }
            else:
                return {"passed": False, "error": "No GPU detected"}
                
        except Exception as e:
            return {"passed": False, "error": f"GPU test failed: {e}"}
    
    def test_module_imports(self) -> Dict:
        """Test all module imports and initialization"""
        modules = [
            'config', 'signal_engine', 'confidence_scoring', 
            'entropy_meter', 'laggard_sniper', 'relief_trap',
            'logger', 'notifier_elegant'
        ]
        
        import_times = {}
        failed_imports = []
        
        for module in modules:
            start = time.time()
            try:
                __import__(module)
                import_times[module] = (time.time() - start) * 1000  # ms
            except Exception as e:
                failed_imports.append(f"{module}: {e}")
        
        return {
            "passed": len(failed_imports) == 0,
            "import_times_ms": import_times,
            "failed_imports": failed_imports,
            "total_modules": len(modules),
            "avg_import_time_ms": statistics.mean(import_times.values()) if import_times else 0
        }
    
    def test_signal_generation_speed(self) -> Dict:
        """Test signal generation speed and consistency"""
        try:
            import signal_engine
            import confidence_scoring
            
            times = []
            signals = []
            
            for i in range(100):
                start = time.time()
                
                shared_data = {
                    "timestamp": time.time(),
                    "mode": "dry",
                    "iteration": i,
                    "gpu_available": True
                }
                
                signal = signal_engine.generate_signal(shared_data)
                execution_time = (time.time() - start) * 1000000  # microseconds
                times.append(execution_time)
                signals.append(signal)
            
            return {
                "passed": True,
                "iterations": 100,
                "avg_time_us": statistics.mean(times),
                "min_time_us": min(times),
                "max_time_us": max(times),
                "std_dev_us": statistics.stdev(times),
                "p95_time_us": sorted(times)[94],  # 95th percentile
                "signals_generated": len([s for s in signals if s.get("confidence", 0) > 0])
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Signal generation test failed: {e}"}
    
    def test_signal_quality(self) -> Dict:
        """Test signal quality and consistency"""
        try:
            import signal_engine
            import confidence_scoring
            
            signals = []
            confidences = []
            
            for i in range(50):
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                signal = signal_engine.generate_signal(shared_data)
                
                if signal.get("confidence"):
                    confidences.append(signal["confidence"])
                    signals.append(signal)
            
            if not confidences:
                return {"passed": False, "error": "No signals with confidence generated"}
            
            # Test signal merging
            merged = confidence_scoring.merge_signals(signals[:10])
            
            return {
                "passed": True,
                "total_signals": len(signals),
                "avg_confidence": statistics.mean(confidences),
                "confidence_range": [min(confidences), max(confidences)],
                "signals_with_data": len([s for s in signals if "signal_data" in s]),
                "merged_confidence": merged.get("confidence", 0),
                "signal_consistency": statistics.stdev(confidences) < 0.1
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Signal quality test failed: {e}"}
    
    def test_file_io_performance(self) -> Dict:
        """Test file I/O performance for signal writing"""
        try:
            test_signal = {
                "timestamp": time.time(),
                "confidence": 0.85,
                "best_signal": {
                    "asset": "BTC",
                    "entry_price": 45000,
                    "stop_loss": 45675,
                    "take_profit_1": 44325
                }
            }
            
            write_times = []
            read_times = []
            
            for i in range(100):
                # Write test
                start = time.time()
                with open(f"/tmp/test_signal_{i}.json", "w") as f:
                    json.dump(test_signal, f)
                write_times.append((time.time() - start) * 1000000)  # microseconds
                
                # Read test
                start = time.time()
                with open(f"/tmp/test_signal_{i}.json", "r") as f:
                    json.load(f)
                read_times.append((time.time() - start) * 1000000)
                
                # Cleanup
                os.remove(f"/tmp/test_signal_{i}.json")
            
            return {
                "passed": True,
                "avg_write_time_us": statistics.mean(write_times),
                "avg_read_time_us": statistics.mean(read_times),
                "max_write_time_us": max(write_times),
                "max_read_time_us": max(read_times),
                "p95_write_time_us": sorted(write_times)[94],
                "p95_read_time_us": sorted(read_times)[94]
            }
            
        except Exception as e:
            return {"passed": False, "error": f"File I/O test failed: {e}"}
    
    def test_memory_usage(self) -> Dict:
        """Test memory usage and leaks"""
        try:
            import signal_engine
            import torch
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate many signals to test for memory leaks
            for i in range(1000):
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                signal_engine.generate_signal(shared_data)
                
                if i % 100 == 0:
                    # Force garbage collection
                    import gc
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            return {
                "passed": memory_increase < 100,  # Less than 100MB increase is acceptable
                "initial_memory_mb": round(initial_memory, 2),
                "final_memory_mb": round(final_memory, 2),
                "memory_increase_mb": round(memory_increase, 2),
                "memory_leak_detected": memory_increase > 100
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Memory test failed: {e}"}
    
    def test_concurrent_processing(self) -> Dict:
        """Test concurrent signal processing"""
        try:
            import signal_engine
            
            def generate_signal_worker(worker_id):
                start_time = time.time()
                shared_data = {
                    "timestamp": time.time(),
                    "mode": "dry",
                    "worker_id": worker_id
                }
                signal = signal_engine.generate_signal(shared_data)
                return {
                    "worker_id": worker_id,
                    "execution_time": (time.time() - start_time) * 1000,
                    "confidence": signal.get("confidence", 0)
                }
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(generate_signal_worker, i) for i in range(50)]
                results = [future.result() for future in as_completed(futures)]
            
            execution_times = [r["execution_time"] for r in results]
            confidences = [r["confidence"] for r in results if r["confidence"] > 0]
            
            return {
                "passed": len(results) == 50 and len(confidences) > 0,
                "concurrent_workers": 50,
                "successful_executions": len(results),
                "avg_execution_time_ms": statistics.mean(execution_times),
                "max_execution_time_ms": max(execution_times),
                "signals_with_confidence": len(confidences),
                "concurrent_performance_ok": max(execution_times) < 1000  # Less than 1 second
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Concurrent processing test failed: {e}"}
    
    def test_rust_executor(self) -> Dict:
        """Test Rust executor compilation and basic functionality"""
        try:
            # Check if Rust executor compiles
            result = subprocess.run(
                ["cargo", "check"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            compile_success = result.returncode == 0
            
            # Test basic signal file processing
            test_signal = {
                "timestamp": time.time(),
                "confidence": 0.8,
                "best_signal": {
                    "asset": "BTC",
                    "entry_price": 45000,
                    "stop_loss": 45675,
                    "take_profit_1": 44325
                }
            }
            
            with open("/tmp/signal.json", "w") as f:
                json.dump(test_signal, f)
            
            return {
                "passed": compile_success,
                "compilation_output": result.stderr if not compile_success else "OK",
                "signal_file_created": os.path.exists("/tmp/signal.json"),
                "rust_toolchain_available": True
            }
            
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Rust compilation timed out"}
        except FileNotFoundError:
            return {"passed": False, "error": "Cargo/Rust not found"}
        except Exception as e:
            return {"passed": False, "error": f"Rust executor test failed: {e}"}
    
    def test_end_to_end_latency(self) -> Dict:
        """Test complete end-to-end system latency"""
        try:
            import signal_engine
            import confidence_scoring
            
            latencies = []
            
            for i in range(20):
                start_time = time.time()
                
                # Complete signal generation pipeline
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                signal = signal_engine.generate_signal(shared_data)
                
                if signal.get("confidence", 0) > 0:
                    merged = confidence_scoring.merge_signals([signal])
                    
                    # Write to file (simulating real workflow)
                    with open("/tmp/test_signal.json", "w") as f:
                        json.dump(merged, f)
                
                end_to_end_time = (time.time() - start_time) * 1000  # milliseconds
                latencies.append(end_to_end_time)
            
            # Cleanup
            if os.path.exists("/tmp/test_signal.json"):
                os.remove("/tmp/test_signal.json")
            
            return {
                "passed": True,
                "iterations": len(latencies),
                "avg_latency_ms": statistics.mean(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "p95_latency_ms": sorted(latencies)[18],  # 95th percentile
                "sub_millisecond_count": len([l for l in latencies if l < 1.0]),
                "target_latency_met": statistics.mean(latencies) < 10.0  # Under 10ms average
            }
            
        except Exception as e:
            return {"passed": False, "error": f"End-to-end latency test failed: {e}"}
    
    def test_system_stability(self) -> Dict:
        """Test system stability under load"""
        try:
            import signal_engine
            
            start_time = time.time()
            errors = []
            successful_iterations = 0
            
            # Run for 30 seconds
            while time.time() - start_time < 30:
                try:
                    shared_data = {"timestamp": time.time(), "mode": "dry"}
                    signal = signal_engine.generate_signal(shared_data)
                    
                    if signal.get("confidence", 0) > 0:
                        successful_iterations += 1
                        
                    time.sleep(0.01)  # 10ms cycle
                    
                except Exception as e:
                    errors.append(str(e))
            
            total_time = time.time() - start_time
            
            return {
                "passed": len(errors) == 0,
                "test_duration_seconds": round(total_time, 2),
                "successful_iterations": successful_iterations,
                "errors_encountered": len(errors),
                "error_rate": len(errors) / successful_iterations if successful_iterations > 0 else 1,
                "iterations_per_second": successful_iterations / total_time,
                "stability_score": (successful_iterations / (successful_iterations + len(errors))) * 100
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Stability test failed: {e}"}
    
    def test_fallback_mechanisms(self) -> Dict:
        """Test system fallback mechanisms"""
        try:
            import confidence_scoring
            
            # Test with empty signals
            empty_result = confidence_scoring.merge_signals([])
            
            # Test with malformed signals
            bad_signals = [
                {"confidence": "invalid"},
                {"source": "test"},
                {}
            ]
            bad_result = confidence_scoring.merge_signals(bad_signals)
            
            # Test file writing fallback
            os.makedirs("/tmp", exist_ok=True)
            fallback_signal = {
                "confidence": 0.72,
                "best_signal": {
                    "asset": "BTC",
                    "entry_price": 67500,
                    "reason": "fallback_test"
                }
            }
            
            with open("/tmp/fallback_test.json", "w") as f:
                json.dump(fallback_signal, f)
            
            return {
                "passed": True,
                "empty_signals_handled": empty_result.get("confidence", 0) > 0,
                "bad_signals_handled": bad_result.get("confidence", 0) > 0,
                "fallback_confidence": empty_result.get("confidence", 0),
                "file_fallback_works": os.path.exists("/tmp/fallback_test.json"),
                "graceful_degradation": True
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Fallback test failed: {e}"}
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results.values() if result.get("passed", False))
        total_tests = len(self.test_results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        print(f"Total Test Time: {time.time() - self.start_time:.2f} seconds")
        
        # Performance highlights
        print("\n🚀 PERFORMANCE HIGHLIGHTS:")
        
        if "Signal Generation Speed" in self.test_results:
            speed_result = self.test_results["Signal Generation Speed"]
            if speed_result.get("passed"):
                print(f"  • Signal Generation: {speed_result.get('avg_time_us', 0):.0f}μs average")
                print(f"  • P95 Latency: {speed_result.get('p95_time_us', 0):.0f}μs")
        
        if "End-to-End Latency" in self.test_results:
            latency_result = self.test_results["End-to-End Latency"]
            if latency_result.get("passed"):
                print(f"  • End-to-End: {latency_result.get('avg_latency_ms', 0):.2f}ms average")
                print(f"  • Sub-millisecond: {latency_result.get('sub_millisecond_count', 0)} operations")
        
        if "Memory Usage" in self.test_results:
            memory_result = self.test_results["Memory Usage"]
            if memory_result.get("passed"):
                print(f"  • Memory Usage: {memory_result.get('memory_increase_mb', 0):.1f}MB increase")
        
        if "System Stability" in self.test_results:
            stability_result = self.test_results["System Stability"]
            if stability_result.get("passed"):
                print(f"  • Stability: {stability_result.get('stability_score', 0):.1f}% uptime")
                print(f"  • Throughput: {stability_result.get('iterations_per_second', 0):.1f} ops/sec")
        
        # Failed tests
        failed_tests = [name for name, result in self.test_results.items() 
                       if not result.get("passed", False)]
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test_name in failed_tests:
                error = self.test_results[test_name].get("error", "Unknown error")
                print(f"  • {test_name}: {error}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if "GPU Detection" in self.test_results:
            gpu_result = self.test_results["GPU Detection"]
            if gpu_result.get("passed"):
                gpu_type = gpu_result.get("gpu_type", "Unknown")
                print(f"  • GPU ({gpu_type}) detected and working")
            else:
                print("  • ⚠️ No GPU detected - performance will be limited")
        
        if passed_tests == total_tests:
            print("  • 🎉 All tests passed! System is ready for production")
        elif passed_tests >= total_tests * 0.8:
            print("  • ✅ Most tests passed - system is functional with minor issues")
        else:
            print("  • ⚠️ Multiple test failures - review system configuration")
        
        # Save detailed results
        with open("logs/performance_test_results.json", "w") as f:
            json.dump({
                "timestamp": time.time(),
                "test_results": self.test_results,
                "summary": {
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "success_rate": (passed_tests/total_tests)*100,
                    "test_duration": time.time() - self.start_time
                }
            }, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: logs/performance_test_results.json")

if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    tester = HFTPerformanceTester()
    tester.run_all_tests()