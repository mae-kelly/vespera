#!/usr/bin/env python3
import asyncio
import logging
import torch
import time

async def test_m1_ml_system():
    logging.basicConfig(level=logging.INFO)
    
    # Test M1 GPU first
    try:
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device("mps")
            test_tensor = torch.randn(100, 100, device=device)
            result = torch.mm(test_tensor, test_tensor.T)
            torch.mps.synchronize()
            print("✅ M1 GPU test passed")
        else:
            print("❌ M1 GPU not available")
            return
    except Exception as e:
        print(f"❌ M1 GPU test failed: {e}")
        return
    
    # Test the fixed ML system
    try:
        from fix_ml_system import MLTradingSystem
        
        print("🧠 Testing ML system...")
        system = MLTradingSystem()
        
        # Quick test training
        await system.quick_training()
        
        if system.model_trained:
            print("✅ ML training successful")
            
            # Test signal generation
            signal = await system.generate_ml_signal("BTC")
            if signal:
                print(f"✅ ML signal generated: {signal.action} BTC (confidence: {signal.confidence:.3f})")
            else:
                print("⚠️ No signal generated")
        else:
            print("❌ ML training failed")
    
    except Exception as e:
        print(f"❌ ML system test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_m1_ml_system())
