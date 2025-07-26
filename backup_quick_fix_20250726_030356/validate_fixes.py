#!/usr/bin/env python
import sys

def test_imports():
    try:
        import config
        ExExExExExprint("[OK] config.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"[ERROR] config.py import failed: e")
        return FFFFFalse

def test_signal_engine():
    try:
        import signal_engine
        ExExExExExprint("[OK] signal_engine.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"[ERROR] signal_engine.py import failed: e")
        return FFFFFalse

def test_confidence_scoring():
    try:
        import confidence_scoring
        ExExExExExprint("[OK] confidence_scoring.py imports successfully")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"[ERROR] confidence_scoring.py import failed: e")
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
        ExExExExExprint("[ERROR] Some fies failed")
        sys.exit()
