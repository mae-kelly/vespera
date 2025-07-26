import time
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import config

@dataclass
class PaperPosition:
    """Represents a paper trading position"""
    id: str
    asset: str
    side: str  # "buy" or "sell"
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    entry_time: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    status: str = "open"  # open, closed, stopped_out
    
    def update_pnl(self, current_price: float):
        """Update unrealized PnL based on current price"""
        self.current_price = current_price
        if self.side == "sell":  # Short position
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
        else:  # Long position
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity

@dataclass
class PaperTrade:
    """Represents a completed paper trade"""
    asset: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    commission: float
    entry_time: float
    exit_time: float
    exit_reason: str  # "take_profit", "stop_loss", "manual"

class PaperTradingEngine:
    """Paper trading engine with real market data"""
    
    def __init__(self):
        self.balance = config.PAPER_INITIAL_BALANCE
        self.initial_balance = config.PAPER_INITIAL_BALANCE
        self.positions: Dict[str, PaperPosition] = {}
        self.trade_history: List[PaperTrade] = []
        self.total_trades = 0
        self.winning_trades = 0
        self.total_commission = 0.0
        self.max_drawdown = 0.0
        self.peak_balance = self.balance
        
        # Daily limits
        self.daily_trades = defaultdict(int)
        self.last_trade_date = ""
        
        logging.info(f"📄 Paper trading engine initialized with ${self.balance:,.2f}")
    
    def get_position_size(self, price: float) -> float:
        """Calculate position size based on available balance"""
        max_position_value = self.balance * config.POSITION_SIZE_PERCENT
        return max_position_value / price
    
    def can_open_position(self, asset: str) -> bool:
        """Check if we can open a new position"""
        # Check if position already exists
        if asset in self.positions:
            return False
        
        # Check max open positions
        if len(self.positions) >= config.MAX_OPEN_POSITIONS:
            return False
        
        # Check daily trade limit
        today = time.strftime("%Y-%m-%d")
        if self.daily_trades[today] >= 10:  # 10 trades per day limit
            return False
        
        # Check drawdown
        current_drawdown = (self.peak_balance - self.balance) / self.peak_balance * 100
        if current_drawdown >= config.MAX_DRAWDOWN_PERCENT:
            return False
        
        return True
    
    def open_position(self, signal_data: Dict) -> Optional[Dict]:
        """Open a paper trading position"""
        signal = signal_data.get("signal_data", {})
        asset = signal.get("asset")
        entry_price = signal.get("entry_price")
        stop_loss = signal.get("stop_loss")
        take_profit = signal.get("take_profit_1")
        
        if not all([asset, entry_price, stop_loss, take_profit]):
            logging.error("Invalid signal data for position opening")
            return None
        
        if not self.can_open_position(asset):
            logging.warning(f"Cannot open position for {asset}")
            return None
        
        # Calculate position size
        quantity = self.get_position_size(entry_price)
        position_value = quantity * entry_price
        commission = position_value * config.PAPER_COMMISSION_RATE
        
        # Check if we have enough balance
        if position_value + commission > self.balance:
            logging.warning(f"Insufficient balance for {asset} position")
            return None
        
        # Create position
        position_id = f"{asset}_{int(time.time())}"
        position = PaperPosition(
            id=position_id,
            asset=asset,
            side=signal.get("signal_type", "SHORT").lower().replace("short", "sell").replace("long", "buy"),
            entry_price=entry_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=time.time(),
            current_price=entry_price
        )
        
        # Deduct from balance (commission only, since this is paper trading)
        self.balance -= commission
        self.total_commission += commission
        
        # Store position
        self.positions[asset] = position
        
        # Update daily trade count
        today = time.strftime("%Y-%m-%d")
        self.daily_trades[today] += 1
        self.total_trades += 1
        
        logging.info(f"📄 PAPER POSITION OPENED: {asset} {position.side} @ ${entry_price:.2f} (qty: {quantity:.6f})")
        
        return {
            "position_id": position_id,
            "asset": asset,
            "side": position.side,
            "entry_price": entry_price,
            "quantity": quantity,
            "commission": commission,
            "status": "opened"
        }
    
    def update_positions(self, market_prices: Dict[str, float]):
        """Update all positions with current market prices"""
        positions_to_close = []
        
        for asset, position in self.positions.items():
            if asset in market_prices:
                current_price = market_prices[asset]
                position.update_pnl(current_price)
                
                # Check stop loss and take profit
                if position.side == "sell":  # Short position
                    if current_price >= position.stop_loss:
                        positions_to_close.append((asset, "stop_loss", current_price))
                    elif current_price <= position.take_profit:
                        positions_to_close.append((asset, "take_profit", current_price))
                else:  # Long position
                    if current_price <= position.stop_loss:
                        positions_to_close.append((asset, "stop_loss", current_price))
                    elif current_price >= position.take_profit:
                        positions_to_close.append((asset, "take_profit", current_price))
        
        # Close positions that hit stops
        for asset, reason, exit_price in positions_to_close:
            self.close_position(asset, reason, exit_price)
    
    def close_position(self, asset: str, reason: str, exit_price: float) -> Optional[Dict]:
        """Close a paper trading position"""
        if asset not in self.positions:
            return None
        
        position = self.positions[asset]
        position.current_price = exit_price
        position.update_pnl(exit_price)
        
        # Calculate final P&L
        pnl = position.unrealized_pnl
        commission = position.quantity * exit_price * config.PAPER_COMMISSION_RATE
        net_pnl = pnl - commission
        
        # Update balance
        self.balance += net_pnl
        self.total_commission += commission
        
        # Track statistics
        if net_pnl > 0:
            self.winning_trades += 1
        
        # Update peak balance and drawdown
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance
        
        current_drawdown = (self.peak_balance - self.balance) / self.peak_balance * 100
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        # Create trade record
        trade = PaperTrade(
            asset=asset,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            pnl=net_pnl,
            commission=commission,
            entry_time=position.entry_time,
            exit_time=time.time(),
            exit_reason=reason
        )
        
        self.trade_history.append(trade)
        
        # Remove position
        del self.positions[asset]
        
        logging.info(f"📄 PAPER POSITION CLOSED: {asset} {reason} @ ${exit_price:.2f} | P&L: ${net_pnl:.2f}")
        
        return {
            "asset": asset,
            "exit_reason": reason,
            "exit_price": exit_price,
            "pnl": net_pnl,
            "commission": commission,
            "status": "closed"
        }
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        total_value = self.balance + total_unrealized_pnl
        
        win_rate = (self.winning_trades / max(len(self.trade_history), 1)) * 100
        
        return {
            "balance": self.balance,
            "unrealized_pnl": total_unrealized_pnl,
            "total_value": total_value,
            "total_return": ((total_value - self.initial_balance) / self.initial_balance) * 100,
            "open_positions": len(self.positions),
            "total_trades": len(self.trade_history),
            "winning_trades": self.winning_trades,
            "win_rate": win_rate,
            "total_commission": self.total_commission,
            "max_drawdown": self.max_drawdown,
            "daily_trades_today": self.daily_trades[time.strftime("%Y-%m-%d")]
        }
    
    def get_positions_display(self) -> List[Dict]:
        """Get positions in display format"""
        return [
            {
                "asset": pos.asset,
                "side": pos.side,
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "quantity": pos.quantity,
                "unrealized_pnl": pos.unrealized_pnl,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit,
                "duration": time.time() - pos.entry_time
            }
            for pos in self.positions.values()
        ]
    
    def save_state(self, filename: str = "/tmp/paper_trading_state.json"):
        """Save paper trading state to file"""
        state = {
            "balance": self.balance,
            "initial_balance": self.initial_balance,
            "positions": [asdict(pos) for pos in self.positions.values()],
            "trade_history": [asdict(trade) for trade in self.trade_history[-50:]],  # Last 50 trades
            "statistics": self.get_portfolio_summary(),
            "timestamp": time.time()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save paper trading state: {e}")

# Global paper trading engine instance
paper_engine = PaperTradingEngine()

def get_paper_engine():
    """Get the global paper trading engine"""
    return paper_engine