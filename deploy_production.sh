#!/bin/bash

set -e

echo "🚀 DEPLOYING HFT SYSTEM FOR REAL PRODUCTION TRADING"
echo "=================================================="

# Validate environment
echo "🔍 Validating production environment..."

# Check required environment variables
required_vars=("OKX_API_KEY" "OKX_SECRET_KEY" "OKX_PASSPHRASE" "TELEGRAM_BOT_TOKEN" "TELEGRAM_CHAT_ID")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        missing_vars+=("$var")
    fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo "❌ MISSING REQUIRED ENVIRONMENT VARIABLES:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Set these in your .env file:"
    echo "OKX_API_KEY=your_real_api_key"
    echo "OKX_SECRET_KEY=your_real_secret_key"
    echo "OKX_PASSPHRASE=your_real_passphrase"
    echo "TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
    echo "TELEGRAM_CHAT_ID=your_telegram_chat_id"
    exit 1
fi

echo "✅ Environment variables validated"

# Set production mode
export MODE="live"
export OKX_TESTNET="false"  # REAL trading
export PYTHONUNBUFFERED=1

echo "📦 Installing production dependencies..."
pip install -q torch torchvision cupy-cuda12x cudf pandas websocket-client python-telegram-bot requests

echo "🔧 Building Rust production components..."
cargo build --release

echo "🧪 Running production readiness test..."
python3 -c "
import config
errors = config.validate_config()
if errors:
    print('❌ Configuration errors:')
    for error in errors:
        print(f'   - {error}')
    exit(1)
else:
    print('✅ Production configuration valid')

import signal_engine
signal_engine.feed.start_feed()
import time
time.sleep(3)
print('✅ Real market data feed started')
"

echo "⚠️  FINAL PRODUCTION WARNING:"
echo "   - This system will trade with REAL MONEY"
echo "   - Ensure your OKX account has sufficient funds"
echo "   - Monitor the system closely after deployment"
echo "   - Stop immediately if unexpected behavior occurs"
echo ""

read -p "Are you ready to start REAL MONEY trading? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 STARTING PRODUCTION HFT SYSTEM..."
echo "===================================="

# Create logs directory
mkdir -p logs /tmp data

LOG_FILE="logs/production.log"

# Start Python cognition layer
echo "🧠 Starting Python cognition layer (REAL trading)..."
python3 main.py --mode=live >> $LOG_FILE 2>&1 &
PYTHON_PID=$!

sleep 5

if ! ps -p $PYTHON_PID > /dev/null; then
    echo "❌ Python layer failed to start"
    tail -20 $LOG_FILE
    exit 1
fi

# Start Rust execution layer
echo "⚡ Starting Rust execution layer (REAL trading)..."
MODE=live ./target/release/hft_executor >> $LOG_FILE 2>&1 &
RUST_PID=$!

sleep 3

if ! ps -p $RUST_PID > /dev/null; then
    echo "❌ Rust layer failed to start"
    tail -20 $LOG_FILE
    kill $PYTHON_PID 2>/dev/null || true
    exit 1
fi

echo "✅ PRODUCTION SYSTEM LIVE - REAL MONEY TRADING ACTIVE"
echo "====================================================="
echo "📊 Python PID: $PYTHON_PID"
echo "⚡ Rust PID: $RUST_PID"
echo "📄 Logs: $LOG_FILE"
echo "💰 Mode: LIVE TRADING WITH REAL MONEY"
echo ""
echo "🚨 IMPORTANT: Monitor the logs continuously!"
echo "   tail -f $LOG_FILE"
echo ""
echo "To stop the system:"
echo "   kill $PYTHON_PID $RUST_PID"

# Keep the script running to monitor
trap 'echo "🔴 Stopping production system..."; kill $PYTHON_PID $RUST_PID 2>/dev/null || true; exit 0' INT TERM

while true; do
    if ! ps -p $PYTHON_PID > /dev/null; then
        echo "❌ Python layer crashed!"
        kill $RUST_PID 2>/dev/null || true
        exit 1
    fi
    
    if ! ps -p $RUST_PID > /dev/null; then
        echo "❌ Rust layer crashed!"
        kill $PYTHON_PID 2>/dev/null || true
        exit 1
    fi
    
    sleep 30
done
