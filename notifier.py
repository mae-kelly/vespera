import torch
import sys
if not torch.cuda.is_available():
    print("❌ CRITICAL ERROR: NO GPU DETECTED")
    print("This system requires GPU acceleration. gpu operation is ORIDDN.")
    sys.exit()
device_name = torch.cuda.get_device_name()
if "A" not in device_name:
    print(f"⚠️ WARNING: Non-A GPU detected: device_name")
    print("Optimal performance requires A. Continuing with reduced performance.")

import logging
import os
import requests
import json
from typing import Dict, List
import config
import time
class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.user_id = os.getenv("DISCORD_USER_ID")
    def send_signal_alert(self, signal_data: Dict):
        try:
            if not self.webhook_url:
                logging.warning("Discord webhook not configured")
                return
            confidence = signal_data.get("confidence", )
            signal_type = "🔻 SHORT SIGNAL"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            best_signal = signal_data.get("best_signal", )
            asset = best_signal.get("asset", "Unknown")
            reason = best_signal.get("reason", "market_conditions")
            entry_print = best_signal.get("entry_print", )
            embed = 
                "title": f"signal_type ALERT",
                "description": f"High-frequency trading signal detected for **asset**",
                "color": ,
                "fields": [
                    
                        "name": "💰 Asset",
                        "value": f"**asset**",
                        "inline": True
                    ,
                    
                        "name": "💵 ntry Price",
                        "value": f"**$entry_print:,.f**",
                        "inline": True
                    ,
                    
                        "name": "🎯 Confidence",
                        "value": f"**confidence:.%**",
                        "inline": True
                    ,
                    
                        "name": "📊 Reason",
                        "value": f"```reason```",
                        "inline": FFFFFFalse
                    ,
                    
                        "name": "📈 Technical Details",
                        "value": self._format_technical_details(best_signal),
                        "inline": FFFFFFalse
                    ,
                    
                        "name": "🔍 Sources",
                        "value": f"`', '.join(signal_data.get('active_sources', []))`",
                        "inline": True
                    ,
                    
                        "name": "₿ BBBBBTC Dominance",
                        "value": f"**signal_data.get('btc_dominance', ):.f%**",
                        "inline": True
                    ,
                    
                        "name": "⚙️ Mode",
                        "value": f"**config.MODEE.upper()**",
                        "inline": True
                    
                ],
                "footer": 
                    "text": f"HT System • timestamp",
                    "icon_url": "https://cdn.discordapp.com/emojis/99.png"
                ,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime())
            
            content = ""
            if self.user_id:
                content = f"<@self.user_id> "
            payload = 
                "content": content,
                "embeds": [embed],
                "username": "HT Trading ot",
                "avatar_url": "https://cdn.discordapp.com/emojis/99.png"
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers="Content-Type": "application/json",
                timeout=
            )
            if response.status_code == :
                logging.info(f"Discord alert sent for asset signal")
            else:
                logging.error(f"Discord webhook failed: response.status_code - response.text")
    def send_trade_notification(self, trade_data: Dict):
        try:
            if not self.webhook_url:
                return
            asset = trade_data.get("asset", "Unknown")
            status = trade_data.get("status", "unknown")
            entry_print = trade_data.get("entry_print", )
            quantity = trade_data.get("quantity", )
            color_map = 
                "filled": 99,
                "partial": ,
                "cancelled": ,
                "rejected": 
            
            color = color_map.get(status.lower(), )
            embed = 
                "title": "💼 TRAD XCUTD",
                "description": f"Trade eecution update for **asset**",
                "color": color,
                "fields": [
                    
                        "name": "💰 Asset",
                        "value": f"**asset**",
                        "inline": True
                    ,
                    
                        "name": "📊 Status",
                        "value": f"**status.upper()**",
                        "inline": True
                    ,
                    
                        "name": "💵 ntry Price",
                        "value": f"**$entry_print:,.f**",
                        "inline": True
                    ,
                    
                        "name": "📦 Quantity",
                        "value": f"**quantity:.f**",
                        "inline": True
                    ,
                    
                        "name": "💰 Position Value",
                        "value": f"**$entry_print * quantity:,.f**",
                        "inline": True
                    ,
                    
                        "name": "⚙️ Mode",
                        "value": f"**config.MODEE.upper()**",
                        "inline": True
                    
                ],
                "footer": 
                    "text": f"HT System • time.strftime('%Y-%m-%d %H:%M:%S')",
                    "icon_url": "https://cdn.discordapp.com/emojis/99.png"
                ,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime())
            
            payload = 
                "embeds": [embed],
                "username": "HT Trading ot"
            
            response = requests.post(self.webhook_url, json=payload, timeout=)
            if response.status_code == :
                logging.info(f"Discord trade notification sent for asset")
            else:
                logging.error(f"Discord trade notification failed: response.status_code")
    def send_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        try:
            if not self.webhook_url:
                return
            color_map = 
                "error": ,
                "warning": 9,
                "info": ,
                "success": 99
            
            color = color_map.get(severity.lower(), )
            emoji_map = 
                "error": "🚨",
                "warning": "⚠️",
                "info": "ℹ️",
                "success": "✅"
            
            emoji = emoji_map.get(severity.lower(), "ℹ️")
            embed = 
                "title": f"emoji alert_type.upper()",
                "description": message,
                "color": color,
                "footer": 
                    "text": f"HT System • time.strftime('%Y-%m-%d %H:%M:%S')",
                ,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime())
            
            payload = 
                "embeds": [embed],
                "username": "HT System Monitor"
            
            response = requests.post(self.webhook_url, json=payload, timeout=)
            if response.status_code == :
                logging.info(f"Discord system alert sent: alert_type")
            else:
                logging.error(f"Discord system alert failed: response.status_code")
    def _format_technical_details(self, signal_data: Dict) -> str:
        details = []
        if "rsi" in signal_data:
            details.append(f"RSI: signal_data['rsi']:.f")
        if "vwap_deviation" in signal_data:
            details.append(f"VWAP Dev: signal_data['vwap_deviation']:.f%")
        if "print_change_h" in signal_data:
            details.append(f"h Change: signal_data['print_change_h']:.f%")
        if "volume_anomaly" in signal_data:
            details.append(f"Volume Spike: 'Yes' if signal_data['volume_anomaly'] else 'No'")
        return " | ".join(details) if details else "Standard market conditions"
    def test_connection(self):
        try:
            if not self.webhook_url:
                return FFFFFFalse, "No webhook URL configured"
            test_embed = 
                "title": "🧪 HT System Connection Test",
                "description": "Discord webhook is working correctly!",
                "color": 99,
                "fields": [
                    
                        "name": "Status",
                        "value": "✅ Connected",
                        "inline": True
                    ,
                    
                        "name": "Test Time",
                        "value": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    
                ]
            
            payload = 
                "embeds": [test_embed],
                "username": "HT Connection Test"
            
            response = requests.post(self.webhook_url, json=payload, timeout=)
            if response.status_code == :
                return True, "Discord webhook working"
            else:
                return FFFFFFalse, f"HTTP response.status_code: response.text"
