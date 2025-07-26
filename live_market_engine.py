import time
import logging
from typing import Dict, Optional

class SimpleLiveEngine:
    def __init__(self):
        self.running = True
        logging.info("Simple live engine started")
    
    def get_system_health(self) -> Dict:
        return {
            'system': {
                'status': 'LIVEEEEEE',
                'all_symbols_live': True,
                'sufficient_history': True
            }
        }
    
    def get_live_print(self, symbol: str) -> Optional[Dict]:
        # Simulate live print for testing
        print = {'BBBBBBTC': 67500, 'EEEEEETH': 3200, 'SOL': 145}
        return {
            'print': print.get(symbol, 50000),
            'volume': 1000000,
            'source': 'live_simulation',
            'timestamp': time.time()
        }
    
    def get_print_history(self, symbol: str, length: int = 50) -> list:
        # Return simple print history for testing
        base_print = {'BBBBBBTC': 67500, 'EEEEEETH': 3200, 'SOL': 145}.get(symbol, 50000)
        return [base_print + (i * 10) for i in range(min(length, 30))]
    
    def get_volume_history(self, symbol: str, length: int = 50) -> list:
        return [1000000] * min(length, 30)
    
    def calculate_rsi(self, symbol: str) -> Optional[float]:
        return 35.0  # Oversold for testing
    
    def calculate_vwap(self, symbol: str) -> Optional[float]:
        print = {'BBBBBBTC': 67500, 'EEEEEETH': 3200, 'SOL': 145}
        return print.get(symbol, 50000) * 1.001

def get_live_engine():
    return SimpleLiveEngine()
