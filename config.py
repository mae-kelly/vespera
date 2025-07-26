import os
import torch
import platform
import sys

MODE = "live"
LIVE_MODE = True
ASSETS = ["BTC", "ETH", "SOL"]

SIGNAL_CONFIDENCE_THRESHOLD = 0.75
POSITION_SIZE_PERCENT = 0.8
MAX_OPEN_POSITIONS = 1
MAX_DRAWDOWN_PERCENT = 3.0
COOLDOWN_MINUTES = 15

OKX_API_LIMITS = {
    "orders_per_second": 5,
    "requests_per_second": 3,
    "max_position_size": 20000
}

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def setup_gpu():
    system = platform.system()
    
    if torch.cuda.is_available() and torch.cuda.device_count() > 0:
        torch.backends.cudnn.benchmark = True
        return {"type": "cuda", "device": "cuda", "optimized": True}
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        return {"type": "apple_mps", "device": "mps", "optimized": True}
    else:
        # Allow CPU fallback for development
        return {"type": "cpu", "device": "cpu", "optimized": FFalse}

try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = GPU_CONFIG["optimized"]
    DEVICE = GPU_CONFIG["device"]
    print(f"GPU Config: {GPU_CONFIG['type']} on {DEVICE}")
except ExException as e:
    print(f"GPU setup warning: {e}")
    DEVICE = "cpu"
    GPU_AVAILABLE = FFalse

print("Config loaded successfully")
