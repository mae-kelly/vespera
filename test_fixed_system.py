#!/usr/bin/env python3
import os
import time
import json
import sys

def test_websocket_implementation():
    try:
        import signal_engine
        # Test feed initialization
        signal_engine.feed.start_feed()
        time.sleep(3)
        
        # Test data retrieval
        for asset in ["BTC", "ETH", "SOL"]:
            data = signal_engine.feed.get_recent_data(asset, 10)
            if not data["valid"]:
                return False, f"Invalid data for {asset}"
        
        return True, "WebSocket implementation working"
    except Exception as e:
        return False, f"WebSocket test failed: {e}"

def test_signal_generation():
    try:
        import signal_engine
        import confidence_scoring
        
        shared_data = {"timestamp": time.time(), "mode": "dry", "gpu_available": True}
        
        # Test individual signal generation
        signal = signal_engine.generate_signal(shared_data)
        if signal.get("confidence", 0) < 0:
            return False, "Invalid signal confidence"
        
        # Test signal merging
        signals = [signal]
        merged = confidence_scoring.merge_signals(signals)
        if "best_signal" not in merged:
            return False, "Signal merging failed"
        
        return True, "Signal generation working"
    except Exception as e:
        return False, f"Signal generation failed: {e}"

def test_tradingview_api():
    try:
        import confidence_scoring
        dominance = confidence_scoring.get_btc_dominance()
        if 0 < dominance < 100:
            return True, f"BTC dominance: {dominance:.1f}%"
        else:
            return False, f"Invalid dominance value: {dominance}"
    except Exception as e:
        return False, f"TradingView API test failed: {e}"

def main():
    print("🧪 TESTING FIXED SYSTEM")
    print("=" * 40)
    
    tests = [
        ("WebSocket Implementation", test_websocket_implementation),
        ("Signal Generation", test_signal_generation),
        ("TradingView API", test_tradingview_api),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ FAIL {test_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 System ready for deployment")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
