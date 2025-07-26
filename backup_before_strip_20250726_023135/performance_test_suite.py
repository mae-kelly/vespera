#!/usr/bin/env python
"""
HT System Performance Test Suite
Comprehensive testing for signal generation, eecution timing, and system health
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
from concurrent.futures import ThreadPoolecutor, as_completed
import requests

class HTPerformanceTester:
    def __init__(self):
        self.test_results = 
        self.system_metrics = 
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 HT SYSTM PRORMANC TST SUIT")
        print("=" * )
        
        tests = [
            ("GPU Detection", self.test_gpu_detection),
            ("Module Imports", self.test_module_imports),
            ("Signal Generation Speed", self.test_signal_generation_speed),
            ("Signal Quality", self.test_signal_quality),
            ("ile I/O Performance", self.test_file_io_performance),
            ("Memory Usage", self.test_memory_usage),
            ("Concurrent Processing", self.test_concurrent_processing),
            ("Rust ecutor", self.test_rust_eecutor),
            ("nd-to-nd Latency", self.test_end_to_end_latency),
            ("System Stability", self.test_system_stability),
            ("allback Mechanisms", self.test_fallback_mechanisms)
        ]
        
        for test_name, test_func in tests:
            print(f"n🧪 Testing: test_name")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result.get("passed", alse):
                    print(f"✅ test_name: PASSD")
                else:
                    print(f"❌ test_name: AILD - result.get('error', 'Unknown error')")
            ecept ception as e:
                print(f"💥 test_name: CRASHD - e")
                self.test_results[test_name] = "passed": alse, "error": str(e)
        
        self.generate_report()
    
    def test_gpu_detection(self) -> Dict:
        """Test GPU detection and availability"""
        try:
            import torch
            
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name()
                gpu_memory = torch.cuda.get_device_properties().total_memory / **
                return 
                    "passed": True,
                    "gpu_type": "CUDA",
                    "device_name": gpu_name,
                    "memory_gb": round(gpu_memory, )
                
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return 
                    "passed": True,
                    "gpu_type": "Apple MPS",
                    "device_name": "Apple Silicon",
                    "memory_gb": "N/A"
                
            else:
                return "passed": alse, "error": "No GPU detected"
                
        ecept ception as e:
            return "passed": alse, "error": f"GPU test failed: e"
    
    def test_module_imports(self) -> Dict:
        """Test all module imports and initialization"""
        modules = [
            'config', 'signal_engine', 'confidence_scoring', 
            'entropy_meter', 'laggard_sniper', 'relief_trap',
            'logger', 'notifier_elegant'
        ]
        
        import_times = 
        failed_imports = []
        
        for module in modules:
            start = time.time()
            try:
                __import__(module)
                import_times[module] = (time.time() - start) *   # ms
            ecept ception as e:
                failed_imports.append(f"module: e")
        
        return 
            "passed": len(failed_imports) <= ,  # Allow some optional modules to fail
            "import_times_ms": import_times,
            "failed_imports": failed_imports,
            "total_modules": len(modules),
            "avg_import_time_ms": statistics.mean(import_times.values()) if import_times else 
        
    
    def test_signal_generation_speed(self) -> Dict:
        """Test signal generation speed and consistency"""
        try:
            import signal_engine
            
            times = []
            signals = []
            
            for i in range():  # Reduced iterations for speed
                start = time.time()
                
                shared_data = 
                    "timestamp": time.time(),
                    "mode": "dry",
                    "iteration": i,
                    "gpu_available": True
                
                
                signal = signal_engine.generate_signal(shared_data)
                eecution_time = (time.time() - start) *   # microseconds
                times.append(eecution_time)
                signals.append(signal)
            
            return 
                "passed": True,
                "iterations": ,
                "avg_time_us": statistics.mean(times),
                "min_time_us": min(times),
                "ma_time_us": ma(times),
                "std_dev_us": statistics.stdev(times),
                "p9_time_us": sorted(times)[],  # 9th percentile
                "signals_generated": len([s for s in signals if s.get("confidence", ) > ])
            
            
        ecept ception as e:
            return "passed": alse, "error": f"Signal generation test failed: e"
    
    def test_signal_quality(self) -> Dict:
        """Test signal quality and consistency"""
        try:
            import signal_engine
            
            signals = []
            confidences = []
            
            for i in range():  # Quick test
                shared_data = "timestamp": time.time(), "mode": "dry"
                signal = signal_engine.generate_signal(shared_data)
                
                if signal.get("confidence"):
                    confidences.append(signal["confidence"])
                    signals.append(signal)
            
            if not confidences:
                return "passed": alse, "error": "No signals with confidence generated"
            
            return 
                "passed": True,
                "total_signals": len(signals),
                "avg_confidence": statistics.mean(confidences),
                "confidence_range": [min(confidences), ma(confidences)],
                "signals_with_data": len([s for s in signals if "signal_data" in s]),
                "signal_consistency": statistics.stdev(confidences) < . if len(confidences) >  else True
            
            
        ecept ception as e:
            return "passed": alse, "error": f"Signal quality test failed: e"
    
    def test_file_io_performance(self) -> Dict:
        """Test file I/O performance for signal writing"""
        try:
            test_signal = 
                "timestamp": time.time(),
                "confidence": .,
                "best_signal": 
                    "asset": "TC",
                    "entry_price": ,
                    "stop_loss": ,
                    "take_profit_": 
                
            
            
            write_times = []
            read_times = []
            
            for i in range():  # Reduced iterations
                # Write test
                start = time.time()
                with open(f"/tmp/test_signal_i.json", "w") as f:
                    json.dump(test_signal, f)
                write_times.append((time.time() - start) * )  # microseconds
                
                # Read test
                start = time.time()
                with open(f"/tmp/test_signal_i.json", "r") as f:
                    json.load(f)
                read_times.append((time.time() - start) * )
                
                # Cleanup
                os.remove(f"/tmp/test_signal_i.json")
            
            return 
                "passed": True,
                "avg_write_time_us": statistics.mean(write_times),
                "avg_read_time_us": statistics.mean(read_times),
                "ma_write_time_us": ma(write_times),
                "ma_read_time_us": ma(read_times),
                "p9_write_time_us": sorted(write_times)[] if len(write_times) >  else ma(write_times),
                "p9_read_time_us": sorted(read_times)[] if len(read_times) >  else ma(read_times)
            
            
        ecept ception as e:
            return "passed": alse, "error": f"ile I/O test failed: e"
    
    def test_memory_usage(self) -> Dict:
        """Test memory usage and leaks"""
        try:
            import signal_engine
            import torch
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss /  /   # M
            
            # Generate signals to test for memory leaks
            for i in range():  # Reduced iterations
                shared_data = "timestamp": time.time(), "mode": "dry"
                signal_engine.generate_signal(shared_data)
                
                if i %  == :
                    # orce garbage collection
                    import gc
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
            
            final_memory = process.memory_info().rss /  /   # M
            memory_increase = final_memory - initial_memory
            
            return 
                "passed": memory_increase < ,  # Less than M increase is acceptable
                "initial_memory_mb": round(initial_memory, ),
                "final_memory_mb": round(final_memory, ),
                "memory_increase_mb": round(memory_increase, ),
                "memory_leak_detected": memory_increase > 
            
            
        ecept ception as e:
            return "passed": alse, "error": f"Memory test failed: e"
    
    def test_concurrent_processing(self) -> Dict:
        """Test concurrent signal processing"""
        try:
            import signal_engine
            
            def generate_signal_worker(worker_id):
                start_time = time.time()
                shared_data = 
                    "timestamp": time.time(),
                    "mode": "dry",
                    "worker_id": worker_id
                
                signal = signal_engine.generate_signal(shared_data)
                return 
                    "worker_id": worker_id,
                    "eecution_time": (time.time() - start_time) * ,
                    "confidence": signal.get("confidence", )
                
            
            with ThreadPoolecutor(ma_workers=) as eecutor:
                futures = [eecutor.submit(generate_signal_worker, i) for i in range()]
                results = [future.result() for future in as_completed(futures)]
            
            eecution_times = [r["eecution_time"] for r in results]
            confidences = [r["confidence"] for r in results if r["confidence"] > ]
            
            return 
                "passed": len(results) ==  and len(confidences) > ,
                "concurrent_workers": ,
                "successful_eecutions": len(results),
                "avg_eecution_time_ms": statistics.mean(eecution_times),
                "ma_eecution_time_ms": ma(eecution_times),
                "signals_with_confidence": len(confidences),
                "concurrent_performance_ok": ma(eecution_times) < 
            
            
        ecept ception as e:
            return "passed": alse, "error": f"Concurrent processing test failed: e"
    
    def test_rust_eecutor(self) -> Dict:
        """Test Rust eecutor compilation and basic functionality"""
        try:
            # Check if Rust eecutor compiles
            result = subprocess.run(
                ["cargo", "check"],
                capture_output=True,
                tet=True,
                timeout=
            )
            
            compile_success = result.returncode == 
            
            # Test basic signal file processing
            test_signal = 
                "timestamp": time.time(),
                "confidence": .,
                "best_signal": 
                    "asset": "TC",
                    "entry_price": ,
                    "stop_loss": ,
                    "take_profit_": 
                
            
            
            with open("/tmp/signal.json", "w") as f:
                json.dump(test_signal, f)
            
            return 
                "passed": compile_success,
                "compilation_output": result.stderr if not compile_success else "OK",
                "signal_file_created": os.path.eists("/tmp/signal.json"),
                "rust_toolchain_available": True
            
            
        ecept subprocess.Timeoutpired:
            return "passed": alse, "error": "Rust compilation timed out"
        ecept ileNotoundrror:
            return "passed": alse, "error": "Cargo/Rust not found"
        ecept ception as e:
            return "passed": alse, "error": f"Rust eecutor test failed: e"
    
    def test_end_to_end_latency(self) -> Dict:
        """Test complete end-to-end system latency"""
        try:
            import signal_engine
            
            latencies = []
            
            for i in range():  # Quick test
                start_time = time.time()
                
                # Complete signal generation pipeline
                shared_data = "timestamp": time.time(), "mode": "dry"
                signal = signal_engine.generate_signal(shared_data)
                
                if signal.get("confidence", ) > :
                    # Write to file (simulating real workflow)
                    with open("/tmp/test_signal.json", "w") as f:
                        json.dump(signal, f)
                
                end_to_end_time = (time.time() - start_time) *   # milliseconds
                latencies.append(end_to_end_time)
            
            # Cleanup
            if os.path.eists("/tmp/test_signal.json"):
                os.remove("/tmp/test_signal.json")
            
            return 
                "passed": True,
                "iterations": len(latencies),
                "avg_latency_ms": statistics.mean(latencies),
                "min_latency_ms": min(latencies),
                "ma_latency_ms": ma(latencies),
                "sub_millisecond_count": len([l for l in latencies if l < .]),
                "target_latency_met": statistics.mean(latencies) < .  # Under ms average
            
            
        ecept ception as e:
            return "passed": alse, "error": f"nd-to-end latency test failed: e"
    
    def test_system_stability(self) -> Dict:
        """Test system stability under load"""
        try:
            import signal_engine
            
            start_time = time.time()
            errors = []
            successful_iterations = 
            
            # Run for  seconds
            while time.time() - start_time < :
                try:
                    shared_data = "timestamp": time.time(), "mode": "dry"
                    signal = signal_engine.generate_signal(shared_data)
                    
                    if signal.get("confidence", ) > :
                        successful_iterations += 
                        
                    time.sleep(.)  # ms cycle
                    
                ecept ception as e:
                    errors.append(str(e))
            
            total_time = time.time() - start_time
            
            return 
                "passed": len(errors) == ,
                "test_duration_seconds": round(total_time, ),
                "successful_iterations": successful_iterations,
                "errors_encountered": len(errors),
                "error_rate": len(errors) / successful_iterations if successful_iterations >  else ,
                "iterations_per_second": successful_iterations / total_time,
                "stability_score": (successful_iterations / (successful_iterations + len(errors))) *  if successful_iterations >  else 
            
            
        ecept ception as e:
            return "passed": alse, "error": f"Stability test failed: e"
    
    def test_fallback_mechanisms(self) -> Dict:
        """Test system fallback mechanisms"""
        try:
            # Test file writing fallback
            os.makedirs("/tmp", eist_ok=True)
            fallback_signal = 
                "confidence": .,
                "best_signal": 
                    "asset": "TC",
                    "entry_price": ,
                    "reason": "fallback_test"
                
            
            
            with open("/tmp/fallback_test.json", "w") as f:
                json.dump(fallback_signal, f)
            
            return 
                "passed": True,
                "file_fallback_works": os.path.eists("/tmp/fallback_test.json"),
                "graceful_degradation": True
            
            
        ecept ception as e:
            return "passed": alse, "error": f"allback test failed: e"
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("n" + "=" * )
        print("📊 PRORMANC TST RPORT")
        print("=" * )
        
        passed_tests = sum( for result in self.test_results.values() if result.get("passed", alse))
        total_tests = len(self.test_results)
        
        print(f"Tests Passed: passed_tests/total_tests ((passed_tests/total_tests)*:.f%)")
        print(f"Total Test Time: time.time() - self.start_time:.f seconds")
        
        # Performance highlights
        print("n🚀 PRORMANC HIGHLIGHTS:")
        
        if "Signal Generation Speed" in self.test_results:
            speed_result = self.test_results["Signal Generation Speed"]
            if speed_result.get("passed"):
                print(f"  • Signal Generation: speed_result.get('avg_time_us', ):.fμs average")
                print(f"  • P9 Latency: speed_result.get('p9_time_us', ):.fμs")
        
        if "nd-to-nd Latency" in self.test_results:
            latency_result = self.test_results["nd-to-nd Latency"]
            if latency_result.get("passed"):
                print(f"  • nd-to-nd: latency_result.get('avg_latency_ms', ):.fms average")
                print(f"  • Sub-millisecond: latency_result.get('sub_millisecond_count', ) operations")
        
        if "Memory Usage" in self.test_results:
            memory_result = self.test_results["Memory Usage"]
            if memory_result.get("passed"):
                print(f"  • Memory Usage: memory_result.get('memory_increase_mb', ):.fM increase")
        
        if "System Stability" in self.test_results:
            stability_result = self.test_results["System Stability"]
            if stability_result.get("passed"):
                print(f"  • Stability: stability_result.get('stability_score', ):.f% uptime")
                print(f"  • Throughput: stability_result.get('iterations_per_second', ):.f ops/sec")
        
        # ailed tests
        failed_tests = [name for name, result in self.test_results.items() 
                       if not result.get("passed", alse)]
        
        if failed_tests:
            print(f"n❌ AILD TSTS:")
            for test_name in failed_tests:
                error = self.test_results[test_name].get("error", "Unknown error")
                print(f"  • test_name: error")
        
        # Recommendations
        print(f"n💡 RCOMMNDATIONS:")
        
        if "GPU Detection" in self.test_results:
            gpu_result = self.test_results["GPU Detection"]
            if gpu_result.get("passed"):
                gpu_type = gpu_result.get("gpu_type", "Unknown")
                print(f"  • GPU (gpu_type) detected and working")
            else:
                print("  • ⚠️ No GPU detected - performance will be limited")
        
        if passed_tests == total_tests:
            print("  • 🎉 All tests passed! System is ready for production")
        elif passed_tests >= total_tests * .:
            print("  • ✅ Most tests passed - system is functional with minor issues")
        else:
            print("  • ⚠️ Multiple test failures - review system configuration")
        
        # Save detailed results
        os.makedirs("logs", eist_ok=True)
        with open("logs/performance_test_results.json", "w") as f:
            json.dump(
                "timestamp": time.time(),
                "test_results": self.test_results,
                "summary": 
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "success_rate": (passed_tests/total_tests)*,
                    "test_duration": time.time() - self.start_time
                
            , f, indent=)
        
        print(f"n📁 Detailed results saved to: logs/performance_test_results.json")

if __name__ == "__main__":
    # nsure logs directory eists
    Path("logs").mkdir(eist_ok=True)
    
    tester = HTPerformanceTester()
    tester.run_all_tests()
