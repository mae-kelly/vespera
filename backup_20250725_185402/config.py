import os
import torch
import cupy as cp

MODE = "dry"
ASSETS = ["BTC", "ETH", "SOL"]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SIGNAL_CONFIDENCE_THRESHOLD = 0.7
POSITION_SIZE_PERCENT = 2.0
MAX_OPEN_POSITIONS = 3

def validate_config():
    errors = []
    if MODE not in ["dry", "live"]:
        errors.append("MODE must be 'dry' or 'live'")
    if POSITION_SIZE_PERCENT <= 0 or POSITION_SIZE_PERCENT > 100:
        errors.append("POSITION_SIZE_PERCENT must be between 0 and 100")
    return errors
