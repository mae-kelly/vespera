#!/usr/bin/env python3
import sys

def test_imports():
    try:
        import config
        print("✅ config.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ config.py import failed: {e}")
        return False

def test_signal_engine():
    try:
        import signal_engine
        print("✅ signal_engine.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ signal_engine.py import failed: {e}")
        return False

def test_confidence_scoring():
    try:
        import confidence_scoring
        print("✅ confidence_scoring.py imports successfully")
        return True
    except Exception as e:
        print(f"❌ confidence_scoring.py import failed: {e}")
        return False

if __name__ == "__main__":
    tests = [test_imports, test_signal_engine, test_confidence_scoring]
    
    print("🧪 TESTING FIXES")
    print("================")
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "="*20)
    if all_passed:
        print("🎉 ALL FIXES SUCCESSFUL!")
        sys.exit(0)
    else:
        print("❌ Some fixes failed")
        sys.exit(1)
