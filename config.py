import os
import torch
import platform
import sys

# Trading Mode Configuration
MODE = os.getenv("MODE", "paper")  # Default to paper trading
PAPER_TRADING = MODE == "paper"
LIVE_TRADING = MODE == "live"

ASSETS = ["BTC", "ETH", "SOL"]

# Paper Trading Configuration
PAPER_INITIAL_BALANCE = float(os.getenv("PAPER_INITIAL_BALANCE", "10000.0"))  # $10k starting balance
PAPER_COMMISSION_RATE = float(os.getenv("PAPER_COMMISSION_RATE", "0.001"))  # 0.1% commission

# Signal and Risk Configuration
SIGNAL_CONFIDENCE_THRESHOLD = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.75"))
POSITION_SIZE_PERCENT = float(os.getenv("POSITION_SIZE_PERCENT", "0.02"))  # 2% of balance per trade
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "3"))
MAX_DRAWDOWN_PERCENT = float(os.getenv("MAX_DRAWDOWN_PERCENT", "5.0"))  # 5% max drawdown
COOLDOWN_MINUTES = int(os.getenv("COOLDOWN_MINUTES", "5"))  # Shorter cooldown for paper trading

# Live Trading Configuration (only used when MODE=live)
OKX_API_LIMITS = {
    "orders_per_second": 5,
    "requests_per_second": 3,
    "max_position_size": 20000
}

# Notifications
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def setup_gpu():
    system = platform.system()
    
    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
        torch.backends.cudnn.benchmark = True
        return {"type": "cuda", "device": "cuda", "optimized": True}
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return {"type": "apple_mps", "device": "mps", "optimized": True}
    else:
        # For paper trading, allow CPU fallback
        if PAPER_TRADING:
            print("⚠️ No GPU detected - using CPU for paper trading")
            return {"type": "cpu", "device": "cpu", "optimized": False}
        else:
            raise RuntimeError("PRODUCTION TERMINATED: No GPU acceleration available for live trading")

try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = GPU_CONFIG["optimized"]
    DEVICE = GPU_CONFIG["device"]
    print(f"Mode: {MODE.upper()} | GPU Config: {GPU_CONFIG['type']} on {DEVICE}")
except Exception as e:
    print(f"GPU setup warning: {e}")
    DEVICE = "cpu"
    GPU_AVAILABLE = False

# Validation for live trading
if LIVE_TRADING:
    required_env_vars = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        raise RuntimeError(f"Live trading requires: {missing_vars}")
    
    if not GPU_AVAILABLE:
        raise RuntimeError("Live trading requires GPU acceleration")

print(f"✅ Config loaded successfully - {MODE.upper()} MODE")
if PAPER_TRADING:
    print(f"📄 Paper trading with ${PAPER_INITIAL_BALANCE:,.0f} virtual balance")