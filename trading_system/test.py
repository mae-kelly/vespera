#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "config"))

def test():
    print("🧪 Testing unified system...")
    
    try:
        from unified_config import MODE, DEVICE
        print(f"✅ Config: {MODE} mode, {DEVICE} device")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    try:
        from unified_trading_system import UnifiedTradingSystem
        system = UnifiedTradingSystem()
        print("✅ System created successfully")
        return True
    except Exception as e:
        print(f"❌ System error: {e}")
        return False

if __name__ == "__main__":
    success = test()
    if success:
        print("🎉 Tests passed! Ready to run.")
    else:
        print("❌ Tests failed. Check setup.")
