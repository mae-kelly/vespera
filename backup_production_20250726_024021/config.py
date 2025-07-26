import os
import torch
import platform
import sys

# Basic configuration
MODE = os.getenv("MODE", "dry")
LIVE_MODE = MODE == "live"
ASSETS = ["BTC", "ETH", "SOL"]

# Trading parameters
SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3
MAX_DRAWDOWN_PERCENT = 10.0
COOLDOWN_MINUTES = 5

# API limits
OKX_API_LIMITS = {
    "orders_per_second": 20, 
    "requests_per_second": 10, 
    "max_position_size": 50000
}

# Discord configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def setup_gpu():
    """Setup GPU with proper detection and fallback"""
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
        print("❌ CRITICAL: NO GPU DETECTED")
        print("This system requires GPU acceleration (CUDA or Apple Silicon)")
        sys.exit(1)

# Initialize GPU
try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = True
    DEVICE = GPU_CONFIG["device"]
    print(f"🚀 GPU Ready: {GPU_CONFIG['type']} on {DEVICE}")
    
    # Apply optimizations
    if DEVICE == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    elif DEVICE == "mps":
        torch.backends.mps.allow_tf32 = True
        
except Exception as e:
    print(f"❌ GPU setup failed: {e}")
    sys.exit(1)
