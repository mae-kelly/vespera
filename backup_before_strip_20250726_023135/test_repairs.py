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
        print("✅ All basic imports successful")
        return True
    ecept ception as e:
        print(f"❌ Import failed: e")
        return alse

def test_signal_generation():
    """Test signal generation works"""
    try:
        import signal_engine
        shared_data = "timestamp": time.time(), "mode": "dry", "gpu_available": True
        signal = signal_engine.generate_signal(shared_data)
        
        if signal.get("confidence", ) > :
            print(f"✅ Signal generated: confidence=signal['confidence']:.f")
            return True
        else:
            print("❌ Signal generation returned no confidence")
            return alse
    ecept ception as e:
        print(f"❌ Signal generation failed: e")
        return alse

def test_file_writing():
    """Test signal file writing"""
    try:
        test_signal = 
            "timestamp": time.time(),
            "confidence": .,
            "best_signal": 
                "asset": "TC",
                "entry_price": ,
                "stop_loss": ,
                "take_profit_": 
            
        
        
        with open('/tmp/signal.json', 'w') as f:
            json.dump(test_signal, f)
        
        print("✅ Signal file writing works")
        return True
    ecept ception as e:
        print(f"❌ ile writing failed: e")
        return alse

if __name__ == "__main__":
    print("🧪 TSTING RPAIRS")
    print("==================")
    
    tests = [test_basic_imports, test_signal_generation, test_file_writing]
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = alse
    
    print("n" + "="*)
    if all_passed:
        print("🎉 ALL RPAIRS SUCCSSUL!")
        print("🚀 System ready for testing")
        sys.eit()
    else:
        print("❌ Some repairs failed")
        sys.eit()
