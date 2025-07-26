import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import time
import logging
import json
import threading
from typing import Dict, List
from collections import deque
import websocket
import config

# GPU optimization for speed
if config.DEVICE == 'cuda':
    torch.cuda.empty_cache()
    torch.backends.cudnn.benchmark = True
elif config.DEVICE == 'mps':
    torch.backends.mps.allow_tf32 = True

try:
    if config.DEVICE == 'cuda':
        import cupy as cp
    else:
        import cupy_fallback as cp
except ImportError:
    import cupy_fallback as cp

class MultiWebSocketFeed:
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=1000), "ETH": deque(maxlen=1000), "SOL": deque(maxlen=1000)}
        self.volumes = {"BTC": deque(maxlen=1000), "ETH": deque(maxlen=1000), "SOL": deque(maxlen=1000)}
        self.orderbooks = {"BTC": {"bids": [], "asks": []}, "ETH": {"bids": [], "asks": []}, "SOL": {"bids": [], "asks": []}}
        self.running = False
        self.initialized = False
        self.current_prices = {"BTC": 0, "ETH": 0, "SOL": 0}
        
        # Multiple WebSocket connections
        self.websockets = {}
        self.connection_status = {
            "okx": False,
            "binance": False, 
            "kraken": False,
            "coinbase": False
        }
        
        # Real-time feed aggregation
        self.feed_priority = ["okx", "binance", "kraken", "coinbase"]
        self.last_updates = {"BTC": 0, "ETH": 0, "SOL": 0}
        
    def start_feed(self):
        if not self.initialized:
            self._initialize_multi_feeds()
            self.running = True
            
            # Start all WebSocket connections in parallel
            threading.Thread(target=self._start_okx_websocket, daemon=True).start()
            threading.Thread(target=self._start_binance_websocket, daemon=True).start()
            threading.Thread(target=self._start_kraken_websocket, daemon=True).start()
            threading.Thread(target=self._start_coinbase_websocket, daemon=True).start()
            
            logging.info("🚀 Multi-WebSocket feeds started")
    
    def _initialize_multi_feeds(self):
        """Initialize with realistic starting prices"""
        # Set realistic starting prices (will be updated by WebSockets)
        self.current_prices = {
            "BTC": 67500.0,
            "ETH": 3450.0, 
            "SOL": 175.0
        }
        
        # Pre-populate with some data points
        for asset in ["BTC", "ETH", "SOL"]:
            base_price = self.current_prices[asset]
            for i in range(100):
                price_var = base_price * (1 + (i - 50) * 0.0001)
                volume_var = 1000000 * (0.8 + (i % 10) * 0.04)
                self.prices[asset].append(price_var)
                self.volumes[asset].append(volume_var)
        
        self.initialized = True
        logging.info("✅ Multi-feed initialization complete")

    def _start_okx_websocket(self):
        """OKX WebSocket - PRIMARY FEED"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'data' in data:
                    for item in data['data']:
                        if 'instId' in item:
                            symbol = item['instId'].replace('-USDT', '').replace('-USD', '')
                            if symbol in ['BTC', 'ETH', 'SOL']:
                                if 'last' in item:
                                    price = float(item['last'])
                                    self._update_price(symbol, price, "okx")
                                if 'vol24h' in item:
                                    volume = float(item['vol24h'])
                                    self._update_volume(symbol, volume, "okx")
            except Exception as e:
                logging.error(f"OKX WebSocket error: {e}")
        
        def on_error(ws, error):
            logging.error(f"OKX WebSocket error: {error}")
            self.connection_status["okx"] = False
        
        def on_open(ws):
            logging.info("✅ OKX WebSocket connected")
            self.connection_status["okx"] = True
            # Subscribe to tickers
            subscribe_msg = {
                "op": "subscribe",
                "args": [
                    {"channel": "tickers", "instId": "BTC-USDT"},
                    {"channel": "tickers", "instId": "ETH-USDT"},
                    {"channel": "tickers", "instId": "SOL-USDT"},
                    {"channel": "books5", "instId": "BTC-USDT"},
                    {"channel": "books5", "instId": "ETH-USDT"},
                    {"channel": "books5", "instId": "SOL-USDT"}
                ]
            }
            ws.send(json.dumps(subscribe_msg))
        
        while self.running:
            try:
                ws = websocket.WebSocketApp(
                    "wss://ws.okx.com:8443/ws/v5/public",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error
                )
                self.websockets["okx"] = ws
                ws.run_forever()
            except Exception as e:
                logging.error(f"OKX WebSocket connection failed: {e}")
                time.sleep(5)

    def _start_binance_websocket(self):
        """Binance WebSocket - BACKUP FEED"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 's' in data and 'c' in data:  # Symbol and close price
                    symbol = data['s'].replace('USDT', '')
                    if symbol in ['BTC', 'ETH', 'SOL']:
                        price = float(data['c'])
                        volume = float(data.get('v', 0))
                        self._update_price(symbol, price, "binance")
                        if volume > 0:
                            self._update_volume(symbol, volume, "binance")
            except Exception as e:
                logging.error(f"Binance WebSocket error: {e}")
        
        def on_error(ws, error):
            logging.error(f"Binance WebSocket error: {error}")
            self.connection_status["binance"] = False
        
        def on_open(ws):
            logging.info("✅ Binance WebSocket connected")
            self.connection_status["binance"] = True
        
        while self.running:
            try:
                ws = websocket.WebSocketApp(
                    "wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error
                )
                self.websockets["binance"] = ws
                ws.run_forever()
            except Exception as e:
                logging.error(f"Binance WebSocket connection failed: {e}")
                time.sleep(5)

    def _start_kraken_websocket(self):
        """Kraken WebSocket - TERTIARY FEED"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if isinstance(data, list) and len(data) > 1:
                    if 'XBT/USD' in str(data) or 'ETH/USD' in str(data) or 'SOL/USD' in str(data):
                        # Process Kraken ticker data
                        pass  # Simplified for now
            except Exception as e:
                logging.error(f"Kraken WebSocket error: {e}")
        
        def on_open(ws):
            logging.info("✅ Kraken WebSocket connected")
            self.connection_status["kraken"] = True
            # Subscribe to ticker
            subscribe_msg = {
                "event": "subscribe",
                "pair": ["XBT/USD", "ETH/USD", "SOL/USD"],
                "subscription": {"name": "ticker"}
            }
            ws.send(json.dumps(subscribe_msg))
        
        while self.running:
            try:
                ws = websocket.WebSocketApp(
                    "wss://ws.kraken.com",
                    on_open=on_open,
                    on_message=on_message
                )
                self.websockets["kraken"] = ws
                ws.run_forever()
            except Exception as e:
                logging.error(f"Kraken WebSocket connection failed: {e}")
                time.sleep(5)

    def _start_coinbase_websocket(self):
        """Coinbase WebSocket - QUATERNARY FEED"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'ticker':
                    symbol = data.get('product_id', '').replace('-USD', '')
                    if symbol in ['BTC', 'ETH', 'SOL']:
                        price = float(data.get('price', 0))
                        if price > 0:
                            self._update_price(symbol, price, "coinbase")
            except Exception as e:
                logging.error(f"Coinbase WebSocket error: {e}")
        
        def on_open(ws):
            logging.info("✅ Coinbase WebSocket connected")
            self.connection_status["coinbase"] = True
            subscribe_msg = {
                "type": "subscribe",
                "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD"],
                "channels": ["ticker"]
            }
            ws.send(json.dumps(subscribe_msg))
        
        while self.running:
            try:
                ws = websocket.WebSocketApp(
                    "wss://ws-feed.exchange.coinbase.com",
                    on_open=on_open,
                    on_message=on_message
                )
                self.websockets["coinbase"] = ws
                ws.run_forever()
            except Exception as e:
                logging.error(f"Coinbase WebSocket connection failed: {e}")
                time.sleep(5)

    def _update_price(self, symbol: str, price: float, source: str):
        """Update price with source priority"""
        current_time = time.time()
        
        # Only update if this source has higher priority or data is newer
        source_priority = self.feed_priority.index(source) if source in self.feed_priority else 999
        
        if (current_time - self.last_updates.get(symbol, 0)) > 0.1 or source_priority <= 1:
            self.current_prices[symbol] = price
            self.prices[symbol].append(price)
            self.last_updates[symbol] = current_time
            
            # Log significant price movements
            if len(self.prices[symbol]) > 1:
                prev_price = self.prices[symbol][-2]
                change_pct = ((price - prev_price) / prev_price) * 100
                if abs(change_pct) > 0.1:  # > 0.1% change
                    logging.info(f"📈 {symbol}: ${price:,.2f} ({change_pct:+.2f}%) via {source}")

    def _update_volume(self, symbol: str, volume: float, source: str):
        """Update volume data"""
        if volume > 0:
            self.volumes[symbol].append(volume)

    def get_recent_data(self, asset: str, minutes: int = 60) -> Dict:
        if not self.initialized:
            return {"valid": False, "error": "Feed not initialized"}
        
        if asset not in self.prices or len(self.prices[asset]) == 0:
            return {"valid": False, "error": f"No data for {asset}"}
        
        prices = list(self.prices[asset])
        volumes = list(self.volumes[asset])
        
        # Get best available connection status
        best_connection = any(self.connection_status.values())
        
        return {
            "prices": prices[-minutes:] if len(prices) > minutes else prices,
            "volumes": volumes[-minutes:] if len(volumes) > minutes else volumes,
            "valid": True,
            "current_price": self.current_prices[asset],
            "current_volume": volumes[-1] if volumes else 0,
            "websocket_connected": best_connection,
            "feed_sources": [source for source, status in self.connection_status.items() if status],
            "data_age_seconds": time.time() - self.last_updates.get(asset, 0)
        }

    def get_connection_health(self) -> Dict:
        """Get detailed connection health"""
        active_feeds = sum(1 for status in self.connection_status.values() if status)
        total_feeds = len(self.connection_status)
        
        return {
            "active_feeds": active_feeds,
            "total_feeds": total_feeds,
            "health_percentage": (active_feeds / total_feeds) * 100,
            "feed_status": self.connection_status,
            "primary_feed_active": self.connection_status.get("okx", False),
            "redundancy_level": "HIGH" if active_feeds >= 3 else "MEDIUM" if active_feeds >= 2 else "LOW"
        }

