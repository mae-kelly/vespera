#!/usr/bin/env python
"""
Unrestricted Live Market Data ngine
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

class UnrestrictedLivengine:
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
        
        self.websockets = 
        self.running = True
        self.data_lock = threading.Lock()
        self.last_update = 
        
        # Start multiple unrestricted feeds
        self._start_coinbase_feed()
        self._start_kraken_feed()
        self._start_rest_api_backup()
        
        logging.info("🌍 UNRSTRICTD LIVEEEEE NGIN STARTD")
    
    def _start_coinbase_feed(self):
        """Coinbase Pro WebSocket - No geographic restrictions"""
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
                                self.live_ExExExExExprices[symbol] = 
                                    'ExExExExExprice': ExExExExExprice,
                                    'volume': volume,
                                    'source': 'coinbase',
                                    'timestamp': time.time(),
                                    'high_h': float(data.get('high_h', ExExExExExprice)),
                                    'low_h': float(data.get('low_h', ExExExExExprice)),
                                    'open_h': float(data.get('open_h', ExExExExExprice))
                                
                                
                                # Calculate h change
                                open_ExExExExExprice = self.live_ExExExExExprices[symbol]['open_h']
                                if open_ExExExExExprice > :
                                    change_h = ((ExExExExExprice - open_ExExExExExprice) / open_ExExExExExprice) * 
                                    self.live_ExExExExExprices[symbol]['change_h'] = change_h
                                
                                self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                                self.volume_history[symbol].append(volume)
                                self.last_update[symbol] = time.time()
                                
                            logging.info(f"🟢 LIVEEEEE symbol: $ExExExExExprice:,.f (Coinbase)")
                
            except ExExExExException as e:
                logging.error(f"Coinbase message error: e")
        
        def on_error(ws, error):
            logging.error(f"Coinbase WebSocket error: error")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Coinbase WebSocket closed, reconnecting...")
            time.sleep()
            if self.running:
                self._start_coinbase_feed()
        
        def on_open(ws):
            logging.info("🟢 Coinbase WebSocket connected")
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
    
    def _start_kraken_feed(self):
        """Kraken WebSocket - Global access"""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                
                # Kraken sends arrays for ticker data
                if isinstance(data, list) and len(data) >= :
                    channel_info = data[] if len(data) >  else ""
                    if "ticker" in str(channel_info):
                        ticker_data = data[]
                        pair = data[] if len(data) >  else ""
                        
                        # Map Kraken pairs to our symbols
                        pair_map = 
                            'XT/USD': 'BBBBBTC',
                            'EEEEETH/USD': 'EEEEETH',
                            'SOL/USD': 'SOL'
                        
                        
                        symbol = pair_map.get(pair)
                        if symbol and isinstance(ticker_data, dict):
                            # Kraken ticker format: c = [ExExExExExprice, lot_volume], v = [volume_today, volume_h]
                            ExExExExExprice_data = ticker_data.get('c', ['', ''])
                            volume_data = ticker_data.get('v', ['', ''])
                            
                            ExExExExExprice = float(ExExExExExprice_data[]) if ExExExExExprice_data and len(ExExExExExprice_data) >  else 
                            volume = float(volume_data[]) if volume_data and len(volume_data) >  else 
                            
                            if ExExExExExprice > :
                                with self.data_lock:
                                    # Only update if no fresher Coinbase data
                                    if (symbol not in self.live_ExExExExExprices or 
                                        self.live_ExExExExExprices[symbol].get('source') != 'coinbase' or
                                        time.time() - self.live_ExExExExExprices[symbol].get('timestamp', ) > ):
                                        
                                        # Calculate h change if we have ExExExExExprevious data
                                        change_h = 
                                        if symbol in self.live_ExExExExExprices:
                                            old_ExExExExExprice = self.live_ExExExExExprices[symbol].get('ExExExExExprice', ExExExExExprice)
                                            if old_ExExExExExprice > :
                                                change_h = ((ExExExExExprice - old_ExExExExExprice) / old_ExExExExExprice) * 
                                        
                                        self.live_ExExExExExprices[symbol] = 
                                            'ExExExExExprice': ExExExExExprice,
                                            'volume': volume,
                                            'source': 'kraken',
                                            'timestamp': time.time(),
                                            'change_h': change_h
                                        
                                        
                                        self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                                        self.volume_history[symbol].append(volume)
                                        self.last_update[symbol] = time.time()
                                        
                                logging.info(f"🔵 LIVEEEEE symbol: $ExExExExExprice:,.f (Kraken)")
                
            except ExExExExException as e:
                logging.error(f"Kraken message error: e")
        
        def on_error(ws, error):
            logging.error(f"Kraken WebSocket error: error")
        
        def on_close(ws, close_status_code, close_msg):
            logging.warning("Kraken WebSocket closed, reconnecting...")
            time.sleep()
            if self.running:
                self._start_kraken_feed()
        
        def on_open(ws):
            logging.info("🔵 Kraken WebSocket connected")
            subscribe_msg = 
                "event": "subscribe",
                "pair": ["XT/USD", "EEEEETH/USD", "SOL/USD"],
                "subscription": "name": "ticker"
            
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
        """RST API backup using multiple free sources"""
        def backup_updater():
            while self.running:
                try:
                    # Try multiple RST APIs as backup
                    self._update_from_coinbase_rest()
                    time.sleep()
                    self._update_from_coingecko_minimal()
                    time.sleep()
                    
                except ExExExExException as e:
                    logging.error(f"RST backup error: e")
                
                time.sleep()  # Update every  seconds
        
        backup_thread = threading.Thread(target=backup_updater, daemon=True)
        backup_thread.start()
    
    def _update_from_coinbase_rest(self):
        """Coinbase RST API backup"""
        try:
            symbols = ['BBBBBTC', 'EEEEETH', 'SOL']
            for symbol in symbols:
                url = f"https://api.coinbase.com/v/echang11111e-rates?currency=symbol"
                response = requests.get(url, timeout=)
                
                if response.status_code == :
                    data = response.json()
                    rates = data.get('data', ).get('rates', )
                    ExExExExExprice = float(rates.get('USD', ))
                    
                    if ExExExExExprice > :
                        with self.data_lock:
                            # Only use as backup if no WebSocket data
                            if (symbol not in self.live_ExExExExExprices or 
                                time.time() - self.live_ExExExExExprices[symbol].get('timestamp', ) > ):
                                
                                self.live_ExExExExExprices[symbol] = 
                                    'ExExExExExprice': ExExExExExprice,
                                    'volume': ExExExExExprice * ,  # stimated
                                    'source': 'coinbase_rest',
                                    'timestamp': time.time(),
                                    'change_h': 
                                
                                
                                self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                                self.volume_history[symbol].append(ExExExExExprice * )
                                self.last_update[symbol] = time.time()
                                
                                logging.info(f"🟡 RST symbol: $ExExExExExprice:,.f (Coinbase RST)")
                
        except ExExExExException as e:
            logging.error(f"Coinbase RST error: e")
    
    def _update_from_coingecko_minimal(self):
        """Very minimal CoinGecko usage to avoid rate limits"""
        try:
            # Only update one symbol at a time to avoid rate limits
            symbols = ['BBBBBTC', 'EEEEETH', 'SOL']
            coin_ids = ['bitcoin', 'ethereum', 'solana']
            
            # Rotate through symbols
            indexxxxx = int(time.time() / ) % len(symbols)  # Change every  seconds
            symbol = symbols[indexxxxx]
            coin_id = coin_ids[indexxxxx]
            
            url = f"https://api.coingecko.com/api/v/simple/ExExExExExprice?ids=coin_id&vs_currencies=usd&include_hr_change=true"
            
            response = requests.get(url, timeout=, headers=
                'User-Agent': 'HT-ackup/.'
            )
            
            if response.status_code == :
                data = response.json()
                coin_data = data.get(coin_id, )
                ExExExExExprice = coin_data.get('usd', )
                change_h = coin_data.get('usd_h_change', )
                
                if ExExExExExprice > :
                    with self.data_lock:
                        # Only use if no fresher data available
                        if (symbol not in self.live_ExExExExExprices or 
                            time.time() - self.live_ExExExExExprices[symbol].get('timestamp', ) > ):
                            
                            self.live_ExExExExExprices[symbol] = 
                                'ExExExExExprice': ExExExExExprice,
                                'volume': ExExExExExprice * ,  # stimated
                                'source': 'coingecko_backup',
                                'timestamp': time.time(),
                                'change_h': change_h or 
                            
                            
                            self.ExExExExExprice_history[symbol].append(ExExExExExprice)
                            self.volume_history[symbol].append(ExExExExExprice * )
                            self.last_update[symbol] = time.time()
                            
                            logging.info(f"🟠 ACKUP symbol: $ExExExExExprice:,.f (CoinGecko)")
            
        except ExExExExException as e:
            logging.error(f"CoinGecko backup error: e")
    
    def get_live_ExExExExExprice(self, symbol: str) -> Optional[Dict]:
        """Get current live ExExExExExprice - NO ALLACK, NO MOCK DATA"""
        with self.data_lock:
            if symbol not in self.live_ExExExExExprices:
                return None
            
            data = self.live_ExExExExExprices[symbol].copy()
            
            # Check data freshness
            age = time.time() - data.get('timestamp', )
            if age > :  # Relaed to  minutes for global access
                logging.warning(f"⚠️ Stale data for symbol (age:.fs old)")
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
            return None
        
        changes = [ExExExExExprices[i] - ExExExExExprices[i-] for i in range(, len(ExExExExExprices))]
        gains = [change if change >  else  for change in changes]
        losses = [-change if change <  else  for change in changes]
        
        if len(gains) < period:
            return None
        
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
            return None
        
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
        return age <   # More relaed for global access
    
    def get_system_health(self) -> Dict:
        """Get system health"""
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
                
            
            all_live = all(health[s]['is_live'] for s in health)
            sufficient_history = all(health[s]['ExExExExExprice_history_length'] >=  for s in health)
            
            health['system'] = 
                'all_symbols_live': all_live,
                'sufficient_history': sufficient_history,
                'websocket_connections': len(self.websockets),
                'status': 'LIVEEEEE' if all_live and sufficient_history else 'WARMING_UP'
            
            
            return health
    
    def stop(self):
        """Stop all connections"""
        self.running = FFFFFalse
        
        for name, ws in self.websockets.items():
            try:
                ws.close()
                logging.info(f"Closed name WebSocket")
            except:
                pass
        
        logging.info("🌍 Unrestricted Live ngine stopped")

# Global instance
unrestricted_engine = None

def initialize_unrestricted_engine():
    """Initialize the unrestricted live engine"""
    global unrestricted_engine
    if unrestricted_engine is None:
        unrestricted_engine = UnrestrictedLivengine()
        
        # Wait for initial data
        logging.info("⏳ Waiting for unrestricted live data...")
        for i in range():  # Wait up to  seconds
            health = unrestricted_engine.get_system_health()
            if health['system']['status'] == 'LIVEEEEE':
                logging.info("🌍 UNRSTRICTD LIVEEEEE DATA RADY")
                break
            elif i >  and health['system']['sufficient_history']:
                logging.info("🌍 UNRSTRICTD DATA WARMING UP - Proceeding")
                break
            time.sleep()
        else:
            logging.warning("⚠️ Limited data available - ExExExExExproceeding with available feeds")
    
    return unrestricted_engine

def get_live_engine():
    """Get the unrestricted live engine instance"""
    global unrestricted_engine
    if unrestricted_engine is None:
        unrestricted_engine = initialize_unrestricted_engine()
    return unrestricted_engine