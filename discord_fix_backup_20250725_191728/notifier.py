import logging
import os
from typing import Dict, List
import config
import time

def send_signal_alert(signal_data: Dict):
    """Send signal alert via Telegram"""
    try:
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not telegram_token or not telegram_chat_id:
            logging.warning("Telegram credentials not configured")
            return
        
        # Import telegram library
        try:
            import telegram
        except ImportError:
            logging.error("python-telegram-bot library not installed")
            return
        
        bot = telegram.Bot(token=telegram_token)
        
        # Format message with required fields
        confidence = signal_data.get("confidence", 0)
        signal_type = "SHORT SIGNAL"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Extract asset and reason from best signal
        best_signal = signal_data.get("best_signal", {})
        asset = best_signal.get("asset", "Unknown")
        reason = best_signal.get("reason", "market_conditions")
        entry_price = best_signal.get("entry_price", 0)
        
        # Create message
        message = f"""🚨 {signal_type} ALERT 🚨

Asset: {asset}
Entry Price: ${entry_price:,.2f}
Confidence: {confidence:.1%}
Reason: {reason}
Timestamp: {timestamp}

Sources: {', '.join(signal_data.get('active_sources', []))}
BTC Dominance: {signal_data.get('btc_dominance', 0):.1f}%"""
        
        # Add technical details if available
        if best_signal:
            if "rsi" in best_signal:
                message += f"\nRSI: {best_signal['rsi']:.1f}"
            if "vwap_deviation" in best_signal:
                message += f"\nVWAP Deviation: {best_signal['vwap_deviation']:.1f}%"
        
        message += f"\n\nMode: {config.MODE.upper()}"
        
        # Send message
        bot.send_message(chat_id=telegram_chat_id, text=message)
        logging.info(f"Telegram alert sent for {asset} signal")
        
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")

def send_trade_notification(trade_data: Dict):
    """Send trade execution notification"""
    try:
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not telegram_token or not telegram_chat_id:
            return
        
        import telegram
        bot = telegram.Bot(token=telegram_token)
        
        asset = trade_data.get("asset", "Unknown")
        status = trade_data.get("status", "unknown")
        entry_price = trade_data.get("entry_price", 0)
        quantity = trade_data.get("quantity", 0)
        
        message = f"""💼 TRADE EXECUTED

Asset: {asset}
Status: {status.upper()}
Entry: ${entry_price:,.2f}
Quantity: {quantity:.4f}
Mode: {config.MODE.upper()}

Time: {time.strftime("%Y-%m-%d %H:%M:%S")}"""
        
        bot.send_message(chat_id=telegram_chat_id, text=message)
        logging.info(f"Trade notification sent for {asset}")
        
    except Exception as e:
        logging.error(f"Failed to send trade notification: {e}")
