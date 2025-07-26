#!/usr/bin/env python3
"""Quick system test"""

print("🚀 Quick System Test")
print("===================")

try:
    print("1. Testing imports...")
    import config
    import signal_engine
    import cupy_fallback as cp
    print("✅ All imports successful")
    
    print("\n2. Testing signal generation...")
    signal_engine.feed.start_feed()
    import time
    time.sleep(2)
    
    shared_data = {"timestamp": time.time(), "mode": "dry", "iteration": 1}
    signal = signal_engine.generate_signal(shared_data)
    
    if signal.get("confidence", 0) > 0:
        print(f"✅ Signal generated: {signal['confidence']:.3f}")
    else:
        print("⚠️ No signal yet - system starting up")
    
    print("\n3. Testing config...")
    errors = config.validate_config()
    if not errors:
        print("✅ Config valid")
    else:
        print(f"⚠️ Config issues: {errors}")
    
    print("\n🎉 Quick test completed successfully!")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
