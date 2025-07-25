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
        self.user_id = os.getenv("DISCORD_USER_ID")  # Optional for mentions
        
    def send_signal_alert(self, signal_data: Dict):
        """Send signal alert via Discord webhook"""
        try:
            if not self.webhook_url:
                logging.warning("Discord webhook not configured")
                return
            
            # Format message with required fields
            confidence = signal_data.get("confidence", 0)
            signal_type = "🔻 SHORT SIGNAL"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # Extract asset and reason from best signal
            best_signal = signal_data.get("best_signal", {})
            asset = best_signal.get("asset", "Unknown")
            reason = best_signal.get("reason", "market_conditions")
            entry_price = best_signal.get("entry_price", 0)
            
            # Create rich Discord embed
            embed = {
                "title": f"{signal_type} ALERT",
                "description": f"High-frequency trading signal detected for **{asset}**",
                "color": 15158332,  # Red color for short signals
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
            
            # Add mention if user ID provided
            content = ""
            if self.user_id:
                content = f"<@{self.user_id}> "
            
            payload = {
                "content": content,
                "embeds": [embed],
                "username": "HFT Trading Bot",
                "avatar_url": "https://cdn.discordapp.com/emojis/741744692896284683.png"
            }
            
            # Send to Discord
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
                
        except Exception as e:
            logging.error(f"Failed to send Discord alert: {e}")
    
    def send_trade_notification(self, trade_data: Dict):
        """Send trade execution notification"""
        try:
            if not self.webhook_url:
                return
            
            asset = trade_data.get("asset", "Unknown")
            status = trade_data.get("status", "unknown")
            entry_price = trade_data.get("entry_price", 0)
            quantity = trade_data.get("quantity", 0)
            
            # Choose color based on status
            color_map = {
                "filled": 3066993,      # Green
                "partial": 15844367,    # Gold  
                "cancelled": 10038562,  # Dark grey
                "rejected": 15158332    # Red
            }
            color = color_map.get(status.lower(), 3447003)  # Default blue
            
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
                
        except Exception as e:
            logging.error(f"Failed to send Discord trade notification: {e}")
    
    def send_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Send system alerts (errors, warnings, status updates)"""
        try:
            if not self.webhook_url:
                return
            
            # Color based on severity
            color_map = {
                "error": 15158332,    # Red
                "warning": 16776960,  # Yellow
                "info": 3447003,      # Blue
                "success": 3066993    # Green
            }
            color = color_map.get(severity.lower(), 3447003)
            
            # Emoji based on severity
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
                
        except Exception as e:
            logging.error(f"Failed to send Discord system alert: {e}")
    
    def _format_technical_details(self, signal_data: Dict) -> str:
        """Format technical analysis details"""
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
        """Test Discord webhook connection"""
        try:
            if not self.webhook_url:
                return False, "No webhook URL configured"
            
            test_embed = {
                "title": "🧪 HFT System Connection Test",
                "description": "Discord webhook is working correctly!",
                "color": 3066993,  # Green
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
                
        except Exception as e:
            return False, str(e)

# Create global notifier instance
discord_notifier = DiscordNotifier()

# Backward compatibility functions
def send_signal_alert(signal_data: Dict):
    """Send signal alert via Discord"""
    discord_notifier.send_signal_alert(signal_data)

def send_trade_notification(trade_data: Dict):
    """Send trade execution notification"""
    discord_notifier.send_trade_notification(trade_data)

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    """Send system alert"""
    discord_notifier.send_system_alert(alert_type, message, severity)
