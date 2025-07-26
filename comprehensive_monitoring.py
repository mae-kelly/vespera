import psutil
import time
import json
import threading

class SystemMonitor:
    def __init__(self):
        self.monitoring = True
        self.metrics = {
            "cpu_percent": [],
            "memory_percent": [],
            "disk_usage": [],
            "network_io": [],
            "process_count": 0
        }
        
    def start_monitoring(self):
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        
    def _monitor_loop(self):
        while self.monitoring:
            try:
                self.metrics["cpu_percent"].append(psutil.cpu_percent())
                self.metrics["memory_percent"].append(psutil.virtual_memory().percent)
                self.metrics["disk_usage"].append(psutil.disk_usage('/').percent)
                self.metrics["process_count"] = len(psutil.pids())
                
                if len(self.metrics["cpu_percent"]) > 100:
                    for key in ["cpu_percent", "memory_percent", "disk_usage"]:
                        self.metrics[key] = self.metrics[key][-50:]
                        
                time.sleep(5)
            except:
                pass
                
    def get_health_status(self):
        if not self.metrics["cpu_percent"]:
            return "unknown"
            
        avg_cpu = sum(self.metrics["cpu_percent"][-10:]) / len(self.metrics["cpu_percent"][-10:])
        avg_memory = sum(self.metrics["memory_percent"][-10:]) / len(self.metrics["memory_percent"][-10:])
        
        if avg_cpu > 90 or avg_memory > 90:
            return "critical"
        elif avg_cpu > 70 or avg_memory > 70:
            return "warning"
        else:
            return "healthy"
            
    def export_system_metrics(self):
        with open("/tmp/system_metrics.json", "w") as f:
            json.dump({
                "health_status": self.get_health_status(),
                "current_metrics": {
                    "cpu_percent": self.metrics["cpu_percent"][-1] if self.metrics["cpu_percent"] else 0,
                    "memory_percent": self.metrics["memory_percent"][-1] if self.metrics["memory_percent"] else 0,
                    "process_count": self.metrics["process_count"]
                },
                "timestamp": time.time()
            }, f, indent=2)

system_monitor = SystemMonitor()
system_monitor.start_monitoring()
