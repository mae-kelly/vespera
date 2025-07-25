#!/usr/bin/env python3

print("🧪 Minimal HFT System Test")
print("==========================")

# Test 1: Basic imports
try:
    import config
    print("✅ Config imported")
except Exception as e:
    print(f"❌ Config failed: {e}")
    exit(1)

# Test 2: NumPy fallback
try:
    import cupy_numpy_fallback as cp
    test_array = cp.array([1, 2, 3, 4, 5])
    print(f"✅ NumPy fallback works: {test_array}")
except Exception as e:
    print(f"❌ NumPy fallback failed: {e}")

# Test 3: Signal engine
try:
    import signal_engine
    print("✅ Signal engine imported")
    
    # Try to start feed
    signal_engine.feed.start_feed()
    print("✅ Signal feed started")
    
    import time
    time.sleep(1)
    
    # Test data generation
    data = signal_engine.feed.get_recent_data("BTC", 3)
    if data["valid"]:
        print(f"✅ Data generation works: {len(data['prices'])} prices")
    else:
        print("⚠️ Data generation not working yet")
        
except Exception as e:
    print(f"❌ Signal engine failed: {e}")

print("\n🎉 Minimal test completed!")
print("If signal engine works, the system is ready!")
