#!/bin/bash
# Setup production environment variables

echo "🔴 SETTING UP PRODUCTION ENVIRONMENT"

# Force production mode
export MODE=live
export OKX_TESTNET=false

# Check for required API keys
if [ -z "$OKX_API_KEY" ]; then
    echo "❌ CRITICAL: OKX_API_KEY must be set for production"
    echo "export OKX_API_KEY=your_api_key"
    exit 1
fi

if [ -z "$OKX_SECRET_KEY" ]; then
    echo "❌ CRITICAL: OKX_SECRET_KEY must be set for production"
    echo "export OKX_SECRET_KEY=your_secret_key"
    exit 1
fi

if [ -z "$OKX_PASSPHRASE" ]; then
    echo "❌ CRITICAL: OKX_PASSPHRASE must be set for production"
    echo "export OKX_PASSPHRASE=your_passphrase"
    exit 1
fi

# Optional Discord notifications
if [ -z "$DISCORD_WEBHOOK_URL" ]; then
    echo "⚠️  WARNING: Discord webhook not configured"
    echo "export DISCORD_WEBHOOK_URL=your_webhook (optional)"
fi

echo "✅ Production environment validated"
echo "🔴 LIVE TRADING MODE ACTIVE"
