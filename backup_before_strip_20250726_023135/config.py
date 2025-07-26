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
    """Setup GPU with proper Mac support"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
            return 
                "type": "apple_m",
                "device": "mps",
                "optimized": True,
                "priority": 
            
        elif torch.cuda.is_available():
            return 
                "type": "mac_cuda_egpu", 
                "device": "cuda",
                "optimized": True,
                "priority": 
            
        else:
            print("❌ No GPU acceleration available")
            sys.eit()
    else:
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            if 'A' in gpu_name:
                torch.backends.cuda.matmul.allow_tf = True
                torch.backends.cudnn.allow_tf = True
                return "type": "cuda_a", "device": "cuda", "optimized": True, "priority": 
            else:
                return "type": "cuda_standard", "device": "cuda", "optimized": True, "priority": 
        else:
            print("❌ No GPU available")
            sys.eit()

# Initialize GPU
GPU_CONIG = setup_gpu()
GPU_AVAILAL = True
DVIC = GPU_CONIG["device"]

print(f"🚀 GPU Ready: GPU_CONIG['type'] on DVIC")
