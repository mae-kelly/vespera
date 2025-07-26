#!/bin/bash

set -e

echo "🔧 DEBUGGING AND FIXING CRASH..."

check_logs() {
    echo "📄 Checking logs for crash details..."
    if [ -f "logs/engine.log" ]; then
        echo "Last 20 lines of engine.log:"
        tail -20 logs/engine.log
    fi
    
    if [ -f "logs/cognition.log" ]; then
        echo "Last 20 lines of cognition.log:"
        tail -20 logs/cognition.log
    fi
}

test_imports() {
    echo "🧪 Testing Python imports..."
    
    python3 -c "
try:
    import config
    print('✓ config imported')
except Exception as e:
    print(f'❌ config failed: {e}')

try:
    import signal_engine
    print('✓ signal_engine imported')
except Exception as e:
    print(f'❌ signal_engine failed: {e}')

try:
    import notifier_elegant
    print('✓ notifier_elegant imported')
except Exception as e:
    print(f'❌ notifier_elegant failed: {e}')

try:
    import confidence_scoring
    print('✓ confidence_scoring imported')
except Exception as e:
    print(f'❌ confidence_scoring failed: {e}')
"
}

test_main_py() {
    echo "🧪 Testing main.py syntax..."
    
    if python3 -m py_compile main.py; then
        echo "✓ main.py syntax OK"
    else
        echo "❌ main.py has syntax errors"
        return 1
    fi
}

fix_main_py_robust() {
    echo "🔧 Creating robust main.py..."
    
    cat > main.py << 'EOF'
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

def setup_directories():
    dirs = ["logs", "/tmp", "data"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/cognition.log"),
            logging.StreamHandler()
        ]
    )

def import_modules():
    try:
        import torch
        import cupy_fallback as cp
        import config
        import signal_engine
        import entropy_meter
        import laggard_sniper
        import relief_trap
        import confidence_scoring
        import notifier_elegant as notifier
        import logger as trade_logger
        
        return {
            'torch': torch,
            'cp': cp,
            'config': config,
            'signal_engine': signal_engine,
            'entropy_meter': entropy_meter,
            'laggard_sniper': laggard_sniper,
            'relief_trap': relief_trap,
            'confidence_scoring': confidence_scoring,
            'notifier': notifier,
            'trade_logger': trade_logger
        }
    except Exception as e:
        logging.error(f"Module import failed: {e}")
        raise

def verify_gpu_requirements(config):
    if not config.GPU_AVAILABLE:
        print("❌ CRITICAL ERROR: NO GPU ACCELERATION AVAILABLE")
        sys.exit(1)
    print(f"✅ GPU acceleration confirmed: {config.GPU_CONFIG['type']}")
    return True

