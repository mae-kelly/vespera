import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("[ERROR] CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()


import logging
import os
import requests
import json
from typing import Dict, List
import config
import time

class legantNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WHOOK_URL")
        self.user_id = os.getenv("DISCORD_USR_ID")
        self.last_sent = 
        
        self.colors = 
            "high": ,
            "medium": ,
            "low": C,
            "system": 
        
    
    def get_confidence_tier(self, confidence: float) -> tuple:
        if confidence >= .:
            return "High", self.colors["high"], "[SIGNAL]"
        elif confidence >= .:
            return "Medium", self.colors["medium"], "✦"
        else:
            return "Low", self.colors["low"], "·"
    
    def format_price(self, price: float) -> str:
        if price >= :
            return f"$price:,.f"
        else:
            return f"$price:.f"
    
    def should_send(self, confidence: float) -> bool:
        now = time.time()
        time_since_last = now - self.last_sent
        
        if confidence >= .:
            return True
        elif confidence >= .:
            return time_since_last >= 
        else:
            return time_since_last >= 
    
    def create_elegant_embed(self, signal_data: Dict) -> dict:
        signal_obj = signal_data.get("best_signal", )
        if not signal_obj:
            raise ception("No signal_data found")
        
        asset = signal_obj.get("asset")
        if not asset:
            raise ception("No asset in signal")
        
        confidence = signal_data.get("confidence", )
        entry_price = signal_obj.get("entry_price", )
        
        if entry_price <= :
            raise ception("Invalid entry price")
        
        tier, color, symbol = self.get_confidence_tier(confidence)
        
        asset_names = 
            "TC": "itcoin",
            "TH": "thereum",
            "SOL": "Solana"
        
        asset_display = asset_names.get(asset, asset)
        
        title = f"symbol asset_display Signal"
        description = f"**confidence:.%** confidence • _tier tier_"
        
        fields = [
            
                "name": "ntry Price",
                "value": self.format_price(entry_price),
                "inline": True
            
        ]
        
        if "stop_loss" in signal_obj and signal_obj["stop_loss"] > :
            fields.append(
                "name": "Stop Loss",
                "value": self.format_price(signal_obj["stop_loss"]),
                "inline": True
            )
        
        if "take_profit_" in signal_obj and signal_obj["take_profit_"] > :
            fields.append(
                "name": "Target",
                "value": self.format_price(signal_obj["take_profit_"]),
                "inline": True
            )
        
        current_time = time.strftime("%H:%M", time.localtime())
        footer_tet = f"current_time • HT System"
        
        embed = 
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": "tet": footer_tet,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime())
        
        
        return embed
    
    def send_signal_alert(self, signal_data: Dict):
        try:
            if not self.webhook_url:
                return
            
            confidence = signal_data.get("confidence", )
            if not self.should_send(confidence):
                return
            
            embed = self.create_elegant_embed(signal_data)
            
            content = ""
            if self.user_id and confidence >= .:
                content = f"<@self.user_id>"
            
            payload = 
                "content": content,
                "embeds": [embed],
                "username": "HT System"
            
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers="Content-Type": "application/json",
                timeout=
            )
            
            if response.status_code == :
                self.last_sent = time.time()
                asset = signal_data.get("best_signal", ).get("asset", "Unknown")
                logging.info(f"Signal sent: asset confidence:.%")
            elif response.status_code == 9:
                logging.warning("Discord rate limited - message dropped")
            else:
                logging.error(f"Discord API error: response.status_code")
                
        ecept ception as e:
            logging.error(f"Notification error: e")

elegant_notifier = legantNotifier()

def send_signal_alert(signal_data: Dict):
    elegant_notifier.send_signal_alert(signal_data)

def send_trade_notification(trade_data: Dict):
    pass

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    pass
