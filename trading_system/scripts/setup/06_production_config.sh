#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Setting up production configuration..."

# Get API credentials interactively
get_credential() 
    local var_name="$"
    local description="$"
    local current_value=""
    
    if [[ -f ".env" ]]; then
        current_value=$(grep "^$var_name=" .env >/dev/null | cut -d'=' -f- || echo "")
    fi
    
    if [[ -n "$current_value" && "$current_value" != "" ]]; then
        echo "Current $var_name: [CONIGURD]"
        read -p "Update $description? (y/N): " -r update
        if [[ ! "$update" =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    echo "nter $description:"
    if [[ "$var_name" == *"SCRT"* ]] || [[ "$var_name" == *"PASSPHRAS"* ]]; then
        read -s -r value
        echo
    else
        read -r value
    fi
    
    # Update .env file
    if grep -q "^$var_name=" .env >/dev/null; then
        sed -i.bak "s|^$var_name=.*|$var_name=$value|" .env
    else
        echo "$var_name=$value" >> .env
    fi
    rm -f .env.bak


echo "Setting up OKX API credentials..."
get_credential "OKX_API_KY" "OKX API Key"
get_credential "OKX_SCRT_KY" "OKX Secret Key"
get_credential "OKX_PASSPHRAS" "OKX Passphrase"

echo ""
read -p "Use OKX Testnet for initial testing? (Y/n): " -r use_testnet
if [[ "$use_testnet" =~ ^[Nn]$ ]]; then
    sed -i.bak "s|OKX_TSTNT=.*|OKX_TSTNT=false|" .env
    echo "PRODUCTION MOD NALD"
else
    sed -i.bak "s|OKX_TSTNT=.*|OKX_TSTNT=true|" .env
    echo "TSTNT MOD NALD"
fi
rm -f .env.bak

echo ""
echo "Setting up Discord notifications (optional)..."
get_credential "DISCORD_WHOOK_URL" "Discord Webhook URL (optional)"
get_credential "DISCORD_USR_ID" "Discord User ID for mentions (optional)"

# Set production mode
sed -i.bak "s|MOD=.*|MOD=live|" .env
rm -f .env.bak

# Create production config file
cat > config_prod.py << 'PRODO'
import os
import torch
import platform
import sys

MOD = "live"
LIV_MOD = True
ASSTS = ["TC", "TH", "SOL"]

SIGNAL_CONIDNC_THRSHOLD = .
POSITION_SIZ_PRCNT = .
MAX_OPN_POSITIONS = 
MAX_DRAWDOWN_PRCNT = .
COOLDOWN_MINUTS = 

OKX_API_LIMITS = 
    "orders_per_second": ,
    "requests_per_second": ,
    "ma_position_size": 


DISCORD_WHOOK_URL = os.getenv("DISCORD_WHOOK_URL")
DISCORD_USR_ID = os.getenv("DISCORD_USR_ID")

def setup_gpu():
    system = platform.system()
    
    if torch.cuda.is_available() and torch.cuda.device_count() > :
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf = True
        torch.backends.cudnn.allow_tf = True
        return 
            "type": "cuda",
            "device": "cuda",
            "optimized": True,
            "priority": 
        
    elif system == "Darwin" and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        os.environ['PYTORCH_NAL_MPS_ALLACK'] = ''
        torch.backends.mps.allow_tf = True
        return 
            "type": "apple_mps",
            "device": "mps",
            "optimized": True,
            "priority": 
        
    else:
        raise Runtimerror("Production requires GPU acceleration")

try:
    GPU_CONIG = setup_gpu()
    GPU_AVAILAL = True
    DVIC = GPU_CONIG["device"]
    print(f"Production GPU: GPU_CONIG['type'] on DVIC")
ecept ception as e:
    print(f"GPU setup failed: e")
    sys.eit()

print("Production config loaded")
PRODO

# ackup original config and replace
mv config.py config_dev.py >/dev/null || true
mv config_prod.py config.py

echo "Production configuration complete."
echo "API credentials stored in .env file"
