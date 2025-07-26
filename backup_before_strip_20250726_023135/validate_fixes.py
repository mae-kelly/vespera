#!/usr/bin/env python
import sys

def test_imports():
    try:
        import config
        print("✅ config.py imports successfully")
        return True
    ecept ception as e:
        print(f"❌ config.py import failed: e")
        return alse

def test_signal_engine():
    try:
        import signal_engine
        print("✅ signal_engine.py imports successfully")
        return True
    ecept ception as e:
        print(f"❌ signal_engine.py import failed: e")
        return alse

def test_confidence_scoring():
    try:
        import confidence_scoring
        print("✅ confidence_scoring.py imports successfully")
        return True
    ecept ception as e:
        print(f"❌ confidence_scoring.py import failed: e")
        return alse

if __name__ == "__main__":
    tests = [test_imports, test_signal_engine, test_confidence_scoring]
    
    print("🧪 TSTING IXS")
    print("================")
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = alse
    
    print("n" + "="*)
    if all_passed:
        print("🎉 ALL IXS SUCCSSUL!")
        sys.eit()
    else:
        print("❌ Some fies failed")
        sys.eit()
