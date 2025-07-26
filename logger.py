import logging
import pandas as pd
import os
from typing import Dict
import time
from pathlib import Path

def log_signal(signal_data: Dict):
    if not signal_data.get("production_validated"):
        raise RuntimeError("Cannot log non-validated signal in production")
    
    Path("logs").mkdir(exist_ok=True)
    
    best_signal = signal_data.get("signal_data", {})
    asset = best_signal.get("asset", "Unknown")
    entry_price = best_signal.get("entry_price", 0)
    stop_loss = best_signal.get("stop_loss", 0)
    confidence = signal_data.get("confidence")
    
    if confidence is None:
        raise RuntimeError("Signal missing confidence")
    
    if confidence < 0.75:
        raise RuntimeError(f"Production signal below threshold: {confidence:.3f}")
    
    reason = best_signal.get("reason", "production_signal")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    row_data = {
        "asset": asset,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "confidence": confidence,
        "reason": reason,
        "timestamp": timestamp,
        "mode": "PRODUCTION"
    }
    
    df_new = pd.DataFrame([row_data])
    csv_path = "logs/production_signals.csv"
    
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    
    df_combined.to_csv(csv_path, index=False)
    logging.info(f'✅ Production signal logged: {asset} @ ${entry_price:.2f} ({confidence:.1%})')

def log_trade_execution(trade_data: Dict):
    Path("logs").mkdir(exist_ok=True)
    
    execution_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "asset": trade_data.get("asset", "Unknown"),
        "side": trade_data.get("side", "sell"),
        "entry_price": trade_data.get("entry_price", 0),
        "quantity": trade_data.get("quantity", 0),
        "status": trade_data.get("status", "unknown"),
        "order_id": trade_data.get("order_id", ""),
        "mode": "PRODUCTION"
    }
    
    df_new = pd.DataFrame([execution_data])
    csv_path = "logs/production_executions.csv"
    
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    
    df_combined.to_csv(csv_path, index=False)
    logging.info(f"🔴 Production execution logged: {execution_data['asset']} {execution_data['status']}")

def get_trading_stats() -> Dict:
    csv_path = "logs/production_signals.csv"
    if not os.path.exists(csv_path):
        return {"total_signals": 0, "avg_confidence": 0, "status": "NO_DATA"}
    
    df = pd.read_csv(csv_path)
    
    return {
        "total_signals": len(df),
        "avg_confidence": df['confidence'].mean(),
        "assets_traded": df['asset'].nunique(),
        "most_recent_signal": df['timestamp'].iloc[-1] if len(df) > 0 else None,
        "status": "PRODUCTION_ACTIVE"
    }
