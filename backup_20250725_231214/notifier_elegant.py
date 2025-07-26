import logging
import os
import requests
import json
from typing import Dict, List
import config
import time

class ElegantNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.user_id = os.getenv("DISCORD_USER_ID")
        self.last_sent = 0
        
        if not self.webhook_url:
            raise Exception("DISCORD_WEBHOOK_URL required")
        
        self.colors = {
            "high": 0x5865F2,
            "medium": 0x57F287,
            "low": 0xFEE75C,
            "system": 0x2F3136
        }
    
    def get_confidence_tier(self, confidence: float) -> tuple:
        if confidence >= 0.6:
            return "High", self.colors["high"], "⚡"
        elif confidence >= 0.3:
            return "Medium", self.colors["medium"], "✦"
        else:
            return "Low", self.colors["low"], "·"
    
    def format_price(self, price: float) -> str:
        if price >= 1000:
            return f"${price:,.2f}"
        else:
            return f"${price:.4f}"
    
    def should_send(self, confidence: float) -> bool:
        now = time.time()
        time_since_last = now - self.last_sent
        
        if confidence >= 0.6:
            return True
        elif confidence >= 0.4:
            return time_since_last >= 30
        else:
            return time_since_last >= 60
    
    def create_elegant_embed(self, signal_data: Dict) -> dict:
        signal_obj = signal_data.get("signal_data", {})
        if not signal_obj:
            raise Exception("No signal_data found")
        
        asset = signal_obj.get("asset")
        if not asset:
            raise Exception("No asset in signal")
        
        confidence = signal_data.get("confidence", 0)
        entry_price = signal_obj.get("entry_price", 0)
        
        if entry_price <= 0:
            raise Exception("Invalid entry price")
        
        tier, color, symbol = self.get_confidence_tier(confidence)
        
        asset_names = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum", 
            "SOL": "Solana"
        }
        
        asset_display = asset_names.get(asset, asset)
        title = f"{symbol} {asset_display} Signal"
        description = f"**{confidence:.1%}** confidence • _{tier} tier_"
        
        fields = [
            {
                "name": "Entry Price",
                "value": self.format_price(entry_price),
                "inline": True
            }
        ]
        
        if "stop_loss" in signal_obj and signal_obj["stop_loss"] > 0:
            fields.append({
                "name": "Stop Loss", 
                "value": self.format_price(signal_obj["stop_loss"]),
                "inline": True
            })
        
        if "take_profit_1" in signal_obj and signal_obj["take_profit_1"] > 0:
            fields.append({
                "name": "Target",
                "value": self.format_price(signal_obj["take_profit_1"]),
                "inline": True
            })
        
        if "rsi" in signal_obj:
            fields.append({
                "name": "RSI",
                "value": f"{signal_obj['rsi']:.1f}",
                "inline": True
            })
        
        if "price_change_1h" in signal_obj:
            change = signal_obj["price_change_1h"]
            if abs(change) > 0.5:
                fields.append({
                    "name": "1h Change",
                    "value": f"{change:+.1f}%",
                    "inline": True
                })
        
        reason = signal_obj.get("reason", "")
        if reason and len(reason) < 30:
            clean_reason = reason.replace("_", " ").replace("+", " + ").title()
            fields.append({
                "name": "Analysis",
                "value": clean_reason,
                "inline": False
            })
        
        current_time = time.strftime("%H:%M", time.localtime())
        footer_text = f"{current_time} • HFT System"
        
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": {"text": footer_text},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        }
        
        return embed
    
    def send_signal(self, signal_data: Dict):
        confidence = signal_data.get("confidence", 0)
        
        if not self.should_send(confidence):
            return
        
        embed = self.create_elegant_embed(signal_data)
        
        content = ""
        if self.user_id and confidence >= 0.6:
            content = f"<@{self.user_id}>"
        
        payload = {
            "content": content,
            "embeds": [embed],
            "username": "HFT System"
        }
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code != 204:
            if response.status_code == 429:
                logging.warning("Discord rate limited - message dropped")
                return
            else:
                raise Exception(f"Discord API error: {response.status_code}")
        
        self.last_sent = time.time()
        asset = signal_data.get("signal_data", {}).get("asset", "Unknown")
        logging.info(f"Signal sent: {asset} {confidence:.1%}")

elegant_notifier = ElegantNotifier()

def send_signal_alert(signal_data: Dict):
    elegant_notifier.send_signal(signal_data)

def send_trade_notification(trade_data: Dict):
    pass

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    pass
