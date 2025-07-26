import time
import logging
import json
import os
from pathlib import Path

def setup_logging():
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/trading.log"),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    
    print("Starting HFT Production System")
    logging.info("System startup")
    
    try:
        import config
        print(f"Config loaded - Mode: {config.MODE}")
        
        import signal_engine
        print("Signal engine loaded")
        
        import confidence_scoring
        print("Confidence scoring loaded")
        
        iteration = 0
        
        while True:
            iteration += 1
            start_time = time.time()
            
            shared_data = {
                "timestamp": time.time(),
                "mode": config.MODE,
                "iteration": iteration
            }
            
            try:
                signal = signal_engine.generate_signal(shared_data)
                
                if signal.get("confidence", 0) > 0.6:
                    merged = confidence_scoring.merge_signals([signal])
                    
                    if merged.get("confidence", 0) > 0.7:
                        Path("/tmp").mkdir(exist_ok=True)
                        with open("/tmp/signal.json", "w") as f:
                            json.dump(merged, f, indent=2)
                        
                        print(f"Signal generated: {merged['confidence']:.3f}")
                        logging.info(f"Signal: {merged['confidence']:.3f}")
                    else:
                        print(f"Signal below threshold: {merged.get('confidence', 0):.3f}")
                else:
                    print(f"Weak signal: {signal.get('confidence', 0):.3f}")
                
            except Exception as e:
                logging.error(f"Signal generation error: {e}")
                print(f"Error: {e}")
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration} - System running")
            
            cycle_time = time.time() - start_time
            sleep_time = max(0, 1.0 - cycle_time)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        logging.info("System shutdown")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.critical(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
