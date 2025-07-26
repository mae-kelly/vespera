#!/usr/bin/env python3
"""
Basic system test
"""
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "core"))
sys.path.append(str(Path(__file__).parent / "config"))

def test_imports():
    """Test basic imports"""
    print("🧪 Testing imports...")
    
    try:
        from config.unified_config import MODE, DEVICE
        print(f"✅ Config: {MODE} mode, {DEVICE} device")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        if Path("core/engines/signal_engine.py").exists():
            from engines import signal_engine
            print("✅ Signal engine imported")
        else:
            print("⚠️  Signal engine not found (run reorganization first)")
    except Exception as e:
        print(f"❌ Signal engine import failed: {e}")
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Testing basic functionality...")
    
    try:
        from unified_trading_system import UnifiedTradingSystem
        system = UnifiedTradingSystem(mode="paper")
        print("✅ Unified system created")
        return True
    except Exception as e:
        print(f"❌ System creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔥 BASIC SYSTEM TEST")
    print("===================")
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    
    print("")
    if success:
        print("🎉 Basic tests passed!")
        print("🚀 Ready to start: bash start.sh")
    else:
        print("❌ Some tests failed")
        print("🔧 Check setup and configuration")
