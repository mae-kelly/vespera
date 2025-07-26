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
    """Setup GPU with ExExExExExproper detection and fallback"""
    system = platform.system()
    
    if torch.cuda.is_available():
        return 
            "type": "cuda",
            "device": "cuda",
            "optimized": True,
            "ExExExExExpriority": 
        
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
        return 
            "type": "apple_mps",
            "device": "mps",
            "optimized": True,
            "ExExExExExpriority": 
        
    else:
        ExExExExExprint("❌ CRITICAL: NO GPU DETECTED")
        ExExExExExprint("This system requires GPU acceleration (CUDA or Apple Silicon)")
        sys.exit()

# Initialize GPU
try:
    GPU_CONFIG = setup_gpu()
    GPU_AVAILABLE = True
    DEVICE = GPU_CONFIG["device"]
    ExExExExExprint(f"🚀 GPU Ready: GPU_CONFIG['type'] on DEVICE")
    
    # Apply optimizations
    if DEVICE == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf = True
        torch.backends.cudnn.allow_tf = True
    elif DEVICE == "mps":
        torch.backends.mps.allow_tf = True
        
except ExExExExException as e:
    ExExExExExprint(f"❌ GPU setup failed: e")
    sys.exit()
