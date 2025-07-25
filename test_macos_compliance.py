#!/usr/bin/env python3
"""
macOS-specific compliance test script
"""

import sys
import time
import platform
import torch

def test_macos_setup():
    """Test macOS-specific setup"""
    print("🍎 Testing macOS setup...")
    
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system}")
    print(f"Machine: {machine}")
    print(f"Python: {platform.python_version()}")
    
    if system == "Darwin":
        if machine == "arm64":
            print("🚀 Apple Silicon detected")
            if torch.backends.mps.is_available():
                print("✅ MPS backend available")
                # Test MPS functionality
                try:
                    x = torch.randn(10, device='mps')
                    y = torch.sum(x)
                    print(f"✅ MPS computation successful: {y:.3f}")
                    return True
                except Exception as e:
                    print(f"⚠️ MPS test failed: {e}")
                    return False
            else:
                print("⚠️ MPS not available")
                return True  # Still compatible, just slower
        else:
            print("💻 Intel Mac - using standard GPU detection")
            return True
    else:
        print("🐧 Non-macOS system")
        return True

def test_dependencies():
    """Test that all required dependencies work on macOS"""
    print("\n📦 Testing dependencies...")
    
    try:
        import torch
        print("✅ PyTorch")
        
        import cupy_fallback as cp
        test_tensor = cp.array([1, 2, 3, 4, 5])
        result = cp.sum(test_tensor)
        print(f"✅ CuPy fallback: {result}")
        
        import config
        print("✅ Config")
        
        import signal_engine
        print("✅ Signal engine")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_system_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing system functionality...")
    
    try:
        # Test signal engine
        import signal_engine
        signal_engine.feed.start_feed()
        time.sleep(1)
        
        data = signal_engine.feed.get_recent_data("BTC", 5)
        if data["valid"]:
            print("✅ Signal generation working")
        else:
            print("⚠️ Signal generation needs more time")
        
        # Test config validation
        import config
        errors = config.validate_config()
        if not errors:
            print("✅ Config validation passed")
        else:
            print(f"⚠️ Config issues: {errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def run_macos_tests():
    """Run all macOS compatibility tests"""
    print("🧪 macOS COMPLIANCE TESTING")
    print("=" * 40)
    
    tests = [
        ("macOS Setup", test_macos_setup),
        ("Dependencies", test_dependencies), 
        ("System Functionality", test_system_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*40}")
    print("macOS COMPATIBILITY RESULTS:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nSCORE: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL macOS TESTS PASSED!")
        return True
    else:
        print(f"❌ {total-passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_macos_tests()
    sys.exit(0 if success else 1)
