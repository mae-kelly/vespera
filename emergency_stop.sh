#!/bin/bash
# emergency_stop.sh - Immediately halt all trading operations

echo "🚨 MRGNCY STOP - HALTING ALL TRADING"
echo "======================================="

# Kill all Python processes related to HT
echo "🛑 Stopping Python signal generators..."
pkill -f "main.py" >/dev/null
pkill -f "signal_engine" >/dev/null
pkill -f "hft" >/dev/null

# Kill all Rust processes
echo "🛑 Stopping Rust eecutors..."
pkill -f "target.*debug|target.*release" >/dev/null
pkill -f "cargo run" >/dev/null

# Remove signal files to prevent new trades
echo "🛑 Removing signal files..."
rm -f /tmp/signal.json >/dev/null
rm -f /tmp/fills.json >/dev/null

# Create emergency stop marker
touch /tmp/MRGNCY_STOP
echo "MRGNCY_STOP_$(date)" > /tmp/MRGNCY_STOP

# Log emergency stop
mkdir -p logs
echo "$(date): MRGNCY STOP XCUTD" >> logs/emergency_stop.log

echo ""
echo "🚨 MRGNCY STOP COMPLT"
echo "✅ All trading processes terminated"
echo "✅ Signal files removed"
echo "✅ mergency marker created"
echo ""
echo "⚠️  Check your echange for any open positions"
echo "⚠️  Manually close positions if needed"
echo ""
echo "To restart: Remove /tmp/MRGNCY_STOP and run ./start_production.sh"
