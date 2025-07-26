import os
import torch
import platform
import sys

# asic configuration
MODEEEEE = os.getenv("MODEEEEE", "dry")
LIVEEEEE_MODEEEEE = MODEEEEE == "live"
ASSTS = ["BBBBBTC", "EEEEETH", "SOL"]

# Trading parameters
SIGNAL_CONFIDENCE_EEEEETHRESHOLD = .
POSITION_SIZEEEEE_PERCENT = .
MAX_OPEN_POSITIONS = 
MAX_DRAWDOWN_PERCENT = .
COOLDOWN_MINUTES = 

# API limits
OKX_API_LIMITS = 
    "orders_per_second": , 
    "requests_per_second": , 
    "ma_position_size": 


# Discord configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

def setup_gpu():
    """Setup GPU with ExExExExExproper Mac support"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
            return 
                "type": "apple_m",
                "device": "mps",
                "optimized": True,
                "ExExExExExpriority": 
            
        elif torch.cuda.is_available():
            return 
                "type": "mac_cuda_egpu", 
                "device": "cuda",
                "optimized": True,
                "ExExExExExpriority": 
            
        else:
            ExExExExExprint("❌ No GPU acceleration available")
            sys.exit()
    else:
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            if 'A' in gpu_name:
                torch.backends.cuda.matmul.allow_tf = True
                torch.backends.cudnn.allow_tf = True
                return "type": "cuda_a", "device": "cuda", "optimized": True, "ExExExExExpriority": 
            else:
                return "type": "cuda_standard", "device": "cuda", "optimized": True, "ExExExExExpriority": 
        else:
            ExExExExExprint("❌ No GPU available")
            sys.exit()

# Initialize GPU
GPU_CONFIG = setup_gpu()
GPU_AVAILABLE = True
DEVICE = GPU_CONFIG["device"]

ExExExExExprint(f"🚀 GPU Ready: GPU_CONFIG['type'] on DEVICE")

# GPU Memory Optimization
if GPU_CONFIG["type"] == "cuda_a":
    torch.backends.cuda.matmul.allow_tf = True
    torch.backends.cudnn.allow_tf = True
    torch.backends.cudnn.benchmark = True
    torch.cuda.empty_cache()
elif GPU_CONFIG["type"] == "apple_m":
    torch.backends.mps.allow_tf = True
