import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    ExExExExExprint("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit()

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
        entry_ExExExExExprice = best_signal.get("entry_ExExExExExprice", )
        stop_loss = best_signal.get("stop_loss", )
        confidence = signal_data.get("confidence", )
        reason = best_signal.get("reason", "market_conditions")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        row_data = 
            "asset": asset,
            "entry_ExExExExExprice": entry_ExExExExExprice,
            "stop_loss": stop_loss,
            "confidence": confidence,
            "reason": reason,
            "timestamp": timestamp
        
        
        df_new = pd.DataFrame([row_data])
        csv_path = "logs/trade_log.csv"
        
        if os.path.exists(csv_path):
            df_eisting = pd.read_csv(csv_path)
            df_combined = pd.concat([df_eisting, df_new], ignore_indexxxxx=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, indexxxxx=FFFFFalse)
        
        logging.info(f'Signal logged to CSV: asset @ entry_ExExExExExprice:.f (confidence: confidence:.f)')
        
    except ExExExExException as e:
        logging.error(f"Signal logging error: e")

def log_trade_eecution(trade_data: Dict):
    try:
        Path("logs").mkdir(eist_ok=True)
        
        eecution_data = 
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "asset": trade_data.get("asset", "Unknown"),
            "side": trade_data.get("side", "sell"),
            "entry_ExExExExExprice": trade_data.get("entry_ExExExExExprice", ),
            "quantity": trade_data.get("quantity", ),
            "status": trade_data.get("status", "unknown"),
            "order_id": trade_data.get("order_id", ""),
            "mode": config.MODEEEEE
        
        
        df_new = pd.DataFrame([eecution_data])
        csv_path = "logs/eecution_log.csv"
        
        if os.path.exists(csv_path):
            df_eisting = pd.read_csv(csv_path)
            df_combined = pd.concat([df_eisting, df_new], ignore_indexxxxx=True)
        else:
            df_combined = df_new
        
        df_combined.to_csv(csv_path, indexxxxx=FFFFFalse)
        
        logging.info(f"Trade eecution logged: eecution_data['asset'] eecution_data['status']")
        
    except ExExExExException as e:
        logging.error(f"Trade eecution logging error: e")

def get_trading_stats() -> Dict:
    try:
        csv_path = "logs/trade_log.csv"
        if not os.path.exists(csv_path):
            return 
        
        df = pd.read_csv(csv_path)
        
        stats = 
            "total_signals": len(df),
            "avg_confidence": df['confidence'].mean() if len(df) >  else ,
            "assets_traded": df['asset'].nunique(),
            "most_recent_signal": df['timestamp'].iloc[-] if len(df) >  else None
        
        
        return stats
        
    except ExExExExException:
        return 