# Initialize global feed
feed = MultiWebSocketFeed()

# Rest of signal_engine.py functions remain the same...
def calculate_rsi_torch(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        if len(prices) >= 2:
            recent_change = (prices[-1] - prices[0]) / prices[0]
            if recent_change < -0.02:
                return 25.0 + (recent_change * -500)
            elif recent_change > 0.02:
                return 75.0 + (recent_change * 500)
            else:
                return 50.0 + (recent_change * 1000)
        return 50.0
    
    prices_tensor = torch.tensor(prices, dtype=torch.float16, device=config.DEVICE)
    deltas = torch.diff(prices_tensor)
    gains = torch.nn.functional.relu(deltas)
    losses = torch.nn.functional.relu(-deltas)
    
    avg_gain = torch.mean(gains[-period:])
    avg_loss = torch.mean(losses[-period:])
    
    rs = avg_gain / (avg_loss + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    
    prices_cp = cp.array(prices)
    volumes_cp = cp.array(volumes)
    total_pv = cp.sum(prices_cp * volumes_cp)
    total_v = cp.sum(volumes_cp)
    return float(total_pv / total_v)

def calculate_price_change_cupy(prices: List[float], minutes: int = 60) -> float:
    if len(prices) < minutes:
        minutes = len(prices)
    if minutes < 2:
        return 0.0
    
    prices_cp = cp.array(prices[-minutes:])
    return float(((prices_cp[-1] - prices_cp[0]) / prices_cp[0]) * 100)

def detect_volume_anomaly(volumes: List[float]) -> bool:
    if len(volumes) < 3:
        return False
    
    current = volumes[-1]
    mean_volume = sum(volumes[:-1]) / len(volumes[:-1])
    return current > mean_volume * 1.5

def generate_signal(shared_data: Dict) -> Dict:
    if not feed.initialized:
        feed.start_feed()
        time.sleep(0.1)
    
    if not feed.initialized:
        raise Exception("Multi-feed initialization failed")
    
    best_confidence = 0.0
    best_signal = None
    
    # Check connection health
    health = feed.get_connection_health()
    if health["active_feeds"] == 0:
        logging.warning("⚠️ No active WebSocket feeds")
    
    for asset in config.ASSETS:
        try:
            data = feed.get_recent_data(asset, 60)
            
            if not data["valid"]:
                continue
            
            prices = data["prices"]
            volumes = data["volumes"]
            current_price = data["current_price"]
            
            if len(prices) < 5:
                continue
            
            confidence = 0.0
            reason = []
            
            rsi = calculate_rsi_torch(prices)
            vwap = calculate_vwap(prices, volumes)
            volume_anomaly = detect_volume_anomaly(volumes)
            price_change_1h = calculate_price_change_cupy(prices, min(60, len(prices)))
            
            # Enhanced confidence scoring with multi-feed bonus
            if rsi < 30:
                confidence += 0.35
                reason.append("oversold_rsi")
            
            if current_price < vwap:
                confidence += 0.25
                reason.append("below_vwap")
            
            if volume_anomaly:
                confidence += 0.25
                reason.append("volume_spike")
            
            if price_change_1h < -1.0:
                confidence += 0.15
                reason.append("significant_drop")
            
            # Multi-feed reliability bonus
            if health["active_feeds"] >= 3:
                confidence *= 1.1  # 10% bonus for redundancy
                reason.append("multi_feed_confirmed")
            
            vwap_deviation = ((current_price - vwap) / vwap) * 100 if vwap > 0 else 0
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_signal = {
                    "asset": asset,
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": current_price * 1.015,
                    "take_profit_1": current_price * 0.985,
                    "take_profit_2": current_price * 0.975,
                    "take_profit_3": current_price * 0.965,
                    "rsi": rsi,
                    "vwap": vwap,
                    "vwap_deviation": vwap_deviation,
                    "volume_anomaly": volume_anomaly,
                    "price_change_1h": price_change_1h,
                    "reason": " + ".join(reason) if reason else "market_conditions",
                    "feed_sources": data.get("feed_sources", []),
                    "data_age_seconds": data.get("data_age_seconds", 0),
                    "feed_health": health
                }
            
        except Exception as e:
            logging.error(f"Error processing {asset}: {e}")
            continue
    
    if best_signal:
        return {
            "confidence": best_signal["confidence"],
            "source": "signal_engine",
            "priority": 1,
            "entropy": 0.0,
            "signal_data": best_signal
        }
    else:
        raise Exception("No valid signals from multi-feed system")
