import os
import torch
import platform
import sys
MODE = os.getenv("MODE", "dry")
LIVE_MODE = MODE == "live"
ASSETS = ["BTC", "ETH", "SOL"]
SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3
MAX_DRAWDOWN_PERCENT = 10.0
COOLDOWN_MINUTES = 5
OKX_API_LIMITS = {"orders_per_second": 20, "requests_per_second": 10, "max_position_size": 50000}
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")
def setup_mandatory_gpu_acceleration():
    system = platform.system()
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        if "A100" in device_name:
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.cuda.empty_cache()
            return {"type": "cuda_a100", "device": "cuda", "optimized": True, "priority": 1}
    if system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return {"type": "apple_silicon", "device": "mps", "optimized": True, "priority": 2}
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        return {"type": "cuda_standard", "device": "cuda", "optimized": True, "priority": 3}
    print("❌ SYSTEM TERMINATED: NO GPU DETECTED")
    sys.exit(1)
GPU_CONFIG = setup_mandatory_gpu_acceleration()
GPU_AVAILABLE = True
DEVICE = GPU_CONFIG["device"]
