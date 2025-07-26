import json
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal
import csv
import os

@dataclass
class CapitalState:
    total_capital: float
    available_capital: float
    deployed_capital: float
    reserved_capital: float
    daily_pnl: float
    total_pnl: float
    max_drawdown: float
    current_drawdown: float
    peak_capital: float
    trades_today: int
    last_update: float

@dataclass
class RiskMetrics:
    position_count: int
    largest_position_pct: float
    total_exposure_pct: float
    avg_hold_time: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_consecutive_losses: int

class CapitalManager:
    def __init__(self, initial_capital: float = 1000.0):
        self.state = CapitalState(
            total_capital=initial_capital,
            available_capital=initial_capital,
            deployed_capital=0.0,
            reserved_capital=initial_capital * 0.1,
            daily_pnl=0.0,
            total_pnl=0.0,
            max_drawdown=0.0,
            current_drawdown=0.0,
            peak_capital=initial_capital,
            trades_today=0,
            last_update=time.time()
        )
        
        self.max_position_size_pct = 0.33
        self.max_total_exposure_pct = 0.85
        self.max_daily_trades = 50
        self.emergency_stop_drawdown = 0.15
        
        self.trade_history = []
        self.positions = {}
        self.daily_stats = {}
        
        self._load_state()
    
    def allocate_capital(self, amount: float, trade_id: str, confidence: float = 0.5) -> bool:
        if not self._can_allocate(amount):
            return False
        
        position_size_limit = self.state.total_capital * self.max_position_size_pct
        if amount > position_size_limit:
            amount = position_size_limit
        
        confidence_multiplier = min(confidence * 1.5, 1.0)
        adjusted_amount = amount * confidence_multiplier
        
        if adjusted_amount > self.state.available_capital:
            return False
        
        self.state.available_capital -= adjusted_amount
        self.state.deployed_capital += adjusted_amount
        self.state.trades_today += 1
        
        self.positions[trade_id] = {
            "amount": adjusted_amount,
            "timestamp": time.time(),
            "confidence": confidence
        }
        
        self._save_state()
        logging.info(f"Allocated ${adjusted_amount:.2f} for trade {trade_id}")
        return True
    
    def release_capital(self, trade_id: str, realized_pnl: float) -> bool:
        if trade_id not in self.positions:
            return False
        
        position = self.positions.pop(trade_id)
        original_amount = position["amount"]
        
        self.state.deployed_capital -= original_amount
        self.state.available_capital += (original_amount + realized_pnl)
        self.state.total_capital += realized_pnl
        self.state.daily_pnl += realized_pnl
        self.state.total_pnl += realized_pnl
        
        if self.state.total_capital > self.state.peak_capital:
            self.state.peak_capital = self.state.total_capital
            self.state.current_drawdown = 0.0
        else:
            self.state.current_drawdown = (self.state.peak_capital - self.state.total_capital) / self.state.peak_capital
            self.state.max_drawdown = max(self.state.max_drawdown, self.state.current_drawdown)
        
        trade_record = {
            "trade_id": trade_id,
            "amount": original_amount,
            "pnl": realized_pnl,
            "pnl_pct": (realized_pnl / original_amount) * 100,
            "timestamp": time.time(),
            "confidence": position["confidence"]
        }
        
        self.trade_history.append(trade_record)
        self._save_state()
        
        logging.info(f"Released ${original_amount:.2f} with PnL ${realized_pnl:.2f} ({(realized_pnl/original_amount)*100:.1f}%)")
        return True
    
    def _can_allocate(self, amount: float) -> bool:
        if amount > self.state.available_capital:
            return False
        
        if self.state.trades_today >= self.max_daily_trades:
            return False
        
        if self.state.current_drawdown >= self.emergency_stop_drawdown:
            return False
        
        future_exposure = (self.state.deployed_capital + amount) / self.state.total_capital
        if future_exposure > self.max_total_exposure_pct:
            return False
        
        return True
    
    def calculate_optimal_position_size(self, confidence: float, volatility: float = 0.02) -> float:
        base_size = self.state.total_capital * 0.02
        
        confidence_factor = min(confidence * 2.0, 1.5)
        volatility_factor = max(0.5, 1.0 - (volatility * 5))
        capital_factor = min(self.state.available_capital / self.state.total_capital, 1.0)
        
        optimal_size = base_size * confidence_factor * volatility_factor * capital_factor
        
        max_position = self.state.total_capital * self.max_position_size_pct
        return min(optimal_size, max_position, self.state.available_capital * 0.9)
    
    def get_capital_summary(self) -> Dict:
        return {
            "total_capital": self.state.total_capital,
            "available_capital": self.state.available_capital,
            "deployed_capital": self.state.deployed_capital,
            "available_pct": (self.state.available_capital / self.state.total_capital) * 100,
            "deployed_pct": (self.state.deployed_capital / self.state.total_capital) * 100,
            "daily_pnl": self.state.daily_pnl,
            "total_pnl": self.state.total_pnl,
            "total_return_pct": (self.state.total_pnl / 1000.0) * 100,
            "current_drawdown_pct": self.state.current_drawdown * 100,
            "max_drawdown_pct": self.state.max_drawdown * 100,
            "trades_today": self.state.trades_today,
            "active_positions": len(self.positions)
        }
    
    def get_risk_metrics(self) -> RiskMetrics:
        if not self.trade_history:
            return RiskMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
        
        winning_trades = [t for t in self.trade_history if t["pnl"] > 0]
        losing_trades = [t for t in self.trade_history if t["pnl"] < 0]
        
        win_rate = len(winning_trades) / len(self.trade_history) if self.trade_history else 0
        
        total_wins = sum(t["pnl"] for t in winning_trades)
        total_losses = abs(sum(t["pnl"] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        returns = [t["pnl_pct"] for t in self.trade_history]
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if len(returns) > 1 else 0
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        
        consecutive_losses = 0
        max_consecutive_losses = 0
        for trade in self.trade_history:
            if trade["pnl"] < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0
        
        position_sizes = [p["amount"] for p in self.positions.values()]
        largest_position_pct = max(position_sizes) / self.state.total_capital * 100 if position_sizes else 0
        total_exposure_pct = self.state.deployed_capital / self.state.total_capital * 100
        
        avg_hold_time = 0.0
        if self.trade_history:
            hold_times = []
            for trade in self.trade_history:
                if trade.get("entry_time") and trade.get("exit_time"):
                    hold_times.append(trade["exit_time"] - trade["entry_time"])
            avg_hold_time = sum(hold_times) / len(hold_times) / 3600 if hold_times else 0
        
        return RiskMetrics(
            position_count=len(self.positions),
            largest_position_pct=largest_position_pct,
            total_exposure_pct=total_exposure_pct,
            avg_hold_time=avg_hold_time,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_consecutive_losses=max_consecutive_losses
        )
    
    def emergency_liquidate_all(self) -> bool:
        if self.state.current_drawdown >= self.emergency_stop_drawdown:
            logging.critical("EMERGENCY LIQUIDATION TRIGGERED")
            
            for trade_id in list(self.positions.keys()):
                self.release_capital(trade_id, -self.positions[trade_id]["amount"] * 0.05)
            
            self.state.available_capital = self.state.total_capital
            self.state.deployed_capital = 0.0
            self._save_state()
            return True
        return False
    
    def _save_state(self):
        state_data = {
            "state": asdict(self.state),
            "positions": self.positions,
            "trade_history": self.trade_history[-1000:],
            "last_saved": time.time()
        }
        
        try:
            with open("capital_state.json", "w") as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save capital state: {e}")
    
    def _load_state(self):
        try:
            with open("capital_state.json", "r") as f:
                data = json.load(f)
                
                if "state" in data:
                    self.state = CapitalState(**data["state"])
                
                if "positions" in data:
                    self.positions = data["positions"]
                
                if "trade_history" in data:
                    self.trade_history = data["trade_history"]
                    
        except FileNotFoundError:
            pass
        except Exception as e:
            logging.error(f"Failed to load capital state: {e}")

def update_position(trade_data: Dict):
    capital_manager = CapitalManager()
    
    trade_id = trade_data.get("tx_hash", f"trade_{int(time.time())}")
    amount = trade_data.get("amount_in_eth", 0.0)
    confidence = trade_data.get("confidence_score", 0.5)
    
    success = capital_manager.allocate_capital(amount, trade_id, confidence)
    
    if success:
        logging.info(f"Capital allocated for trade: {trade_id}")
    else:
        logging.warning(f"Capital allocation failed for trade: {trade_id}")
    
    return success

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = CapitalManager()
    summary = manager.get_capital_summary()
    metrics = manager.get_risk_metrics()
    
    print("Capital Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\nRisk Metrics:")
    for key, value in asdict(metrics).items():
        print(f"  {key}: {value}")
