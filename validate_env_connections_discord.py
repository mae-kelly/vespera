#!/usr/bin/env python3
import os
import sys
import time
import hmac
import hashlib
import base64
import requests
import json
from datetime import datetime

def test_okx_connection():
    """Test actual OKX API connection"""
    print("🔗 Testing OKX API Connection...")
    
    api_key = os.getenv('OKX_API_KEY')
    secret_key = os.getenv('OKX_SECRET_KEY')
    passphrase = os.getenv('OKX_PASSPHRASE')
    
    if not all([api_key, secret_key, passphrase]):
        print("❌ Missing OKX credentials")
        return False
    
    try:
        timestamp = datetime.utcnow().isoformat()[:-3] + 'Z'
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(
                base64.b64decode(secret_key),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json'
        }
        
        url = 'https://www.okx.com/api/v5/account/balance'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ OKX API connection successful")
                
                if data.get('data') and len(data['data']) > 0:
                    details = data['data'][0].get('details', [])
                    for detail in details:
                        if detail.get('ccy') == 'USDT':
                            balance = float(detail.get('eq', 0))
                            print(f"✅ USDT Balance: ${balance:,.2f}")
                            if balance < 100:
                                print("⚠️ WARNING: Low balance for trading")
                            break
                return True
            else:
                print(f"❌ OKX API error: {data.get('msg', 'Unknown error')}")
                return False
        else:
            print(f"❌ OKX HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OKX connection failed: {e}")
        return False

def test_discord_connection():
    """Test Discord webhook connection"""
    print("\n💬 Testing Discord Webhook Connection...")
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    user_id = os.getenv('DISCORD_USER_ID')
    
    if not webhook_url:
        print("❌ Missing Discord webhook URL")
        return False
    
    try:
        # Test webhook with a rich embed
        embed = {
            "title": "🧪 HFT System Connection Test",
            "description": "Discord webhook is working perfectly!",
            "color": 3066993,  # Green
            "fields": [
                {
                    "name": "Status",
                    "value": "✅ Connected",
                    "inline": True
                },
                {
                    "name": "Test Time",
                    "value": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "inline": True
                },
                {
                    "name": "Features",
                    "value": "Rich embeds, mentions, real-time alerts",
                    "inline": False
                }
            ],
            "footer": {
                "text": "HFT Trading System"
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        
        content = ""
        if user_id:
            content = f"<@{user_id}> Discord integration test successful!"
        
        payload = {
            "content": content,
            "embeds": [embed],
            "username": "HFT Trading Bot"
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 204:
            print("✅ Discord webhook working perfectly")
            print("✅ Rich embeds supported")
            if user_id:
                print("✅ User mentions working")
            else:
                print("ℹ️ Add DISCORD_USER_ID for mention support")
            return True
        else:
            print(f"❌ Discord webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Discord connection failed: {e}")
        return False

def test_market_data_connection():
    """Test market data connections"""
    print("\n📊 Testing Market Data Connections...")
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin,ethereum,solana",
            "vs_currencies": "usd"
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_price = data.get('bitcoin', {}).get('usd')
            if btc_price:
                print(f"✅ CoinGecko API: BTC = ${btc_price:,.2f}")
            else:
                print("❌ CoinGecko API: No price data")
                return False
        else:
            print(f"❌ CoinGecko API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CoinGecko connection failed: {e}")
        return False
    
    try:
        import websocket
        
        connection_success = False
        
        def on_open(ws):
            nonlocal connection_success
            print("✅ Binance WebSocket connection successful")
            connection_success = True
            ws.close()
        
        def on_error(ws, error):
            print(f"❌ Binance WebSocket error: {error}")
        
        ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws/stream",
            on_open=on_open,
            on_error=on_error
        )
        
        import threading
        ws_thread = threading.Thread(target=lambda: ws.run_forever())
        ws_thread.daemon = True
        ws_thread.start()
        
        time.sleep(3)
        return connection_success
        
    except Exception as e:
        print(f"❌ Binance WebSocket test failed: {e}")
        return False

def main():
    print("🧪 DISCORD INTEGRATION CONNECTION TESTING")
    print("=" * 50)
    
    results = []
    
    results.append(("OKX API", test_okx_connection()))
    results.append(("Discord Webhook", test_discord_connection()))
    results.append(("Market Data", test_market_data_connection()))
    
    print("\n" + "=" * 50)
    print("📋 CONNECTION TEST RESULTS:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CONNECTIONS SUCCESSFUL!")
        print("✅ Discord integration working perfectly")
        print("💬 Rich notifications with embeds enabled")
        print("🚀 System ready for production deployment")
        return True
    else:
        print("❌ SOME CONNECTIONS FAILED!")
        print("🔧 Fix the failed connections before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
