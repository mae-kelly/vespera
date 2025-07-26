#!/bin/bash
# Setup production environment variables

echo "🔴 STTING UP PRODUCTION NVIRONMNT"

# orce production mode
eport MOD=live
eport OKX_TSTNT=false

# Check for required API keys
if [ -z "$OKX_API_KY" ]; then
    echo "❌ CRITICAL: OKX_API_KY must be set for production"
    echo "eport OKX_API_KY=your_api_key"
    eit 
fi

if [ -z "$OKX_SCRT_KY" ]; then
    echo "❌ CRITICAL: OKX_SCRT_KY must be set for production"
    echo "eport OKX_SCRT_KY=your_secret_key"
    eit 
fi

if [ -z "$OKX_PASSPHRAS" ]; then
    echo "❌ CRITICAL: OKX_PASSPHRAS must be set for production"
    echo "eport OKX_PASSPHRAS=your_passphrase"
    eit 
fi

# Optional Discord notifications
if [ -z "$DISCORD_WHOOK_URL" ]; then
    echo "⚠️  WARNING: Discord webhook not configured"
    echo "eport DISCORD_WHOOK_URL=your_webhook (optional)"
fi

echo "✅ Production environment validated"
echo "🔴 LIV TRADING MOD ACTIV"
