#!/usr/bin/env python3
"""
Quick Start Script for HFT Trading System
This script will get you running in under 5 minutes
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def create_env_file():
    """Create .env file with default values"""
    env_content = """# Trading Mode
MODE=paper

# OKX API Configuration (Required for market data)
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here
OKX_PASSPHRASE=your_okx_passphrase_here
OKX_TESTNET=false

# Paper Trading Settings
PAPER_INITIAL_BALANCE=10000.0
PAPER_COMMISSION_RATE=0.001

# Trading Parameters
SIGNAL_CONFIDENCE_THRESHOLD=0.75
POSITION_SIZE_PERCENT=0.02
MAX_OPEN_POSITIONS=3
MAX_DRAWDOWN_PERCENT=5.0
COOLDOWN_MINUTES=5

# Notifications (Optional)
DISCORD_WEBHOOK_URL=
DISCORD_USER_ID=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# System Configuration
LOG_LEVEL=INFO
PYTHONPATH=.
"""
    
    if not Path(".env").exists():
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("⚠️  Please update your OKX API credentials in .env file")
        return False
    else:
        print("✅ .env file already exists")
        return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "torch", "torchvision", "torchaudio",
        "websocket-client", "requests", "pandas", "numpy",
        "python-dotenv", "pyyaml"
    ]
    
    for package in packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} already installed")
        except ImportError:
            print(f"⬇️ Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def create_directories():
    """Create required directories"""
    dirs = ["logs", "tmp", "data"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created {dir_name}/ directory")

def test_imports():
    """Test critical imports"""
    print("🧪 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA GPU: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Apple MPS detected")
        else:
            print("⚠️ No GPU detected - CPU mode only")
        
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import websocket
        import requests
        import pandas
        import numpy
        print("✅ All required packages available")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def create_test_files():
    """Create test signal and fills files"""
    
    # Create empty fills file
    with open("/tmp/fills.json", "w") as f:
        json.dump([], f)
    print("✅ Created /tmp/fills.json")
    
    # Create test signal file
    test_signal = {
        "confidence": 0.0,
        "source": "test",
        "timestamp": time.time(),
        "production_validated": False
    }
    
    with open("/tmp/signal.json", "w") as f:
        json.dump(test_signal, f, indent=2)
    print("✅ Created /tmp/signal.json")

def check_api_credentials():
    """Check if API credentials are configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OKX_API_KEY", "")
    
    if not api_key or api_key == "your_okx_api_key_here":
        print("⚠️ OKX API credentials not configured")
        print("   Please update .env file with your OKX API credentials")
        print("   Even paper trading needs API access for live market data")
        return False
    else:
        print("✅ OKX API credentials configured")
        return True

def run_quick_test():
    """Run a quick test of the system"""
    print("🏃 Running quick system test...")
    
    try:
        # Test config import
        import config
        print(f"✅ Config loaded - Mode: {config.MODE}")
        
        # Test OKX market data
        from okx_market_data import get_okx_engine
        engine = get_okx_engine()
        print("✅ OKX market data engine initialized")
        
        # Test signal engine
        import signal_engine
        print("✅ Signal engine available")
        
        # Test paper trading engine
        if config.PAPER_TRADING:
            from paper_trading_engine import get_paper_engine
            paper_engine = get_paper_engine()
            print("✅ Paper trading engine initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    print("🚀 HFT Trading System - Quick Start")
    print("=" * 50)
    
    # Step 1: Create environment file
    env_exists = create_env_file()
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Test imports
    if not test_imports():
        print("❌ Dependency issues found. Please fix and try again.")
        return False
    
    # Step 5: Create test files
    create_test_files()
    
    # Step 6: Check API credentials
    credentials_ok = check_api_credentials()
    
    # Step 7: Run system test
    if not credentials_ok:
        print("⚠️ Skipping system test due to missing API credentials")
        print("\n📋 Next Steps:")
        print("1. Update .env file with your OKX API credentials")
        print("2. Run: python3 quick_start.py")
        print("3. Then run: python3 main.py --mode paper")
        return False
    
    if run_quick_test():
        print("\n🎉 System is ready!")
        print("\n📋 Start Trading:")
        print("• Paper Trading: python3 main.py --mode paper")
        print("• Live Trading:  python3 main.py --mode live")
        print("\n📊 Monitor progress in the terminal output")
        
        # Ask if user wants to start paper trading now
        response = input("\n🤖 Start paper trading now? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("\n🚀 Starting paper trading...")
            os.system("python3 main.py --mode paper")
        
        return True
    else:
        print("\n❌ System test failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)