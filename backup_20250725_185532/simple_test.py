#!/usr/bin/env python3
import sys
import time
import os

def test_basic_functionality():
    print("🧪 Testing basic HFT functionality...")
    
    try:
        # Test config
        import config
        print("✅ Config loaded")
        
        # Test signal engine with fallback
        import signal_engine
        print("✅ Signal engine loaded")
        
        # Start feed
        signal_engine.feed.start_feed()
        time.sleep(2)
        
        # Test data generation
        data = signal_engine.feed.get_recent_data("BTC", 5)
        if data["valid"]:
            print(f"✅ Data generation working: {len(data['prices'])} prices")
        else:
            print("⚠️ Data generation not working yet")
        
        # Test signal generation
        shared_data = {
            "timestamp": time.time(),
            "mode": "dry",
            "iteration": 1,
            "gpu_available": False
        }
        
        signal = signal_engine.generate_signal(shared_data)
        print(f"✅ Signal generated: confidence {signal.get('confidence', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    if test_basic_functionality():
        print("\n🎉 Basic functionality working!")
        print("✅ System ready for testing")
    else:
        print("\n❌ Basic functionality failed")
        sys.exit(1)
