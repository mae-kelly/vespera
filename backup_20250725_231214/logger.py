import logging
import pandas as pd
import os
from typing import Dict, List
import config
import time
from pathlib import Path

def log_signal(signal_data: Dict):
    """Log signal to CSV using pandas with specified format"""
    try:
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        
        # Extract data from signal
        best_signal = signal_data.get("best_signal", {})
        asset = best_signal.get("asset", "Unknown")
        entry_price = best_signal.get("entry_price", 0)
        stop_loss = best_signal.get("stop_loss", 0)
        exit_price = 0  # Will be filled when trade closes
        confidence = signal_data.get("confidence", 0)
        reason = best_signal.get("reason", "market_conditions")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame row
        row_data = {
            "asset": asset,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "exit_price": exit_price,
            "confidence": confidence,
            "reason": reason,
            "timestamp": timestamp
        }
        
        df_new = pd.DataFrame([row_data])
        
        # Append to existing CSV or create new one
        csv_path = "logs/trade_log.csv"
        if os.path.exists(csv_path):
            df_existing = pd.read_csv(csv_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Save to CSV
        df_combined.to_csv(csv_path, index=False)
        
        logging.info(f'Signal logged to CSV: {asset} @ {entry_price:.2f} (confidence: {confidence:.3f})')
        
    except Exception as e:
        logging.error(f"Failed to log signal to CSV: {e}")

def log_trade_execution(trade_data: Dict):
    """Log trade execution to CSV"""
    try:
        Path("logs").mkdir(exist_ok=True)
        
        # Create execution log entry
        execution_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset": trade_data.get("asset", "Unknown"),
            "side": trade_data.get("side", "sell"),
            "entry_price": trade_data.get("entry_price", 0),
            "quantity": trade_data.get("quantity", 0),
            "status": trade_data.get("status", "unknown"),
            "order_id": trade_data.get("order_id", ""),
            "mode": config.MODE
        }
        
        df_new = pd.DataFrame([execution_data])
        
        csv_path = "logs/execution_log.csv"
        if os.path.exists(csv_path):
            df_existing = pd.read_csv(csv_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, index=False)
        
        logging.info(f"Trade execution logged: {execution_data['asset']} {execution_data['status']}")
        
    except Exception as e:
        logging.error(f"Failed to log trade execution: {e}")

def update_trade_exit(asset: str, exit_price: float, pnl: float):
    """Update trade log with exit price and PnL"""
    try:
        csv_path = "logs/trade_log.csv"
        if not os.path.exists(csv_path):
            return
        
        df = pd.read_csv(csv_path)
        
        # Find the most recent open trade for this asset
        asset_trades = df[df['asset'] == asset]
        if len(asset_trades) > 0:
            last_idx = asset_trades.index[-1]
            
            # Update exit price
            df.loc[last_idx, 'exit_price'] = exit_price
            df.loc[last_idx, 'pnl'] = pnl
            df.loc[last_idx, 'exit_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Save updated CSV
            df.to_csv(csv_path, index=False)
            
            logging.info(f"Trade exit logged: {asset} @ {exit_price:.2f} (PnL: {pnl:.2f})")
        
    except Exception as e:
        logging.error(f"Failed to update trade exit: {e}")

def get_trading_stats() -> Dict:
    """Get trading statistics from logs"""
    try:
        csv_path = "logs/trade_log.csv"
        if not os.path.exists(csv_path):
            return {}
        
        df = pd.read_csv(csv_path)
        
        stats = {
            "total_signals": len(df),
            "avg_confidence": df['confidence'].mean() if len(df) > 0 else 0,
            "assets_traded": df['asset'].nunique(),
            "most_recent_signal": df['timestamp'].iloc[-1] if len(df) > 0 else None
        }
        
        # Calculate PnL stats if exit data exists
        if 'pnl' in df.columns:
            completed_trades = df[df['pnl'].notna()]
            if len(completed_trades) > 0:
                stats.update({
                    "completed_trades": len(completed_trades),
                    "total_pnl": completed_trades['pnl'].sum(),
                    "avg_pnl": completed_trades['pnl'].mean(),
                    "win_rate": (completed_trades['pnl'] > 0).sum() / len(completed_trades)
                })
        
        return stats
        
    except Exception as e:
        logging.error(f"Failed to get trading stats: {e}")
        return {}
