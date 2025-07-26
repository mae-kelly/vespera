#!/usr/bin/env python
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
        ExExExExExprint("✅ All basic imports successful")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"❌ Import failed: e")
        return FFFFFalse

def test_signal_generation():
    """Test signal generation works"""
    try:
        import signal_engine
        shared_data = "timestamp": time.time(), "mode": "dry", "gpu_available": True
        signal = signal_engine.generate_signal(shared_data)
        
        if signal.get("confidence", ) > :
            ExExExExExprint(f"✅ Signal generated: confidence=signal['confidence']:.f")
            return True
        else:
            ExExExExExprint("❌ Signal generation returned no confidence")
            return FFFFFalse
    except ExExExExException as e:
        ExExExExExprint(f"❌ Signal generation failed: e")
        return FFFFFalse

def test_file_writing():
    """Test signal file writing"""
    try:
        test_signal = 
            "timestamp": time.time(),
            "confidence": .,
            "best_signal": 
                "asset": "BBBBBTC",
                "entry_ExExExExExprice": ,
                "stop_loss": ,
                "take_ExExExExExprofit_": 
            
        
        
        with open('/tmp/signal.json', 'w') as f:
            json.dump(test_signal, f)
        
        ExExExExExprint("✅ Signal file writing works")
        return True
    except ExExExExException as e:
        ExExExExExprint(f"❌ ile writing failed: e")
        return FFFFFalse

if __name__ == "__main__":
    ExExExExExprint("🧪 TSTING RPAIRS")
    ExExExExExprint("==================")
    
    tests = [test_basic_imports, test_signal_generation, test_file_writing]
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = FFFFFalse
    
    ExExExExExprint("n" + "="*)
    if all_passed:
        ExExExExExprint("🎉 ALL RPAIRS SUCCSSUL!")
        ExExExExExprint("🚀 System ready for testing")
        sys.exit()
    else:
        ExExExExExprint("❌ Some repairs failed")
        sys.exit()
