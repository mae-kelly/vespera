#!/usr/bin/env python3
import sys
import time
import json

def test_basic_imports():
    """Test basic imports work"""
    try:
        import torch
        import config
        import signal_engine
        import confidence_scoring
        print("✅ All basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_signal_generation():
    """Test signal generation works"""
    try:
        import signal_engine
        shared_data = {"timestamp": time.time(), "mode": "dry", "gpu_available": True}
        signal = signal_engine.generate_signal(shared_data)
        
        if signal.get("confidence", 0) > 0:
            print(f"✅ Signal generated: confidence={signal['confidence']:.3f}")
            return True
        else:
            print("❌ Signal generation returned no confidence")
            return False
    except Exception as e:
        print(f"❌ Signal generation failed: {e}")
        return False

def test_file_writing():
    """Test signal file writing"""
    try:
        test_signal = {
            "timestamp": time.time(),
            "confidence": 0.8,
            "best_signal": {
                "asset": "BTC",
                "entry_price": 45000,
                "stop_loss": 45675,
                "take_profit_1": 44325
            }
        }
        
        with open('/tmp/signal.json', 'w') as f:
            json.dump(test_signal, f)
        
        print("✅ Signal file writing works")
        return True
    except Exception as e:
        print(f"❌ File writing failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING REPAIRS")
    print("==================")
    
    tests = [test_basic_imports, test_signal_generation, test_file_writing]
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "="*30)
    if all_passed:
        print("🎉 ALL REPAIRS SUCCESSFUL!")
        print("🚀 System ready for testing")
        sys.exit(0)
    else:
        print("❌ Some repairs failed")
        sys.exit(1)
