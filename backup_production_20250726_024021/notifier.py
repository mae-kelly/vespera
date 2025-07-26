import torch
import sys
if not torch.cuda.is_available():
    print("❌ CRITICAL ERROR: NO GPU DETECTED")
    print("This system requires GPU acceleration. gpu operation is FORBIDDEN.")
    sys.exit(1)
device_name = torch.cuda.get_device_name(0)
if "A100" not in device_name:
    print(f"⚠️ WARNING: Non-A100 GPU detected: {device_name}")
    print("Optimal performance requires A100. Continuing with reduced performance.")

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
            confidence = signal_data.get("confidence", 0)
            signal_type = "🔻 SHORT SIGNAL"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            best_signal = signal_data.get("best_signal", {})
            asset = best_signal.get("asset", "Unknown")
            reason = best_signal.get("reason", "market_conditions")
            entry_price = best_signal.get("entry_price", 0)
            embed = {
                "title": f"{signal_type} ALERT",
                "description": f"High-frequency trading signal detected for **{asset}**",
                "color": 15158332,
                "fields": [
                    {
                        "name": "💰 Asset",
                        "value": f"**{asset}**",
                        "inline": True
                    },
                    {
                        "name": "💵 Entry Price",
                        "value": f"**${entry_price:,.2f}**",
                        "inline": True
                    },
                    {
                        "name": "🎯 Confidence",
                        "value": f"**{confidence:.1%}**",
                        "inline": True
                    },
                    {
                        "name": "📊 Reason",
                        "value": f"```{reason}```",
                        "inline": False
                    },
                    {
                        "name": "📈 Technical Details",
                        "value": self._format_technical_details(best_signal),
                        "inline": False
                    },
                    {
                        "name": "🔍 Sources",
                        "value": f"`{', '.join(signal_data.get('active_sources', []))}`",
                        "inline": True
                    },
                    {
                        "name": "₿ BTC Dominance",
                        "value": f"**{signal_data.get('btc_dominance', 0):.1f}%**",
                        "inline": True
                    },
                    {
                        "name": "⚙️ Mode",
                        "value": f"**{config.MODE.upper()}**",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"HFT System • {timestamp}",
                    "icon_url": "https://cdn.discordapp.com/emojis/741744692896284683.png"
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
            content = ""
            if self.user_id:
                content = f"<@{self.user_id}> "
            payload = {
                "content": content,
                "embeds": [embed],
                "username": "HFT Trading Bot",
                "avatar_url": "https://cdn.discordapp.com/emojis/741744692896284683.png"
            }
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 204:
                logging.info(f"Discord alert sent for {asset} signal")
            else:
                logging.error(f"Discord webhook failed: {response.status_code} - {response.text}")
    def send_trade_notification(self, trade_data: Dict):
        try:
            if not self.webhook_url:
                return
            asset = trade_data.get("asset", "Unknown")
            status = trade_data.get("status", "unknown")
            entry_price = trade_data.get("entry_price", 0)
            quantity = trade_data.get("quantity", 0)
            color_map = {
                "filled": 3066993,
                "partial": 15844367,
                "cancelled": 10038562,
                "rejected": 15158332
            }
            color = color_map.get(status.lower(), 3447003)
            embed = {
                "title": "💼 TRADE EXECUTED",
                "description": f"Trade execution update for **{asset}**",
                "color": color,
                "fields": [
                    {
                        "name": "💰 Asset",
                        "value": f"**{asset}**",
                        "inline": True
                    },
                    {
                        "name": "📊 Status",
                        "value": f"**{status.upper()}**",
                        "inline": True
                    },
                    {
                        "name": "💵 Entry Price",
                        "value": f"**${entry_price:,.2f}**",
                        "inline": True
                    },
                    {
                        "name": "📦 Quantity",
                        "value": f"**{quantity:.4f}**",
                        "inline": True
                    },
                    {
                        "name": "💰 Position Value",
                        "value": f"**${entry_price * quantity:,.2f}**",
                        "inline": True
                    },
                    {
                        "name": "⚙️ Mode",
                        "value": f"**{config.MODE.upper()}**",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"HFT System • {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "icon_url": "https://cdn.discordapp.com/emojis/741744692896284683.png"
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
            payload = {
                "embeds": [embed],
                "username": "HFT Trading Bot"
            }
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                logging.info(f"Discord trade notification sent for {asset}")
            else:
                logging.error(f"Discord trade notification failed: {response.status_code}")
    def send_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        try:
            if not self.webhook_url:
                return
            color_map = {
                "error": 15158332,
                "warning": 16776960,
                "info": 3447003,
                "success": 3066993
            }
            color = color_map.get(severity.lower(), 3447003)
            emoji_map = {
                "error": "🚨",
                "warning": "⚠️",
                "info": "ℹ️",
                "success": "✅"
            }
            emoji = emoji_map.get(severity.lower(), "ℹ️")
            embed = {
                "title": f"{emoji} {alert_type.upper()}",
                "description": message,
                "color": color,
                "footer": {
                    "text": f"HFT System • {time.strftime('%Y-%m-%d %H:%M:%S')}",
                },
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            }
            payload = {
                "embeds": [embed],
                "username": "HFT System Monitor"
            }
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                logging.info(f"Discord system alert sent: {alert_type}")
            else:
                logging.error(f"Discord system alert failed: {response.status_code}")
    def _format_technical_details(self, signal_data: Dict) -> str:
        details = []
        if "rsi" in signal_data:
            details.append(f"RSI: {signal_data['rsi']:.1f}")
        if "vwap_deviation" in signal_data:
            details.append(f"VWAP Dev: {signal_data['vwap_deviation']:.1f}%")
        if "price_change_1h" in signal_data:
            details.append(f"1h Change: {signal_data['price_change_1h']:.1f}%")
        if "volume_anomaly" in signal_data:
            details.append(f"Volume Spike: {'Yes' if signal_data['volume_anomaly'] else 'No'}")
        return " | ".join(details) if details else "Standard market conditions"
    def test_connection(self):
        try:
            if not self.webhook_url:
                return False, "No webhook URL configured"
            test_embed = {
                "title": "🧪 HFT System Connection Test",
                "description": "Discord webhook is working correctly!",
                "color": 3066993,
                "fields": [
                    {
                        "name": "Status",
                        "value": "✅ Connected",
                        "inline": True
                    },
                    {
                        "name": "Test Time",
                        "value": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "inline": True
                    }
                ]
            }
            payload = {
                "embeds": [test_embed],
                "username": "HFT Connection Test"
            }
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                return True, "Discord webhook working"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
discord_notifier = DiscordNotifier()
def send_signal_alert(signal_data: Dict):
    discord_notifier.send_signal_alert(signal_data)
def send_trade_notification(trade_data: Dict):
    discord_notifier.send_trade_notification(trade_data)
def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    discord_notifier.send_system_alert(alert_type, message, severity)