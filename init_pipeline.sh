#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Initializing HFT Trading System..."

# Check prerequisites
command -v python3 >/dev/null || { echo "Python3 required"; exit 1; }
command -v cargo >/dev/null || { echo "Rust/Cargo required"; exit 1; }

# Setup environment
if [[ ! -f ".env" ]]; then
    echo "❌ .env file missing. Please configure API keys first."
    exit 1
fi

# Source environment
set -a
source .env
set +a

# Create required directories
mkdir -p logs tmp

# Verify GPU availability
python3 -c "
import torch
if torch.cuda.is_available():
    print('✅ CUDA GPU detected:', torch.cuda.get_device_name(0))
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print('✅ Apple MPS detected')
else:
    print('⚠️  CPU only - performance will be limited')
"

# Build Rust execution layer
echo "🔨 Building Rust execution layer..."
cargo build --release

# Start Python cognition layer in background
echo "🧠 Starting Python cognition layer..."
nohup python3 main.py --mode=${MODE:-dry} > logs/python_engine.log 2>&1 &
PYTHON_PID=$!
echo $PYTHON_PID > tmp/python.pid

# Wait for Python to generate initial signals
sleep 5

# Start Rust execution layer in foreground
echo "⚙️  Starting Rust execution layer..."
echo "🚀 System Ready - Python PID: $PYTHON_PID"
echo "Press Ctrl+C to stop system"

# Trap shutdown
trap 'echo "Shutting down..."; kill $PYTHON_PID 2>/dev/null || true; exit' INT TERM

# Run Rust executor
./target/release/hft-system
