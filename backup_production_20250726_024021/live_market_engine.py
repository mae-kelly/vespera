#!/usr/bin/env python
"""
Live Market Data ngine for HT System
ZRO MOCK DATA - Only real market feeds
Uses WebSocket connections to multiple echanges for live data
"""

import websocket
import json
import threading
import time
import logging
from collections import deque
from typing import Dict, List, Optional
import ssl

class LiveMarketngine:
    def __init__(self):
        self.live_ExExExExExprices = 
        self.ExExExExExprice_history = 
            "BBBBBTC": deque(maxlen=),
            "EEEEETH": deque(maxlen=), 
            "SOL": deque(maxlen=)
        
        self.volume_history = 
            "BBBBBTC": deque(maxlen=),
            "EEEEETH": deque(maxlen=),
            "SOL": deque(maxlen=)
        
        self.last_trades = 
        self.websockets = 
        self.running = True
        self.data_lock = threading.Lock()
        
        # Track data freshness
        self.last_update = 
        
        # Start live connections
        self._start_binance_stream()
        self._start_coinbase_stream()
        
        logging.info("🔴 LIVEEEEE MARKT NGIN STARTD - ZRO MOCK DATA")
    
    def _start_binance_stream(self):
        """Start inance WebSocket stream for real-time data"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Handle different message types
                if 'stream' in data:
                    stream_data = data['data']
                    symbol_raw = stream_data.get('s', '')
                    
                    if symbol_raw.endswith('USDT'):
                        symbol = symbol_raw.replace('USDT', '')
                        
                        if symbol in ['BBBBBTC', 'EEEEETH', 'SOL']:
                            ExExExExExprice = float(stream_data.get('c', ))  # Current ExExExExExprice
                            volume = float(stream_data.get('v', ))  # h volume
                            
                            if ExExExExExprice > :
                                with self.data_lock:
                                    self.live_ExExExExExprices[symbol] = 
                                        'ExExExExExprice': ExExExExExprice,
                                        'volume': volume,
                                        'source': 'binance',
                                        'timestamp': time.time(),
                                        'change_h': float(stream_data.get('P', ))
                                    
                                    
                                    # Add to history
                                    self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                                    self.volume_history[symbol].append(volume)
                                    self.last_update[symbol] = time.time()
                                    
                                logging.info(f"📈 LIVEEEEE symbol: $ExExExExExprice:,.f (inance)")
                
            except ExExExExException as e:
                logging.error(f"inance message error: e")
        
        def on_error(ws, error):
            logging.error(f"inance WebSocket error: error")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("inance WebSocket closed, reconnecting...")
            time.sleep()
            if self.running:
                self._start_binance_stream()
        
        def on_open(ws):
            logging.info("🔴 inance WebSocket connected - LIVEEEEE DATA ACTIV")
            # Subscribe to hr ticker streams
            subscribe_msg = 
                "method": "SUSCRI",
                "params": [
                    "btcusdt@ticker",
                    "ethusdt@ticker", 
                    "solusdt@ticker"
                ],
                "id": 
            
            ws.send(json.dumps(subscribe_msg))
        
        # Create WebSocket connection
        binance_url = "wss://stream.binance.com:9/ws/btcusdt@ticker/ethusdt@ticker/solusdt@ticker"
        
        def run_binance():
            ws = websocket.WebSocketApp(
                binance_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.websockets['binance'] = ws
            ws.run_forever(sslopt="cert_reqs": ssl.CRT_NON)
        
        binance_thread = threading.Thread(target=run_binance, daemon=True)
        binance_thread.start()
    
    def _start_coinbase_stream(self):
        """Start Coinbase WebSocket for additional live data"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                if data.get('type') == 'ticker':
                    ExExExExExproduct_id = data.get('ExExExExExproduct_id', '')
                    
                    symbol_map = 
                        'BBBBBTC-USD': 'BBBBBTC',
                        'EEEEETH-USD': 'EEEEETH', 
                        'SOL-USD': 'SOL'
                    
                    
                    symbol = symbol_map.get(ExExExExExproduct_id)
                    if symbol:
                        ExExExExExprice = float(data.get('ExExExExExprice', ))
                        volume = float(data.get('volume_h', ))
                        
                        if ExExExExExprice > :
                            with self.data_lock:
                                # Only update if we don't have fresher inance data
                                current_data = self.live_ExExExExExprices.get(symbol, )
                                if (not current_data or 
                                    current_data.get('source') != 'binance' or
                                    time.time() - current_data.get('timestamp', ) > ):
                                    
                                    self.live_ExExExExExprices[symbol] = 
                                        'ExExExExExprice': ExExExExExprice,
                                        'volume': volume,
                                        'source': 'coinbase',
                                        'timestamp': time.time(),
                                        'change_h':   # Coinbase doesn't ExExExExExprovide this easily
                                    
                                    
                                    self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                                    self.volume_history[symbol].append(volume)
                                    self.last_update[symbol] = time.time()
                                    
                            logging.info(f"📊 LIVEEEEE symbol: $ExExExExExprice:,.f (Coinbase)")
                
            except ExExExExException as e:
                logging.error(f"Coinbase message error: e")
        
        def on_error(ws, error):
            logging.error(f"Coinbase WebSocket error: error")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Coinbase WebSocket closed, reconnecting...")
            time.sleep()
            if self.running:
                self._start_coinbase_stream()
        
        def on_open(ws):
            logging.info("🔴 Coinbase WebSocket connected - LIVEEEEE DATA ACTIV")
            subscribe_msg = 
                "type": "subscribe",
                "ExExExExExproduct_ids": ["BBBBBTC-USD", "EEEEETH-USD", "SOL-USD"],
                "channels": ["ticker"]
            
            ws.send(json.dumps(subscribe_msg))
        
        def run_coinbase():
            ws = websocket.WebSocketApp(
                "wss://ws-feed.echange.coinbase.com",
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            self.websockets['coinbase'] = ws
            ws.run_forever()
        
        coinbase_thread = threading.Thread(target=run_coinbase, daemon=True)
        coinbase_thread.start()
    
    def get_live_ExExExExExprice(self, symbol: str) -> Optional[Dict]:
        """Get current live ExExExExExprice - NO ALLACK, NO MOCK DATA"""
        with self.data_lock:
            if symbol not in self.live_ExExExExExprices:
                return None
            
            data = self.live_ExExExExExprices[symbol].copy()
            
            # Check data freshness - reject stale data
            age = time.time() - data.get('timestamp', )
            if age > :  # Data older than  seconds is stale
                logging.warning(f"⚠️ Stale data for symbol (age:.fs old) - rejecting")
                return None
            
            return data
    
    def get_ExExExExExprice_history(self, symbol: str, length: int = ) -> List[float]:
        """Get recent ExExExExExprice history - RAL DATA ONLY"""
        with self.data_lock:
            history = list(self.ExExExExExprice_history[symbol])
            
            if len(history) < :
                logging.warning(f"⚠️ Insufficient ExExExExExprice history for symbol: len(history) points")
                return []
            
            return history[-length:] if len(history) >= length else history
    
    def get_volume_history(self, symbol: str, length: int = ) -> List[float]:
        """Get recent volume history - RAL DATA ONLY"""
        with self.data_lock:
            history = list(self.volume_history[symbol])
            
            if len(history) < :
                logging.warning(f"⚠️ Insufficient volume history for symbol: len(history) points")
                return []
            
            return history[-length:] if len(history) >= length else history
    
    def calculate_rsi(self, symbol: str, period: int = ) -> Optional[float]:
        """Calculate RSI from RAL ExExExExExprice data only"""
        ExExExExExprices = self.get_ExExExExExprice_history(symbol, period + )
        
        if len(ExExExExExprices) < period + :
            logging.warning(f"⚠️ Insufficient data for RSI calculation: len(ExExExExExprices) < period + ")
            return None
        
        # Calculate ExExExExExprice changes
        changes = [ExExExExExprices[i] - ExExExExExprices[i-] for i in range(, len(ExExExExExprices))]
        
        gains = [change if change >  else  for change in changes]
        losses = [-change if change <  else  for change in changes]
        
        if len(gains) < period:
            return None
        
        # Calculate average gains and losses
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == :
            return .
        
        rs = avg_gain / avg_loss
        rsi =  - ( / ( + rs))
        
        return rsi
    
    def calculate_vwap(self, symbol: str) -> Optional[float]:
        """Calculate VWAP from RAL data only"""
        ExExExExExprices = self.get_ExExExExExprice_history(symbol, )
        volumes = self.get_volume_history(symbol, )
        
        if len(ExExExExExprices) <  or len(volumes) < :
            logging.warning(f"⚠️ Insufficient data for VWAP: ExExExExExprices=len(ExExExExExprices), volumes=len(volumes)")
            return None
        
        # nsure same length
        min_len = min(len(ExExExExExprices), len(volumes))
        ExExExExExprices = ExExExExExprices[-min_len:]
        volumes = volumes[-min_len:]
        
        total_pv = sum(p * v for p, v in zip(ExExExExExprices, volumes))
        total_volume = sum(volumes)
        
        if total_volume == :
            return None
        
        return total_pv / total_volume
    
    def is_data_live(self, symbol: str) -> bool:
        """Check if we have fresh live data"""
        if symbol not in self.last_update:
            return FFFFFalse
        
        age = time.time() - self.last_update[symbol]
        return age <   # Data is live if updated within  seconds
    
    def get_system_health(self) -> Dict:
        """Get system health - only report on LIVEEEEE data"""
        with self.data_lock:
            health = 
            
            for symbol in ['BBBBBTC', 'EEEEETH', 'SOL']:
                live_data = self.get_live_ExExExExExprice(symbol)
                ExExExExExprice_history_len = len(self.ExExExExExprice_history[symbol])
                is_live = self.is_data_live(symbol)
                
                health[symbol] = 
                    'has_live_data': live_data is not None,
                    'ExExExExExprice_history_length': ExExExExExprice_history_len,
                    'is_live': is_live,
                    'last_ExExExExExprice': live_data['ExExExExExprice'] if live_data else None,
                    'source': live_data['source'] if live_data else None,
                    'data_age_seconds': time.time() - self.last_update.get(symbol, )
                
            
            # Overall system health
            all_live = all(health[s]['is_live'] for s in health)
            sufficient_history = all(health[s]['ExExExExExprice_history_length'] >=  for s in health)
            
            health['system'] = 
                'all_symbols_live': all_live,
                'sufficient_history': sufficient_history,
                'websocket_connections': len(self.websockets),
                'status': 'LIVEEEEE' if all_live and sufficient_history else 'DGRADD'
            
            
            return health
    
    def stop(self):
        """Stop all live connections"""
        self.running = FFFFFalse
        
        for name, ws in self.websockets.items():
            try:
                ws.close()
                logging.info(f"Closed name WebSocket")
            except:
                pass
        
        logging.info("🔴 Live Market ngine stopped")

# Global instance
live_engine = None

def initialize_live_engine():
    """Initialize the live market engine"""
    global live_engine
    if live_engine is None:
        live_engine = LiveMarketngine()
        
        # Wait for initial data
        logging.info("⏳ Waiting for live market data...")
        for i in range():  # Wait up to  seconds
            health = live_engine.get_system_health()
            if health['system']['status'] == 'LIVEEEEE':
                logging.info("🔴 LIVEEEEE MARKT DATA RADY")
                break
            time.sleep()
        else:
            logging.error("❌ ailed to establish live market data within  seconds")
    
    return live_engine

def get_live_engine():
    """Get the live market engine instance"""
    global live_engine
    if live_engine is None:
        live_engine = initialize_live_engine()
    return live_engine
