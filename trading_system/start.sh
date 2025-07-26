#!/bin/bash
echo "🚀 Starting Unified Trading System..."

cd "$(dirname "$0")"
source venv/bin/activate

# Load environment
export $(grep -v '^#' config/.env | xargs) 2>/dev/null || true

echo "📄 Mode: ${MODE:-paper}"
python unified_trading_system.py --mode ${MODE:-paper}
