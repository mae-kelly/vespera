#!/bin/bash
# emergency_stop.sh - Immediately halt all trading operations

echo "🚨 EMERGENCY STOP - HALTING ALL TRADING"
echo "======================================="

# Kill all Python processes related to HFT
echo "🛑 Stopping Python signal generators..."
pkill -f "main.py" 2>/dev/null
pkill -f "signal_engine" 2>/dev/null
pkill -f "hft" 2>/dev/null

# Kill all Rust processes
echo "🛑 Stopping Rust executors..."
pkill -f "target.*debug\|target.*release" 2>/dev/null
pkill -f "cargo run" 2>/dev/null

# Remove signal files to prevent new trades
echo "🛑 Removing signal files..."
rm -f /tmp/signal.json 2>/dev/null
rm -f /tmp/fills.json 2>/dev/null

# Create emergency stop marker
touch /tmp/EMERGENCY_STOP
echo "EMERGENCY_STOP_$(date)" > /tmp/EMERGENCY_STOP

# Log emergency stop
mkdir -p logs
echo "$(date): EMERGENCY STOP EXECUTED" >> logs/emergency_stop.log

echo ""
echo "🚨 EMERGENCY STOP COMPLETE"
echo "✅ All trading processes terminated"
echo "✅ Signal files removed"
echo "✅ Emergency marker created"
echo ""
echo "⚠️  Check your exchange for any open positions"
echo "⚠️  Manually close positions if needed"
echo ""
echo "To restart: Remove /tmp/EMERGENCY_STOP and run ./start_production.sh"
