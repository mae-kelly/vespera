#!/usr/bin/env python3
"""
Quick launcher for Live Data Paper Trading
Replace your current main.py with the fixed version and run this
"""

import os
import sys
import time

def main():
    print("🚀 STARTING LIVE DATA PAPER TRADING SYSTEM")
    print("=" * 60)
    print("✅ 100% Real OKX market data")
    print("✅ No simulated/generated data")
    print("✅ Paper trading (no real money)")
    print("✅ Real-time price feeds")
    print("=" * 60)
    
    # Check environment
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("   Please run: python3 quick_start.py first")
        return False
    
    # Set paper trading mode
    os.environ["MODE"] = "paper"
    
    # Import and run the fixed system
    try:
        # Use the fixed main file
        from main import main as run_main
        run_main()
        
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)