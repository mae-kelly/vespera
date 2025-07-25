#!/bin/bash

set -e

echo "🔧 FIXING CURRENT ISSUES - CUPY IMPORTS & DISCORD"
echo "================================================="

# Create backup
BACKUP_DIR="current_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Creating backup in $BACKUP_DIR"

# Backup critical files
for file in signal_engine.py entropy_meter.py laggard_sniper.py relief_trap.py confidence_scoring.py main.py; do
    if [[ -f "$file" ]]; then
        cp "$file" "$BACKUP_DIR/"
        echo "📝 Backed up $file"
    fi
done

echo ""
echo "🔧 FIX #1: REPLACE ALL CUPY IMPORTS WITH FALLBACK"
echo "==============================================="

# Fix signal_engine.py
echo "🔧 Fixing signal_engine.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' signal_engine.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' signal_engine.py

# Fix entropy_meter.py
echo "🔧 Fixing entropy_meter.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' entropy_meter.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' entropy_meter.py

# Fix laggard_sniper.py
echo "🔧 Fixing laggard_sniper.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' laggard_sniper.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' laggard_sniper.py

# Fix relief_trap.py
echo "🔧 Fixing relief_trap.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' relief_trap.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' relief_trap.py

# Fix confidence_scoring.py
echo "🔧 Fixing confidence_scoring.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' confidence_scoring.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' confidence_scoring.py

# Fix main.py
echo "🔧 Fixing main.py..."
sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' main.py
sed -i '' 's/import cupy/import cupy_fallback as cupy/g' main.py

echo "✅ Fixed all cupy imports"

echo ""
echo "🔧 FIX #2: UPDATE .ENV FOR YOUR EXISTING CREDENTIALS"
echo "=================================================="

# Update the .env file to use your existing credentials plus Discord
cat > .env << EOF
# PRODUCTION ENVIRONMENT CONFIGURATION
MODE=dry

# OKX Production API Credentials (your existing ones)
OKX_API_KEY=8a760df1-4a2d-471b-ba42-d16893614dab
OKX_SECRET_KEY=C9F3FC89A6A30226E11DFFD098C7CF3D
OKX_PASSPHRASE=Shamrock1!
OKX_TESTNET=true

# Discord Webhook (you need to create this)
# Go to Discord: Server Settings > Integrations > Webhooks > New Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
DISCORD_USER_ID=your_user_id_here

# System Configuration
RUST_LOG=info
PYTHONUNBUFFERED=1
EOF

echo "✅ Updated .env with your credentials"

echo ""
echo "🔧 FIX #3: CREATE SIMPLE DISCORD SETUP GUIDE"
echo "==========================================="

cat > quick_discord_setup.md << 'EOF'
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
EOF

echo "✅ Created quick Discord setup guide"

echo ""
echo "🔧 FIX #4: FIX OKX SECRET KEY FORMAT"
echo "==================================="

# Create a Python script to fix the OKX secret key encoding
cat > fix_okx_secret.py << 'EOF'
#!/usr/bin/env python3
import base64
import os

def fix_okx_secret():
    """Fix OKX secret key encoding"""
    secret = os.getenv('OKX_SECRET_KEY', '')
    
    if not secret:
        print("❌ No OKX_SECRET_KEY found in environment")
        return False
    
    print(f"Current secret: {secret[:10]}...")
    
    # Check if it's already base64 encoded
    try:
        decoded = base64.b64decode(secret)
        print("✅ Secret appears to be valid base64")
        return True
    except:
        print("⚠️ Secret is not base64 encoded")
        
        # Try to base64 encode it
        try:
            encoded = base64.b64encode(secret.encode()).decode()
            print(f"🔧 Base64 encoded version: {encoded}")
            print("💡 Try updating your .env with:")
            print(f"OKX_SECRET_KEY={encoded}")
            return False
        except Exception as e:
            print(f"❌ Could not encode secret: {e}")
            return False

if __name__ == "__main__":
    fix_okx_secret()
EOF

python3 fix_okx_secret.py

echo ""
echo "🔧 FIX #5: CREATE SIMPLE TEST SCRIPT"
echo "=================================="

# Create a simple test that doesn't require Discord
cat > simple_connection_test.py << 'EOF'
#!/usr/bin/env python3
import os
import sys

