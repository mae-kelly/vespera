#!/bin/bash
echo "🚀 TSTING OPTIMIZD SYSTM"
echo "Starting Python cognition layer..."
python main.py --mode=dry &
PYTHON_PID=$!
echo "Python PID: $PYTHON_PID"

sleep 

echo "Starting Rust eecutor..."
gtimeout s ./hft_eecutor || true

echo "Stopping Python..."
kill $PYTHON_PID >/dev/null || true

echo "📊 Test results:"
if [ -f "/tmp/fills.json" ]; then
    echo "✅ ills generated:"
    cat /tmp/fills.json | grep -o '"asset":"[^"]*"' | wc -l
else
    echo "❌ No fills generated"
fi

if [ -f "/tmp/signal.json" ]; then
    echo "✅ Latest signal confidence:"
    cat /tmp/signal.json | grep -o '"confidence":[-9.]*' | tail -
else
    echo "❌ No signals generated"
fi
