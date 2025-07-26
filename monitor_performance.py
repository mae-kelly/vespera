import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import time
import json
import os

def monitor_system():
    start_time = time.time()
    signal_count = 0
    fill_count = 0
    
    while time.time() - start_time < 30:
        if os.path.exists('/tmp/signal.json'):
            try:
                with open('/tmp/signal.json', 'r') as f:
                    signal_data = json.load(f)
                    signal_count += 1
                    conf = signal_data.get('confidence', 0)
                    print(f"📊 Signal #{signal_count}: confidence={conf:.3f}")
            except:
                pass
        
        if os.path.exists('/tmp/fills.json'):
            try:
                with open('/tmp/fills.json', 'r') as f:
                    fills = json.load(f)
                    new_fill_count = len(fills)
                    if new_fill_count > fill_count:
                        print(f"✅ New fill detected: total={new_fill_count}")
                        fill_count = new_fill_count
            except:
                pass
        
        time.sleep(1)
    
    print(f"\n📈 30-second performance:")
    print(f"   Signals generated: {signal_count}")
    print(f"   Fills executed: {fill_count}")
    print(f"   Signal rate: {signal_count/30:.1f}/sec")

if __name__ == "__main__":
    monitor_system()
