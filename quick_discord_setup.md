# Quick Discord Setup (2 minutes)

## Option 1: Create Your Own Private Server (Recommended)

1. **Open Discord** (web, desktop, or mobile)
2. **Click the "+"** in the left sidebar
3. **Select "Create My Own"**
4. **Choose "For me and my friends"**
5. **Name it**: "Trading Alerts" 
6. **Create one channel**: #alerts
7. **Right-click #alerts** → Edit Channel → Integrations → Webhooks
8. **Click "New Webhook"**
9. **Copy the Webhook URL**
10. **Paste it into your .env file** as DISCORD_WEBHOOK_URL

## Option 2: Use Any Existing Discord Server

1. **Go to any Discord server** you're already in
2. **Find a channel** you can use (or create #trading-alerts)
3. **Right-click the channel** → Edit Channel → Integrations → Webhooks
4. **Create webhook and copy URL**

## Option 3: Skip Discord for Now

If you want to skip Discord notifications:
1. Leave DISCORD_WEBHOOK_URL as placeholder
2. The system will still work, just without notifications
3. You'll see warnings but trading will function

## Test Your Setup

After adding webhook URL to .env:
```bash
./validate_env_connections.sh
```

You should see a test message in your Discord channel!