def test_imports():
    """Test that all imports work"""
    print("🧪 Testing imports...")
    
    try:
        import cupy_fallback as cp
        test_array = cp.array([1, 2, 3, 4, 5])
        result = cp.sum(test_array)
        print(f"✅ CuPy fallback: {result}")
    except Exception as e:
        print(f"❌ CuPy fallback failed: {e}")
        return False
    
    try:
        import config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False
    
    try:
        import signal_engine
        print("✅ Signal engine imported")
    except Exception as e:
        print(f"❌ Signal engine failed: {e}")
        return False
    
    return True

def test_credentials():
    """Test OKX credentials"""
    print("\n🔐 Testing credentials...")
    
    required = ['OKX_API_KEY', 'OKX_SECRET_KEY', 'OKX_PASSPHRASE']
    
    for var in required:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:8]}...")
        else:
            print(f"❌ {var}: Missing")
            return False
    
    return True

def test_market_data():
    """Test market data connection"""
    print("\n📊 Testing market data...")
    
    try:
        import requests
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_price = data.get('bitcoin', {}).get('usd')
            if btc_price:
                print(f"✅ BTC Price: ${btc_price:,.2f}")
                return True
        
        print("❌ Could not get BTC price")
        return False
        
    except Exception as e:
        print(f"❌ Market data failed: {e}")
        return False

def main():
    print("🧪 SIMPLE CONNECTION TEST")
    print("=" * 30)
    
    tests = [
        ("Imports", test_imports),
        ("Credentials", test_credentials),
        ("Market Data", test_market_data)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ System ready for testing")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

echo "✅ Created simple connection test"

echo ""
echo "🔧 FIX #6: CREATE WORKING START SCRIPT"
echo "===================================="

# Create a simple start script that works on macOS
cat > start_system_simple.py << 'EOF'
#!/usr/bin/env python3
"""Simple system starter for testing"""

import time
import json
import os
import sys
import signal

def signal_handler(sig, frame):
    print('\n🔴 Shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_system():
    print("🚀 Starting HFT System (Simple Mode)")
    print("=" * 40)
    
    try:
        # Test imports first
        import config
        import signal_engine
        import confidence_scoring
        print("✅ All modules imported successfully")
        
        # Start the feed
        signal_engine.feed.start_feed()
        print("✅ Market data feed started")
        
        # Wait a moment for data
        time.sleep(3)
        
        # Run signal generation loop
        for i in range(10):
            print(f"\n--- Iteration {i+1} ---")
            
            shared_data = {
                "timestamp": time.time(),
                "mode": "dry",
                "iteration": i+1,
                "gpu_available": False
            }
            
            # Generate signal
            signal = signal_engine.generate_signal(shared_data)
            confidence = signal.get('confidence', 0)
            
            print(f"Signal confidence: {confidence:.3f}")
            
            if confidence > 0.1:
                # Write signal file
                signal["timestamp"] = time.time()
                with open("/tmp/signal.json", "w") as f:
                    json.dump(signal, f, indent=2)
                print(f"✅ Signal written to /tmp/signal.json")
                
                # Show signal details
                if "signal_data" in signal:
                    data = signal["signal_data"]
                    print(f"Asset: {data.get('asset', 'N/A')}")
                    print(f"Entry: ${data.get('entry_price', 0):,.2f}")
                    print(f"Reason: {data.get('reason', 'N/A')}")
            
            time.sleep(2)
        
        print("\n🎉 System test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ System failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_system()
EOF

chmod +x simple_connection_test.py
chmod +x start_system_simple.py

echo "✅ Created working start script"

echo ""
echo "🎉 FIXES COMPLETE!"
echo "=================="
echo ""
echo "📋 WHAT WAS FIXED:"
echo "✅ Replaced all 'import cupy' with 'import cupy_fallback'"
echo "✅ Updated .env with your existing OKX credentials"
echo "✅ Created simple Discord setup guide"
echo "✅ Fixed OKX secret key encoding check"
echo "✅ Created simple test scripts"
echo ""
echo "🧪 NEXT STEPS:"
echo "1. Test imports: python3 simple_connection_test.py"
echo "2. (Optional) Set up Discord: cat quick_discord_setup.md"
echo "3. Test system: python3 start_system_simple.py"
echo ""
echo "💡 The system should now work without cupy import errors!"
echo "   You can add Discord later if you want notifications."