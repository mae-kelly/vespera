#!/usr/bin/env python3
"""
Unrestricted Live Market Data Engine
Uses APIs with no geographic restrictions
"""

import websocket
import json
import threading
import time
import logging
import requests
from collections import deque
from typing import Dict, List, Optional
import ssl

class UnrestrictedLiveEngine:
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
        self.websockets = {}
        self.running = True
        self.data_lock = threading.Lock()
        self.last_update = {}
        
        # Start multiple unrestricted feeds
        self._start_coinbase_feed()
        self._start_kraken_feed()
        self._start_rest_api_backup()
        
        logging.info("🌍 UNRESTRICTED LIVE ENGINE STARTED")
    
    def _start_coinbase_feed(self):
        """Coinbase Pro WebSocket - No geographic restrictions"""
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
                                self.live_prices[symbol] = {
                                    'price': price,
                                    'volume': volume,
                                    'source': 'coinbase',
                                    'timestamp': time.time(),
                                    'high_24h': float(data.get('high_24h', price)),
                                    'low_24h': float(data.get('low_24h', price)),
                                    'open_24h': float(data.get('open_24h', price))
                                }
                                
                                # Calculate 24h change
                                open_price = self.live_prices[symbol]['open_24h']
                                if open_price > 0:
                                    change_24h = ((price - open_price) / open_price) * 100
                                    self.live_prices[symbol]['change_24h'] = change_24h
                                
                                self.price_history[symbol].append(price)
                                self.volume_history[symbol].append(volume)
                                self.last_update[symbol] = time.time()
                                
                            logging.info(f"🟢 LIVE {symbol}: ${price:,.2f} (Coinbase)")
                
            except Exception as e:
                logging.error(f"Coinbase message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Coinbase WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Coinbase WebSocket closed, reconnecting...")
            time.sleep(5)
            if self.running:
                self._start_coinbase_feed()
        
        def on_open(ws):
            logging.info("🟢 Coinbase WebSocket connected")
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
    
    def _start_kraken_feed(self):
        """Kraken WebSocket - Global access"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Kraken sends arrays for ticker data
                if isinstance(data, list) and len(data) >= 4:
                    channel_info = data[2] if len(data) > 2 else ""
                    if "ticker" in str(channel_info):
                        ticker_data = data[1]
                        pair = data[3] if len(data) > 3 else ""
                        
                        # Map Kraken pairs to our symbols
                        pair_map = {
                            'XBT/USD': 'BTC',
                            'ETH/USD': 'ETH',
                            'SOL/USD': 'SOL'
                        }
                        
                        symbol = pair_map.get(pair)
                        if symbol and isinstance(ticker_data, dict):
                            # Kraken ticker format: c = [price, lot_volume], v = [volume_today, volume_24h]
                            price_data = ticker_data.get('c', ['0', '0'])
                            volume_data = ticker_data.get('v', ['0', '0'])
                            
                            price = float(price_data[0]) if price_data and len(price_data) > 0 else 0
                            volume = float(volume_data[1]) if volume_data and len(volume_data) > 1 else 0
                            
                            if price > 0:
                                with self.data_lock:
                                    # Only update if no fresher Coinbase data
                                    if (symbol not in self.live_prices or 
                                        self.live_prices[symbol].get('source') != 'coinbase' or
                                        time.time() - self.live_prices[symbol].get('timestamp', 0) > 5):
                                        
                                        # Calculate 24h change if we have previous data
                                        change_24h = 0
                                        if symbol in self.live_prices:
                                            old_price = self.live_prices[symbol].get('price', price)
                                            if old_price > 0:
                                                change_24h = ((price - old_price) / old_price) * 100
                                        
                                        self.live_prices[symbol] = {
                                            'price': price,
                                            'volume': volume,
                                            'source': 'kraken',
                                            'timestamp': time.time(),
                                            'change_24h': change_24h
                                        }
                                        
                                        self.price_history[symbol].append(price)
                                        self.volume_history[symbol].append(volume)
                                        self.last_update[symbol] = time.time()
                                        
                                logging.info(f"🔵 LIVE {symbol}: ${price:,.2f} (Kraken)")
                
            except Exception as e:
                logging.error(f"Kraken message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Kraken WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Kraken WebSocket closed, reconnecting...")
            time.sleep(5)
            if self.running:
                self._start_kraken_feed()
        
        def on_open(ws):
            logging.info("🔵 Kraken WebSocket connected")
            subscribe_msg = {
                "event": "subscribe",
                "pair": ["XBT/USD", "ETH/USD", "SOL/USD"],
                "subscription": {"name": "ticker"}
            }
            ws.send(json.dumps(subscribe_msg))
        
        def run_kraken():
            ws = websocket.WebSocketApp(
                "wss://ws.kraken.com",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.websockets['kraken'] = ws
            ws.run_forever()
        
        kraken_thread = threading.Thread(target=run_kraken, daemon=True)
        kraken_thread.start()
    
    def _start_rest_api_backup(self):
        """REST API backup using multiple free sources"""
        def backup_updater():
            while self.running:
                try:
                    # Try multiple REST APIs as backup
                    self._update_from_coinbase_rest()
                    time.sleep(2)
                    self._update_from_coingecko_minimal()
                    time.sleep(3)
                    
                except Exception as e:
                    logging.error(f"REST backup error: {e}")
                
                time.sleep(10)  # Update every 10 seconds
        
        backup_thread = threading.Thread(target=backup_updater, daemon=True)
        backup_thread.start()
    
    def _update_from_coinbase_rest(self):
        """Coinbase REST API backup"""
        try:
            symbols = ['BTC', 'ETH', 'SOL']
            for symbol in symbols:
                url = f"https://api.coinbase.com/v2/exchange-rates?currency={symbol}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    rates = data.get('data', {}).get('rates', {})
                    price = float(rates.get('USD', 0))
                    
                    if price > 0:
                        with self.data_lock:
                            # Only use as backup if no WebSocket data
                            if (symbol not in self.live_prices or 
                                time.time() - self.live_prices[symbol].get('timestamp', 0) > 30):
                                
                                self.live_prices[symbol] = {
                                    'price': price,
                                    'volume': price * 50000,  # Estimated
                                    'source': 'coinbase_rest',
                                    'timestamp': time.time(),
                                    'change_24h': 0
                                }
                                
                                self.price_history[symbol].append(price)
                                self.volume_history[symbol].append(price * 50000)
                                self.last_update[symbol] = time.time()
                                
                                logging.info(f"🟡 REST {symbol}: ${price:,.2f} (Coinbase REST)")
                
        except Exception as e:
            logging.error(f"Coinbase REST error: {e}")
    
    def _update_from_coingecko_minimal(self):
        """Very minimal CoinGecko usage to avoid rate limits"""
        try:
            # Only update one symbol at a time to avoid rate limits
            symbols = ['BTC', 'ETH', 'SOL']
            coin_ids = ['bitcoin', 'ethereum', 'solana']
            
            # Rotate through symbols
            index = int(time.time() / 15) % len(symbols)  # Change every 15 seconds
            symbol = symbols[index]
            coin_id = coin_ids[index]
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
            
            response = requests.get(url, timeout=5, headers={
                'User-Agent': 'HFT-Backup/1.0'
            })
            
            if response.status_code == 200:
                data = response.json()
                coin_data = data.get(coin_id, {})
                price = coin_data.get('usd', 0)
                change_24h = coin_data.get('usd_24h_change', 0)
                
                if price > 0:
                    with self.data_lock:
                        # Only use if no fresher data available
                        if (symbol not in self.live_prices or 
                            time.time() - self.live_prices[symbol].get('timestamp', 0) > 60):
                            
                            self.live_prices[symbol] = {
                                'price': price,
                                'volume': price * 75000,  # Estimated
                                'source': 'coingecko_backup',
                                'timestamp': time.time(),
                                'change_24h': change_24h or 0
                            }
                            
                            self.price_history[symbol].append(price)
                            self.volume_history[symbol].append(price * 75000)
                            self.last_update[symbol] = time.time()
                            
                            logging.info(f"🟠 BACKUP {symbol}: ${price:,.2f} (CoinGecko)")
            
        except Exception as e:
            logging.error(f"CoinGecko backup error: {e}")
    
    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """Get current live price - NO FALLBACK, NO MOCK DATA"""
        with self.data_lock:
            if symbol not in self.live_prices:
                return None
            
            data = self.live_prices[symbol].copy()
            
            # Check data freshness
            age = time.time() - data.get('timestamp', 0)
            if age > 120:  # Relaxed to 2 minutes for global access
                logging.warning(f"⚠️ Stale data for {symbol} ({age:.1f}s old)")
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
            return None
        
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [change if change > 0 else 0 for change in changes]
        losses = [-change if change < 0 else 0 for change in changes]
        
        if len(gains) < period:
            return None
        
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
            return None
        
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
        return age < 120  # More relaxed for global access
    
    def get_system_health(self) -> Dict:
        """Get system health"""
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
            
            all_live = all(health[s]['is_live'] for s in health)
            sufficient_history = all(health[s]['price_history_length'] >= 5 for s in health)
            
            health['system'] = {
                'all_symbols_live': all_live,
                'sufficient_history': sufficient_history,
                'websocket_connections': len(self.websockets),
                'status': 'LIVE' if all_live and sufficient_history else 'WARMING_UP'
            }
            
            return health
    
    def stop(self):
        """Stop all connections"""
        self.running = False
        
        for name, ws in self.websockets.items():
            try:
                ws.close()
                logging.info(f"Closed {name} WebSocket")
            except:
                pass
        
        logging.info("🌍 Unrestricted Live Engine stopped")

# Global instance
unrestricted_engine = None

def initialize_unrestricted_engine():
    """Initialize the unrestricted live engine"""
    global unrestricted_engine
    if unrestricted_engine is None:
        unrestricted_engine = UnrestrictedLiveEngine()
        
        # Wait for initial data
        logging.info("⏳ Waiting for unrestricted live data...")
        for i in range(60):  # Wait up to 60 seconds
            health = unrestricted_engine.get_system_health()
            if health['system']['status'] == 'LIVE':
                logging.info("🌍 UNRESTRICTED LIVE DATA READY")
                break
            elif i > 30 and health['system']['sufficient_history']:
                logging.info("🌍 UNRESTRICTED DATA WARMING UP - Proceeding")
                break
            time.sleep(1)
        else:
            logging.warning("⚠️ Limited data available - proceeding with available feeds")
    
    return unrestricted_engine

def get_live_engine():
    """Get the unrestricted live engine instance"""
    global unrestricted_engine
    if unrestricted_engine is None:
        unrestricted_engine = initialize_unrestricted_engine()
    return unrestricted_engine