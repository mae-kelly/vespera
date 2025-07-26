#!/bin/bash
set -euo pipefail

echo "🔄 Restarting HFT System..."

# Stop existing processes
if [[ -f "tmp/python.pid" ]]; then
    PID=$(cat tmp/python.pid)
    kill $PID 2>/dev/null || true
    rm -f tmp/python.pid
fi

pkill -f "hft-system" 2>/dev/null || true

# Clean old signals
rm -f /tmp/signal.json

# Wait for cleanup
sleep 3

# Restart system
./init_pipeline.sh
