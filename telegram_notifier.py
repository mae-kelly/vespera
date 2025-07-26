import os
import asyncio
import logging
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
import json
import time

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        
        if self.bot_token and self.chat_id:
            self.bot = Bot(token=self.bot_token)
            logging.info("✅ Telegram bot initialized")
        else:
            logging.warning("⚠️ Telegram credentials not configured")
    
    async def send_signal_alert(self, signal_data: Dict):
        """Send trading signal alert via Telegram"""
        if not self.bot:
            return
        
        try:
            confidence = signal_data.get("confidence", 0)
            best_signal = signal_data.get("best_signal", {})
            asset = best_signal.get("asset", "Unknown")
            entry_price = best_signal.get("entry_price", 0)
            reason = best_signal.get("reason", "market_conditions")
            
            # Create formatted message
            message = f"""
🎯 <b>HFT SIGNAL ALERT</b>

💰 <b>Asset:</b> {asset}
💵 <b>Entry Price:</b> ${entry_price:,.2f}
📊 <b>Confidence:</b> {confidence:.1%}
📈 <b>Strategy:</b> {reason}

🔍 <b>Technical Details:</b>
"""
            
            # Add technical indicators if available
            if "rsi" in best_signal:
                message += f"• RSI: {best_signal['rsi']:.1f}\n"
            if "vwap" in best_signal:
                message += f"• VWAP: ${best_signal['vwap']:.2f}\n"
            if "volume_ratio" in best_signal:
                message += f"• Volume Ratio: {best_signal['volume_ratio']:.1f}x\n"
            
            # Add risk management
            if "stop_loss" in best_signal:
                message += f"\n🛡️ <b>Stop Loss:</b> ${best_signal['stop_loss']:.2f}"
            if "take_profit_1" in best_signal:
                message += f"\n🎯 <b>Take Profit:</b> ${best_signal['take_profit_1']:.2f}"
            
            # Add timestamp and mode
            message += f"\n\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
            message += f"\n⚙️ Mode: {os.getenv('MODE', 'dry').upper()}"
            
            # Send with appropriate urgency
            if confidence >= 0.85:
                message = "🚨 <b>HIGH PRIORITY</b> 🚨\n" + message
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logging.info(f"📱 Telegram alert sent for {asset} signal")
            
        except TelegramError as e:
            logging.error(f"Telegram send error: {e}")
        except Exception as e:
            logging.error(f"Telegram notification error: {e}")
    
    async def send_trade_execution(self, trade_data: Dict):
        """Send trade execution notification"""
        if not self.bot:
            return
        
        try:
            asset = trade_data.get("asset", "Unknown")
            status = trade_data.get("status", "unknown")
            entry_price = trade_data.get("entry_price", 0)
            quantity = trade_data.get("quantity", 0)
            
            # Status emoji mapping
            status_emoji = {
                "filled": "✅",
                "partial": "🟡", 
                "cancelled": "❌",
                "rejected": "🚫"
            }
            
            emoji = status_emoji.get(status.lower(), "📊")
            
            message = f"""
{emoji} <b>TRADE EXECUTION</b>

💰 <b>Asset:</b> {asset}
📊 <b>Status:</b> {status.upper()}
💵 <b>Price:</b> ${entry_price:,.2f}
📦 <b>Quantity:</b> {quantity:.4f}
💼 <b>Value:</b> ${entry_price * quantity:,.2f}

⏰ {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
⚙️ Mode: {os.getenv('MODE', 'dry').upper()}
"""
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logging.info(f"📱 Trade execution alert sent for {asset}")
            
        except Exception as e:
            logging.error(f"Telegram trade notification error: {e}")
    
    async def send_system_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Send system alert"""
        if not self.bot:
            return
        
        try:
            severity_emoji = {
                "error": "🚨",
                "warning": "⚠️",
                "info": "ℹ️",
                "success": "✅"
            }
            
            emoji = severity_emoji.get(severity.lower(), "📢")
            
            alert_message = f"""
{emoji} <b>SYSTEM ALERT</b>

<b>Type:</b> {alert_type.upper()}
<b>Message:</b> {message}

⏰ {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
"""
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=alert_message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logging.error(f"Telegram system alert error: {e}")
    
    async def send_daily_summary(self, stats: Dict):
        """Send daily trading summary"""
        if not self.bot:
            return
        
        try:
            message = f"""
📊 <b>DAILY TRADING SUMMARY</b>

📈 <b>Signals Generated:</b> {stats.get('total_signals', 0)}
💰 <b>Trades Executed:</b> {stats.get('total_trades', 0)}
📊 <b>Success Rate:</b> {stats.get('success_rate', 0):.1%}
💵 <b>Total PnL:</b> ${stats.get('total_pnl', 0):,.2f}

🎯 <b>Best Performing Asset:</b> {stats.get('best_asset', 'N/A')}
⚡ <b>Avg Confidence:</b> {stats.get('avg_confidence', 0):.1%}

⏰ {time.strftime('%Y-%m-%d', time.gmtime())}
"""
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logging.error(f"Telegram daily summary error: {e}")
    
    async def test_connection(self):
        """Test Telegram bot connection"""
        if not self.bot:
            return False, "Bot not configured"
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="🧪 <b>HFT System Test</b>\n\nTelegram integration is working correctly!",
                parse_mode='HTML'
            )
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {e}"

# Global instance
telegram_notifier = TelegramNotifier()

# Async wrapper functions for compatibility
def send_signal_alert(signal_data: Dict):
    """Sync wrapper for signal alerts"""
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegram_notifier.send_signal_alert(signal_data))
    except RuntimeError:
        # Create new loop if none exists
        asyncio.run(telegram_notifier.send_signal_alert(signal_data))

def send_trade_notification(trade_data: Dict):
    """Sync wrapper for trade notifications"""
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegram_notifier.send_trade_execution(trade_data))
    except RuntimeError:
        asyncio.run(telegram_notifier.send_trade_execution(trade_data))

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    """Sync wrapper for system alerts"""
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegram_notifier.send_system_alert(alert_type, message, severity))
    except RuntimeError:
        asyncio.run(telegram_notifier.send_system_alert(alert_type, message, severity))
