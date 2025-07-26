import websocket
import json
import threading
import time
import logging
import requests
from collections import deque
from typing import Dict, List, Optional
import ssl

class OKXMarketData:
    """OKX-only market data engine for both paper and live trading"""
    
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=100), "ETH": deque(maxlen=100), "SOL": deque(maxlen=100)}
        self.volumes = {"BTC": deque(maxlen=100), "ETH": deque(maxlen=100), "SOL": deque(maxlen=100)}
        self.current_prices = {}
        self.current_volumes = {}
        self.running = True
        self.data_lock = threading.Lock()
        self.last_update = {}
        self.connection_status = "connecting"
        
        # OKX WebSocket URL
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/public"
        
        # Start WebSocket connection
        self._start_okx_websocket()
        
        logging.info("🔥 OKX market data engine started")
    
    def _start_okx_websocket(self):
        """Start OKX WebSocket connection"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self._process_okx_message(data)
            except Exception as e:
                logging.error(f"OKX WebSocket message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"OKX WebSocket error: {error}")
            self.connection_status = "error"
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("OKX WebSocket connection closed")
            self.connection_status = "closed"
            if self.running:
                time.sleep(5)
                self._start_okx_websocket()
        
        def on_open(ws):
            logging.info("✅ OKX WebSocket connected")
            self.connection_status = "connected"
            
            # Subscribe to ticker data for BTC, ETH, SOL
            subscribe_message = {
                "op": "subscribe",
                "args": [
                    {"channel": "tickers", "instId": "BTC-USDT"},
                    {"channel": "tickers", "instId": "ETH-USDT"},
                    {"channel": "tickers", "instId": "SOL-USDT"}
                ]
            }
            
            ws.send(json.dumps(subscribe_message))
            logging.info("📡 Subscribed to OKX tickers: BTC, ETH, SOL")
        
        def run_websocket():
            while self.running:
                try:
                    self.ws = websocket.WebSocketApp(
                        self.ws_url,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_close,
                        on_open=on_open
                    )
                    
                    # Configure SSL context
                    self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                    
                except Exception as e:
                    logging.error(f"OKX WebSocket connection failed: {e}")
                    time.sleep(5)
        
        # Start WebSocket in background thread
        ws_thread = threading.Thread(target=run_websocket, daemon=True)
        ws_thread.start()
    
    def _process_okx_message(self, data):
        """Process OKX WebSocket messages"""
        try:
            if data.get("event") == "subscribe":
                logging.info("✅ OKX subscription confirmed")
                return
            
            if "data" not in data:
                return
            
            for item in data["data"]:
                inst_id = item.get("instId", "")
                
                # Map OKX instrument IDs to our asset names
                asset_map = {
                    "BTC-USDT": "BTC",
                    "ETH-USDT": "ETH", 
                    "SOL-USDT": "SOL"
                }
                
                if inst_id in asset_map:
                    asset = asset_map[inst_id]
                    
                    # Extract price and volume data
                    last_price = float(item.get("last", 0))
                    volume_24h = float(item.get("vol24h", 0))
                    
                    if last_price > 0:
                        with self.data_lock:
                            self.prices[asset].append(last_price)
                            self.volumes[asset].append(volume_24h)
                            self.current_prices[asset] = last_price
                            self.current_volumes[asset] = volume_24h
                            self.last_update[asset] = time.time()
                            
                            if self.connection_status != "live":
                                self.connection_status = "live"
                                logging.info("🔥 OKX market data is now LIVE")
                        
        except Exception as e:
            logging.error(f"Error processing OKX message: {e}")
    
    def get_recent_data(self, symbol: str, length: int = 50) -> Dict:
        """Get recent price data for signal generation"""
        with self.data_lock:
            if symbol not in self.prices or len(self.prices[symbol]) < 5:
                return {"valid": False, "prices": [], "volumes": []}
            
            return {
                "valid": True,
                "prices": list(self.prices[symbol])[-length:],
                "volumes": list(self.volumes[symbol])[-length:],
                "current_price": self.current_prices.get(symbol, 0)
            }
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> float:
        """Calculate RSI from OKX price data"""
        data = self.get_recent_data(symbol, period + 10)
        if not data["valid"] or len(data["prices"]) < period + 1:
            return 50.0
        
        prices = data["prices"]
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, change) for change in changes]
        losses = [max(0, -change) for change in changes]
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_system_health(self) -> Dict:
        """Get system health status"""
        with self.data_lock:
            current_time = time.time()
            health_data = {}
            
            # Check each asset
            for asset in ['BTC', 'ETH', 'SOL']:
                last_update = self.last_update.get(asset, 0)
                age = current_time - last_update
                has_data = len(self.prices[asset]) > 0
                is_fresh = age < 60  # Fresh if updated within 60 seconds
                
                health_data[asset] = {
                    'has_data': has_data,
                    'data_age_seconds': age,
                    'is_fresh': is_fresh,
                    'price_count': len(self.prices[asset]),
                    'current_price': self.current_prices.get(asset, 0)
                }
            
            # Overall system status
            all_fresh = all(health_data[asset]['is_fresh'] for asset in health_data)
            sufficient_data = all(health_data[asset]['price_count'] >= 5 for asset in health_data)
            
            if self.connection_status == "live" and all_fresh and sufficient_data:
                system_status = 'LIVE'
            elif self.connection_status == "connected" or (sufficient_data and not all_fresh):
                system_status = 'WARMING_UP'
            else:
                system_status = 'CONNECTING'
            
            return {
                'system': {
                    'status': system_status,
                    'connection_status': self.connection_status,
                    'all_symbols_live': all_fresh,
                    'sufficient_history': sufficient_data,
                    'timestamp': current_time
                },
                'assets': health_data
            }
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get current live price from OKX"""
        with self.data_lock:
            if symbol not in self.current_prices:
                # Fallback to REST API if WebSocket data not available
                return self._get_price_from_rest_api(symbol)
            
            return {
                'price': self.current_prices[symbol],
                'volume': self.current_volumes.get(symbol, 0),
                'source': 'okx_websocket',
                'timestamp': self.last_update.get(symbol, time.time())
            }
    
    def _get_price_from_rest_api(self, symbol: str) -> Optional[Dict]:
        """Fallback to OKX REST API for price data"""
        try:
            # OKX REST API endpoint
            inst_id = f"{symbol}-USDT"
            url = f"https://www.okx.com/api/v5/market/ticker?instId={inst_id}"
            
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("code") == "0" and data.get("data"):
                ticker = data["data"][0]
                price = float(ticker.get("last", 0))
                volume = float(ticker.get("vol24h", 0))
                
                if price > 0:
                    # Update our cache
                    with self.data_lock:
                        self.current_prices[symbol] = price
                        self.current_volumes[symbol] = volume
                        self.last_update[symbol] = time.time()
                    
                    return {
                        'price': price,
                        'volume': volume,
                        'source': 'okx_rest_api',
                        'timestamp': time.time()
                    }
            
        except Exception as e:
            logging.error(f"OKX REST API error for {symbol}: {e}")
        
        return None
    
    def get_price_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get price history from OKX data"""
        with self.data_lock:
            if symbol not in self.prices:
                return []
            return list(self.prices[symbol])[-length:]
    
    def get_volume_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get volume history from OKX data"""
        with self.data_lock:
            if symbol not in self.volumes:
                return []
            return list(self.volumes[symbol])[-length:]
    
    def calculate_vwap(self, symbol: str) -> Optional[float]:
        """Calculate VWAP from OKX data"""
        prices = self.get_price_history(symbol, 20)
        volumes = self.get_volume_history(symbol, 20)
        
        if len(prices) < 10 or len(volumes) < 10:
            return None
        
        min_len = min(len(prices), len(volumes))
        prices = prices[-min_len:]
        volumes = volumes[-min_len:]
        
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        
        if total_volume == 0:
            return None
        
        return total_pv / total_volume
    
    def get_okx_account_balance(self, api_key: str, secret_key: str, passphrase: str) -> Optional[float]:
        """Get account balance from OKX (for live trading)"""
        try:
            import hmac
            import base64
            from datetime import datetime
            
            # OKX API authentication
            timestamp = datetime.utcnow().isoformat() + 'Z'
            method = 'GET'
            request_path = '/api/v5/account/balance'
            body = ''
            
            message = timestamp + method + request_path + body
            signature = base64.b64encode(
                hmac.new(
                    base64.b64decode(secret_key),
                    message.encode('utf-8'),
                    hmac.sha256
                ).digest()
            ).decode()
            
            headers = {
                'OK-ACCESS-KEY': api_key,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': passphrase,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://www.okx.com' + request_path,
                headers=headers,
                timeout=10
            )
            
            data = response.json()
            
            if data.get("code") == "0" and data.get("data"):
                account_data = data["data"][0]
                details = account_data.get("details", [])
                
                for detail in details:
                    if detail.get("ccy") == "USDT":
                        balance = float(detail.get("eq", 0))
                        return balance
            
        except Exception as e:
            logging.error(f"Error getting OKX account balance: {e}")
        
        return None
    
    def stop(self):
        """Stop the market data engine"""
        self.running = False
        if hasattr(self, 'ws'):
            self.ws.close()
        logging.info("🛑 OKX market data engine stopped")

# Global instance
okx_market_data = OKXMarketData()

def get_okx_engine():
    """Get the global OKX market data engine"""
    return okx_market_data