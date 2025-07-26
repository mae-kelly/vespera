#!/bin/bash
# Simple monitor that works on macOS

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

check_python() {
    pgrep -f "python.*main.py" >/dev/null 2>&1
}

check_signals() {
    [[ -f "/tmp/signal.json" ]] && [[ $(find /tmp/signal.json -mmin -2 2>/dev/null | wc -l) -gt 0 ]]
}

restart_python() {
    echo "Restarting Python..."
    pkill -f "python.*main.py" 2>/dev/null || true
    sleep 2
    
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    fi
    
    nohup python3 main.py > logs/main.log 2>&1 &
    sleep 3
    check_python
}

case "${1:-status}" in
    status)
        echo "=== System Status ==="
        echo "Python: $(check_python && echo "✅ Running" || echo "❌ Stopped")"
        echo "Signals: $(check_signals && echo "✅ Fresh" || echo "❌ Stale")"
        ;;
    monitor)
        echo "Starting simple monitor..."
        while true; do
            if check_python; then
                echo "$(date '+%H:%M:%S') - System OK"
            else
                echo "$(date '+%H:%M:%S') - Restarting..."
                restart_python
            fi
            sleep 30
        done
        ;;
    restart)
        restart_python && echo "✅ Restarted" || echo "❌ Failed"
        ;;
    *)
        echo "Usage: $0 [status|monitor|restart]"
        ;;
esac
