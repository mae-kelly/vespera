#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
import importlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import argparse

import torch
import cupy as cp

import signal_engine
import entropy_meter
import laggard_sniper
import relief_trap
import confidence_scoring
import notifier
import logger as trade_logger
import config

def setup_directories():
    dirs = ["logs", "/tmp", "data"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)

def setup_gpu():
    """Setup GPU with A100 detection and fallback"""
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        if "A100" in device_name:
            print(f"🚀 A100 GPU detected: {device_name}")
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.cuda.empty_cache()
            
            # Setup CuPy for A100
            cp.cuda.Device(0).use()
            mempool = cp.get_default_memory_pool()
            mempool.set_limit(size=2**33)  # 8GB limit
            
            print("✅ A100 optimization enabled")
            return True
        else:
            print(f"⚠️ WARNING: Non-A100 GPU detected: {device_name}")
            print("⚠️ Falling back to CPU mode for optimal compatibility")
            return False
    else:
        print("⚠️ WARNING: No CUDA GPU available, using CPU fallback")
        return False

def reload_modules():
    """Reload all signal modules every 60 seconds"""
    modules_to_reload = [
        signal_engine, entropy_meter, laggard_sniper, 
        relief_trap, confidence_scoring, notifier, trade_logger
    ]
    
    for module in modules_to_reload:
        try:
            importlib.reload(module)
        except Exception as e:
            logging.warning(f"Failed to reload {module.__name__}: {e}")

def run_signal_module(module_name: str, shared_data: Dict) -> Dict:
    try:
        if module_name == "signal_engine":
            return signal_engine.generate_signal(shared_data)
        elif module_name == "entropy_meter":
            return entropy_meter.calculate_entropy_signal(shared_data)
        elif module_name == "laggard_sniper":
            return laggard_sniper.detect_laggard_opportunity(shared_data)
        elif module_name == "relief_trap":
            return relief_trap.detect_relief_trap(shared_data)
        else:
            return {"confidence": 0.0, "source": module_name, "priority": 0, "entropy": 0.0}
    except Exception as e:
        logging.error(f"Error in {module_name}: {e}")
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
    
    # Setup GPU
    gpu_available = setup_gpu()
    
    config.MODE = args.mode
    print(f"🚀 Starting HFT system in {config.MODE} mode")
    logging.info(f"Starting HFT system in {config.MODE} mode")
    
    iteration = 0
    last_reload_time = time.time()
    
    try:
        while True:
            iteration += 1
            start_time = time.time()
            
            # Reload modules every 60 seconds
            if time.time() - last_reload_time >= 60:
                reload_modules()
                last_reload_time = time.time()
                logging.info("Modules reloaded")
            
            shared_data = {
                "timestamp": time.time(),
                "mode": config.MODE,
                "iteration": iteration,
                "gpu_available": gpu_available
            }
            
            # Collect signals using ThreadPoolExecutor
            signals = []
            modules = ["signal_engine", "entropy_meter", "laggard_sniper", "relief_trap"]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_module = {
                    executor.submit(run_signal_module, module, shared_data): module 
                    for module in modules
                }
                
                for future in as_completed(future_to_module, timeout=5):
                    module = future_to_module[future]
                    try:
                        signal = future.result()
                        signals.append(signal)
                    except Exception as e:
                        logging.error(f"Module {module} failed: {e}")
                        signals.append({"confidence": 0.0, "source": module, "priority": 0, "entropy": 0.0})
            
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
                    
                    # Send notifications
                    notifier.send_signal_alert(merged)
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