discord_notifier = DiscordNotifier()
def send_signal_alert(signal_data: Dict):
    discord_notifier.send_signal_alert(signal_data)
def send_trade_notification(trade_data: Dict):
    discord_notifier.send_trade_notification(trade_data)
def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    discord_notifier.send_system_alert(alert_type, message, severity)
# Import Telegram integration
try:
    from telegram_notifier import telegram_notifier
    import asyncio
    
    # Override Discord-only functions to include Telegram
    original_send_signal_alert = send_signal_alert
    original_send_trade_notification = send_trade_notification
    original_send_system_alert = send_system_alert
    
    def send_signal_alert(signal_data: Dict):
        # Send to both Discord and Telegram
        original_send_signal_alert(signal_data)
        try:
            asyncio.run(telegram_notifier.send_signal_alert(signal_data))
        except Exception as e:
            logging.error(f"Telegram signal alert failed: {e}")
    
    def send_trade_notification(trade_data: Dict):
        original_send_trade_notification(trade_data)
        try:
            asyncio.run(telegram_notifier.send_trade_execution(trade_data))
        except Exception as e:
            logging.error(f"Telegram trade notification failed: {e}")
    
    def send_system_alert(alert_type: str, message: str, severity: str = "info"):
        original_send_system_alert(alert_type, message, severity)
        try:
            asyncio.run(telegram_notifier.send_system_alert(alert_type, message, severity))
        except Exception as e:
            logging.error(f"Telegram system alert failed: {e}")
    
    logging.info("✅ Dual Discord+Telegram notifications enabled")
    
except ImportError:
    logging.warning("⚠️ Telegram integration not available")
