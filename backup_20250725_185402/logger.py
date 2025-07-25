import logging
from typing import Dict, List
import config

def logger_function(shared_data: Dict) -> Dict:
    return {
        "confidence": 0.0,
        "source": "logger",
        "priority": 3,
        "entropy": 0.0
    }

# Create appropriate function names for each module

def log_signal(signal_data: Dict):
    logging.info(f'Signal logged: {signal_data.get("confidence", 0):.3f}')

