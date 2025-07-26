#!/usr/bin/env python3
import json
import time
import os
from datetime import datetime

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def load_signal_data():
    try:
        with open('/tmp/signal.json', 'r') as f:
            return json.load(f)
    except:
        return None

def format_confidence(confidence):
    if confidence >= 0.8:
        return f"🟢 {confidence:.3f}"
    elif confidence >= 0.6:
        return f"🟡 {confidence:.3f}"
    else:
        return f"🔴 {confidence:.3f}"

def main():
    print("🔍 HFT Signal Monitoring Dashboard")
    print("=================================")
    print("Press Ctrl+C to exit\n")
    
    signal_count = 0
    strong_signals = 0
    
    try:
        while True:
            clear_screen()
            
            print("🔍 HFT SIGNAL MONITORING DASHBOARD")
            print("=" * 50)
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Signals Processed: {signal_count}")
            print(f"Strong Signals (>0.7): {strong_signals}")
            print("-" * 50)
            
            # Load latest signal
            signal_data = load_signal_data()
            
            if signal_data:
                confidence = signal_data.get('confidence', 0)
                source = signal_data.get('source', 'unknown')
                timestamp = signal_data.get('timestamp', 0)
                
                if confidence > 0.7:
                    strong_signals += 1
                
                signal_count += 1
                
                print(f"Latest Signal:")
                print(f"  Confidence: {format_confidence(confidence)}")
                print(f"  Source: {source}")
                print(f"  Age: {time.time() - timestamp:.1f}s")
                
                if 'signal_data' in signal_data:
                    sig_data = signal_data['signal_data']
                    print(f"  Asset: {sig_data.get('asset', 'N/A')}")
                    print(f"  Entry Price: ${sig_data.get('entry_price', 0):,.2f}")
                    print(f"  RSI: {sig_data.get('rsi', 'N/A'):.1f}")
                    print(f"  Reason: {sig_data.get('reason', 'N/A')}")
                
                if signal_data.get('enhancement_applied'):
                    print("  🚀 ENHANCEMENT APPLIED")
                
                if confidence >= 0.75:
                    print("\n🎯 STRONG SIGNAL DETECTED!")
                    print("   This signal would trigger trading in production mode")
                
            else:
                print("⏳ Waiting for signals...")
            
            print("\n" + "-" * 50)
            print("Signal Strength Guide:")
            print("🟢 High (0.8+)  🟡 Medium (0.6-0.8)  🔴 Low (<0.6)")
            print("\nPress Ctrl+C to exit")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")

if __name__ == "__main__":
    main()
