#!/usr/bin/env python3
import json
import time
import subprocess
import os
from datetime import datetime

def check_python_process():
    try:
        result = subprocess.run(['pgrep', '-f', 'python.*main.py'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_signal_freshness():
    try:
        stat = os.stat('/tmp/signal.json')
        age = time.time() - stat.st_mtime
        return age < 120  # Fresh if less than 2 minutes old
    except:
        return False

def load_latest_signal():
    try:
        with open('/tmp/signal.json', 'r') as f:
            return json.load(f)
    except:
        return None

def main():
    print("🔍 HFT SYSTEM STATUS CHECK")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check Python process
    python_running = check_python_process()
    print(f"Python Process: {'✅ Running' if python_running else '❌ Stopped'}")
    
    # Check signal generation
    signals_fresh = check_signal_freshness()
    print(f"Signal Generation: {'✅ Active' if signals_fresh else '❌ Stale'}")
    
    # Check latest signal
    signal = load_latest_signal()
    if signal:
        confidence = signal.get('confidence', 0)
        age = time.time() - signal.get('timestamp', 0)
        print(f"Latest Signal: {confidence:.3f} confidence ({age:.1f}s ago)")
        
        if 'signal_data' in signal:
            sig_data = signal['signal_data']
            print(f"  Asset: {sig_data.get('asset', 'N/A')}")
            print(f"  RSI: {sig_data.get('rsi', 'N/A'):.1f}")
        
        if confidence >= 0.75:
            print("🎯 STRONG SIGNAL ACTIVE!")
    else:
        print("Latest Signal: ❌ No signal file found")
    
    # Overall status
    print()
    if python_running and signals_fresh:
        print("🟢 SYSTEM STATUS: HEALTHY")
    elif python_running:
        print("🟡 SYSTEM STATUS: RUNNING (signals may be stale)")
    else:
        print("🔴 SYSTEM STATUS: STOPPED")
    
    print()
    print("Commands:")
    print("  python3 main.py              # Start/restart system")
    print("  python3 monitor_dashboard.py # Real-time monitoring")
    print("  python3 check_system.py      # This status check")

if __name__ == "__main__":
    main()
