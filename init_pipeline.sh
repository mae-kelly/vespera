#!/bin/bash

# Enhanced Multi-WebSocket HFT System Pipeline
set -euo pipefail

MODE="${1:-dry}"
LOG_DIR="logs"
PYTHON_LOG="$LOG_DIR/engine.log"
RUST_LOG="$LOG_DIR/rust_executor.log"
SYSTEM_LOG="$LOG_DIR/system.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$SYSTEM_LOG"
}

check_prerequisites() {
    log "🔍 Checking multi-WebSocket prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        exit 1
    fi
    
    if [[ ! -f "./hft_executor" ]]; then
        echo -e "${RED}❌ Rust executor not found. Run: cargo build --release${NC}"
        exit 1
    fi
    
    chmod +x ./hft_executor
    
    # Check WebSocket dependencies
    python3 -c "import websocket, requests" 2>/dev/null || {
        echo -e "${RED}❌ Missing WebSocket dependencies. Installing...${NC}"
        pip install websocket-client requests
    }
    
    python3 -c "
import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print('❌ CRITICAL: NO GPU DETECTED')
    sys.exit(1)
else:
    device = 'CUDA' if torch.cuda.is_available() else 'MPS'
    print(f'✅ GPU acceleration available: {device}')
"
    
    log "✅ All multi-WebSocket prerequisites satisfied"
}

setup_environment() {
    log "⚙️ Setting up multi-feed environment..."
    
    if [[ -f ".env" ]]; then
        set -a
        source .env
        set +a
        log "✅ Environment variables loaded"
    else
        log "⚠️ No .env file found - using defaults"
    fi
    
    export MODE="$MODE"
    export RUST_LOG="info"
    export PYTHONUNBUFFERED=1
    
    mkdir -p /tmp
    echo "[]" > /tmp/fills.json
    echo "{}" > /tmp/signal.json
    
    log "✅ Multi-feed environment configured for $MODE mode"
}

start_python_cognition() {
    log "🧠 Starting Python multi-WebSocket cognition layer..."
    
    python3 main.py --mode="$MODE" >> "$PYTHON_LOG" 2>&1 &
    PYTHON_PID=$!
    
    sleep 3
    
    if kill -0 $PYTHON_PID 2>/dev/null; then
        log "✅ Python multi-feed cognition layer running (PID: $PYTHON_PID)"
        echo $PYTHON_PID > "$LOG_DIR/python.pid"
    else
        log "❌ Python cognition layer failed to start"
        exit 1
    fi
}

start_rust_execution() {
    log "🦀 Starting OKX-focused Rust execution layer..."
    log "⚡ Sub-500μs execution targeting enabled"
    
    exec ./hft_executor 2>&1 | tee -a "$RUST_LOG"
}

cleanup() {
    log "🔴 Shutdown signal received"
    
    if [[ -f "$LOG_DIR/python.pid" ]]; then
        PYTHON_PID=$(cat "$LOG_DIR/python.pid")
        if kill -0 $PYTHON_PID 2>/dev/null; then
            log "Stopping Python multi-feed layer (PID: $PYTHON_PID)"
            kill $PYTHON_PID
            wait $PYTHON_PID 2>/dev/null || true
        fi
        rm -f "$LOG_DIR/python.pid"
    fi
    
    log "✅ Multi-feed system shutdown complete"
    exit 0
}

show_status() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              MULTI-WEBSOCKET HFT SYSTEM                     ║"
    echo "║          OKX-Focused + Multi-Feed Intelligence              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${CYAN}Mode:${NC} $MODE"
    echo -e "${CYAN}GPU:${NC} $(python3 -c "import torch; print('CUDA' if torch.cuda.is_available() else 'MPS' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'CPU')")"
    echo -e "${CYAN}Exchange:${NC} OKX (Primary)"
    echo -e "${CYAN}Feeds:${NC} OKX + Binance + Kraken + Coinbase"
    echo -e "${CYAN}Logs:${NC} $LOG_DIR/"
    echo -e "${CYAN}Time:${NC} $(date '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
}

monitor_system() {
    (
        while true; do
            sleep 30
            
            if [[ -f "/tmp/signal.json" ]]; then
                SIGNAL_AGE=$(( $(date +%s) - $(stat -c %Y /tmp/signal.json 2>/dev/null || echo 0) ))
                if [[ $SIGNAL_AGE -lt 60 ]]; then
                    log "📊 Multi-feed system healthy - signals flowing"
                fi
            fi
            
            if [[ -f "$LOG_DIR/python.pid" ]]; then
                PYTHON_PID=$(cat "$LOG_DIR/python.pid")
                if ! kill -0 $PYTHON_PID 2>/dev/null; then
                    log "⚠️ Python multi-feed layer died - restarting"
                    start_python_cognition
                fi
            fi
        done
    ) &
    MONITOR_PID=$!
    echo $MONITOR_PID > "$LOG_DIR/monitor.pid"
}

main() {
    trap cleanup SIGINT SIGTERM EXIT
    
    > "$SYSTEM_LOG"
    > "$PYTHON_LOG"
    > "$RUST_LOG"
    
    show_status
    check_prerequisites
    setup_environment
    start_python_cognition
    monitor_system
    
    echo -e "${GREEN}"
    echo "🚀 Multi-WebSocket System Live"
    echo "=================================="
    echo "✅ Python Multi-Feed: Background"
    echo "✅ OKX Rust Executor: Foreground"
    echo "✅ GPU Acceleration: Active"
    echo "✅ WebSocket Feeds: 4x Redundancy"
    echo "✅ Real-time Data: Multi-Source"
    echo "✅ Signal Processing: Enhanced"
    echo -e "${NC}"
    
    log "🚀 Multi-WebSocket System Live - Enhanced startup complete"
    log "📊 Feed monitoring: OKX + Binance + Kraken + Coinbase"
    
    start_rust_execution
}

if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    echo "Multi-WebSocket HFT System Pipeline Launcher"
    echo ""
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes:"
    echo "  dry   - Simulation mode (default)"
    echo "  live  - Live trading mode"
    echo ""
    echo "Features:"
    echo "  • 4x WebSocket feed redundancy"
    echo "  • OKX-focused execution"
    echo "  • Sub-500μs targeting"
    echo "  • Multi-exchange price aggregation"
    echo ""
    exit 0
fi

if [[ "$MODE" != "dry" ]] && [[ "$MODE" != "live" ]]; then
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo "Valid modes: dry, live"
    exit 1
fi

main "$@"
