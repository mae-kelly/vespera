import time
import threading
from collections import deque
import json

class PerformanceMetrics:
    def __init__(self):
        self.signal_latencies = deque(maxlen=1000)
        self.execution_times = deque(maxlen=1000)
        self.memory_usage = deque(maxlen=100)
        self.error_counts = {"signal": 0, "execution": 0, "connection": 0}
        self.start_time = time.time()
        
    def record_signal_latency(self, latency_us):
        self.signal_latencies.append(latency_us)
        
    def record_execution_time(self, exec_time_ms):
        self.execution_times.append(exec_time_ms)
        
    def record_error(self, error_type):
        self.error_counts[error_type] += 1
        
    def get_performance_report(self):
        return {
            "avg_signal_latency_us": sum(self.signal_latencies) / len(self.signal_latencies) if self.signal_latencies else 0,
            "min_signal_latency_us": min(self.signal_latencies) if self.signal_latencies else 0,
            "avg_execution_time_ms": sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0,
            "total_errors": sum(self.error_counts.values()),
            "uptime_seconds": time.time() - self.start_time,
            "signals_processed": len(self.signal_latencies)
        }
        
    def export_metrics(self):
        with open("/tmp/performance_metrics.json", "w") as f:
            json.dump(self.get_performance_report(), f, indent=2)

metrics = PerformanceMetrics()
