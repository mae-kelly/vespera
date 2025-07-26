#!/usr/bin/env python3
"""
Live Market Data Engine for HFT System
ZERO MOCK DATA - Only real market feeds
Uses WebSocket connections to multiple exchanges for live data
"""

import websocket
import json
import threading
import time
import logging
from collections import deque
from typing import Dict, List, Optional
import ssl

class LiveMarketEngine:
    def __init__(self):
        self.live_prices = {}
        self.price_history = {
            "BTC": deque(maxlen=200),
            "ETH": deque(maxlen=200), 
            "SOL": deque(maxlen=200)
        }
        self.volume_history = {
            "BTC": deque(maxlen=200),
            "ETH": deque(maxlen=200),
            "SOL": deque(maxlen=200)
        }
        self.last_trades = {}
        self.websockets = {}
        self.running = True
        self.data_lock = threading.Lock()
        
        # Track data freshness
        self.last_update = {}
        
        # Start live connections
        self._start_binance_stream()
        self._start_coinbase_stream()
        
        logging.info("🔴 LIVE MARKET ENGINE STARTED - ZERO MOCK DATA")
    
    def _start_binance_stream(self):
        """Start Binance WebSocket stream for real-time data"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Handle different message types
                if 'stream' in data:
                    stream_data = data['data']
                    symbol_raw = stream_data.get('s', '')
                    
                    if symbol_raw.endswith('USDT'):
                        symbol = symbol_raw.replace('USDT', '')
                        
                        if symbol in ['BTC', 'ETH', 'SOL']:
                            price = float(stream_data.get('c', 0))  # Current price
                            volume = float(stream_data.get('v', 0))  # 24h volume
                            
                            if price > 0:
                                with self.data_lock:
                                    self.live_prices[symbol] = {
                                        'price': price,
                                        'volume': volume,
                                        'source': 'binance',
                                        'timestamp': time.time(),
                                        'change_24h': float(stream_data.get('P', 0))
                                    }
                                    
                                    # Add to history
                                    self.price_history[symbol].append(price)
                                    self.volume_history[symbol].append(volume)
                                    self.last_update[symbol] = time.time()
                                    
                                logging.info(f"📈 LIVE {symbol}: ${price:,.2f} (Binance)")
                
            except Exception as e:
                logging.error(f"Binance message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Binance WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Binance WebSocket closed, reconnecting...")
            time.sleep(5)
            if self.running:
                self._start_binance_stream()
        
        def on_open(ws):
            logging.info("🔴 Binance WebSocket connected - LIVE DATA ACTIVE")
            # Subscribe to 24hr ticker streams
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@ticker",
                    "ethusdt@ticker", 
                    "solusdt@ticker"
                ],
                "id": 1
            }
            ws.send(json.dumps(subscribe_msg))
        
        # Create WebSocket connection
        binance_url = "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker"
        
        def run_binance():
            ws = websocket.WebSocketApp(
                binance_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.websockets['binance'] = ws
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        
        binance_thread = threading.Thread(target=run_binance, daemon=True)
        binance_thread.start()
    
    def _start_coinbase_stream(self):
        """Start Coinbase WebSocket for additional live data"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                if data.get('type') == 'ticker':
                    product_id = data.get('product_id', '')
                    
                    symbol_map = {
                        'BTC-USD': 'BTC',
                        'ETH-USD': 'ETH', 
                        'SOL-USD': 'SOL'
                    }
                    
                    symbol = symbol_map.get(product_id)
                    if symbol:
                        price = float(data.get('price', 0))
                        volume = float(data.get('volume_24h', 0))
                        
                        if price > 0:
                            with self.data_lock:
                                # Only update if we don't have fresher Binance data
                                current_data = self.live_prices.get(symbol, {})
                                if (not current_data or 
                                    current_data.get('source') != 'binance' or
                                    time.time() - current_data.get('timestamp', 0) > 2):
                                    
                                    self.live_prices[symbol] = {
                                        'price': price,
                                        'volume': volume,
                                        'source': 'coinbase',
                                        'timestamp': time.time(),
                                        'change_24h': 0  # Coinbase doesn't provide this easily
                                    }
                                    
                                    self.price_history[symbol].append(price)
                                    self.volume_history[symbol].append(volume)
                                    self.last_update[symbol] = time.time()
                                    
                            logging.info(f"📊 LIVE {symbol}: ${price:,.2f} (Coinbase)")
                
            except Exception as e:
                logging.error(f"Coinbase message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Coinbase WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Coinbase WebSocket closed, reconnecting...")
            time.sleep(5)
            if self.running:
                self._start_coinbase_stream()
        
        def on_open(ws):
            logging.info("🔴 Coinbase WebSocket connected - LIVE DATA ACTIVE")
            subscribe_msg = {
                "type": "subscribe",
                "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD"],
                "channels": ["ticker"]
            }
            ws.send(json.dumps(subscribe_msg))
        
        def run_coinbase():
            ws = websocket.WebSocketApp(
                "wss://ws-feed.exchange.coinbase.com",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.websockets['coinbase'] = ws
            ws.run_forever()
        
        coinbase_thread = threading.Thread(target=run_coinbase, daemon=True)
        coinbase_thread.start()
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get current live price - NO FALLBACK, NO MOCK DATA"""
        with self.data_lock:
            if symbol not in self.live_prices:
                return None
            
            data = self.live_prices[symbol].copy()
            
            # Check data freshness - reject stale data
            age = time.time() - data.get('timestamp', 0)
            if age > 10:  # Data older than 10 seconds is stale
                logging.warning(f"⚠️ Stale data for {symbol} ({age:.1f}s old) - rejecting")
                return None
            
            return data
    
    def get_price_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get recent price history - REAL DATA ONLY"""
        with self.data_lock:
            history = list(self.price_history[symbol])
            
            if len(history) < 5:
                logging.warning(f"⚠️ Insufficient price history for {symbol}: {len(history)} points")
                return []
            
            return history[-length:] if len(history) >= length else history
    
    def get_volume_history(self, symbol: str, length: int = 50) -> List[float]:
        """Get recent volume history - REAL DATA ONLY"""
        with self.data_lock:
            history = list(self.volume_history[symbol])
            
            if len(history) < 5:
                logging.warning(f"⚠️ Insufficient volume history for {symbol}: {len(history)} points")
                return []
            
            return history[-length:] if len(history) >= length else history
    
    def calculate_rsi(self, symbol: str, period: int = 14) -> Optional[float]:
        """Calculate RSI from REAL price data only"""
        prices = self.get_price_history(symbol, period + 10)
        
        if len(prices) < period + 1:
            logging.warning(f"⚠️ Insufficient data for RSI calculation: {len(prices)} < {period + 1}")
            return None
        
        # Calculate price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        if len(gains) < period:
            return None
        
        # Calculate average gains and losses
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_vwap(self, symbol: str) -> Optional[float]:
        """Calculate VWAP from REAL data only"""
        prices = self.get_price_history(symbol, 20)
        volumes = self.get_volume_history(symbol, 20)
        
        if len(prices) < 5 or len(volumes) < 5:
            logging.warning(f"⚠️ Insufficient data for VWAP: prices={len(prices)}, volumes={len(volumes)}")
            return None
        
        # Ensure same length
        min_len = min(len(prices), len(volumes))
        prices = prices[-min_len:]
        volumes = volumes[-min_len:]
        
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        
        if total_volume == 0:
            return None
        
        return total_pv / total_volume
    
    def is_data_live(self, symbol: str) -> bool:
        """Check if we have fresh live data"""
        if symbol not in self.last_update:
            return False
        
        age = time.time() - self.last_update[symbol]
        return age < 15  # Data is live if updated within 15 seconds
    
    def get_system_health(self) -> Dict:
        """Get system health - only report on LIVE data"""
        with self.data_lock:
            health = {}
            
            for symbol in ['BTC', 'ETH', 'SOL']:
                live_data = self.get_live_price(symbol)
                price_history_len = len(self.price_history[symbol])
                is_live = self.is_data_live(symbol)
                
                health[symbol] = {
                    'has_live_data': live_data is not None,
                    'price_history_length': price_history_len,
                    'is_live': is_live,
                    'last_price': live_data['price'] if live_data else None,
                    'source': live_data['source'] if live_data else None,
                    'data_age_seconds': time.time() - self.last_update.get(symbol, 0)
                }
            
            # Overall system health
            all_live = all(health[s]['is_live'] for s in health)
            sufficient_history = all(health[s]['price_history_length'] >= 10 for s in health)
            
            health['system'] = {
                'all_symbols_live': all_live,
                'sufficient_history': sufficient_history,
                'websocket_connections': len(self.websockets),
                'status': 'LIVE' if all_live and sufficient_history else 'DEGRADED'
            }
            
            return health
    
    def stop(self):
        """Stop all live connections"""
        self.running = False
        
        for name, ws in self.websockets.items():
            try:
                ws.close()
                logging.info(f"Closed {name} WebSocket")
            except:
                pass
        
        logging.info("🔴 Live Market Engine stopped")

# Global instance
live_engine = None

def initialize_live_engine():
    """Initialize the live market engine"""
    global live_engine
    if live_engine is None:
        live_engine = LiveMarketEngine()
        
        # Wait for initial data
        logging.info("⏳ Waiting for live market data...")
        for i in range(30):  # Wait up to 30 seconds
            health = live_engine.get_system_health()
            if health['system']['status'] == 'LIVE':
                logging.info("🔴 LIVE MARKET DATA READY")
                break
            time.sleep(1)
        else:
            logging.error("❌ Failed to establish live market data within 30 seconds")
    
    return live_engine

def get_live_engine():
    """Get the live market engine instance"""
    global live_engine
    if live_engine is None:
        live_engine = initialize_live_engine()
    return live_engine
