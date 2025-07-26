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
import entropy_meter
import laggard_sniper
import relief_trap
import confidence_scoring

class ConcurrentHFTSystem:
    def __init__(self, mode="dry"):
        self.mode = mode
        self.running = True
        self.iteration = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.last_reload = time.time()
        
        # Signal modules for concurrent execution
        self.signal_modules = [
            ('entropy', entropy_meter.calculate_entropy_signal),
            ('laggard', laggard_sniper.detect_laggard_opportunity), 
            ('relief', relief_trap.detect_relief_trap),
            ('main', signal_engine.generate_signal)
        ]
        
        Path("/tmp").mkdir(exist_ok=True)
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Concurrent HFT System started in {mode} mode")
    
    def reload_modules_if_needed(self):
        """Reload modules every 60 seconds"""
        if time.time() - self.last_reload > 60:
            try:
                importlib.reload(signal_engine)
                importlib.reload(entropy_meter)
                importlib.reload(laggard_sniper)
                importlib.reload(relief_trap)
                importlib.reload(confidence_scoring)
                logging.info("🔄 Modules reloaded")
                self.last_reload = time.time()
            except Exception as e:
                logging.error(f"Module reload failed: {e}")
    
    def run_signal_module(self, module_name, func, shared_data):
        """Run a single signal module"""
        try:
            start_time = time.time()
            result = func(shared_data)
            execution_time = (time.time() - start_time) * 1000
            result['execution_time_ms'] = execution_time
            result['module'] = module_name
            return result
        except Exception as e:
            logging.error(f"Signal module {module_name} failed: {e}")
            return {"confidence": 0.0, "source": module_name, "error": str(e)}
    
    def generate_concurrent_signals(self, shared_data):
        """Generate signals from all modules concurrently"""
        futures = []
        
        # Submit all signal generation tasks
        for module_name, func in self.signal_modules:
            future = self.executor.submit(self.run_signal_module, module_name, func, shared_data)
            futures.append(future)
        
        # Collect results as they complete
        signals = []
        for future in as_completed(futures, timeout=5.0):
            try:
                signal = future.result()
                if signal.get("confidence", 0) > 0.1:
                    signals.append(signal)
            except Exception as e:
                logging.error(f"Future completion error: {e}")
        
        return signals
    
    def run(self):
        """Main execution loop"""
        while self.running:
            try:
                self.iteration += 1
                start_time = time.time()
                
                # Reload modules every 60s
                self.reload_modules_if_needed()
                
                # Create shared data
                shared_data = {
                    "timestamp": time.time(),
                    "mode": self.mode,
                    "iteration": self.iteration
                }
                
                # Generate signals concurrently
                signals = self.generate_concurrent_signals(shared_data)
                
                if signals:
                    # Merge signals using confidence scoring
                    merged = confidence_scoring.merge_signals(signals)
                    
                    if merged.get("confidence", 0) > 0.7:
                        # Write signal for Rust execution layer
                        with open("/tmp/signal.json", "w") as f:
                            json.dump(merged, f, indent=2)
                        
                        logging.info(f"🎯 Strong signal: {merged['confidence']:.3f} from {len(signals)} modules")
                    else:
                        logging.debug(f"Weak signal: {merged.get('confidence', 0):.3f}")
                else:
                    logging.debug("No signals generated")
                
                # Maintain 1Hz execution rate
                cycle_time = time.time() - start_time
                sleep_time = max(0, 1.0 - cycle_time)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logging.info("Shutting down...")
                break
            except Exception as e:
                logging.error(f"Main loop error: {e}")
                time.sleep(1)
        
        self.executor.shutdown(wait=True)

def main():
    parser = argparse.ArgumentParser(description='HFT Trading System')
    parser.add_argument('--mode', choices=['dry', 'live'], default='dry',
                       help='Trading mode (default: dry)')
    args = parser.parse_args()
    
    system = ConcurrentHFTSystem(mode=args.mode)
    system.run()

if __name__ == "__main__":
    main()
