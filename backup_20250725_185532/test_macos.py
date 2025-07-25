#!/usr/bin/env python3
import subprocess
import time
import signal
import os
import sys

def test_system():
    print("🚀 Testing HFT system on macOS...")
    
    # Start the system
    try:
        proc = subprocess.Popen(['./init_pipeline.sh', 'dry'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
        
        # Wait 5 seconds
        time.sleep(5)
        
        # Check for signal file
        if os.path.exists('/tmp/signal.json'):
            print("✅ System working - signal file created")
            with open('/tmp/signal.json', 'r') as f:
                content = f.read()
                print("Signal preview:", content[:200] + "..." if len(content) > 200 else content)
        else:
            print("⚠️ No signal file yet")
        
        # Clean shutdown
        proc.terminate()
        proc.wait(timeout=5)
        print("✅ System test completed")
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
    
    # Cleanup any remaining processes
    try:
        subprocess.run(['pkill', '-f', 'python3 main.py'], check=False)
        subprocess.run(['pkill', '-f', 'hft_executor'], check=False)
    except:
        pass

if __name__ == "__main__":
    test_system()
