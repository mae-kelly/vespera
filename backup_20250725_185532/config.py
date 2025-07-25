import os
import torch

# Core configuration
LIVE_MODE = True  # Can be overridden by command line
MODE = "dry"  # Will be set by main.py
ASSETS = ["BTC", "ETH", "SOL"]

# Trading parameters
SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3
MAX_DRAWDOWN_PERCENT = 10.0
COOLDOWN_MINUTES = 5

# OKX API configuration
OKX_API_LIMITS = {
    "orders_per_second": 20,
    "requests_per_second": 10,
    "max_position_size": 50000  # USD
}

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# GPU fallback configuration
def setup_gpu_fallback():
    """Setup GPU with fallback to CPU if A100 not available"""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        if "A100" not in device_name:
            print(f"⚠️ WARNING: Non-A100 GPU detected: {device_name}")
            print("⚠️ Performance may be suboptimal. Consider using A100 for best results.")
            return False
        return True
    else:
        print("⚠️ WARNING: No CUDA GPU available, using CPU fallback")
        return False

# Validation function
def validate_config():
    """Validate all configuration parameters"""
    errors = []
    
    if MODE not in ["dry", "live"]:
        errors.append("MODE must be 'dry' or 'live'")
    
    if SIGNAL_CONFIDENCE_THRESHOLD <= 0 or SIGNAL_CONFIDENCE_THRESHOLD > 1:
        errors.append("SIGNAL_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if POSITION_SIZE_PERCENT <= 0 or POSITION_SIZE_PERCENT > 100:
        errors.append("POSITION_SIZE_PERCENT must be between 0 and 100")
    
    if MAX_OPEN_POSITIONS <= 0:
        errors.append("MAX_OPEN_POSITIONS must be positive")
    
    if not ASSETS or len(ASSETS) == 0:
        errors.append("ASSETS list cannot be empty")
    
    return errors

# Initialize GPU detection
GPU_AVAILABLE = setup_gpu_fallback()

print(f"✅ Config loaded - Mode: {MODE}, GPU: {GPU_AVAILABLE}, Assets: {ASSETS}")
