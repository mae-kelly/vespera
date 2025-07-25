import time
import logging
from typing import Dict, List, Optional
import websocket
import json
import threading
from collections import deque
import torch
import cupy as cp
import config
import requests

class PriceDataFeed:
    def __init__(self):
        self.prices = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.volumes = {"BTC": deque(maxlen=120), "ETH": deque(maxlen=120), "SOL": deque(maxlen=120)}
        self.running = False
        self.ws = None
        self.use_simulation = config.MODE == "dry"
        
    def start_feed(self):
        if not self.running:
            if self.use_simulation:
                threading.Thread(target=self._simulate_feed, daemon=True).start()
            else:
                threading.Thread(target=self._start_websocket_feed, daemon=True).start()
    
    def _start_websocket_feed(self):
        """Real Coingecko WebSocket API implementation"""
        self.running = True
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if 'price' in data and 'id' in data:
                    asset_map = {'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL'}
                    asset = asset_map.get(data['id'])
                    if asset:
                        self.prices[asset].append(float(data['price']))
                        self.volumes[asset].append(float(data.get('total_volume', 1000000)))
            except Exception as e:
                logging.error(f"WebSocket message error: {e}")
        
        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")
        
        def on_close(ws):
            logging.info("WebSocket connection closed")
            if self.running:
                time.sleep(5)
                self._start_websocket_feed()  # Reconnect
        
        def on_open(ws):
            logging.info("Connected to Coingecko WebSocket")
            # Subscribe to price updates
            subscribe_msg = {
                "method": "SUBSCRIBE",
                "params": ["bitcoin@ticker", "ethereum@ticker", "solana@ticker"],
                "id": 1
            }
            ws.send(json.dumps(subscribe_msg))
        
        # Use Coingecko WebSocket (fallback to simulation if unavailable)
        try:
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                "wss://ws-api.coingecko.com/v2",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            self.ws.run_forever()
        except Exception as e:
            logging.error(f"WebSocket failed, falling back to simulation: {e}")
            self._simulate_feed()
    
    def _simulate_feed(self):
        self.running = True
        base_prices = {"BTC": 45000, "ETH": 2500, "SOL": 100}
        
        # Pre-populate with initial data
        for asset in config.ASSETS:
            for i in range(60):
                price = base_prices[asset] * (1 + (i * -0.001))
                volume = 1000000 + (i * 50000)
                self.prices[asset].append(price)
                self.volumes[asset].append(volume)
        
        while self.running:
            for asset in config.ASSETS:
                volatility = {"BTC": 0.015, "ETH": 0.020, "SOL": 0.025}[asset]
                
                if torch.cuda.is_available():
                    noise = cp.random.normal(0, volatility)
                    volume_mult = cp.random.exponential(1.0)
                else:
                    import numpy as np
                    noise = np.random.normal(0, volatility)
                    volume_mult = np.random.exponential(1.0)
                
                if len(self.prices[asset]) > 0:
                    last_price = self.prices[asset][-1]
                else:
                    last_price = base_prices[asset]
                
                new_price = last_price * (1 + float(noise))
                volume = 1000000 * float(volume_mult)
                
                self.prices[asset].append(new_price)
                self.volumes[asset].append(volume)
            
            time.sleep(1)
    
    def get_recent_data(self, asset: str, minutes: int = 60) -> Dict:
        if asset not in self.prices:
            return {"prices": [], "volumes": [], "valid": False}
        
        prices = list(self.prices[asset])
        volumes = list(self.volumes[asset])
        
        if len(prices) == 0:
            return {"prices": [], "volumes": [], "valid": False}
        
        return {
            "prices": prices[-minutes:] if len(prices) > minutes else prices,
            "volumes": volumes[-minutes:] if len(volumes) > minutes else volumes,
            "valid": True,
            "current_price": prices[-1],
            "current_volume": volumes[-1]
        }

feed = PriceDataFeed()

def calculate_rsi_torch(prices: List[float], period: int = 14) -> float:
    """RSI calculation using torch.nn.functional"""
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
    """1-hour percent change using cupy.diff over 60×1-min candles"""
    if len(prices) < minutes:
        return 0.0
    
    if torch.cuda.is_available():
        prices_cp = cp.array(prices[-minutes:])
        price_changes = cp.diff(prices_cp)
        hour_change = (prices_cp[-1] - prices_cp[0]) / prices_cp[0] * 100
        return float(hour_change)
    else:
        return (prices[-1] - prices[-minutes]) / prices[-minutes] * 100

def detect_volume_anomaly(volumes: List[float]) -> bool:
    if len(volumes) < 3:
        return False
    
    current = volumes[-1]
    mean_volume = sum(volumes[:-1]) / len(volumes[:-1])
    return current > mean_volume * 1.5  # Exact 1.5x threshold as specified

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
            
            # RSI calculation using torch.nn.functional
            rsi = calculate_rsi_torch(prices)
            
            # VWAP calculation
            vwap = calculate_vwap(prices, volumes)
            
            # Volume anomaly detection (exact 1.5x threshold)
            volume_anomaly = detect_volume_anomaly(volumes)
            
            # 1-hour price change using cupy.diff
            price_change_1h = calculate_price_change_cupy(prices, 60)
            
            # Signal conditions
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
