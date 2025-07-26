import os
from pathlib import Path

# Load environment if .env exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Basic configuration
MODE = os.getenv("MODE", "paper")
PAPER_TRADING = MODE == "paper"
LIVE_TRADING = MODE == "live"

ASSETS = ["BTC", "ETH", "SOL"]
PAPER_INITIAL_BALANCE = float(os.getenv("PAPER_INITIAL_BALANCE", "10000.0"))
PAPER_COMMISSION_RATE = float(os.getenv("PAPER_COMMISSION_RATE", "0.001"))
SIGNAL_CONFIDENCE_THRESHOLD = float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.75"))
POSITION_SIZE_PERCENT = float(os.getenv("POSITION_SIZE_PERCENT", "0.02"))
MAX_OPEN_POSITIONS = int(os.getenv("MAX_OPEN_POSITIONS", "3"))
MAX_DRAWDOWN_PERCENT = float(os.getenv("MAX_DRAWDOWN_PERCENT", "5.0"))

# API keys
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY", "")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")

# GPU setup
def setup_gpu():
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    except:
        return "cpu"

DEVICE = setup_gpu()
print(f"🔧 Config loaded: {MODE} mode, {DEVICE} device")
