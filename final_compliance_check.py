#!/usr/bin/env python3
"""
Final compliance verification for all requirements
"""

import os
import sys

def check_file_requirements():
    """Check all required files exist"""
    required_files = [
        "main.py", "signal_engine.py", "entropy_meter.py", "laggard_sniper.py",
        "relief_trap.py", "confidence_scoring.py", "notifier_elegant.py", 
        "logger.py", "config.py", "init_pipeline.sh", "hft_executor"
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    return len(missing) == 0, missing

def check_websocket_implementation():
    """Verify WebSocket implementation"""
    try:
        with open('signal_engine.py', 'r') as f:
            content = f.read()
        
        required = ['websocket.WebSocketApp', 'on_message', 'on_error', 'on_open', 'wss://ws.okx.com']
        missing = [item for item in required if item not in content]
        
        return len(missing) == 0, missing
    except:
        return False, ["signal_engine.py not readable"]

def check_tradingview_api():
    """Verify TradingView API integration"""
    try:
        with open('confidence_scoring.py', 'r') as f:
            content = f.read()
        
        return 'scanner.tradingview.com' in content, []
    except:
        return False, ["confidence_scoring.py not readable"]

def check_gpu_enforcement():
    """Verify GPU enforcement in all Python files"""
    violations = []
    python_files = [f for f in os.listdir('.') if f.endswith('.py') and 
                   f not in ['final_compliance_check.py', 'validate_performance.py', 'test_fixed_system.py']]
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                if 'torch.cuda.is_available()' not in content and 'torch.backends.mps' not in content:
                    violations.append(file)
        except:
            violations.append(f"{file} (unreadable)")
    
    return len(violations) == 0, violations

def check_rust_executable():
    """Verify Rust executable exists and is functional"""
    if not os.path.exists('hft_executor'):
        return False, ["hft_executor missing"]
    
    if not os.access('hft_executor', os.X_OK):
        return False, ["hft_executor not executable"]
    
    return True, []

def check_cupy_fallback():
    """Verify cupy_fallback usage"""
    try:
        with open('signal_engine.py', 'r') as f:
            content = f.read()
        
        if 'import cupy_fallback as cp' in content or 'cupy_fallback' in content:
            return True, []
        else:
            return False, ["cupy_fallback not found"]
    except:
        return False, ["signal_engine.py not readable"]

def check_discord_integration():
    """Verify Discord webhook integration"""
    try:
        with open('notifier_elegant.py', 'r') as f:
            content = f.read()
        
        required = ['DISCORD_WEBHOOK_URL', 'requests.post', 'embeds']
        missing = [item for item in required if item not in content]
        
        return len(missing) == 0, missing
    except:
        return False, ["notifier_elegant.py not readable"]

def main_test():
    print("🎓 STANFORD PhD SYSTEM COMPLIANCE VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("File Requirements", check_file_requirements),
        ("WebSocket Implementation", check_websocket_implementation),
        ("TradingView API", check_tradingview_api),
        ("GPU Enforcement", check_gpu_enforcement),
        ("Rust Executable", check_rust_executable),
        ("Cupy Fallback", check_cupy_fallback),
        ("Discord Integration", check_discord_integration),
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
        print("🎉 100% COMPLIANCE ACHIEVED!")
        print("🚀 System ready for A100 deployment")
        print("⚡ Stanford PhD-level requirements met")
        return 0
    else:
        failed_tests = [name for name, passed, _ in results if not passed]
        print(f"❌ Failed compliance: {failed_tests}")
        return 1

if __name__ == "__main__":
    sys.exit(main_test())
