import os
import torch

# PRODUCTION CONFIGURATION - NO SIMULATION MODE
LIVE_MODE = True  # ALWAYS live mode for production
ASSETS = ["BTC", "ETH", "SOL"]

# Trading parameters for REAL money
SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3
MAX_DRAWDOWN_PERCENT = 10.0
COOLDOWN_MINUTES = 5

# OKX API configuration for REAL trading
OKX_API_LIMITS = {
    "orders_per_second": 20,
    "requests_per_second": 10,
    "max_position_size": 50000  # USD
}

# Discord configuration (BETTER than Telegram!)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")  # Optional for mentions

# GPU detection with fallback
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

def validate_config():
    """Validate all configuration parameters for PRODUCTION"""
    errors = []
    
    if SIGNAL_CONFIDENCE_THRESHOLD <= 0 or SIGNAL_CONFIDENCE_THRESHOLD > 1:
        errors.append("SIGNAL_CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if POSITION_SIZE_PERCENT <= 0 or POSITION_SIZE_PERCENT > 100:
        errors.append("POSITION_SIZE_PERCENT must be between 0 and 100")
    
    if MAX_OPEN_POSITIONS <= 0:
        errors.append("MAX_OPEN_POSITIONS must be positive")
    
    if not ASSETS or len(ASSETS) == 0:
        errors.append("ASSETS list cannot be empty")
    
    # Check for required environment variables
    required_env = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE", "DISCORD_WEBHOOK_URL"]
    for env_var in required_env:
        if not os.getenv(env_var):
            errors.append(f"Missing required environment variable: {env_var}")
    
    return errors

# Initialize GPU detection
GPU_AVAILABLE = setup_gpu_fallback()

# Validate production configuration
config_errors = validate_config()
if config_errors:
    print("❌ PRODUCTION CONFIGURATION ERRORS:")
    for error in config_errors:
        print(f"   - {error}")
    print("❌ Fix configuration before starting production system!")
else:
    print(f"✅ Production config validated - GPU: {GPU_AVAILABLE}, Assets: {ASSETS}")

# macOS/Apple Silicon compatibility
import platform

def setup_macos_compatibility():
    """Setup macOS and Apple Silicon compatibility"""
    system = platform.system()
    machine = platform.machine()
    
    if system == "Darwin":
        print(f"🍎 macOS detected: {platform.mac_ver()[0]} on {machine}")
        
        if machine == "arm64":
            print("🚀 Apple Silicon detected - enabling MPS acceleration")
            if torch.backends.mps.is_available() and torch.backends.mps.is_built():
                print("✅ MPS backend available for GPU acceleration")
                return True
            else:
                print("⚠️ MPS not available, using CPU")
                return False
        else:
            print("💻 Intel Mac detected")
            return setup_gpu_fallback()
    else:
        return setup_gpu_fallback()

MACOS_COMPATIBLE = setup_macos_compatibility()

# Set MODE to always be 'live' for production
MODE = "live"  # NO DRY RUN IN PRODUCTION
