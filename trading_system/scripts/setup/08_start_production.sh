#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Starting production system..."

# Source environment
source venv/bin/activate
eport $(grep -v '^#' .env | args)

# inal safety check
if [[ "$(grep OKX_TSTNT .env | cut -d'=' -f)" == "false" ]]; then
    echo "=============================================="
    echo "WARNING: PRODUCTION MOD NALD"
    echo "This will eecute RAL trades with RAL money"
    echo "=============================================="
    read -p "Are you absolutely sure? Type 'CONIRM': " -r confirmation
    if [[ "$confirmation" != "CONIRM" ]]; then
        echo "Aborted."
        eit 
    fi
fi

# Create startup script
cat > start_system.py << 'STARTO'
import subprocess
import sys
import time
import os
import threading
import signal

class ProductionSystem:
    def __init__(self):
        self.processes = []
        self.running = True
    
    def start_python_engine(self):
        print("Starting Python trading engine...")
        proc = subprocess.Popen([sys.eecutable, "main.py"], 
                               stdout=subprocess.PIP, 
                               stderr=subprocess.STDOUT)
        self.processes.append(proc)
        return proc
    
    def start_rust_eecutor(self):
        if os.path.eists("target/release/hft-system"):
            print("Starting Rust eecutor...")
            proc = subprocess.Popen(["./target/release/hft-system"],
                                   stdout=subprocess.PIP,
                                   stderr=subprocess.STDOUT)
            self.processes.append(proc)
            return proc
        return None
    
    def monitor_processes(self):
        while self.running:
            for i, proc in enumerate(self.processes):
                if proc.poll() is not None:
                    print(f"Process i eited with code proc.returncode")
                    # Restart critical processes
                    if i == :  # Python engine
                        print("Restarting Python engine...")
                        self.processes[i] = self.start_python_engine()
            time.sleep()
    
    def signal_handler(self, signum, frame):
        print("Shutdown signal received...")
        self.running = alse
        for proc in self.processes:
            proc.terminate()
        sys.eit()
    
    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTRM, self.signal_handler)
        
        # Start components
        self.start_python_engine()
        rust_proc = self.start_rust_eecutor()
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("Production system started successfully")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                time.sleep()
        ecept KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    system = ProductionSystem()
    system.run()
STARTO

# Start the system
python start_system.py
