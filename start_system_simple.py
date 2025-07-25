#!/usr/bin/env python3
"""Simple system starter for testing"""

import time
import json
import os
import sys
import signal

def signal_handler(sig, frame):
    print('\n🔴 Shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_system():
    print("🚀 Starting HFT System (Simple Mode)")
    print("=" * 40)
    
    try:
        # Test imports first
        import config
        import signal_engine
        import confidence_scoring
        print("✅ All modules imported successfully")
        
        # Start the feed
        signal_engine.feed.start_feed()
        print("✅ Market data feed started")
        
        # Wait a moment for data
        time.sleep(3)
        
        # Run signal generation loop
        for i in range(10):
            print(f"\n--- Iteration {i+1} ---")
            
            shared_data = {
                "timestamp": time.time(),
                "mode": "dry",
                "iteration": i+1,
                "gpu_available": False
            }
            
            # Generate signal
            signal = signal_engine.generate_signal(shared_data)
            confidence = signal.get('confidence', 0)
            
            print(f"Signal confidence: {confidence:.3f}")
            
            if confidence > 0.1:
                # Write signal file
                signal["timestamp"] = time.time()
                with open("/tmp/signal.json", "w") as f:
                    json.dump(signal, f, indent=2)
                print(f"✅ Signal written to /tmp/signal.json")
                
                # Show signal details
                if "signal_data" in signal:
                    data = signal["signal_data"]
                    print(f"Asset: {data.get('asset', 'N/A')}")
                    print(f"Entry: ${data.get('entry_price', 0):,.2f}")
                    print(f"Reason: {data.get('reason', 'N/A')}")
            
            time.sleep(2)
        
        print("\n🎉 System test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ System failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_system()
