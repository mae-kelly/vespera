import websocket
import json
import threading
import time
import logging
import requests
from collections import deque
from typing import Dict, List, Optional

class RealTimeMarketData:
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=100), "ETH": deque(maxlen=100), "SOL": deque(maxlen=100)}
        self.volumes = {"BTC": deque(maxlen=100), "ETH": deque(maxlen=100), "SOL": deque(maxlen=100)}
        self.current_prices = {}
        self.running = True
        self.data_lock = threading.Lock()
        self.last_update = {}  # Track last update times
        
        # Start WebSocket feeds
        self._start_binance_websocket()
        self._start_coinbase_websocket()
        
        logging.info("Real-time market data engine started")
    
    def _start_binance_websocket(self):
        """Binance WebSocket for price data"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'stream' in data and 'data' in data:
                    stream_data = data['data']
                    symbol = stream_data.get('s', '')
                    price = float(stream_data.get('c', 0))
                    volume = float(stream_data.get('v', 0))
                    
                    # Map symbols
                    symbol_map = {'BTCUSDT': 'BTC', 'ETHUSDT': 'ETH', 'SOLUSDT': 'SOL'}
                    if symbol in symbol_map:
                        asset = symbol_map[symbol]
                        with self.data_lock:
                            self.prices[asset].append(price)
                            self.volumes[asset].append(volume)
                            self.current_prices[asset] = price
                            self.last_update[asset] = time.time()
            except Exception as e:
                logging.error(f"Binance WebSocket error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Binance WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            if self.running:
                time.sleep(5)
                self._start_binance_websocket()
        
        def run_binance():
            ws_url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker"
            ws = websocket.WebSocketApp(ws_url,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            ws.run_forever()
        
        threading.Thread(target=run_binance, daemon=True).start()
    
    def _start_coinbase_websocket(self):
        """Coinbase Pro WebSocket as backup"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'ticker':
                    product_id = data.get('product_id', '')
                    price = float(data.get('price', 0))
                    volume = float(data.get('volume_24h', 0))
                    
                    symbol_map = {'BTC-USD': 'BTC', 'ETH-USD': 'ETH', 'SOL-USD': 'SOL'}
                    if product_id in symbol_map:
                        asset = symbol_map[product_id]
                        with self.data_lock:
                            if not self.prices[asset] or time.time() % 2 == 0:  # Use as backup
                                self.prices[asset].append(price)
                                self.volumes[asset].append(volume)
                                self.current_prices[asset] = price
                                self.last_update[asset] = time.time()
            except Exception as e:
                logging.error(f"Coinbase WebSocket error: {e}")
        
        def run_coinbase():
            ws_url = "wss://ws-feed.exchange.coinbase.com"
            ws = websocket.WebSocketApp(ws_url, on_message=on_message)
            
            def on_open(ws):
                subscribe = {
                    "type": "subscribe",
                    "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD"],
                    "channels": ["ticker"]
                }
                ws.send(json.dumps(subscribe))
            
            ws.on_open = on_open
            ws.run_forever()
        
        threading.Thread(target=run_coinbase, daemon=True).start()
    
    def get_recent_data(self, symbol: str, length: int = 50) -> Dict:
        """Get recent price data for signal generation"""
        with self.data_lock:
            if symbol not in self.prices or len(self.prices[symbol]) < 10:
                return {"valid": False, "prices": [], "volumes": []}
            
            return {
                "valid": True,
                "prices": list(self.prices[symbol])[-length:],
                "volumes": list(self.volumes[symbol])[-length:],
                "current_price": self.current_prices.get(symbol, 0)
            }
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> float:
        """Calculate RSI from real price data"""
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
        """Get system health status - REQUIRED METHOD"""
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
            sufficient_data = all(health_data[asset]['price_count'] >= 10 for asset in health_data)
            
            system_status = 'LIVE' if all_fresh and sufficient_data else 'WARMING_UP'
            
            return {
                'system': {
                    'status': system_status,
                    'all_symbols_live': all_fresh,
                    'sufficient_history': sufficient_data,
                    'timestamp': current_time
                },
                'assets': health_data
            }
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get current live price"""
        with self.data_lock:
            if symbol not in self.current_prices:
                raise RuntimeError("Production error: None return not allowed")
            
            return {
                'price': self.current_prices[symbol],
                'volume': self.volumes[symbol][-1] if self.volumes[symbol] else 0,
                'source': 'live_websocket',
                'timestamp': self.last_update.get(symbol, time.time())
            }
    
    def get_price_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get price history"""
        with self.data_lock:
            if symbol not in self.prices:
                raise RuntimeError("Production error: Empty return not allowed")
            return list(self.prices[symbol])[-length:]
    
    def get_volume_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get volume history"""
        with self.data_lock:
            if symbol not in self.volumes:
                raise RuntimeError("Production error: Empty return not allowed")
            return list(self.volumes[symbol])[-length:]
    
    def calculate_vwap(self, symbol: str) -> Optional[float]:
        """Calculate VWAP"""
        prices = self.get_price_history(symbol, 20)
        volumes = self.get_volume_history(symbol, 20)
        
        if len(prices) < 10 or len(volumes) < 10:
            raise RuntimeError("Production error: None return not allowed")
        
        min_len = min(len(prices), len(volumes))
        prices = prices[-min_len:]
        volumes = volumes[-min_len:]
        
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        
        if total_volume == 0:
            raise RuntimeError("Production error: None return not allowed")
        
        return total_pv / total_volume
    
    def stop(self):
        self.running = False

# Global instance
market_data_engine = RealTimeMarketData()

def get_live_engine():
    return market_data_engine
