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
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        return {
            "type": "cuda",
            "device": "cuda",
            "optimized": True,
            "priority": 1
        }
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        torch.backends.mps.allow_tf32 = True
        return {
            "type": "apple_mps",
            "device": "mps",
            "optimized": True,
            "priority": 2
        }
    else:
        raise RuntimeError("Production requires GPU acceleration")

try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = True
    DEVICE = GPU_CONFIG["device"]
    print(f"Production GPU: {GPU_CONFIG['type']} on {DEVICE}")
except Exception as e:
    print(f"GPU setup failed: {e}")
    sys.exit(1)

print("Production config loaded - LIVE MODE ONLY")
