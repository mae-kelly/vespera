#!/usr/bin/env python3
import asyncio
import logging
import os
import sys

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check GPU availability - A100 or M1 MPS required
    try:
        import torch
        import platform
        
        gpu_detected = False
        
        # Check CUDA first (A100 preferred)
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logging.info(f"🚀 CUDA GPU: {gpu_name} ({gpu_memory:.1f}GB)")
            gpu_detected = True
            
            if "A100" in gpu_name:
                logging.info("🔥 A100 GPU detected - optimal performance")
            elif gpu_memory >= 24:
                logging.info("✅ High-end GPU detected - good performance")
            else:
                logging.warning("⚠️  Low GPU memory - may impact training speed")
        
        # Check Apple MPS (M1/M2)
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            try:
                test_tensor = torch.zeros(1, device='mps')
                logging.info("🍎 Apple M1/M2 MPS GPU detected and functional")
                gpu_detected = True
            except Exception as e:
                logging.error(f"MPS detected but failed test: {e}")
        
        # Try alternative MPS detection for older PyTorch versions
        elif platform.system() == "Darwin":
            try:
                device = torch.device("mps")
                test_tensor = torch.zeros(1, device=device)
                logging.info("🍎 MPS device functional (alternative detection)")
                gpu_detected = True
            except Exception as e:
                logging.error(f"MPS alternative detection failed: {e}")
        
        if not gpu_detected:
            logging.error("❌ NO GPU DETECTED")
            logging.error("   Required: A100 CUDA GPU or Apple M1/M2 MPS")
            logging.error("   CPU execution NOT ALLOWED for ML training")
            sys.exit(1)
        
    except ImportError:
        logging.error("PyTorch not installed")
        sys.exit(1)
    
    # Check API credentials
    required_vars = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logging.error(f"Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    logging.info("✅ All requirements met")
    logging.info("🧠 Starting ML-based trading system...")
    logging.info("📊 Phase 1: Initial training on historical data")
    logging.info("🔄 Phase 2: Continuous learning and trading")
    logging.info("🎯 Target: 1000x returns via ML predictions")
    
    # Import and run the ML system
    from real_ml_trading_system import MLTradingSystem
    
    system = MLTradingSystem()
    await system.run_trading_system()

if __name__ == "__main__":
    asyncio.run(main())
