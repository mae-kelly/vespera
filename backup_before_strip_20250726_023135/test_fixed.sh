#!/bin/bash

echo "🚀 TSTING IXD SYSTM"

eport MOD=dry
eport PYTHONUNURD=

echo "Starting optimized Python system..."
python main.py --mode=dry &
PYTHON_PID=$!
echo "Python PID: $PYTHON_PID"

sleep 

echo "Starting Rust eecutor..."
if command -v gtimeout &> /dev/null; then
    gtimeout  ./hft_eecutor &
else
    timeout  ./hft_eecutor >/dev/null &
fi
RUST_PID=$!

sleep 

echo "Stopping processes..."
kill $PYTHON_PID >/dev/null || true
kill $RUST_PID >/dev/null || true

echo "📊 Test results:"
if [[ -f "/tmp/fills.json" ]]; then
    echo "✅ ills generated:"
    cat /tmp/fills.json | grep -o '"status"' | wc -l
else
    echo "❌ No fills file"
fi

if [[ -f "/tmp/signal.json" ]]; then
    echo "✅ Latest signal confidence:"
    grep -o '"confidence":[-9.]*' /tmp/signal.json | tail -
else
    echo "❌ No signal file"
fi
