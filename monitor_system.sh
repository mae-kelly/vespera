#!/bin/bash
set -euo pipefail

check_python() {
    if [[ -f "tmp/python.pid" ]]; then
        PID=$(cat tmp/python.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "✅ Python engine running (PID: $PID)"
            return 0
        fi
    fi
    echo "❌ Python engine stopped"
    return 1
}

check_signals() {
    if [[ -f "/tmp/signal.json" ]]; then
        AGE=$(($(date +%s) - $(stat -c %Y /tmp/signal.json 2>/dev/null || echo 0)))
        if [[ $AGE -lt 60 ]]; then
            echo "✅ Signals fresh (${AGE}s old)"
            return 0
        fi
    fi
    echo "❌ No fresh signals"
    return 1
}

check_rust() {
    if pgrep -f "hft-system" >/dev/null; then
        echo "✅ Rust executor running"
        return 0
    fi
    echo "❌ Rust executor stopped"
    return 1
}

show_latest_signal() {
    if [[ -f "/tmp/signal.json" ]]; then
        CONFIDENCE=$(jq -r '.confidence // 0' /tmp/signal.json 2>/dev/null || echo "0")
        ASSET=$(jq -r '.best_signal.asset // "N/A"' /tmp/signal.json 2>/dev/null || echo "N/A")
        echo "📊 Latest: $ASSET confidence=$CONFIDENCE"
    fi
}

echo "🔍 HFT System Health Check"
echo "========================="
check_python && PYTHON_OK=1 || PYTHON_OK=0
check_signals && SIGNALS_OK=1 || SIGNALS_OK=0
check_rust && RUST_OK=1 || RUST_OK=0
show_latest_signal

if [[ $PYTHON_OK -eq 1 && $SIGNALS_OK -eq 1 && $RUST_OK -eq 1 ]]; then
    echo "🟢 System Status: HEALTHY"
else
    echo "🔴 System Status: DEGRADED"
fi
