set -e
MODE=${1:-dry}
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/engine.log"
mkdir -p $LOG_DIR /tmp data
echo "🚀 Initializing HFT Crypto Shorting System in $MODE mode"
cleanup() {
    echo "🔴 Shutting down system..."
    if [[ -n "$PYTHON_PID" ]]; then
        kill $PYTHON_PID 2>/dev/null || true
    fi
    if [[ -n "$RUST_PID" ]]; then
        kill $RUST_PID 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo "✅ System shutdown complete"
}
trap cleanup EXIT INT TERM
export MODE=$MODE
export PYTHONPATH="$PWD:$PYTHONPATH"
export PYTHONUNBUFFERED=1
echo "🧠 Starting Python cognition layer..."
python3 main.py --mode=$MODE >> $LOG_FILE 2>&1 &
PYTHON_PID=$!
sleep 3
if ! ps -p $PYTHON_PID > /dev/null 2>&1; then
    echo "❌ Python cognition layer failed to start"
    echo "📄 Last 10 lines of log:"
    tail -10 $LOG_FILE 2>/dev/null || echo "No log file found"
    exit 1
fi
echo "✅ Python layer started (PID: $PYTHON_PID)"
if [[ -f "./target/release/hft_executor" ]]; then
    echo "⚙️ Starting Rust execution layer..."
    MODE=$MODE ./target/release/hft_executor >> $LOG_FILE 2>&1 &
    RUST_PID=$!
    
    sleep 2
    
    if ! ps -p $RUST_PID > /dev/null 2>&1; then
        echo "❌ Rust execution layer failed to start"
        tail -10 $LOG_FILE
        exit 1
    fi
    echo "✅ Rust layer started (PID: $RUST_PID)"
else
    echo "⚠️ Rust executor not found, running Python-only mode"
    RUST_PID=""
fi
echo "✅ System components started"
echo "📊 Python PID: $PYTHON_PID"
if [[ -n "$RUST_PID" ]]; then
    echo "⚡ Rust PID: $RUST_PID"
fi
echo "📄 Logs: $LOG_FILE"
echo ""
echo "🚀 System Live"
echo ""
echo "Press Ctrl+C to stop..."
HEALTH_CHECK_INTERVAL=30
LAST_HEALTH_CHECK=0
SECONDS=0
while true; do
    if ! ps -p $PYTHON_PID > /dev/null 2>&1; then
        echo "💀 Python layer crashed"
        exit 1
    fi
    
    if [[ -n "$RUST_PID" ]] && ! ps -p $RUST_PID > /dev/null 2>&1; then
        echo "💀 Rust layer crashed"
        exit 1
    fi
    
    if [[ $((SECONDS % 300)) -eq 0 ]] && [[ $SECONDS -gt 0 ]]; then
        echo "⏱️ System uptime: ${SECONDS}s | Mode: $MODE"
        
        if [[ -f "/tmp/signal.json" ]]; then
            echo "📡 Signal file exists"
        else
            echo "📡 Waiting for signals..."
        fi
        
        if [[ -f "/tmp/fills.json" ]]; then
            FILL_COUNT=$(grep -o '"timestamp"' /tmp/fills.json 2>/dev/null | wc -l || echo "0")
            echo "📋 Total fills: $FILL_COUNT"
        fi
        
        echo "💾 Log size: $(du -h $LOG_FILE 2>/dev/null | cut -f1 || echo "0K")"
        echo ""
    fi
    
    sleep 1
done