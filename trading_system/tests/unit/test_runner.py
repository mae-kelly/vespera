#!/usr/bin/env python3
"""
Simple Test Runner - Run the fixed test files that actually work
"""
import os
import sys
import subprocess

def setup_env():
    """Setup environment for paper trading"""
    os.environ["MODE"] = "paper"
    os.environ["OKX_API_KEY"] = "test_key"
    os.environ["OKX_SECRET_KEY"] = "test_secret"
    os.environ["OKX_PASSPHRASE"] = "test_passphrase"
    os.environ["DISCORD_WEBHOOK_URL"] = "https://discord.com/api/webhooks/test"
    print("🔧 Environment set for paper trading tests")

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING: {test_file}")
    print(f"{'='*60}")
    
    if not os.path.exists(test_file):
        print(f"❌ {test_file} not found!")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            timeout=60,
            env=os.environ.copy()
        )
        
        success = result.returncode == 0
        print(f"\n📊 {test_file}: {'✅ PASSED' if success else '❌ FAILED'}")
        return success
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run the working fixed tests"""
    print("🔥 SIMPLE TEST RUNNER")
    print("="*60)
    print("📄 Using Python 3.13 Compatible Tests")
    print("="*60)
    
    setup_env()
    
    # Use the fixed test files that actually work
    tests = [
        "test_signal_engine_fixed.py",
        "test_confidence_scoring_fixed.py", 
        "test_paper_trading_fixed.py"
    ]
    
    results = {}
    for test in tests:
        results[test] = run_test(test)
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n{'='*60}")
    print("🔥 RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"📊 {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    for test, success in results.items():
        component = test.replace("_fixed.py", "").replace("test_", "").replace("_", " ").title()
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {component:<20} {status}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Core system functional")
        print("📄 Paper trading ready")
    else:
        print(f"\n❌ {total-passed} TESTS FAILED")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)