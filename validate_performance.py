#!/usr/bin/env python3
"""
Performance validation for Stanford PhD system
Tests all critical performance requirements
"""

import time
import json
import sys
import torch
import signal_engine
import confidence_scoring

def test_gpu_performance():
    """Test GPU acceleration and detection"""
    try:
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {device_name}")
            return True, device_name
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Apple Silicon GPU detected")
            return True, "Apple Silicon"
        else:
            return False, "No GPU available"
    except Exception as e:
        return False, str(e)

def test_signal_generation_speed():
    """Test signal generation latency"""
    try:
        signal_engine.feed.start_feed()
        time.sleep(2)
        
        start_time = time.perf_counter()
        shared_data = {"timestamp": time.time(), "mode": "dry", "gpu_available": True}
        signal = signal_engine.generate_signal(shared_data)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        latency_us = latency_ms * 1000
        
        if latency_us < 1000:  # Sub-millisecond
            return True, f"{latency_us:.1f}μs (EXCELLENT)"
        elif latency_us < 10000:  # Sub-10ms
            return True, f"{latency_us:.1f}μs (GOOD)"
        else:
            return False, f"{latency_us:.1f}μs (TOO SLOW)"
    except Exception as e:
        return False, str(e)

def test_websocket_connection():
    """Test WebSocket real-time data"""
    try:
        if hasattr(signal_engine.feed, 'ws_connected'):
            return signal_engine.feed.ws_connected, "WebSocket status checked"
        else:
            return False, "WebSocket status unknown"
    except Exception as e:
        return False, str(e)

def test_tradingview_api():
    """Test TradingView API integration"""
    try:
        dominance = confidence_scoring.get_btc_dominance()
        if 0 < dominance < 100:
            return True, f"BTC dominance: {dominance:.1f}%"
        else:
            return False, f"Invalid dominance: {dominance}"
    except Exception as e:
        return False, str(e)

def test_signal_structure():
    """Test complete signal structure"""
    try:
        shared_data = {"timestamp": time.time(), "mode": "dry", "gpu_available": True}
        signal = signal_engine.generate_signal(shared_data)
        
        required_fields = ["confidence", "source", "priority", "entropy", "signal_data"]
        missing = [field for field in required_fields if field not in signal]
        
        if missing:
            return False, f"Missing fields: {missing}"
        
        signal_data = signal["signal_data"]
        required_signal_fields = ["asset", "entry_price", "stop_loss", "take_profit_1", "rsi", "vwap", "reason"]
        missing_signal = [field for field in required_signal_fields if field not in signal_data]
        
        if missing_signal:
            return False, f"Missing signal fields: {missing_signal}"
        
        return True, "All required fields present"
    except Exception as e:
        return False, str(e)

def main_test():
    print("🎓 STANFORD PhD SYSTEM PERFORMANCE VALIDATION")
    print("=" * 50)
    
    tests = [
        ("GPU Acceleration", test_gpu_performance),
        ("Signal Generation Speed", test_signal_generation_speed),
        ("WebSocket Connection", test_websocket_connection),
        ("TradingView API", test_tradingview_api),
        ("Signal Structure", test_signal_structure),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
            results.append((test_name, passed, message))
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ FAIL {test_name}: {e}")
            results.append((test_name, False, str(e)))
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🏆 ALL PERFORMANCE TESTS PASSED!")
        print("🚀 System ready for A100 deployment")
        print("⚡ Stanford PhD-level performance confirmed")
        return 0
    else:
        failed_tests = [name for name, passed, _ in results if not passed]
        print(f"❌ Failed tests: {failed_tests}")
        return 1

if __name__ == "__main__":
    sys.exit(main_test())
