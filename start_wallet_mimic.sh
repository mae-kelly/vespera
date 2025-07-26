#!/bin/bash
set -euo pipefail

echo "🚀 Starting Real Wallet Mimic System for 1000x Returns"
echo "=================================================="

# Check environment
if [[ ! -f ".env" ]]; then
    echo "❌ .env file not found"
    echo "📝 Copy environment_template.env to .env and configure your API keys"
    exit 1
fi

# Load environment
export $(grep -v '^#' .env | xargs)

# Validate critical variables
required_vars=("ETHEREUM_RPC_URL" "OKX_API_KEY" "ETHEREUM_WALLET_ADDRESS")
for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "❌ Required environment variable $var not set"
        exit 1
    fi
done

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install web3 websockets aiohttp eth-abi requests >/dev/null 2>&1 || {
    echo "❌ Failed to install dependencies"
    exit 1
}

echo "✅ Environment validated"
echo "💰 Initial Capital: $${INITIAL_CAPITAL:-1000}"
echo "🔗 Ethereum RPC: ${ETHEREUM_RPC_URL:0:50}..."
echo "📡 Wallet Address: ${ETHEREUM_WALLET_ADDRESS:0:10}..."
echo ""
echo "🎯 TARGET: $1,000 → $1,000,000 via wallet mirroring"
echo "⚡ STRATEGY: Real-time alpha wallet monitoring"
echo "🔥 MODE: Live token trading on OKX DEX"
echo ""
echo "Starting in 3 seconds..."
sleep 3

python3 wallet_mimic_real.py
