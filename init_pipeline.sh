#!/bin/bash

set -e

MODE=${1:-dry}
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/engine.log"

mkdir -p $LOG_DIR /tmp data

echo "🚀 Initializing HFT Crypto Shorting System in $MODE mode"

cleanup() {
    echo "🔴 Shutting down system..."
    kill $PYTHON_PID 2>/dev/null || true
    kill $RUST_PID 2>/dev/null || true
    wait
    echo "✅ System shutdown complete"
}

trap cleanup EXIT INT TERM

if command -v pip3 &> /dev/null; then
    pip3 install -q torch torchvision cupy-cuda12x requests websocket-client pandas > /dev/null 2>&1
elif command -v pip &> /dev/null; then
    pip install -q torch torchvision cupy-cuda12x requests websocket-client pandas > /dev/null 2>&1
fi

if command -v cargo &> /dev/null; then
    cargo build --release --quiet 2>/dev/null || echo "⚠️ Rust build failed, continuing..."
fi

echo "🧠 Starting Python cognition layer..."
MODE=$MODE python3 main.py --mode=$MODE >> $LOG_FILE 2>&1 &
PYTHON_PID=$!

sleep 3

if ! ps -p $PYTHON_PID > /dev/null; then
    echo "❌ Python cognition layer failed to start"
    tail -10 $LOG_FILE
    exit 1
fi

if [[ -f "./target/release/hft_executor" ]]; then
    echo "⚙️ Starting Rust execution layer..."
    MODE=$MODE ./target/release/hft_executor >> $LOG_FILE 2>&1 &
    RUST_PID=$!
    
    sleep 2
    
    if ! ps -p $RUST_PID > /dev/null; then
        echo "❌ Rust execution layer failed to start"
        tail -10 $LOG_FILE
        exit 1
    fi
else
    echo "⚠️ Rust executor not found, running Python-only mode"
    RUST_PID=""
fi

check_system_health() {
    if ! ps -p $PYTHON_PID > /dev/null; then
        echo "❌ Python cognition layer crashed"
        return 1
    fi
    
    if [[ -n "$RUST_PID" ]] && ! ps -p $RUST_PID > /dev/null; then
        echo "❌ Rust execution layer crashed"
        return 1
    fi
    
    if [ ! -f "/tmp/signal.json" ] && [ $SECONDS -gt 60 ]; then
        echo "⚠️ No signals generated yet (${SECONDS}s elapsed)"
    fi
    
    return 0
}

echo "✅ System components started"
echo "📊 Python PID: $PYTHON_PID"
if [[ -n "$RUST_PID" ]]; then
    echo "⚡ Rust PID: $RUST_PID"
fi
echo "📄 Logs: $LOG_FILE"
echo ""
echo "🚀 System Live"
echo ""

HEALTH_CHECK_INTERVAL=30
LAST_HEALTH_CHECK=0

while true; do
    CURRENT_TIME=$SECONDS
    
    if [ $((CURRENT_TIME - LAST_HEALTH_CHECK)) -ge $HEALTH_CHECK_INTERVAL ]; then
        if ! check_system_health; then
            echo "💀 System health check failed"
            exit 1
        fi
        LAST_HEALTH_CHECK=$CURRENT_TIME
    fi
    
    if [ $((CURRENT_TIME % 300)) -eq 0 ]; then
        echo "⏱️ System uptime: ${CURRENT_TIME}s | Mode: $MODE"
        
        if [ -f "/tmp/signal.json" ]; then
            echo "📡 Signal file exists"
        fi
        
        if [ -f "/tmp/fills.json" ]; then
            FILL_COUNT=$(cat /tmp/fills.json 2>/dev/null | grep -o '"timestamp"' | wc -l || echo "0")
            echo "📋 Total fills: $FILL_COUNT"
        fi
        
        echo "💾 Log size: $(du -h $LOG_FILE 2>/dev/null | cut -f1 || echo "0K")"
        echo ""
    fi
    
    sleep 1
done
