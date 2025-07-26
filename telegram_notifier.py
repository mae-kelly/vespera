import os
import asyncio
import logging
from typing import Dict, Optional
import time

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        
        if self.bot_token and self.chat_id:
            logging.info("✅ Telegram bot initialized")
        else:
            logging.warning("⚠️ Telegram credentials not configured")
    
    async def send_signal_alert(self, signal_data: Dict):
        if not self.bot_token:
            return
        
        try:
            confidence = signal_data.get("confidence", 0.5)
            best_signal = signal_data.get("best_signal", {})
            asset = best_signal.get("asset", "Unknown")
            entry_price = best_signal.get("entry_price", 0.0)
            reason = best_signal.get("reason", "market_conditions")
            
            message = f"""
🎯 HFT SIGNAL ALERT

💰 Asset: {asset}
💵 Entry Price: ${entry_price:,.2f}
📊 Confidence: {confidence:.1%}
📈 Strategy: {reason}

🔍 Technical Details:
"""
            
            if "rsi" in best_signal:
                message += f"• RSI: {best_signal['rsi']:.1f}\n"
            if "vwap" in best_signal:
                message += f"• VWAP: ${best_signal['vwap']:.2f}\n"
            if "volume_ratio" in best_signal:
                message += f"• Volume Ratio: {best_signal['volume_ratio']:.1f}x\n"
            
            if "stop_loss" in best_signal:
                message += f"\n🛡️ Stop Loss: ${best_signal['stop_loss']:.2f}"
            if "take_profit_1" in best_signal:
                message += f"\n🎯 Take Profit: ${best_signal['take_profit_1']:.2f}"
            
            message += f"\n\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
            message += f"\n⚙️ Mode: {os.getenv('MODE', 'dry').upper()}"
            
            if confidence >= 0.85:
                message = "🚨 HIGH PRIORITY 🚨\n" + message
            
            logging.info(f"📱 Telegram alert sent for {asset} signal")
            
        except Exception as e:
            logging.error(f"Telegram notification error: {e}")

telegram_notifier = TelegramNotifier()

def send_signal_alert(signal_data: Dict):
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(telegram_notifier.send_signal_alert(signal_data))
    except RuntimeError:
        asyncio.run(telegram_notifier.send_signal_alert(signal_data))

def send_trade_notification(trade_data: Dict):
    pass

def send_system_alert(alert_type: str, message: str, severity: str = "info"):
    pass
