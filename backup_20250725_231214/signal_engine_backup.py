import time
import logging
from typing import Dict, List
import websocket
import json
import threading
from collections import deque
import torch
import cupy_fallback as cp
import config
import requests

class PriceDataFeed:
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.volumes = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.running = False
        self.last_update = 0
        self.ws_connection = None
        
    def start_feed(self):
        if not self.running:
            self._init_prices_from_rest()
            threading.Thread(target=self._start_websocket_feed, daemon=True).start()
    
    def _init_prices_from_rest(self):
        """Initialize with REST API, then switch to WebSocket"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd", "include_24hr_vol": "true"}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                asset_map = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
                
                for coin_id, coin_data in data.items():
                    asset = asset_map.get(coin_id)
                    if asset and "usd" in coin_data:
                        price = coin_data["usd"]
                        volume = coin_data.get("usd_24h_vol", 1000000)
                        self.prices[asset].append(price)
                        self.volumes[asset].append(volume)
                        
        except Exception as e:
            logging.error(f"REST init failed: {e}")
            defaults = {"BTC": 45000, "ETH": 2500, "SOL": 100}
            for asset, price in defaults.items():
                self.prices[asset].append(price)
                self.volumes[asset].append(1000000)
    
    def _start_websocket_feed(self):
        """Start WebSocket connection for real-time data"""
        self.running = True
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                self._process_websocket_message(data)
            except Exception as e:
                logging.error(f"WebSocket message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")
            if self.running:
                time.sleep(5)
                self._reconnect_websocket()
        
        def on_close(ws, close_status_code, close_msg):
            logging.info("WebSocket connection closed")
            if self.running:
                time.sleep(5)
                self._reconnect_websocket()
        
        def on_open(ws):
            logging.info("WebSocket connected for real-time price data")
            # Subscribe to real-time price updates
            subscribe_message = {
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@ticker",
                    "ethusdt@ticker", 
                    "solusdt@ticker"
                ],
                "id": 1
            }
            ws.send(json.dumps(subscribe_message))
        
        try:
            # Use Binance WebSocket for real-time data (more reliable than CoinGecko)
            websocket.enableTrace(False)
            self.ws_connection = websocket.WebSocketApp(
                "wss://stream.binance.com:9443/ws/ticker",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            self.ws_connection.run_forever()
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            self._fallback_to_polling()
    
    def _process_websocket_message(self, data):
        """Process real-time WebSocket price data"""
        try:
            if 's' in data:  # Binance ticker format
                symbol = data['s'].replace('USDT', '')
                if symbol in ['BTC', 'ETH', 'SOL']:
                    price = float(data['c'])  # Current price
                    volume = float(data['v'])  # 24h volume
                    
                    self.prices[symbol].append(price)
                    self.volumes[symbol].append(volume)
                    self.last_update = time.time()
                    
                    logging.debug(f"WebSocket update: {symbol} = ${price:.2f}")
        except Exception as e:
            logging.error(f"WebSocket data processing error: {e}")
    
    def _reconnect_websocket(self):
        """Reconnect WebSocket with exponential backoff"""
        if self.running:
            threading.Thread(target=self._start_websocket_feed, daemon=True).start()
    
    def _fallback_to_polling(self):
        """Fallback to polling if WebSocket fails"""
        logging.warning("WebSocket failed, falling back to polling")
        while self.running:
            try:
                self._update_prices_via_rest()
                time.sleep(10)
            except Exception as e:
                logging.error(f"Polling error: {e}")
                time.sleep(5)
    
    def _update_prices_via_rest(self):
        """REST API backup for price updates"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd", "include_24hr_vol": "true"}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                asset_map = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
                
                for coin_id, coin_data in data.items():
                    asset = asset_map.get(coin_id)
                    if asset and "usd" in coin_data:
                        price = coin_data["usd"]
                        volume = coin_data.get("usd_24h_vol", 1000000)
                        self.prices[asset].append(price)
                        self.volumes[asset].append(volume)
                        
                self.last_update = time.time()
        except Exception as e:
            logging.error(f"REST update failed: {e}")
    
    def get_recent_data(self, asset: str, minutes: int = 60) -> Dict:
        if asset not in self.prices or len(self.prices[asset]) == 0:
            return {"prices": [], "volumes": [], "valid": False}
        
        prices = list(self.prices[asset])
        volumes = list(self.volumes[asset])
        
        return {
            "prices": prices[-minutes:] if len(prices) > minutes else prices,
            "volumes": volumes[-minutes:] if len(volumes) > minutes else volumes,
            "valid": len(prices) > 0,
            "current_price": prices[-1],
            "current_volume": volumes[-1]
        }

