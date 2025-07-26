#!/usr/bin/env python3
import torch
import sys
import time
import json
import logging
import importlib
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import config
import signal_engine
import confidence_scoring

class ProductionHFTSystem:
    def __init__(self, mode="live"):
        if mode != "live":
            raise RuntimeError("Only live mode allowed in production")
        
        self.mode = mode
        self.running = True
        self.iteration = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.last_reload = time.time()
        
        self.signal_modules = [('main', signal_engine.generate_signal)]
        
        Path("/tmp").mkdir(exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Production HFT System started in {mode} mode")
    
    def reload_modules_if_needed(self):
        if time.time() - self.last_reload > 60:
            try:
                importlib.reload(signal_engine)
                importlib.reload(confidence_scoring)
                logging.info("Production modules reloaded")
                self.last_reload = time.time()
            except Exception as e:
                raise RuntimeError(f"Module reload failed: {e}")
    
    def run_signal_module(self, module_name, func, shared_data):
        try:
            start_time = time.time()
            result = func(shared_data)
            execution_time = (time.time() - start_time) * 1000
            result['execution_time_ms'] = execution_time
            result['module'] = module_name
            return result
        except Exception as e:
            raise RuntimeError(f"Signal module {module_name} failed: {e}")
    
    def generate_concurrent_signals(self, shared_data):
        futures = []
        
        for module_name, func in self.signal_modules:
            future = self.executor.submit(self.run_signal_module, module_name, func, shared_data)
            futures.append(future)
        
        signals = []
        for future in as_completed(futures, timeout=5.0):
            try:
                signal = future.result()
                confidence = signal.get("confidence")
                if confidence is None:
                    raise RuntimeError("Signal missing confidence")
                if confidence > 0.1:
                    signals.append(signal)
            except Exception as e:
                raise RuntimeError(f"Future completion failed: {e}")
        
        return signals
    
    def run(self):
        while self.running:
            try:
                self.iteration += 1
                start_time = time.time()
                
                self.reload_modules_if_needed()
                
                shared_data = {
                    "timestamp": time.time(),
                    "mode": self.mode,
                    "iteration": self.iteration
                }
                
                signals = self.generate_concurrent_signals(shared_data)
                
                if signals:
                    merged = confidence_scoring.merge_signals(signals)
                    
                    confidence = merged.get("confidence")
                    if confidence is None:
                        raise RuntimeError("Merged signal missing confidence")
                    
                    if confidence >= 0.75:
                        with open("/tmp/signal.json", "w") as f:
                            json.dump(merged, f, indent=2)
                        
                        logging.info(f"Production signal: {confidence:.3f} from {len(signals)} modules")
                    else:
                        logging.debug(f"Signal below threshold: {confidence:.3f}")
                else:
                    raise RuntimeError("No signals generated")
                
                cycle_time = time.time() - start_time
                sleep_time = max(0, 1.0 - cycle_time)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logging.info("Production system shutting down...")
                break
            except Exception as e:
                logging.error(f"PRODUCTION ERROR: {e}")
                raise
        
        self.executor.shutdown(wait=True)

def main():
    parser = argparse.ArgumentParser(description='Production HFT Trading System')
    parser.add_argument('--mode', choices=['live'], default='live',
                       help='Trading mode (production only allows live)')
    args = parser.parse_args()
    
    system = ProductionHFTSystem(mode=args.mode)
    system.run()

if __name__ == "__main__":
    main()
