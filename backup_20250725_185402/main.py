#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import argparse

import torch
import cupy as cp

import signal_engine
import entropy_meter
import confidence_scoring
import notifier
import logger as trade_logger
import config

def setup_directories():
    dirs = ["logs", "/tmp", "data"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)

def run_signal_module(module_name: str, shared_data: Dict) -> Dict:
    try:
        if module_name == "signal_engine":
            return signal_engine.generate_signal(shared_data)
        elif module_name == "entropy_meter":
            return entropy_meter.calculate_entropy_signal(shared_data)
        else:
            return {"confidence": 0.0, "source": module_name, "priority": 0, "entropy": 0.0}
    except Exception as e:
        print(f"Error in {module_name}: {e}")
        return {"confidence": 0.0, "source": module_name, "priority": 0, "entropy": 0.0}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dry", "live"], default="dry")
    args = parser.parse_args()
    
    # Setup directories first
    setup_directories()
    
    # Setup logging after directories exist
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/cognition.log"),
            logging.StreamHandler()
        ]
    )
    
    config.MODE = args.mode
    print(f"🚀 Starting HFT system in {config.MODE} mode")
    logging.info(f"Starting HFT system in {config.MODE} mode")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            start_time = time.time()
            
            shared_data = {
                "timestamp": time.time(),
                "mode": config.MODE,
                "iteration": iteration,
                "gpu_available": torch.cuda.is_available()
            }
            
            # Collect signals
            signals = []
            modules = ["signal_engine", "entropy_meter"]
            
            for module in modules:
                signal = run_signal_module(module, shared_data)
                signals.append(signal)
            
            # Merge signals
            if signals:
                merged = confidence_scoring.merge_signals(signals)
                merged["timestamp"] = time.time()
                
                if merged["confidence"] > 0.05:
                    # Write signal file
                    with open("/tmp/signal.json", "w") as f:
                        json.dump(merged, f, indent=2)
                    
                    print(f"✅ Signal: {merged['confidence']:.3f}")
                    logging.info(f"Signal generated: {merged['confidence']:.3f}")
                    
                    trade_logger.log_signal(merged)
            
            # Sleep for next iteration
            cycle_time = time.time() - start_time
            sleep_time = max(0, 1.0 - cycle_time)
            time.sleep(sleep_time)
            
            if iteration % 10 == 0:
                print(f"📊 Iteration {iteration} - System running")
            
    except KeyboardInterrupt:
        print("\n🔴 Shutting down...")
        logging.info("System shutdown")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
