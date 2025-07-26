#!/bin/bash
# Start production HFT system

echo "🔴 STARTING PRODUCTION HFT SYSTEM"
echo "================================="

# Check for emergency stop
if [ -f "/tmp/EMERGENCY_STOP" ]; then
    echo "❌ EMERGENCY STOP DETECTED"
    echo "Remove /tmp/EMERGENCY_STOP to proceed"
    exit 1
fi

# Verify production environment
./setup_production_env.sh || exit 1

# GPU check
python3 -c "
import torch
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print('❌ CRITICAL: GPU required for production')
    exit(1)
print('✅ GPU available for production')
"

# Start Python signal generation
echo "🐍 Starting Python signal generator..."
python3 main.py &
PYTHON_PID=$!

# Wait for signal file to be created
echo "⏳ Waiting for signal generation..."
sleep 10

# Start Rust executor
echo "🦀 Starting Rust executor..."
cargo run --release &
RUST_PID=$!

# Monitor both processes
echo "🔴 PRODUCTION SYSTEM RUNNING"
echo "Python PID: $PYTHON_PID"
echo "Rust PID: $RUST_PID"

# Function to cleanup on exit
cleanup() {
    echo "🔴 STOPPING PRODUCTION SYSTEM"
    kill $PYTHON_PID 2>/dev/null
    kill $RUST_PID 2>/dev/null
    wait
    echo "✅ Production system stopped"
}

trap cleanup EXIT

# Wait for either process to exit
wait
