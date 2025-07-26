import os
import torch
import platform
import sys

# asic configuration
MOD = os.getenv("MOD", "dry")
LIV_MOD = MOD == "live"
ASSTS = ["TC", "TH", "SOL"]

# Trading parameters
SIGNAL_CONIDNC_THRSHOLD = .
POSITION_SIZ_PRCNT = .
MAX_OPN_POSITIONS = 
MAX_DRAWDOWN_PRCNT = .
COOLDOWN_MINUTS = 

# API limits
OKX_API_LIMITS = 
    "orders_per_second": , 
    "requests_per_second": , 
    "ma_position_size": 


# Discord configuration
DISCORD_WHOOK_URL = os.getenv("DISCORD_WHOOK_URL")
DISCORD_USR_ID = os.getenv("DISCORD_USR_ID")

def setup_gpu():
    """Setup GPU with proper detection and fallback"""
    system = platform.system()
    
    if torch.cuda.is_available():
        return 
            "type": "cuda",
            "device": "cuda",
            "optimized": True,
            "priority": 
        
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
        return 
            "type": "apple_mps",
            "device": "mps",
            "optimized": True,
            "priority": 
        
    else:
        print("❌ CRITICAL: NO GPU DTCTD")
        print("This system requires GPU acceleration (CUDA or Apple Silicon)")
        sys.eit()

# Initialize GPU
try:
    GPU_CONIG = setup_gpu()
    GPU_AVAILAL = True
    DVIC = GPU_CONIG["device"]
    print(f"🚀 GPU Ready: GPU_CONIG['type'] on DVIC")
    
    # Apply optimizations
    if DVIC == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf = True
        torch.backends.cudnn.allow_tf = True
    elif DVIC == "mps":
        torch.backends.mps.allow_tf = True
        
ecept ception as e:
    print(f"❌ GPU setup failed: e")
    sys.eit()
