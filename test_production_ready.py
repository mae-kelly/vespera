#!/usr/bin/env python3
"""
Production readiness integration test
"""

import time
import json
import os
import sys

def test_production_readiness():
    """Test that the system is ready for production"""
    print("🧪 PRODUCTION READINESS TEST")
    print("=" * 40)
    
    # Test 1: Configuration
    print("\n1. Testing production configuration...")
    try:
        import config
        errors = config.validate_config()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        print("✅ Configuration valid")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    # Test 2: Real market data
    print("\n2. Testing real market data feed...")
    try:
        import signal_engine
        signal_engine.feed.start_feed()
        time.sleep(5)  # Wait for real data
        
        data = signal_engine.feed.get_recent_data("BTC", 5)
        if data["valid"] and len(data["prices"]) > 0:
            current_price = data["current_price"]
            print(f"✅ Real BTC price: ${current_price:,.2f}")
        else:
            print("❌ No real market data received")
            return False
    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        return False
    
    # Test 3: Signal generation
    print("\n3. Testing real signal generation...")
    try:
        shared_data = {
            "timestamp": time.time(),
            "mode": "live",
            "iteration": 1,
            "gpu_available": config.GPU_AVAILABLE
        }
        
        signal = signal_engine.generate_signal(shared_data)
        confidence = signal.get('confidence', 0)
        print(f"✅ Signal generated: confidence {confidence:.3f}")
        
        if confidence > 0.1:
            print(f"✅ Active signal detected - system working")
        else:
            print("⚠️ Low confidence signal - system functional but waiting for opportunity")
            
    except Exception as e:
        print(f"❌ Signal generation test failed: {e}")
        return False
    
    # Test 4: File system
    print("\n4. Testing file system operations...")
    try:
        test_signal = {"test": True, "timestamp": time.time()}
        with open("/tmp/signal_test.json", "w") as f:
            json.dump(test_signal, f)
        
        with open("/tmp/signal_test.json", "r") as f:
            loaded = json.load(f)
        
        os.remove("/tmp/signal_test.json")
        print("✅ File system operations working")
    except Exception as e:
        print(f"❌ File system test failed: {e}")
        return False
    
    # Test 5: Environment variables
    print("\n5. Testing environment setup...")
    required_env = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("   Configure these in .env file before production deployment")
        return False
    
    print("✅ Environment variables configured")
    
    print("\n" + "=" * 40)
    print("🎉 PRODUCTION READINESS: PASSED")
    print("✅ System ready for live trading deployment")
    return True

if __name__ == "__main__":
    success = test_production_readiness()
    if not success:
        print("\n❌ PRODUCTION READINESS: FAILED")
        print("   Fix the issues above before deploying to production")
        sys.exit(1)
    
    print("\n🚀 Ready to deploy with: ./deploy_production.sh")
