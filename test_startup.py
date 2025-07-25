#!/usr/bin/env python3
import time
import sys

def test_system():
    try:
        print("🧪 Testing system startup...")
        
        # Import all modules
        import config
        import signal_engine
        import entropy_meter
        import laggard_sniper
        import relief_trap
        import confidence_scoring
        print("✅ All modules imported")
        
        # Start signal feed
        signal_engine.feed.start_feed()
        print("✅ Signal feed started")
        
        # Wait for initialization
        time.sleep(3)
        
        # Test signal generation
        shared_data = {
            "timestamp": time.time(),
            "mode": "dry",
            "iteration": 1,
            "gpu_available": False
        }
        
        signal = signal_engine.generate_signal(shared_data)
        confidence = signal.get('confidence', 0)
        print(f"✅ Signal generated: confidence={confidence:.3f}")
        
        if confidence > 0:
            print("🎉 SYSTEM WORKING PERFECTLY!")
        else:
            print("⚠️ System working but no high-confidence signals yet")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_system():
        print("\n🎉 SUCCESS! System is ready to run")
        print("✅ You can now run: python3 main.py --mode=dry")
        print("✅ Or run: ./init_pipeline.sh dry")
    else:
        print("\n❌ System still has issues")
        sys.exit(1)
