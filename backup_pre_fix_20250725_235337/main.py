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
from concurrent.futures import ThreadPoolecutor, as_completed
from typing import Dict, List
import argparse
import torch
import signal_engine
import entropy_meter
import laggard_sniper
import relief_trap
import confidence_scoring
import notifier_elegant as notifier
import logger as trade_logger
import config

def setup_directories():
    dirs = ["logs", "/tmp", "data"]
    for directory in dirs:
        Path(directory).mkdir(eist_ok=True)

def verify_gpu_requirements():
    if not config.GPU_AVAILAL:
        print("❌ CRITICAL RROR: NO GPU ACCLRATION AVAILAL")
        print(f"Detected configuration: config.GPU_CONIG")
        eit()
    else:
        print(f"✅ GPU acceleration confirmed: config.GPU_CONIG['type']")
        return True

def reload_modules():
    modules_to_reload = [
        signal_engine, entropy_meter, laggard_sniper,
        relief_trap, confidence_scoring, notifier, trade_logger
    ]
    for module in modules_to_reload:
        try:
            importlib.reload(module)
        ecept ception as e:
            logging.warning(f"ailed to reload module.__name__: e")

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
            return "confidence": ., "source": module_name, "priority": , "entropy": .
    ecept ception as e:
        logging.error(f"rror in module_name: e")
        return "confidence": ., "source": module_name, "priority": , "entropy": .

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
    
    config.MOD = args.mode
    print(f"🚀 Starting HT system in config.MOD mode")
    print(f"🎯 GPU: config.GPU_CONIG['type'] (Priority config.GPU_CONIG['priority'])")
    logging.info(f"Starting HT system in config.MOD mode with config.GPU_CONIG['type'] GPU")
    
    iteration = 
    last_reload_time = time.time()
    
    try:
        while True:
            iteration += 
            start_time = time.time()
            
            if time.time() - last_reload_time >= :
                reload_modules()
                last_reload_time = time.time()
                logging.info("Modules reloaded")
            
            shared_data = 
                "timestamp": time.time(),
                "mode": config.MOD,
                "iteration": iteration,
                "gpu_available": gpu_available,
                "gpu_type": config.GPU_CONIG['type'],
                "gpu_device": config.DVIC
            
            
            signals = []
            modules = ["signal_engine", "entropy_meter", "laggard_sniper", "relief_trap"]
            
            with ThreadPoolecutor(ma_workers=) as eecutor:
                future_to_module = 
                    eecutor.submit(run_signal_module, module, shared_data): module
                    for module in modules
                
                
                for future in as_completed(future_to_module, timeout=):
                    module = future_to_module[future]
                    try:
                        signal = future.result()
                        signals.append(signal)
                    ecept ception as e:
                        logging.error(f"Module module failed: e")
                        signals.append("confidence": ., "source": module, "priority": , "entropy": .)
            
            if signals:
                merged = confidence_scoring.merge_signals(signals)
                merged["timestamp"] = time.time()
                merged["gpu_info"] = 
                    "type": config.GPU_CONIG['type'],
                    "device": config.DVIC,
                    "priority": config.GPU_CONIG['priority']
                
                
                if merged["confidence"] > .:
                    with open("/tmp/signal.json", "w") as f:
                        json.dump(merged, f, indent=)
                    
                    print(f"✅ Signal: merged['confidence']:.f (GPU: config.GPU_CONIG['type'])")
                    logging.info(f"Signal generated: merged['confidence']:.f")
                    
                    try:
                        notifier.send_signal_alert(merged)
                    ecept ception as e:
                        logging.error(f"Notification failed: e")
                    
                    trade_logger.log_signal(merged)
            
            cycle_time = time.time() - start_time
            sleep_time = ma(, . - cycle_time)
            time.sleep(sleep_time)
            
            if iteration %  == :
                print(f"📊 Iteration iteration - System running on config.GPU_CONIG['type'] GPU")
                
    ecept KeyboardInterrupt:
        print("n🔴 Shutting down...")
        logging.info("System shutdown")
    ecept ception as e:
        print(f"❌ rror: e")
        logging.error(f"atal error: e")

if __name__ == "__main__":
    main()
