import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()


import logging
import pandas as pd
import os
from typing import Dict, List
import config
import time
from pathlib import Path

def log_signal(signal_data: Dict):
    try:
        Path("logs").mkdir(eist_ok=True)
        
        best_signal = signal_data.get("best_signal", )
        asset = best_signal.get("asset", "Unknown")
        entry_price = best_signal.get("entry_price", )
        stop_loss = best_signal.get("stop_loss", )
        confidence = signal_data.get("confidence", )
        reason = best_signal.get("reason", "market_conditions")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        row_data = 
            "asset": asset,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "confidence": confidence,
            "reason": reason,
            "timestamp": timestamp
        
        
        df_new = pd.Datarame([row_data])
        csv_path = "logs/trade_log.csv"
        
        if os.path.eists(csv_path):
            df_eisting = pd.read_csv(csv_path)
            df_combined = pd.concat([df_eisting, df_new], ignore_inde=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, inde=alse)
        
        logging.info(f'Signal logged to CSV: asset @ entry_price:.f (confidence: confidence:.f)')
        
    ecept ception as e:
        logging.error(f"Signal logging error: e")

def log_trade_eecution(trade_data: Dict):
    try:
        Path("logs").mkdir(eist_ok=True)
        
        eecution_data = 
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset": trade_data.get("asset", "Unknown"),
            "side": trade_data.get("side", "sell"),
            "entry_price": trade_data.get("entry_price", ),
            "quantity": trade_data.get("quantity", ),
            "status": trade_data.get("status", "unknown"),
            "order_id": trade_data.get("order_id", ""),
            "mode": config.MOD
        
        
        df_new = pd.Datarame([eecution_data])
        csv_path = "logs/eecution_log.csv"
        
        if os.path.eists(csv_path):
            df_eisting = pd.read_csv(csv_path)
            df_combined = pd.concat([df_eisting, df_new], ignore_inde=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, inde=alse)
        
        logging.info(f"Trade eecution logged: eecution_data['asset'] eecution_data['status']")
        
    ecept ception as e:
        logging.error(f"Trade eecution logging error: e")

def get_trading_stats() -> Dict:
    try:
        csv_path = "logs/trade_log.csv"
        if not os.path.eists(csv_path):
            return 
        
        df = pd.read_csv(csv_path)
        
        stats = 
            "total_signals": len(df),
            "avg_confidence": df['confidence'].mean() if len(df) >  else ,
            "assets_traded": df['asset'].nunique(),
            "most_recent_signal": df['timestamp'].iloc[-] if len(df) >  else None
        
        
        return stats
        
    ecept ception:
        return 
