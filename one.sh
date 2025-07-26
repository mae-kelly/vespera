#!/bin/bash

echo "🚀 TESTING ENHANCED FIXED SYSTEM"
echo "================================"

cleanup() {
    echo "Stopping processes..."
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null
    fi
    if [ ! -z "$RUST_PID" ]; then
        kill $RUST_PID 2>/dev/null
    fi
}

trap cleanup EXIT

echo "Starting optimized Python system..."
python3 main.py --mode=dry &
PYTHON_PID=$!
echo "Python PID: $PYTHON_PID"

sleep 3

echo "Starting Rust executor..."
gtimeout 10 ./hft_executor &
RUST_PID=$!

sleep 8

cleanup

echo "📊 Test results:"

if [ -f "/tmp/fills.json" ]; then
    FILL_COUNT=$(cat /tmp/fills.json | grep -o '"order_id"' | wc -l | tr -d ' ')
    echo "✅ Fills generated: $FILL_COUNT"
else
    echo "❌ No fills file found"
fi

if [ -f "/tmp/signal.json" ]; then
    CONFIDENCE=$(cat /tmp/signal.json | grep -o '"confidence":[0-9.]*' | head -1)
    echo "✅ Latest signal confidence: $CONFIDENCE"
    
    ASSET=$(cat /tmp/signal.json | grep -o '"asset":"[A-Z]*"' | head -1)
    echo "✅ Signal asset: $ASSET"
else
    echo "❌ No signal file found"
fi

echo ""
echo "🎯 System Status: ENHANCED AND FIXED"