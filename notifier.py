import logging
import os
import requests
import json
from typing import Dict
import time

class ProductionNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.user_id = os.getenv("DISCORD_USER_ID")
        
        if not self.webhook_url:
            raise RuntimeError("DISCORD_WEBHOOK_URL required for production")
    
    def send_signal_alert(self, signal_data: Dict):
        if not signal_data.get("production_validated"):
            raise RuntimeError("Non-validated signal rejected in production")
        
        confidence = signal_data.get("confidence")
        if confidence is None:
            raise RuntimeError("Signal missing confidence")
        
        if confidence < 0.75:
            raise RuntimeError(f"Signal confidence {confidence:.3f} below production threshold")
        
        best_signal = signal_data.get("signal_data", {})
        asset = best_signal.get("asset")
        if not asset:
            raise RuntimeError("No asset specified in production signal")
        
        entry_price = best_signal.get("entry_price", 0)
        if entry_price <= 0:
            raise RuntimeError("Invalid entry price in production signal")
        
        embed = {
            "title": f"🔴 PRODUCTION SIGNAL: {asset}",
            "description": f"**{confidence:.1%}** confidence • LIVE EXECUTION",
            "color": 0xFF0000,
            "fields": [
                {"name": "💰 Asset", "value": f"**{asset}**", "inline": True},
                {"name": "💵 Entry Price", "value": f"**${entry_price:,.2f}**", "inline": True},
                {"name": "🎯 Confidence", "value": f"**{confidence:.1%}**", "inline": True}
            ],
            "footer": {"text": f"PRODUCTION • {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        
        payload = {
            "content": f"<@{self.user_id}> 🚨 PRODUCTION TRADE SIGNAL" if self.user_id else None,
            "embeds": [embed],
            "username": "HFT Production System"
        }
        
        response = requests.post(self.webhook_url, json=payload, timeout=5)
        if response.status_code != 204:
            raise RuntimeError(f"Discord notification failed: {response.status_code}")
        
        logging.info(f"🔴 Production alert sent: {asset} @ {confidence:.1%}")

production_notifier = ProductionNotifier()

def send_signal_alert(signal_data: Dict):
    production_notifier.send_signal_alert(signal_data)

def send_trade_notification(trade_data: Dict):
    pass

def send_system_alert(alert_type: str, message: str, severity: str = "error"):
    pass
