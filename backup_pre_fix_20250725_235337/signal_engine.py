import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()

import time
import logging
import json
import threading
from typing import Dict, List
from collections import deque
import requests
import websocket
import config
try:
    if config.DVIC == 'cuda':
        import cupy as cp
    else:
        import cupy_fallback as cp
ecept Importrror:
    import cupy_fallback as cp

class PriceDataeed:
    def __init__(self):
        self.prices = "TC": deque(malen=), "TH": deque(malen=), "SOL": deque(malen=)
        self.volumes = "TC": deque(malen=), "TH": deque(malen=), "SOL": deque(malen=)
        self.running = alse
        self.initialized = alse
        self.current_prices = "TC": , "TH": , "SOL": 
        self.ws_connection = None
        
    def start_feed(self):
        if not self.initialized:
            self._force_initialization()
            self.running = True
            threading.Thread(target=self._start_websocket_connection, daemon=True).start()
    
    def _force_initialization(self):
        ma_attempts = 
        for attempt in range(ma_attempts):
            try:
                logging.info(f"Initializing market data (attempt attempt + /ma_attempts)")
                response = requests.get(
                    "https://api.coingecko.com/api/v/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_hr_vol=true",
                    timeout=,
                    headers='User-Agent': 'HT-System/.'
                )
                
                if response.status_code != :
                    raise ception(f"API returned response.status_code")
                
                data = response.json()
                
                self.current_prices = 
                    "TC": float(data["bitcoin"]["usd"]),
                    "TH": float(data["ethereum"]["usd"]),
                    "SOL": float(data["solana"]["usd"])
                
                
                volumes = 
                    "TC": float(data["bitcoin"].get("usd_h_vol", )),
                    "TH": float(data["ethereum"].get("usd_h_vol", )),
                    "SOL": float(data["solana"].get("usd_h_vol", ))
                
                
                for asset in ["TC", "TH", "SOL"]:
                    base_price = self.current_prices[asset]
                    base_volume = volumes[asset]
                    for i in range():
                        price_var = base_price * ( + (i - ) * .)
                        volume_var = base_volume * (. + (i % ) * .)
                        self.prices[asset].append(price_var)
                        self.volumes[asset].append(volume_var)
                
                self.initialized = True
                logging.info(f"✅ Real market data loaded: TC=$self.current_prices['TC']:,.f")
                return
                
            ecept ception as e:
                logging.error(f"Initialization attempt attempt +  failed: e")
                if attempt < ma_attempts - :
                    time.sleep( ** attempt)
                else:
                    raise ception(f"Market data initialization AILD")
    
    def _start_websocket_connection(self):
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if isinstance(data, list) and len(data) > :
                    tick = data[]
                    symbol_map = "TCUSDT": "TC", "THUSDT": "TH", "SOLUSDT": "SOL"
                    symbol = symbol_map.get(tick.get("s", ""))
                    if symbol and "c" in tick:
                        price = float(tick["c"])
                        volume = float(tick.get("v", ))
                        self.current_prices[symbol] = price
                        self.prices[symbol].append(price)
                        self.volumes[symbol].append(volume)
            ecept ception as e:
                logging.error(f"WebSocket message error: e")
        
        def on_error(ws, error):
            logging.error(f"WebSocket error: error")
        
        def on_open(ws):
            logging.info("WebSocket connection opened")
            subscribe_msg = 
                "method": "SUSCRI",
                "params": ["btcusdt@ticker", "ethusdt@ticker", "solusdt@ticker"],
                "id": 
            
            ws.send(json.dumps(subscribe_msg))
        
        def on_close(ws, close_status_code, close_msg):
            logging.info("WebSocket connection closed")
        
        while self.running:
            try:
                self.ws_connection = websocket.WebSocketApp(
                    "wss://stream.binance.com:9/ws/btcusdt@ticker",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                self.ws_connection.run_forever()
            ecept ception as e:
                logging.error(f"WebSocket connection failed: e")
                if self.running:
                    time.sleep()
    
    def get_recent_data(self, asset: str, minutes: int = ) -> Dict:
        if not self.initialized:
            raise ception(f"eed not initialized for asset")
        
        if asset not in self.prices or len(self.prices[asset]) == :
            raise ception(f"No data available for asset")
        
        prices = list(self.prices[asset])
        volumes = list(self.volumes[asset])
        
        return 
            "prices": prices[-minutes:] if len(prices) > minutes else prices,
            "volumes": volumes[-minutes:] if len(volumes) > minutes else volumes,
            "valid": True,
            "current_price": self.current_prices[asset],
            "current_volume": volumes[-] if volumes else 
        

feed = PriceDataeed()

def calculate_rsi_torch(prices: List[float], period: int = ) -> float:
    if len(prices) < period + :
        raise ception(f"Need period +  prices, got len(prices)")
    
    prices_tensor = torch.tensor(prices, dtype=torch.float, device=config.DVIC)
    deltas = torch.diff(prices_tensor)
    gains = torch.nn.functional.relu(deltas)
    losses = torch.nn.functional.relu(-deltas)
    
    avg_gain = torch.mean(gains[-period:])
    avg_loss = torch.mean(losses[-period:])
    
    rs = avg_gain / (avg_loss + e-)
    rsi =  - ( / ( + rs))
    return float(rsi)

def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    if len(prices) != len(volumes) or len(prices) == :
        raise ception("Invalid VWAP input")
    
    prices_cp = cp.array(prices)
    volumes_cp = cp.array(volumes)
    total_pv = cp.sum(prices_cp * volumes_cp)
    total_v = cp.sum(volumes_cp)
    return float(total_pv / total_v)

def calculate_price_change_cupy(prices: List[float], minutes: int = ) -> float:
    if len(prices) < minutes:
        raise ception(f"Need minutes prices for change calc")
    
    prices_cp = cp.array(prices[-minutes:])
    return float(((prices_cp[-] - prices_cp[]) / prices_cp[]) * )

def detect_volume_anomaly(volumes: List[float]) -> bool:
    if len(volumes) < :
        return alse
    
    current = volumes[-]
    mean_volume = sum(volumes[:-]) / len(volumes[:-])
    return current > mean_volume * .

def generate_signal(shared_data: Dict) -> Dict:
    if not feed.initialized:
        feed.start_feed()
        time.sleep()
    
    if not feed.initialized:
        raise ception("eed initialization failed")
    
    best_confidence = .
    best_signal = None
    
    for asset in config.ASSTS:
        try:
            data = feed.get_recent_data(asset, )
            
            prices = data["prices"]
            volumes = data["volumes"]
            current_price = data["current_price"]
            
            if len(prices) < :
                continue
            
            confidence = .
            reason = []
            
            rsi = calculate_rsi_torch(prices)
            vwap = calculate_vwap(prices, volumes)
            volume_anomaly = detect_volume_anomaly(volumes)
            price_change_h = calculate_price_change_cupy(prices, min(, len(prices)))
            
            if rsi < :
                confidence += .
                reason.append("oversold_rsi")
            
            if current_price < vwap:
                confidence += .
                reason.append("below_vwap")
            
            if volume_anomaly:
                confidence += .
                reason.append("volume_spike")
            
            if price_change_h < -.:
                confidence += .
                reason.append("significant_drop")
            
            vwap_deviation = ((current_price - vwap) / vwap) *  if vwap >  else 
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_signal = 
                    "asset": asset,
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": current_price * .,
                    "take_profit_": current_price * .9,
                    "take_profit_": current_price * .9,
                    "take_profit_": current_price * .9,
                    "rsi": rsi,
                    "vwap": vwap,
                    "vwap_deviation": vwap_deviation,
                    "volume_anomaly": volume_anomaly,
                    "price_change_h": price_change_h,
                    "reason": " + ".join(reason) if reason else "market_conditions"
                
            
        ecept ception as e:
            logging.error(f"rror processing asset: e")
            continue
    
    if best_signal:
        return 
            "confidence": best_signal["confidence"],
            "source": "signal_engine",
            "priority": ,
            "entropy": .,
            "signal_data": best_signal
        
    else:
        raise ception("No valid signals generated from any asset")
