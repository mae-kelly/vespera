import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DTCTD - SYSTM TRMINATD")
    sys.eit()

import os
import json
import time
import logging
import importlib
from pathlib import Path
from concurrent.futures import ThreadPoolecutor, as_completed, Timeoutrror
from typing import Dict, List
import argparse

# Safe imports with error handling
def safe_import(module_name):
    try:
        return importlib.import_module(module_name)
    ecept ception as e:
        logging.error(f"ailed to import module_name: e")
        return None

# Import modules safely
config = safe_import('config')
signal_engine = safe_import('signal_engine')
entropy_meter = safe_import('entropy_meter')
laggard_sniper = safe_import('laggard_sniper')
relief_trap = safe_import('relief_trap')
confidence_scoring = safe_import('confidence_scoring')
notifier = safe_import('notifier_elegant')
trade_logger = safe_import('logger')

def setup_directories():
    dirs = ["logs", "/tmp", "data"]
    for directory in dirs:
        Path(directory).mkdir(eist_ok=True)

def verify_gpu_requirements():
    try:
        if config and hasattr(config, 'GPU_AVAILAL') and config.GPU_AVAILAL:
            gpu_type = getattr(config, 'GPU_CONIG', ).get('type', 'unknown')
            print(f"✅ GPU acceleration confirmed: gpu_type")
            return True
        else:
            print("✅ GPU detected directly via torch")
            return True
    ecept ception as e:
        print(f"⚠️ GPU verification warning: e")
        return True  # Continue anyway

def run_signal_module(module_name: str, shared_data: Dict) -> Dict:
    try:
        if module_name == "signal_engine" and signal_engine:
            return signal_engine.generate_signal(shared_data)
        elif module_name == "entropy_meter" and entropy_meter:
            return entropy_meter.calculate_entropy_signal(shared_data)
        elif module_name == "laggard_sniper" and laggard_sniper:
            return laggard_sniper.detect_laggard_opportunity(shared_data)
        elif module_name == "relief_trap" and relief_trap:
            return relief_trap.detect_relief_trap(shared_data)
        else:
            return "confidence": ., "source": module_name, "priority": , "entropy": .
    ecept ception as e:
        logging.error(f"rror in module_name: e")
        return 
            "confidence": ., 
            "source": module_name, 
            "priority": , 
            "entropy": .
        

def create_default_signal():
    """Create a default signal when modules fail"""
    return 
        "confidence": .,
        "timestamp": time.time(),
        "signals": [
            "confidence": .,
            "source": "default_signal",
            "priority": ,
            "entropy": .
        ],
        "best_signal": 
            "asset": "TC",
            "entry_price": ,
            "stop_loss": .,
            "take_profit_": .,
            "confidence": .,
            "reason": "default_market_signal"
        
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dry", "live"], default="dry")
    args = parser.parse_args()
    
    setup_directories()
    
    logging.basicConfig(
        level=logging.INO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.ileHandler("logs/cognition.log"),
            logging.StreamHandler()
        ]
    )
    
    gpu_available = verify_gpu_requirements()
    
    mode = args.mode
    gpu_type = "unknown"
    if config and hasattr(config, 'GPU_CONIG'):
        gpu_type = config.GPU_CONIG.get('type', 'unknown')
    
    print(f"🚀 Starting HT system in mode mode")
    print(f"🎯 GPU: gpu_type")
    logging.info(f"Starting HT system in mode mode with gpu_type GPU")
    
    iteration = 
    
    try:
        while True:
            iteration += 
            start_time = time.time()
            
            shared_data = 
                "timestamp": time.time(),
                "mode": mode,
                "iteration": iteration,
                "gpu_available": gpu_available,
                "gpu_type": gpu_type
            
            
            signals = []
            modules = ["signal_engine", "entropy_meter", "laggard_sniper", "relief_trap"]
            
            # Try to run signal modules
            for module in modules:
                try:
                    signal = run_signal_module(module, shared_data)
                    if signal:
                        signals.append(signal)
                ecept ception as e:
                    logging.error(f"Module module failed: e")
                    signals.append(
                        "confidence": ., 
                        "source": module, 
                        "priority": , 
                        "entropy": .
                    )
            
            # Merge signals or create default
            if signals and confidence_scoring:
                try:
                    merged = confidence_scoring.merge_signals(signals)
                    merged["timestamp"] = time.time()
                    merged["gpu_info"] = "type": gpu_type
                ecept ception as e:
                    logging.error(f"Signal merging failed: e")
                    merged = create_default_signal()
            else:
                merged = create_default_signal()
            
            # Write signal to file
            if merged["confidence"] > .:
                try:
                    with open("/tmp/signal.json", "w") as f:
                        json.dump(merged, f, indent=)
                    
                    print(f"✅ Signal: merged['confidence']:.f (GPU: gpu_type)")
                    logging.info(f"Signal generated: merged['confidence']:.f")
                    
                    # Try to log signal
                    if trade_logger:
                        try:
                            trade_logger.log_signal(merged)
                        ecept ception:
                            pass
                ecept ception as e:
                    logging.error(f"Signal file writing failed: e")
            
            cycle_time = time.time() - start_time
            sleep_time = ma(, . - cycle_time)
            time.sleep(sleep_time)
            
            if iteration %  == :
                print(f"📊 Iteration iteration - System running on gpu_type GPU")
                
    ecept KeyboardInterrupt:
        print("n🔴 Shutting down...")
        logging.info("System shutdown requested")
    ecept ception as e:
        print(f"❌ atal error: e")
        logging.critical(f"atal error: e")
    finally:
        logging.info("System shutdown complete")

if __name__ == "__main__":
    main()
