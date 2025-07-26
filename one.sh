#!/bin/bash
set -euo pipefail

echo "⚡ QUICK START - UNIFIED TRADING SYSTEM"
echo "======================================"

# Run the fixed reorganization
echo "🔄 Step 1: Reorganizing repository..."
if [ -f "01_reorganize_repo_fixed.sh" ]; then
    bash 01_reorganize_repo_fixed.sh
else
    echo "❌ Reorganization script not found"
    echo "Please create the script from the artifact above"
    exit 1
fi

# Navigate to trading system
cd trading_system

echo ""
echo "🔧 Step 2: Setting up environment..."
bash setup.sh

echo ""
echo "🧪 Step 3: Testing system..."
python test_system.py

echo ""
echo "⚙️  Step 4: Configuration check..."
if grep -q "your_okx_api_key_here" config/.env; then
    echo "⚠️  Please configure your API keys in config/.env"
    echo ""
    echo "📝 Required configuration:"
    echo "1. Edit config/.env"
    echo "2. Set OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE"
    echo "3. Keep MODE=paper for testing"
    echo ""
    echo "🚀 After configuration, run: bash start.sh"
else
    echo "✅ Configuration appears to be set"
    echo ""
    echo "🎯 Starting unified trading system..."
    bash start.sh
fi

echo ""
echo "🎉 QUICK START COMPLETE!"
echo "======================="
echo "✅ Repository reorganized"
echo "✅ Environment set up"
echo "✅ Basic tests passed"
echo ""
echo "📊 To monitor the system:"
echo "   - Watch the console output"
echo "   - Check data/logs/ for detailed logs"
echo "   - Use Ctrl+C to stop"
echo ""
echo "🔄 The system combines:"
echo "   📈 HFT Shorting (crypto short opportunities)"
echo "   👁️  Wallet Mimic (following successful wallets)"
echo ""
echo "⚠️  IMPORTANT: Start with paper trading mode!"