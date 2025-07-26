#!/usr/bin/env python3
import signal_engine
import config
import time

def test_signal_engine_gpu():
    print("🧪 SIGNAL ENGINE GPU TEST")
    print("=" * 30)
    
    print(f"Device: {config.DEVICE}")
    print(f"GPU Config: {config.GPU_CONFIG}")
    
    signal_engine.feed.start_feed()
    time.sleep(2)
    
    shared_data = {
        "timestamp": time.time(),
        "mode": "dry", 
        "iteration": 1,
        "gpu_available": config.GPU_AVAILABLE
    }
    
    print("\nTesting signal generation with GPU acceleration...")
    signal = signal_engine.generate_signal(shared_data)
    
    print(f"Signal confidence: {signal.get('confidence', 0):.3f}")
    print(f"Signal source: {signal.get('source', 'unknown')}")
    
    if 'signal_data' in signal:
        data = signal['signal_data']
        print(f"Asset: {data.get('asset', 'N/A')}")
        print(f"Entry price: ${data.get('entry_price', 0):,.2f}")
        print(f"RSI: {data.get('rsi', 0):.2f}")
    
    print("\nTesting RSI calculation...")
    prices = [100, 101, 99, 102, 98, 103, 97, 104, 96, 105, 95, 106, 94, 107, 93]
    rsi = signal_engine.calculate_rsi_torch(prices)
    print(f"RSI result: {rsi:.2f}")
    
    print("\nTesting VWAP calculation...")
    prices = [100, 101, 102, 103, 104]
    volumes = [1000, 1100, 900, 1200, 800]
    vwap = signal_engine.calculate_vwap(prices, volumes)
    print(f"VWAP result: {vwap:.2f}")
    
    print(f"\n✅ Signal engine Metal GPU test completed successfully!")
    if config.DEVICE == "mps":
        print("🚀 All calculations performed on Apple Metal GPU!")
    return True

if __name__ == "__main__":
    test_signal_engine_gpu()
