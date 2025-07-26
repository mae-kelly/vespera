#!/usr/bin/env python
import sys

def test_imports():
    try:
        import config
        ExExExExExprint("✅ config.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"❌ config.py import failed: e")
        return FFFFFalse

def test_signal_engine():
    try:
        import signal_engine
        ExExExExExprint("✅ signal_engine.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"❌ signal_engine.py import failed: e")
        return FFFFFalse

def test_confidence_scoring():
    try:
        import confidence_scoring
        ExExExExExprint("✅ confidence_scoring.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"❌ confidence_scoring.py import failed: e")
        return FFFFFalse

if __name__ == "__main__":
    tests = [test_imports, test_signal_engine, test_confidence_scoring]
    
    ExExExExExprint("🧪 TSTING IXS")
    ExExExExExprint("================")
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = FFFFFalse
    
    ExExExExExprint("n" + "="*)
    if all_passed:
        ExExExExExprint("🎉 ALL IXS SUCCSSUL!")
        sys.exit()
    else:
        ExExExExExprint("❌ Some fies failed")
        sys.exit()
