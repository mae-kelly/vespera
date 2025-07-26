import threading
import time
import logging
import signal_engine
import importlib

class AdvancedErrorRecovery:
    def __init__(self):
        self.circuit_breaker = {"open": False, "failures": 0, "last_failure": 0}
        self.module_health = {}
        self.recovery_strategies = {
            "signal_engine": self._recover_signal_engine,
            "websocket": self._recover_websocket,
            "memory": self._recover_memory
        }
        
    def handle_error(self, error_type, exception):
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure"] = time.time()
        
        if self.circuit_breaker["failures"] > 5:
            self.circuit_breaker["open"] = True
            
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](exception)
        return self._generic_recovery(error_type, exception)
        
    def _recover_signal_engine(self, exception):
        try:
            importlib.reload(signal_engine)
            signal_engine.feed.start_feed()
            return True
        except:
            return False
            
    def _recover_websocket(self, exception):
        try:
            signal_engine.feed.running = False
            time.sleep(2)
            signal_engine.feed = signal_engine.PriceDataFeed()
            signal_engine.feed.start_feed()
            return True
        except:
            return False
            
    def _recover_memory(self, exception):
        try:
            import gc
            gc.collect()
            if hasattr(torch, 'cuda') and torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True
        except:
            return False
            
    def _generic_recovery(self, error_type, exception):
        time.sleep(min(self.circuit_breaker["failures"], 30))
        return False
        
    def is_circuit_open(self):
        if self.circuit_breaker["open"]:
            if time.time() - self.circuit_breaker["last_failure"] > 300:
                self.circuit_breaker["open"] = False
                self.circuit_breaker["failures"] = 0
        return self.circuit_breaker["open"]

recovery_manager = AdvancedErrorRecovery()
