import time
import logging
from typing import Dict, List, Optional
import websocket
import json
import threading
from collections import deque
import torch
import cupy_fallback as cupy_fallback as cp
import config
import requests

class PriceDataFeed:
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.volumes = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.running = False
        self.ws = None
        
    def start_feed(self):
        if not self.running:
            # REAL implementation - no simulation mode
            threading.Thread(target=self._start_real_feed, daemon=True).start()
    
    def _start_real_feed(self):
        """Use REAL market data - CoinGecko + Binance WebSocket for actual prices"""
        self.running = True
        
        # Initialize with real current prices
        self._get_real_current_prices()
        
        # Start real WebSocket feed (Binance since CoinGecko doesn't have public WS)
        self._start_binance_websocket()
    
    def _get_real_current_prices(self):
        """Get actual current market prices from CoinGecko API"""
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": "bitcoin,ethereum,solana",
                "vs_currencies": "usd",
                "include_24hr_vol": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                asset_map = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}
                
                for coin_id, coin_data in data.items():
                    asset = asset_map.get(coin_id)
                    if asset and "usd" in coin_data:
                        current_price = coin_data["usd"]
                        current_volume = coin_data.get("usd_24h_vol", 0)
                        
                        # Initialize with current real price
                        self.prices[asset].append(current_price)
                        self.volumes[asset].append(current_volume)
                        
                        logging.info(f"Real market price for {asset}: ${current_price:,.2f}")
            
        except Exception as e:
            logging.error(f"Failed to get real prices from CoinGecko: {e}")
            raise Exception("Cannot start without real market data")
    
    def _start_binance_websocket(self):
        """Use Binance WebSocket for real-time price updates (most reliable)"""
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Handle Binance stream format
                if 's' in data and 'c' in data:  # symbol and close price
                    symbol_map = {
                        "BTCUSDT": "BTC",
                        "ETHUSDT": "ETH", 
                        "SOLUSDT": "SOL"
                    }
                    
                    symbol = symbol_map.get(data['s'])
                    if symbol:
                        price = float(data['c'])  # close price
                        volume = float(data.get('v', 0))  # volume
                        
                        self.prices[symbol].append(price)
                        self.volumes[symbol].append(volume)
                        
                        logging.debug(f"Real price update: {symbol} = ${price:,.2f}")
                        
            except Exception as e:
                logging.error(f"Real price feed error: {e}")
        
        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")
            # Reconnect for real trading
            if self.running:
                time.sleep(5)
                self._start_binance_websocket()
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Real price feed disconnected")
            if self.running:
                time.sleep(2)
                self._start_binance_websocket()  # Immediate reconnect
        
        def on_open(ws):
            logging.info("Connected to REAL price feed (Binance)")
            
            # Subscribe to real-time ticker data
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
            logging.info("Subscribed to real market data streams")
        
        try:
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                "wss://stream.binance.com:9443/ws/stream",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            self.ws.run_forever()
            
        except Exception as e:
            logging.error(f"Failed to connect to real price feed: {e}")
            raise Exception("Cannot operate without real market data")
    
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

# Keep all the existing calculation functions but ensure they work with real data
def calculate_rsi_torch(prices: List[float], period: int = 14) -> float:
    """RSI calculation using torch.nn.functional - REAL implementation"""
    if len(prices) < period + 1:
        return 50.0
    
    if torch.cuda.is_available():
        prices_tensor = torch.tensor(prices, dtype=torch.float32, device='cuda')
    else:
        prices_tensor = torch.tensor(prices, dtype=torch.float32)
    
    deltas = torch.diff(prices_tensor)
    gains = torch.nn.functional.relu(deltas)
    losses = torch.nn.functional.relu(-deltas)
    
    # Exponential moving average using conv1d
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
    """REAL VWAP calculation"""
    if len(prices) != len(volumes) or len(prices) == 0:
        return prices[-1] if prices else 0
    
    if torch.cuda.is_available():
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
    """1-hour percent change using cupy.diff over 60×1-min candles - REAL data"""
    if len(prices) < minutes:
        return 0.0
    
    if torch.cuda.is_available():
        prices_cp = cp.array(prices[-minutes:])
        hour_change = (prices_cp[-1] - prices_cp[0]) / prices_cp[0] * 100
        return float(hour_change)
    else:
        return (prices[-1] - prices[-minutes]) / prices[-minutes] * 100

def detect_volume_anomaly(volumes: List[float]) -> bool:
    """REAL volume anomaly detection - exact 1.5x threshold"""
    if len(volumes) < 3:
        return False
    
    current = volumes[-1]
    mean_volume = sum(volumes[:-1]) / len(volumes[:-1])
    return current > mean_volume * 1.5

def generate_signal(shared_data: Dict) -> Dict:
    """Generate REAL trading signals from REAL market data"""
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
            
            # RSI calculation using torch.nn.functional on REAL data
            rsi = calculate_rsi_torch(prices)
            
            # VWAP calculation on REAL data
            vwap = calculate_vwap(prices, volumes)
            
            # Volume anomaly detection (exact 1.5x threshold) on REAL data
            volume_anomaly = detect_volume_anomaly(volumes)
            
            # 1-hour price change using cupy.diff on REAL data
            price_change_1h = calculate_price_change_cupy(prices, 60)
            
            # REAL signal conditions for REAL trading
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
        logging.error(f"REAL signal engine error: {e}")
        return {
            "confidence": 0.0,
            "source": "signal_engine",
            "priority": 1, 
            "entropy": 0.0
        }