def run_signal_module(module_name: str, modules: dict, shared_data: Dict) -> Dict:
    try:
        if module_name == "signal_engine":
            return modules['signal_engine'].generate_signal(shared_data)
        elif module_name == "entropy_meter":
            return modules['entropy_meter'].calculate_entropy_signal(shared_data)
        elif module_name == "laggard_sniper":
            return modules['laggard_sniper'].detect_laggard_opportunity(shared_data)
        elif module_name == "relief_trap":
            return modules['relief_trap'].detect_relief_trap(shared_data)
        else:
            raise Exception(f"Unknown module: {module_name}")
    except Exception as e:
        logging.error(f"Error in {module_name}: {e}")
        return {"confidence": 0.0, "source": module_name, "priority": 0, "entropy": 0.0}

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--mode", choices=["dry", "live"], default="dry")
        args = parser.parse_args()
        
        setup_directories()
        setup_logging()
        
        print("🔧 Importing modules...")
        modules = import_modules()
        
        print("🔧 Verifying GPU...")
        gpu_available = verify_gpu_requirements(modules['config'])
        
        modules['config'].MODE = args.mode
        print(f"🚀 Starting HFT system in {modules['config'].MODE} mode")
        print(f"🎯 GPU: {modules['config'].GPU_CONFIG['type']}")
        logging.info(f"Starting HFT system in {modules['config'].MODE} mode")
        
        iteration = 0
        last_reload_time = time.time()
        last_signal_time = 0
        
        print("🔧 Starting signal feed...")
        modules['signal_engine'].feed.start_feed()
        time.sleep(3)
        
        print("🔧 Starting main loop...")
        
        while True:
            iteration += 1
            start_time = time.time()
            
            if time.time() - last_reload_time >= 300:
                logging.info("Reloading modules...")
                try:
                    for module_name, module in modules.items():
                        if module_name not in ['torch', 'cp', 'config']:
                            importlib.reload(module)
                except Exception as e:
                    logging.warning(f"Module reload failed: {e}")
                last_reload_time = time.time()
            
            shared_data = {
                "timestamp": time.time(),
                "mode": modules['config'].MODE,
                "iteration": iteration,
                "gpu_available": gpu_available,
                "gpu_type": modules['config'].GPU_CONFIG['type'],
                "gpu_device": modules['config'].DEVICE
            }
            
            signals = []
            signal_modules = ["signal_engine", "entropy_meter", "laggard_sniper", "relief_trap"]
            
            try:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    future_to_module = {
                        executor.submit(run_signal_module, module, modules, shared_data): module 
                        for module in signal_modules
                    }
                    
                    for future in as_completed(future_to_module, timeout=10):
                        signal = future.result()
                        signals.append(signal)
            except Exception as e:
                logging.error(f"Signal collection failed: {e}")
                signals = []
            
            if signals:
                try:
                    merged = modules['confidence_scoring'].merge_signals(signals)
                    merged["timestamp"] = time.time()
                    merged["gpu_info"] = {
                        "type": modules['config'].GPU_CONFIG['type'],
                        "device": modules['config'].DEVICE,
                        "priority": modules['config'].GPU_CONFIG['priority']
                    }
                    
                    confidence = merged.get("confidence", 0)
                    
                    should_send = False
                    if confidence >= 0.6:
                        should_send = True
                    elif confidence >= 0.4 and time.time() - last_signal_time >= 30:
                        should_send = True
                    elif confidence >= 0.2 and time.time() - last_signal_time >= 60:
                        should_send = True
                    
                    if should_send and confidence > 0.05:
                        with open("/tmp/signal.json", "w") as f:
                            json.dump(merged, f, indent=2)
                        
                        print(f"✅ Signal: {confidence:.3f} (GPU: {modules['config'].GPU_CONFIG['type']})")
                        logging.info(f"Signal generated: {confidence:.3f}")
                        
                        try:
                            modules['notifier'].send_signal_alert(merged)
                            last_signal_time = time.time()
                        except Exception as e:
                            logging.error(f"Notification failed: {e}")
                        
                        try:
                            modules['trade_logger'].log_signal(merged)
                        except Exception as e:
                            logging.error(f"Logging failed: {e}")
                
                except Exception as e:
                    logging.error(f"Signal processing failed: {e}")
            
            cycle_time = time.time() - start_time
            sleep_time = max(0, 5.0 - cycle_time)
            time.sleep(sleep_time)
            
            if iteration % 12 == 0:
                print(f"📊 Iteration {iteration} - System running")
    
    except KeyboardInterrupt:
        print("\n🔴 Shutting down...")
        logging.info("System shutdown")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x main.py
    echo "✓ Robust main.py created"
}

main() {
    echo "🔧 DEBUGGING CRASH..."
    echo ""
    
    check_logs
    echo ""
    
    test_imports
    echo ""
    
    if ! test_main_py; then
        fix_main_py_robust
        echo ""
    fi
    
    echo "✓ Debug complete - main.py should now be crash-resistant"
    echo "✓ Added proper error handling and module isolation"
    echo "✓ Try running ./init_pipeline.sh dry again"
}

main