#!/bin/bash

set -e

echo "🔐 VALIDATING .env CONFIGURATION & DISCORD CONNECTIONS"
echo "====================================================="

# Load environment variables
if [[ -f ".env" ]]; then
    source .env
    echo "✅ Loaded .env file"
else
    echo "❌ No .env file found!"
    echo "   Create .env file with:"
    echo "   cp .env.production .env"
    echo "   # Then edit with your real credentials"
    exit 1
fi

echo ""
echo "🔍 CHECKING REQUIRED ENVIRONMENT VARIABLES"
echo "=========================================="

# Check all required variables (Discord instead of Telegram)
required_vars=(
    "OKX_API_KEY"
    "OKX_SECRET_KEY" 
    "OKX_PASSPHRASE"
    "DISCORD_WEBHOOK_URL"
)

missing_vars=()
placeholder_vars=()

for var in "${required_vars[@]}"; do
    value="${!var}"
    if [[ -z "$value" ]]; then
        missing_vars+=("$var")
    elif [[ "$value" == *"your_"* ]] || [[ "$value" == *"_here" ]]; then
        placeholder_vars+=("$var")
    else
        echo "✅ $var: ${value:0:20}... (configured)"
    fi
done

# Check optional Discord user ID
if [[ -n "$DISCORD_USER_ID" ]] && [[ "$DISCORD_USER_ID" != *"your_"* ]]; then
    echo "✅ DISCORD_USER_ID: ${DISCORD_USER_ID} (mentions enabled)"
else
    echo "ℹ️ DISCORD_USER_ID: Not set (mentions disabled)"
fi

if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo ""
    echo "❌ MISSING VARIABLES:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
fi

if [[ ${#placeholder_vars[@]} -gt 0 ]]; then
    echo ""
    echo "❌ PLACEHOLDER VALUES DETECTED:"
    for var in "${placeholder_vars[@]}"; do
        echo "   - $var: ${!var}"
    done
fi

if [[ ${#missing_vars[@]} -gt 0 ]] || [[ ${#placeholder_vars[@]} -gt 0 ]]; then
    echo ""
    echo "❌ Fix .env configuration before proceeding!"
    exit 1
fi

echo ""
echo "🧪 TESTING ACTUAL CONNECTIONS"
echo "============================="

python3 validate_env_connections_discord.py

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 DISCORD INTEGRATION VALIDATED SUCCESSFULLY!"
    echo "=============================================="
    echo "✅ All API connections working"
    echo "✅ Authentication successful"
    echo "✅ Market data accessible"
    echo "💬 Discord notifications working with rich embeds"
    echo ""
    echo "🚀 System ready for production deployment!"
    echo "   Run: ./deploy_production.sh"
else
    echo ""
    echo "❌ VALIDATION FAILED!"
    echo "===================="
    echo ""
    echo "🔧 DISCORD SETUP GUIDE:"
    echo ""
    echo "1. Create Discord Webhook:"
    echo "   - Go to your Discord server"
    echo "   - Server Settings > Integrations > Webhooks"
    echo "   - Click 'New Webhook'"
    echo "   - Name it 'HFT Trading Bot'"
    echo "   - Copy webhook URL to DISCORD_WEBHOOK_URL"
    echo ""
    echo "2. Get Your User ID (for mentions):"
    echo "   - Enable Developer Mode in Discord settings"
    echo "   - Right-click your username > Copy ID"
    echo "   - Add to DISCORD_USER_ID (optional)"
    echo ""
    echo "3. Other Issues:"
    echo "   - Check internet connection"
    echo "   - Verify webhook URL format"
    echo "   - Ensure bot has permissions in the channel"
    
    exit 1
fi

# Cleanup
rm -f validate_env_connections_discord.py
