#!/usr/bin/env python3
import os
import sys

def test_imports():
    """Test that all imports work"""
    print("🧪 Testing imports...")
    
    try:
        import cupy_fallback as cp
        test_array = cp.array([1, 2, 3, 4, 5])
        result = cp.sum(test_array)
        print(f"✅ CuPy fallback: {result}")
    except Exception as e:
        print(f"❌ CuPy fallback failed: {e}")
        return False
    
    try:
        import config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False
    
    try:
        import signal_engine
        print("✅ Signal engine imported")
    except Exception as e:
        print(f"❌ Signal engine failed: {e}")
        return False
    
    return True

def test_credentials():
    """Test OKX credentials"""
    print("\n🔐 Testing credentials...")
    
    required = ['OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE']
    
    for var in required:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:8]}...")
        else:
            print(f"❌ {var}: Missing")
            return False
    
    return True

def test_market_data():
    """Test market data connection"""
    print("\n📊 Testing market data...")
    
    try:
        import requests
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_price = data.get('bitcoin', {}).get('usd')
            if btc_price:
                print(f"✅ BTC Price: ${btc_price:,.2f}")
                return True
        
        print("❌ Could not get BTC price")
        return False
        
    except Exception as e:
        print(f"❌ Market data failed: {e}")
        return False

def main():
    print("🧪 SIMPLE CONNECTION TEST")
    print("=" * 30)
    
    tests = [
        ("Imports", test_imports),
        ("Credentials", test_credentials),
        ("Market Data", test_market_data)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ System ready for testing")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
