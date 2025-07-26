import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import logging
import pandas as pd
import os
from typing import Dict, List
import config
import time
from pathlib import Path

def log_signal(signal_data: Dict):
    try:
        Path("logs").mkdir(exist_ok=True)
        
        best_signal = signal_data.get("best_signal", {})
        asset = best_signal.get("asset", "Unknown")
        entry_price = best_signal.get("entry_price", 0)
        stop_loss = best_signal.get("stop_loss", 0)
        confidence = signal_data.get("confidence", 0)
        reason = best_signal.get("reason", "market_conditions")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        row_data = {
            "asset": asset,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "confidence": confidence,
            "reason": reason,
            "timestamp": timestamp
        }
        
        df_new = pd.DataFrame([row_data])
        csv_path = "logs/trade_log.csv"
        
        if os.path.exists(csv_path):
            df_existing = pd.read_csv(csv_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, index=False)
        
        logging.info(f'Signal logged to CSV: {asset} @ {entry_price:.2f} (confidence: {confidence:.3f})')
        
    except Exception as e:
        logging.error(f"Signal logging error: {e}")

def log_trade_execution(trade_data: Dict):
    try:
        Path("logs").mkdir(exist_ok=True)
        
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
        logging.error(f"Trade execution logging error: {e}")

def get_trading_stats() -> Dict:
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
        
        return stats
        
    except Exception:
        return {}
