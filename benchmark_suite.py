#!/usr/bin/env python3
"""
HFT System Benchmark & Stress Test Suite
Comprehensive performance benchmarking and stress testing
"""

import sys
import time
import json
import os
import statistics
import psutil
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

class HFTBenchmarkSuite:
    def __init__(self):
        self.results = {}
        
    def run_benchmarks(self):
        """Run complete benchmark suite"""
        print("🚀 HFT SYSTEM BENCHMARK SUITE")
        print("=" * 50)
        
        benchmarks = [
            ("Signal Generation Throughput", self.benchmark_signal_throughput),
            ("Memory Efficiency", self.benchmark_memory_efficiency),
            ("Latency Distribution", self.benchmark_latency_distribution),
            ("System Stability", self.benchmark_system_stability)
        ]
        
        for benchmark_name, benchmark_func in benchmarks:
            print(f"\n📊 Benchmarking: {benchmark_name}")
            try:
                result = benchmark_func()
                self.results[benchmark_name] = result
                self.print_benchmark_result(benchmark_name, result)
            except Exception as e:
                print(f"💥 {benchmark_name}: FAILED - {e}")
                self.results[benchmark_name] = {"error": str(e), "passed": False}
        
        self.generate_benchmark_report()
    
    def print_benchmark_result(self, name: str, result: Dict):
        """Print benchmark result summary"""
        if result.get("error"):
            print(f"❌ {name}: ERROR - {result['error']}")
        else:
            print(f"✅ {name}: COMPLETED")
    
    def benchmark_signal_throughput(self) -> Dict:
        """Benchmark signal generation throughput"""
        try:
            import signal_engine
            
            # Warm up
            for _ in range(5):
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                signal_engine.generate_signal(shared_data)
            
            # Benchmark throughput
            iterations = 100
            start_time = time.time()
            
            for i in range(iterations):
                shared_data = {"timestamp": time.time(), "mode": "dry", "iteration": i}
                signal_engine.generate_signal(shared_data)
            
            total_time = time.time() - start_time
            throughput = iterations / total_time
            
            return {
                "throughput": throughput,
                "total_time": total_time,
                "passed": True
            }
            
        except Exception as e:
            return {"error": f"Signal throughput benchmark failed: {e}", "passed": False}
    
    def benchmark_memory_efficiency(self) -> Dict:
        """Benchmark memory usage and efficiency"""
        try:
            import signal_engine
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate signals
            for i in range(200):
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                signal_engine.generate_signal(shared_data)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory
            
            return {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "memory_efficient": memory_growth < 20,
                "passed": memory_growth < 50
            }
            
        except Exception as e:
            return {"error": f"Memory efficiency benchmark failed: {e}", "passed": False}
    
    def benchmark_latency_distribution(self) -> Dict:
        """Benchmark latency distribution and percentiles"""
        try:
            import signal_engine
            
            latencies = []
            
            for i in range(50):
                shared_data = {"timestamp": time.time(), "mode": "dry"}
                
                start_time = time.time()
                signal = signal_engine.generate_signal(shared_data)
                latency = (time.time() - start_time) * 1000000  # microseconds
                latencies.append(latency)
            
            latencies.sort()
            p50 = latencies[24]  # 50th percentile
            p95 = latencies[47]  # 95th percentile
            
            avg_latency = statistics.mean(latencies)
            
            return {
                "avg_latency_us": avg_latency,
                "p50_latency_us": p50,
                "p95_latency_us": p95,
                "latency_target_met": p95 < 50000,  # 95% under 50ms
                "passed": p95 < 100000  # 95% under 100ms
            }
            
        except Exception as e:
            return {"error": f"Latency distribution benchmark failed: {e}", "passed": False}
    
    def benchmark_system_stability(self) -> Dict:
        """Benchmark system stability under extended operation"""
        try:
            import signal_engine
            
            start_time = time.time()
            test_duration = 30  # 30 seconds
            
            signals_generated = 0
            errors = 0
            
            while time.time() - start_time < test_duration:
                try:
                    shared_data = {"timestamp": time.time(), "mode": "dry"}
                    signal = signal_engine.generate_signal(shared_data)
                    
                    if signal.get("confidence", 0) > 0:
                        signals_generated += 1
                    
                    time.sleep(0.1)  # 100ms cycle
                    
                except Exception as e:
                    errors += 1
            
            actual_duration = time.time() - start_time
            signals_per_second = signals_generated / actual_duration
            error_rate = errors / signals_generated if signals_generated > 0 else 1
            uptime_score = (signals_generated / (signals_generated + errors)) * 100
            
            return {
                "test_duration_seconds": actual_duration,
                "signals_generated": signals_generated,
                "errors_encountered": errors,
                "signals_per_second": signals_per_second,
                "error_rate": error_rate,
                "uptime_score": uptime_score,
                "system_stable": uptime_score > 90,
                "passed": uptime_score > 80 and error_rate < 0.1
            }
            
        except Exception as e:
            return {"error": f"System stability benchmark failed: {e}", "passed": False}
    
    def generate_benchmark_report(self):
        """Generate comprehensive benchmark report"""
        print("\n" + "=" * 70)
        print("📊 BENCHMARK REPORT")
        print("=" * 70)
        
        passed_benchmarks = sum(1 for result in self.results.values() 
                               if result.get("passed", False))
        total_benchmarks = len(self.results)
        
        print(f"Benchmarks: {passed_benchmarks}/{total_benchmarks} ({(passed_benchmarks/total_benchmarks)*100:.1f}%)")
        
        # Performance summary
        print(f"\n🚀 PERFORMANCE SUMMARY:")
        
        if "Signal Generation Throughput" in self.results:
            throughput = self.results["Signal Generation Throughput"]
            if not throughput.get("error"):
                print(f"  • Throughput: {throughput.get('throughput', 0):.1f} signals/sec")
        
        if "Latency Distribution" in self.results:
            latency = self.results["Latency Distribution"]
            if not latency.get("error"):
                print(f"  • P95 Latency: {latency.get('p95_latency_us', 0):.0f}μs")
        
        if "System Stability" in self.results:
            stability = self.results["System Stability"]
            if not stability.get("error"):
                print(f"  • System Uptime: {stability.get('uptime_score', 0):.1f}%")
        
        overall_score = (passed_benchmarks / total_benchmarks) * 100
        
        if overall_score >= 85:
            print("\n🎉 Excellent performance! System is production-ready")
        elif overall_score >= 70:
            print("\n✅ Good performance with room for optimization")
        else:
            print("\n⚠️ Performance needs improvement")
        
        # Save benchmark results
        os.makedirs("logs", exist_ok=True)
        with open("logs/benchmark_results.json", "w") as f:
            json.dump({
                "timestamp": time.time(),
                "benchmark_results": self.results,
                "overall_score": overall_score
            }, f, indent=2)
        
        print(f"\n📁 Benchmark results saved to: logs/benchmark_results.json")

def main():
    """Main benchmark runner"""
    print("🚀 Starting HFT System Benchmark Suite...")
    
    os.makedirs("logs", exist_ok=True)
    
    benchmark = HFTBenchmarkSuite()
    benchmark.run_benchmarks()
    
    passed_benchmarks = sum(1 for result in benchmark.results.values() 
                           if result.get("passed", False))
    total_benchmarks = len(benchmark.results)
    success_rate = (passed_benchmarks / total_benchmarks) * 100
    
    if success_rate >= 75:
        print("\n🎉 BENCHMARK SUITE COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("\n⚠️ BENCHMARK SUITE REVEALED PERFORMANCE ISSUES")
        return 1

if __name__ == "__main__":
    sys.exit(main())
