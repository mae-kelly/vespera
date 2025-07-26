import os
import torch
import platform
import sys

# PRODUCTION CONFIGURATION - FORCE LIVE MODE
MODE = "live"
LIVE_MODE = True
ASSETS = ["BTC", "ETH", "SOL"]

# PRODUCTION TRADING PARAMETERS
SIGNAL_CONFIDENCE_THRESHOLD = 0.6  # Higher threshold
POSITION_SIZE_PERCENT = 1.0  # Conservative 1%
MAX_OPEN_POSITIONS = 2  # Fewer positions
MAX_DRAWDOWN_PERCENT = 5.0  # Tighter drawdown
COOLDOWN_MINUTES = 10  # Longer cooldown

# PRODUCTION API LIMITS
OKX_API_LIMITS = {
    "orders_per_second": 10,
    "requests_per_second": 5,
    "max_position_size": 25000
}

# Discord notifications
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def setup_gpu():
    """Production GPU setup with strict requirements"""
    system = platform.system()
    
    if torch.cuda.is_available():
        return {
            "type": "cuda",
            "device": "cuda",
            "optimized": True,
            "priority": 1
        }
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        return {
            "type": "apple_mps",
            "device": "mps",
            "optimized": True,
            "priority": 2
        }
    else:
        print("❌ PRODUCTION CRITICAL: NO GPU DETECTED")
        print("Production trading requires GPU acceleration")
        sys.exit(1)

# Initialize GPU for production
try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = True
    DEVICE = GPU_CONFIG["device"]
    print(f"🔴 PRODUCTION GPU: {GPU_CONFIG['type']} on {DEVICE}")
    
    # Production optimizations
    if DEVICE == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    elif DEVICE == "mps":
        torch.backends.mps.allow_tf32 = True
        
except Exception as e:
    print(f"❌ PRODUCTION GPU setup failed: {e}")
    sys.exit(1)

print("🔴 PRODUCTION CONFIG LOADED")
