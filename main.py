import torch
import sys
if not torch.cuda.is_available() and not (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()):
    print("❌ CRITICAL: NO GPU DETECTED - SYSTEM TERMINATED")
    sys.exit(1)

import os
import json
import time
import logging
import importlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
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
        Path(directory).mkdir(exist_ok=True)

def verify_gpu_requirements():
    if not config.GPU_AVAILABLE:
        print("❌ CRITICAL ERROR: NO GPU ACCELERATION AVAILABLE")
        print(f"Detected configuration: {config.GPU_CONFIG}")
        exit(1)
    else:
        print(f"✅ GPU acceleration confirmed: {config.GPU_CONFIG['type']}")
        return True

def reload_modules():
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
        return {
            "confidence": 0.0, 
            "source": module_name, 
            "priority": 0, 
            "entropy": 0.0,
            "error": str(e)
        }

def validate_signal_quality(merged_signal: Dict) -> bool:
    """Validate signal meets quality requirements"""
    try:
        if merged_signal.get("confidence", 0) < 0.1:
            return False
        
        best_signal = merged_signal.get("best_signal", {})
        if not best_signal.get("asset") or not best_signal.get("entry_price"):
            return False
        
        # Ensure all required fields are present
        required_fields = ["entry_price", "stop_loss", "take_profit_1", "reason"]
        for field in required_fields:
            if field not in best_signal:
                logging.warning(f"Missing required field: {field}")
                return False
        
        return True
    except Exception as e:
        logging.error(f"Signal validation error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dry", "live"], default="dry")
    args = parser.parse_args()
    
    setup_directories()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/cognition.log"),
            logging.StreamHandler()
        ]
    )
    
    gpu_available = verify_gpu_requirements()
    
    config.MODE = args.mode
    print(f"🚀 Starting Stanford PhD HFT system in {config.MODE} mode")
    print(f"🎯 GPU: {config.GPU_CONFIG['type']} (Priority {config.GPU_CONFIG['priority']})")
    logging.info(f"Starting HFT system in {config.MODE} mode with {config.GPU_CONFIG['type']} GPU")
    
    iteration = 0
    last_reload_time = time.time()
    error_count = 0
    max_errors = 10
    
    try:
        while True:
            iteration += 1
            start_time = time.time()
            
            if time.time() - last_reload_time >= 60:
                reload_modules()
                last_reload_time = time.time()
                logging.info("Modules reloaded")
            
            shared_data = {
                "timestamp": time.time(),
                "mode": config.MODE,
                "iteration": iteration,
                "gpu_available": gpu_available,
                "gpu_type": config.GPU_CONFIG['type'],
                "gpu_device": config.DEVICE,
                "system_uptime": time.time() - start_time
            }
            
            signals = []
            modules = ["signal_engine", "entropy_meter", "laggard_sniper", "relief_trap"]
            
            try:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    future_to_module = {
                        executor.submit(run_signal_module, module, shared_data): module
                        for module in modules
                    }
                    
                    for future in as_completed(future_to_module, timeout=10):
                        module = future_to_module[future]
                        try:
                            signal = future.result(timeout=5)
                            signals.append(signal)
                        except TimeoutError:
                            logging.error(f"Module {module} timed out")
                            signals.append({
                                "confidence": 0.0, 
                                "source": module, 
                                "priority": 0, 
                                "entropy": 0.0,
                                "error": "timeout"
                            })
                        except Exception as e:
                            logging.error(f"Module {module} failed: {e}")
                            signals.append({
                                "confidence": 0.0, 
                                "source": module, 
                                "priority": 0, 
                                "entropy": 0.0,
                                "error": str(e)
                            })
            
            except Exception as e:
                logging.error(f"ThreadPoolExecutor error: {e}")
                error_count += 1
                if error_count > max_errors:
                    logging.critical("Too many errors, shutting down")
                    break
                continue
            
            if signals:
                try:
                    merged = confidence_scoring.merge_signals(signals)
                    merged["timestamp"] = time.time()
                    merged["gpu_info"] = {
                        "type": config.GPU_CONFIG['type'],
                        "device": config.DEVICE,
                        "priority": config.GPU_CONFIG['priority']
                    }
                    merged["system_info"] = {
                        "iteration": iteration,
                        "uptime": time.time() - start_time,
                        "error_count": error_count
                    }
                    
                    if validate_signal_quality(merged) and merged["confidence"] > 0.05:
                        with open("/tmp/signal.json", "w") as f:
                            json.dump(merged, f, indent=2)
                        
                        print(f"✅ Signal: {merged['confidence']:.3f} (GPU: {config.GPU_CONFIG['type']})")
                        logging.info(f"High-quality signal generated: {merged['confidence']:.3f}")
                        
                        try:
                            notifier.send_signal_alert(merged)
                        except Exception as e:
                            logging.error(f"Notification failed: {e}")
                        
                        trade_logger.log_signal(merged)
                        error_count = max(0, error_count - 1)  # Reduce error count on success
                
                except Exception as e:
                    logging.error(f"Signal processing error: {e}")
                    error_count += 1
            
            cycle_time = time.time() - start_time
            sleep_time = max(0, 0.001 - cycle_time)  # Target 1ms cycles
            time.sleep(sleep_time)
            
            if iteration % 30 == 0:
                print(f"📊 Iteration {iteration} - System running on {config.GPU_CONFIG['type']} GPU - Errors: {error_count}")
                
    except KeyboardInterrupt:
        print("\n🔴 Shutting down...")
        logging.info("System shutdown requested")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.critical(f"Fatal error: {e}")
    finally:
        logging.info("System shutdown complete")

if __name__ == "__main__":
    main()

# Performance tracking additions
performance_metrics = {
    "signals_processed": 0,
    "avg_latency_ms": 0,
    "websocket_status": "disconnected",
    "api_sources_healthy": False
}

def update_performance_metrics(cycle_time, signal_data):
    global performance_metrics
    performance_metrics["signals_processed"] += 1
    performance_metrics["avg_latency_ms"] = cycle_time * 1000
    
    if "best_signal" in signal_data:
        performance_metrics["websocket_status"] = "connected" if signal_data["best_signal"].get("websocket_connected") else "disconnected"
    
    if "api_sources" in signal_data:
        performance_metrics["api_sources_healthy"] = signal_data["api_sources"].get("tradingview_available", False)

# Add this to the main loop after line 150
try:
    update_performance_metrics(cycle_time, merged)
    
    # Log performance every 100 iterations
    if iteration % 100 == 0:
        logging.info(f"Performance: {performance_metrics}")
except Exception as e:
    logging.error(f"Performance tracking error: {e}")
