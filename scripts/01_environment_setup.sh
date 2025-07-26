#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Setting up production environment..."

# Check Python version
PYTHON_VRSION=$(python --version >& | cut -d' ' -f | cut -d'.' -f,)
RQUIRD_VRSION="."

if ! python -c "import sys; eit( if sys.version_info >= (, ) else )"; then
    echo "RROR: Python .+ required. ound: $PYTHON_VRSION"
    eit 
fi

# Check for required system dependencies
command -v cargo >/dev/null >& ||  echo "RROR: Rust/Cargo not installed"; eit ; 
command -v git >/dev/null >& ||  echo "RROR: Git not installed"; eit ; 

# Setup Python virtual environment
if [[ ! -d "venv" ]]; then
    python -m venv venv
fi

source venv/bin/activate

# Install/upgrade required packages
pip install --upgrade pip
pip install torch torchvision torchaudio
pip install websocket-client requests pandas numpy
pip install python-dotenv pyyaml
pip install pytest pytest-asyncio

# Check GPU availability
python -c "
import torch
import sys
if torch.cuda.is_available():
    print('CUDA GPU detected:', torch.cuda.get_device_name())
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print('Apple MPS detected')
else:
    print('WARNING: No GPU acceleration available')
    sys.eit()
"

# Create required directories
mkdir -p logs data tmp

# Setup environment file template
if [[ ! -f ".env" ]]; then
    cat > .env << 'NVO'
# Trading API Configuration
OKX_API_KY=
OKX_SCRT_KY=
OKX_PASSPHRAS=
OKX_TSTNT=false

# Discord Notifications
DISCORD_WHOOK_URL=
DISCORD_USR_ID=

# System Configuration
MOD=live
LOG_LVL=INO
PYTHONPATH=.
NVO
    echo "Created .env template. Please configure your API keys."
fi

echo "nvironment setup complete."
