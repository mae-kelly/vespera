#!/bin/bash

# nhanced Multi-WebSocket HT System Pipeline
set -euo pipefail

MOD="$:-dry"
LOG_DIR="logs"
PYTHON_LOG="$LOG_DIR/engine.log"
RUST_LOG="$LOG_DIR/rust_eecutor.log"
SYSTM_LOG="$LOG_DIR/system.log"

# Colors
RD='[;m'
GRN='[;m'
YLLOW='[;m'
LU='[;m'
PURPL='[;m'
CYAN='[;m'
NC='[m'

mkdir -p "$LOG_DIR"

log() 
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $" | tee -a "$SYSTM_LOG"


check_prerequisites() 
    log "🔍 Checking multi-WebSocket prerequisites..."
    
    if ! command -v python &> /dev/null; then
        echo -e "$RD❌ Python  not found$NC"
        eit 
    fi
    
    if [[ ! -f "./hft_eecutor" ]]; then
        echo -e "$RD❌ Rust eecutor not found. Run: cargo build --release$NC"
        eit 
    fi
    
    chmod + ./hft_eecutor
    
    # Check WebSocket dependencies
    python -c "import websocket, requests" >/dev/null || 
        echo -e "$RD❌ Missing WebSocket dependencies. Installing...$NC"
        pip install websocket-client requests
    
    
    python -c "
import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print('❌ CRITICAL: NO GPU DTCTD')
    sys.eit()
else:
    device = 'CUDA' if torch.cuda.is_available() else 'MPS'
    print(f'✅ GPU acceleration available: device')
"
    
    log "✅ All multi-WebSocket prerequisites satisfied"


setup_environment() 
    log "⚙️ Setting up multi-feed environment..."
    
    if [[ -f ".env" ]]; then
        set -a
        source .env
        set +a
        log "✅ nvironment variables loaded"
    else
        log "⚠️ No .env file found - using defaults"
    fi
    
    eport MOD="$MOD"
    eport RUST_LOG="info"
    eport PYTHONUNURD=
    
    mkdir -p /tmp
    echo "[]" > /tmp/fills.json
    echo "" > /tmp/signal.json
    
    log "✅ Multi-feed environment configured for $MOD mode"


start_python_cognition() 
    log "🧠 Starting Python multi-WebSocket cognition layer..."
    
    python main.py --mode="$MOD" >> "$PYTHON_LOG" >& &
    PYTHON_PID=$!
    
    sleep 
    
    if kill - $PYTHON_PID >/dev/null; then
        log "✅ Python multi-feed cognition layer running (PID: $PYTHON_PID)"
        echo $PYTHON_PID > "$LOG_DIR/python.pid"
    else
        log "❌ Python cognition layer failed to start"
        eit 
    fi


start_rust_eecution() 
    log "🦀 Starting OKX-focused Rust eecution layer..."
    log "⚡ Sub-μs eecution targeting enabled"
    
    eec ./hft_eecutor >& | tee -a "$RUST_LOG"


cleanup() 
    log "🔴 Shutdown signal received"
    
    if [[ -f "$LOG_DIR/python.pid" ]]; then
        PYTHON_PID=$(cat "$LOG_DIR/python.pid")
        if kill - $PYTHON_PID >/dev/null; then
            log "Stopping Python multi-feed layer (PID: $PYTHON_PID)"
            kill $PYTHON_PID
            wait $PYTHON_PID >/dev/null || true
        fi
        rm -f "$LOG_DIR/python.pid"
    fi
    
    log "✅ Multi-feed system shutdown complete"
    eit 


show_status() 
    echo -e "$PURPL"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              MULTI-WSOCKT HT SYSTM                     ║"
    echo "║          OKX-ocused + Multi-eed Intelligence              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "$NC"
    echo -e "$CYANMode:$NC $MOD"
    echo -e "$CYANGPU:$NC $(python -c "import torch; print('CUDA' if torch.cuda.is_available() else 'MPS' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'CPU')")"
    echo -e "$CYANchange:$NC OKX (Primary)"
    echo -e "$CYANeeds:$NC OKX + inance + Kraken + Coinbase"
    echo -e "$CYANLogs:$NC $LOG_DIR/"
    echo -e "$CYANTime:$NC $(date '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""


monitor_system() 
    (
        while true; do
            sleep 
            
            if [[ -f "/tmp/signal.json" ]]; then
                SIGNAL_AG=$(( $(date +%s) - $(stat -c %Y /tmp/signal.json >/dev/null || echo ) ))
                if [[ $SIGNAL_AG -lt  ]]; then
                    log "📊 Multi-feed system healthy - signals flowing"
                fi
            fi
            
            if [[ -f "$LOG_DIR/python.pid" ]]; then
                PYTHON_PID=$(cat "$LOG_DIR/python.pid")
                if ! kill - $PYTHON_PID >/dev/null; then
                    log "⚠️ Python multi-feed layer died - restarting"
                    start_python_cognition
                fi
            fi
        done
    ) &
    MONITOR_PID=$!
    echo $MONITOR_PID > "$LOG_DIR/monitor.pid"


main() 
    trap cleanup SIGINT SIGTRM XIT
    
    > "$SYSTM_LOG"
    > "$PYTHON_LOG"
    > "$RUST_LOG"
    
    show_status
    check_prerequisites
    setup_environment
    start_python_cognition
    monitor_system
    
    echo -e "$GRN"
    echo "🚀 Multi-WebSocket System Live"
    echo "=================================="
    echo "✅ Python Multi-eed: ackground"
    echo "✅ OKX Rust ecutor: oreground"
    echo "✅ GPU Acceleration: Active"
    echo "✅ WebSocket eeds:  Redundancy"
    echo "✅ Real-time Data: Multi-Source"
    echo "✅ Signal Processing: nhanced"
    echo -e "$NC"
    
    log "🚀 Multi-WebSocket System Live - nhanced startup complete"
    log "📊 eed monitoring: OKX + inance + Kraken + Coinbase"
    
    start_rust_eecution


if [[ "$:-" == "-h" ]] || [[ "$:-" == "--help" ]]; then
    echo "Multi-WebSocket HT System Pipeline Launcher"
    echo ""
    echo "Usage: $ [MOD]"
    echo ""
    echo "Modes:"
    echo "  dry   - Simulation mode (default)"
    echo "  live  - Live trading mode"
    echo ""
    echo "eatures:"
    echo "  •  WebSocket feed redundancy"
    echo "  • OKX-focused eecution"
    echo "  • Sub-μs targeting"
    echo "  • Multi-echange price aggregation"
    echo ""
    eit 
fi

if [[ "$MOD" != "dry" ]] && [[ "$MOD" != "live" ]]; then
    echo -e "$RD❌ Invalid mode: $MOD$NC"
    echo "Valid modes: dry, live"
    eit 
fi

main "$@"
