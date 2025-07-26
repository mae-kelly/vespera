import asyncio
import json
import time
import logging
import requests
import websockets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
import threading
from concurrent.futures import ThreadPoolExecutor
import csv
import os
import math
from enum import Enum

class ExitReason(Enum):
    TAKE_PROFIT = "take_profit"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"
    TIME_DECAY = "time_decay"
    VOLUME_SPIKE = "volume_spike"
    WHALE_SELL = "whale_sell"
    MARKET_CRASH = "market_crash"
    MANUAL_EXIT = "manual_exit"

@dataclass
class Position:
    token_address: str
    entry_price: float
    current_price: float
    quantity: float
    entry_time: float
    last_update: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    stop_loss: float
    take_profit_levels: List[float]
    trailing_stop: float
    max_price_seen: float
    original_wallet: str
    confidence_score: float
    is_active: bool = True

@dataclass
class ExitExecution:
    position_id: str
    token_address: str
    exit_price: float
    quantity_sold: float
    realized_pnl: float
    realized_pnl_pct: float
    exit_reason: ExitReason
    execution_time: float
    tx_hash: str
    gas_used: int
    slippage_actual: float

class PriceOracle:
    def __init__(self):
        self.okx_api_base = "https://www.okx.com/api/v5"
        self.dexscreener_base = "https://api.dexscreener.com/latest"
        self.price_cache = {}
        self.cache_ttl = 5
        
    async def get_token_price(self, token_address: str) -> Optional[float]:
        cache_key = token_address.lower()
        current_time = time.time()
        
        if cache_key in self.price_cache:
            cached_price, cached_time = self.price_cache[cache_key]
            if current_time - cached_time < self.cache_ttl:
                return cached_price
        
        price = await self._fetch_price_from_multiple_sources(token_address)
        if price:
            self.price_cache[cache_key] = (price, current_time)
        
        return price
    
    async def _fetch_price_from_multiple_sources(self, token_address: str) -> Optional[float]:
        sources = [
            self._get_okx_price,
            self._get_dexscreener_price,
            self._get_uniswap_price
        ]
        
        prices = []
        for source in sources:
            try:
                price = await source(token_address)
                if price and price > 0:
                    prices.append(price)
            except Exception:
                continue
        
        if not prices:
            return None
        
        if len(prices) == 1:
            return prices[0]
        
        prices.sort()
        if len(prices) >= 3:
            return prices[len(prices)//2]
        else:
            return sum(prices) / len(prices)
    
    async def _get_okx_price(self, token_address: str) -> Optional[float]:
        url = f"{self.okx_api_base}/market/ticker"
        params = {"instId": f"{token_address}-ETH"}
        
        try:
            response = requests.get(url, params=params, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "0" and data.get("data"):
                    return float(data["data"][0]["last"])
        except Exception:
            pass
        return None
    
    async def _get_dexscreener_price(self, token_address: str) -> Optional[float]:
        url = f"{self.dexscreener_base}/dex/tokens/{token_address}"
        
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                if pairs and pairs[0].get("priceUsd"):
                    return float(pairs[0]["priceUsd"])
        except Exception:
            pass
        return None
    
    async def _get_uniswap_price(self, token_address: str) -> Optional[float]:
        return None

class TechnicalAnalyzer:
    def __init__(self):
        self.price_history = {}
        self.volume_history = {}
        
    def add_price_data(self, token_address: str, price: float, volume: float, timestamp: float):
        if token_address not in self.price_history:
            self.price_history[token_address] = []
            self.volume_history[token_address] = []
        
        self.price_history[token_address].append((timestamp, price))
        self.volume_history[token_address].append((timestamp, volume))
        
        max_history = 200
        if len(self.price_history[token_address]) > max_history:
            self.price_history[token_address] = self.price_history[token_address][-max_history:]
            self.volume_history[token_address] = self.volume_history[token_address][-max_history:]
    
    def calculate_rsi(self, token_address: str, period: int = 14) -> Optional[float]:
        if token_address not in self.price_history:
            return None
        
        prices = [p[1] for p in self.price_history[token_address]]
        if len(prices) < period + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [max(0, delta) for delta in deltas]
        losses = [max(0, -delta) for delta in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def detect_volume_spike(self, token_address: str) -> bool:
        if token_address not in self.volume_history:
            return False
        
        volumes = [v[1] for v in self.volume_history[token_address]]
        if len(volumes) < 20:
            return False
        
        recent_volume = volumes[-1]
        avg_volume = sum(volumes[-20:-1]) / 19
        
        return recent_volume > avg_volume * 3.0
    
    def detect_price_momentum(self, token_address: str) -> float:
        if token_address not in self.price_history:
            return 0.0
        
        prices = [p[1] for p in self.price_history[token_address]]
        if len(prices) < 10:
            return 0.0
        
        short_ma = sum(prices[-5:]) / 5
        long_ma = sum(prices[-10:]) / 10
        
        return (short_ma - long_ma) / long_ma

class ExitStrategyEngine:
    def __init__(self):
        self.strategies = {
            "scalping": self._scalping_strategy,
            "swing": self._swing_strategy,
            "momentum": self._momentum_strategy,
            "mean_reversion": self._mean_reversion_strategy
        }
    
    def determine_exit_action(self, position: Position, market_data: Dict) -> Tuple[bool, ExitReason, float]:
        rsi = market_data.get("rsi", 50)
        volume_spike = market_data.get("volume_spike", False)
        momentum = market_data.get("momentum", 0)
        
        hold_time_hours = (time.time() - position.entry_time) / 3600
        
        if position.unrealized_pnl_pct >= 50.0:
            return True, ExitReason.TAKE_PROFIT, 1.0
        
        if position.current_price <= position.stop_loss:
            return True, ExitReason.STOP_LOSS, 1.0
        
        if position.current_price <= position.trailing_stop:
            return True, ExitReason.TRAILING_STOP, 1.0
        
        if hold_time_hours > 24 and position.unrealized_pnl_pct < 5.0:
            return True, ExitReason.TIME_DECAY, 1.0
        
        if volume_spike and position.unrealized_pnl_pct > 20.0:
            return True, ExitReason.VOLUME_SPIKE, 0.5
        
        if rsi > 80 and position.unrealized_pnl_pct > 15.0:
            return True, ExitReason.TAKE_PROFIT, 0.7
        
        if momentum < -0.05 and position.unrealized_pnl_pct > 10.0:
            return True, ExitReason.TAKE_PROFIT, 0.3
        
        return False, None, 0.0
    
    def _scalping_strategy(self, position: Position) -> Tuple[bool, float]:
        if position.unrealized_pnl_pct >= 3.0:
            return True, 1.0
        if position.unrealized_pnl_pct <= -1.5:
            return True, 1.0
        return False, 0.0
    
    def _swing_strategy(self, position: Position) -> Tuple[bool, float]:
        if position.unrealized_pnl_pct >= 25.0:
            return True, 0.5
        if position.unrealized_pnl_pct >= 50.0:
            return True, 1.0
        return False, 0.0
    
    def _momentum_strategy(self, position: Position) -> Tuple[bool, float]:
        if position.unrealized_pnl_pct >= 15.0:
            return True, 0.3
        return False, 0.0
    
    def _mean_reversion_strategy(self, position: Position) -> Tuple[bool, float]:
        if position.unrealized_pnl_pct >= 8.0:
            return True, 1.0
        return False, 0.0

class TrailingStopManager:
    def __init__(self):
        self.trailing_distances = {
            "conservative": 0.05,
            "moderate": 0.08,
            "aggressive": 0.12
        }
    
    def update_trailing_stop(self, position: Position, style: str = "moderate") -> float:
        distance = self.trailing_distances.get(style, 0.08)
        
        if position.current_price > position.max_price_seen:
            position.max_price_seen = position.current_price
        
        new_trailing_stop = position.max_price_seen * (1 - distance)
        
        if new_trailing_stop > position.trailing_stop:
            position.trailing_stop = new_trailing_stop
        
        return position.trailing_stop

class OKXExecutor:
    def __init__(self, api_key: str, secret_key: str, passphrase: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        
    async def execute_sell_order(self, token_address: str, quantity: float, price_limit: Optional[float] = None) -> Optional[Dict]:
        order_data = {
            "instId": f"{token_address}-ETH",
            "tdMode": "cash",
            "side": "sell",
            "ordType": "market" if not price_limit else "limit",
            "sz": str(quantity)
        }
        
        if price_limit:
            order_data["px"] = str(price_limit)
        
        try:
            response = await self._make_authenticated_request("POST", "/api/v5/trade/order", order_data)
            if response and response.get("code") == "0":
                return response.get("data", [{}])[0]
        except Exception as e:
            logging.error(f"Sell order execution failed: {e}")
        
        return None
    
    async def _make_authenticated_request(self, method: str, endpoint: str, data: Dict) -> Optional[Dict]:
        import hmac
        import hashlib
        import base64
        
        timestamp = str(int(time.time() * 1000))
        body = json.dumps(data) if data else ""
        message = f"{timestamp}{method}{endpoint}{body}"
        
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(f"{self.base_url}{endpoint}", headers=headers, data=body, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        return None

class PositionTracker:
    def __init__(self):
        self.positions = {}
        self.closed_positions = []
        self.position_file = "active_positions.json"
        self.closed_file = "closed_positions.json"
        self._load_positions()
    
    def _load_positions(self):
        try:
            with open(self.position_file, "r") as f:
                data = json.load(f)
                for pos_data in data.get("positions", []):
                    position = Position(**pos_data)
                    self.positions[position.token_address] = position
        except FileNotFoundError:
            pass
        
        try:
            with open(self.closed_file, "r") as f:
                self.closed_positions = json.load(f).get("positions", [])
        except FileNotFoundError:
            pass
    
    def add_position(self, position: Position):
        self.positions[position.token_address] = position
        self._save_positions()
    
    def update_position(self, token_address: str, current_price: float):
        if token_address in self.positions:
            position = self.positions[token_address]
            position.current_price = current_price
            position.last_update = time.time()
            
            pnl = (current_price - position.entry_price) * position.quantity
            position.unrealized_pnl = pnl
            position.unrealized_pnl_pct = (pnl / (position.entry_price * position.quantity)) * 100
            
            self._save_positions()
    
    def close_position(self, token_address: str, exit_execution: ExitExecution):
        if token_address in self.positions:
            position = self.positions.pop(token_address)
            position.is_active = False
            
            closed_position = {
                "position": asdict(position),
                "exit_execution": asdict(exit_execution)
            }
            
            self.closed_positions.append(closed_position)
            self._save_positions()
            return position
        return None
    
    def get_active_positions(self) -> List[Position]:
        return list(self.positions.values())
    
    def _save_positions(self):
        active_data = {
            "positions": [asdict(pos) for pos in self.positions.values()],
            "last_updated": time.time()
        }
        
        with open(self.position_file, "w") as f:
            json.dump(active_data, f, indent=2)
        
        closed_data = {
            "positions": self.closed_positions,
            "last_updated": time.time()
        }
        
        with open(self.closed_file, "w") as f:
            json.dump(closed_data, f, indent=2)

class ExitManager:
    def __init__(self):
        self.price_oracle = PriceOracle()
        self.technical_analyzer = TechnicalAnalyzer()
        self.exit_strategy = ExitStrategyEngine()
        self.trailing_stop_manager = TrailingStopManager()
        self.position_tracker = PositionTracker()
        
        self.okx_executor = OKXExecutor(
            os.getenv("OKX_API_KEY"),
            os.getenv("OKX_SECRET_KEY"),
            os.getenv("OKX_PASSPHRASE")
        )
        
        self.running = False
        self.monitor_interval = 2.0
        self.executor = ThreadPoolExecutor(max_workers=8)
        
    async def add_position_from_entry(self, entry_data: Dict):
        position = Position(
            token_address=entry_data["token_address"],
            entry_price=entry_data["entry_price"],
            current_price=entry_data["entry_price"],
            quantity=entry_data["quantity"],
            entry_time=entry_data["timestamp"],
            last_update=time.time(),
            unrealized_pnl=0.0,
            unrealized_pnl_pct=0.0,
            stop_loss=entry_data.get("stop_loss", entry_data["entry_price"] * 0.9),
            take_profit_levels=entry_data.get("take_profit_levels", [
                entry_data["entry_price"] * 1.1,
                entry_data["entry_price"] * 1.25,
                entry_data["entry_price"] * 1.5
            ]),
            trailing_stop=entry_data["entry_price"] * 0.95,
            max_price_seen=entry_data["entry_price"],
            original_wallet=entry_data.get("wallet_followed", "unknown"),
            confidence_score=entry_data.get("confidence_score", 0.5)
        )
        
        self.position_tracker.add_position(position)
        logging.info(f"Added position for tracking: {position.token_address}")
    
    async def monitor_positions(self):
        self.running = True
        logging.info("Starting exit manager monitoring...")
        
        while self.running:
            try:
                active_positions = self.position_tracker.get_active_positions()
                
                if not active_positions:
                    await asyncio.sleep(self.monitor_interval)
                    continue
                
                tasks = []
                for position in active_positions:
                    task = asyncio.create_task(self._evaluate_position(position))
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                logging.error(f"Position monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _evaluate_position(self, position: Position):
        try:
            current_price = await self.price_oracle.get_token_price(position.token_address)
            if not current_price:
                return
            
            self.position_tracker.update_position(position.token_address, current_price)
            
            volume_spike = self.technical_analyzer.detect_volume_spike(position.token_address)
            rsi = self.technical_analyzer.calculate_rsi(position.token_address)
            momentum = self.technical_analyzer.detect_price_momentum(position.token_address)
            
            self.technical_analyzer.add_price_data(
                position.token_address, 
                current_price, 
                0.0,
                time.time()
            )
            
            self.trailing_stop_manager.update_trailing_stop(position)
            
            market_data = {
                "rsi": rsi,
                "volume_spike": volume_spike,
                "momentum": momentum
            }
            
            should_exit, exit_reason, exit_percentage = self.exit_strategy.determine_exit_action(
                position, market_data
            )
            
            if should_exit:
                await self._execute_exit(position, exit_reason, exit_percentage)
                
        except Exception as e:
            logging.error(f"Position evaluation error for {position.token_address}: {e}")
    
    async def _execute_exit(self, position: Position, exit_reason: ExitReason, exit_percentage: float):
        try:
            quantity_to_sell = position.quantity * exit_percentage
            
            execution_result = await self.okx_executor.execute_sell_order(
                position.token_address,
                quantity_to_sell
            )
            
            if not execution_result:
                logging.error(f"Failed to execute exit for {position.token_address}")
                return
            
            exit_price = float(execution_result.get("avgPx", position.current_price))
            realized_pnl = (exit_price - position.entry_price) * quantity_to_sell
            realized_pnl_pct = (realized_pnl / (position.entry_price * quantity_to_sell)) * 100
            
            exit_execution = ExitExecution(
                position_id=position.token_address,
                token_address=position.token_address,
                exit_price=exit_price,
                quantity_sold=quantity_to_sell,
                realized_pnl=realized_pnl,
                realized_pnl_pct=realized_pnl_pct,
                exit_reason=exit_reason,
                execution_time=time.time(),
                tx_hash=execution_result.get("ordId", ""),
                gas_used=0,
                slippage_actual=0.0
            )
            
            if exit_percentage >= 1.0:
                self.position_tracker.close_position(position.token_address, exit_execution)
                logging.info(f"Closed position {position.token_address}: {exit_reason.value} | PnL: {realized_pnl_pct:.2f}%")
            else:
                position.quantity -= quantity_to_sell
                logging.info(f"Partial exit {position.token_address}: {exit_percentage:.1%} | PnL: {realized_pnl_pct:.2f}%")
            
            self._log_exit(exit_execution)
            
        except Exception as e:
            logging.error(f"Exit execution error: {e}")
    
    def _log_exit(self, exit_execution: ExitExecution):
        log_entry = asdict(exit_execution)
        
        try:
            with open("exit_log.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(log_entry)
        except Exception as e:
            logging.error(f"Failed to log exit: {e}")
    
    def stop_monitoring(self):
        self.running = False
        self.executor.shutdown(wait=True)
        logging.info("Exit manager stopped")

def schedule_exit(trade_data: Dict):
    exit_manager = ExitManager()
    asyncio.create_task(exit_manager.add_position_from_entry(trade_data))

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    exit_manager = ExitManager()
    
    try:
        await exit_manager.monitor_positions()
    except KeyboardInterrupt:
        logging.info("Shutting down exit manager...")
        exit_manager.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
