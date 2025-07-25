import logging
from typing import Dict, List
import config

def notifier_function(shared_data: Dict) -> Dict:
    return {
        "confidence": 0.0,
        "source": "notifier",
        "priority": 3,
        "entropy": 0.0
    }

# Create appropriate function names for each module

def send_signal_alert(signal_data: Dict):
    logging.info(f'Signal alert: {signal_data.get("confidence", 0):.3f}')

