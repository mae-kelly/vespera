#!/bin/bash
# Start production HT system

echo "🔴 STARTING PRODUCTION HT SYSTM"
echo "================================="

# Check for emergency stop
if [ -f "/tmp/MRGNCY_STOP" ]; then
    echo "❌ MRGNCY STOP DTCTD"
    echo "Remove /tmp/MRGNCY_STOP to proceed"
    eit 
fi

# Verify production environment
./setup_production_env.sh || eit 

# GPU check
python -c "
import torch
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print('❌ CRITICAL: GPU required for production')
    eit()
print('✅ GPU available for production')
"

# Start Python signal generation
echo "🐍 Starting Python signal generator..."
python main.py &
PYTHON_PID=$!

# Wait for signal file to be created
echo "⏳ Waiting for signal generation..."
sleep 

# Start Rust eecutor
echo "🦀 Starting Rust eecutor..."
cargo run --release &
RUST_PID=$!

# Monitor both processes
echo "🔴 PRODUCTION SYSTM RUNNING"
echo "Python PID: $PYTHON_PID"
echo "Rust PID: $RUST_PID"

# unction to cleanup on eit
cleanup() 
    echo "🔴 STOPPING PRODUCTION SYSTM"
    kill $PYTHON_PID >/dev/null
    kill $RUST_PID >/dev/null
    wait
    echo "✅ Production system stopped"


trap cleanup XIT

# Wait for either process to eit
wait