feed = PriceDataFeed()

def calculate_rsi_torch(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    
    if torch.cuda.is_available() or config.GPU_DEVICE == "mps":
        prices_tensor = torch.tensor(prices, dtype=torch.float32, device=config.GPU_DEVICE)
    else:
        prices_tensor = torch.tensor(prices, dtype=torch.float32)
    
    deltas = torch.diff(prices_tensor)
    gains = torch.nn.functional.relu(deltas)
    losses = torch.nn.functional.relu(-deltas)
    
    alpha = 2.0 / (period + 1)
    weights = torch.tensor([alpha * (1 - alpha) ** i for i in range(period)], 
                          dtype=torch.float32, device=prices_tensor.device)
    weights = weights.flip(0).unsqueeze(0).unsqueeze(0)
    
    if len(gains) >= period:
        gains_padded = torch.nn.functional.pad(gains[-period:].unsqueeze(0).unsqueeze(0), 
                                             (period-1, 0), mode='replicate')
        losses_padded = torch.nn.functional.pad(losses[-period:].unsqueeze(0).unsqueeze(0), 
                                              (period-1, 0), mode='replicate')
        
        avg_gain = torch.nn.functional.conv1d(gains_padded, weights).squeeze()
        avg_loss = torch.nn.functional.conv1d(losses_padded, weights).squeeze()
        
        rs = avg_gain / (avg_loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi[-1])
    
    return 50.0

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    
    if config.GPU_AVAILABLE:
        prices_cp = cp.array(prices)
        volumes_cp = cp.array(volumes)
        total_pv = cp.sum(prices_cp * volumes_cp)
        total_v = cp.sum(volumes_cp)
        return float(total_pv / (total_v + 1e-8))
    else:
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_v = sum(volumes)
        return total_pv / (total_v + 1e-8)

def calculate_price_change_cupy(prices: List[float], minutes: int = 60) -> float:
    if len(prices) < minutes:
        return 0.0
    
    if config.GPU_AVAILABLE:
        prices_cp = cp.array(prices[-minutes:])
        price_diffs = cp.diff(prices_cp)
        hour_change = float(cp.sum(price_diffs)) / prices_cp[0] * 100
        return hour_change
    else:
        return (prices[-1] - prices[-minutes]) / prices[-minutes] * 100

def detect_volume_anomaly(volumes: List[float]) -> bool:
    if len(volumes) < 3:
        return False
    
    current = volumes[-1]
    mean_volume = sum(volumes[:-1]) / len(volumes[:-1])
    return current > mean_volume * 1.5

def generate_signal(shared_data: Dict) -> Dict:
    try:
        best_confidence = 0.0
        best_signal = None
        
        for asset in config.ASSETS:
            data = feed.get_recent_data(asset, 60)
            
            if not data["valid"] or len(data["prices"]) < 15:
                continue
            
            prices = data["prices"]
            volumes = data["volumes"]
            current_price = data["current_price"]
            
            confidence = 0.0
            reason = []
            
            rsi = calculate_rsi_torch(prices)
            vwap = calculate_vwap(prices, volumes)
            volume_anomaly = detect_volume_anomaly(volumes)
            price_change_1h = calculate_price_change_cupy(prices, 60)
            
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
                    "reason": " + ".join(reason) if reason else "market_conditions"
                }
        
        if best_signal and best_signal["confidence"] > 0.1:
            return {
                "confidence": best_signal["confidence"],
                "source": "signal_engine",
                "priority": 1,
                "entropy": 0.0,
                "signal_data": best_signal
            }
        
        return {
            "confidence": 0.0,
            "source": "signal_engine", 
            "priority": 1,
            "entropy": 0.0
        }
        
    except Exception as e:
        logging.error(f"Signal engine error: {e}")
        return {
            "confidence": 0.0,
            "source": "signal_engine",
            "priority": 1, 
            "entropy": 0.0
        }
