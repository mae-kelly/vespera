#!/bin/bash

echo "🚀 TESTING FIXED SYSTEM"

export MODE=dry
export PYTHONUNBUFFERED=1

echo "Starting optimized Python system..."
python3 main.py --mode=dry &
PYTHON_PID=$!
echo "Python PID: $PYTHON_PID"

sleep 5

echo "Starting Rust executor..."
if command -v gtimeout &> /dev/null; then
    gtimeout 10 ./hft_executor &
else
    timeout 10 ./hft_executor 2>/dev/null &
fi
RUST_PID=$!

sleep 8

echo "Stopping processes..."
kill $PYTHON_PID 2>/dev/null || true
kill $RUST_PID 2>/dev/null || true

echo "📊 Test results:"
if [[ -f "/tmp/fills.json" ]]; then
    echo "✅ Fills generated:"
    cat /tmp/fills.json | grep -o '"status"' | wc -l
else
    echo "❌ No fills file"
fi

if [[ -f "/tmp/signal.json" ]]; then
    echo "✅ Latest signal confidence:"
    grep -o '"confidence":[0-9.]*' /tmp/signal.json | tail -1
else
    echo "❌ No signal file"
fi
