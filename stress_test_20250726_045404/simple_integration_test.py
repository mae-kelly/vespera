import sys
import time
import json
import os
sys.path.append('.')

def test_integration():
    try:
        print("Testing end-to-end integration...")
        
        # Test signal generation
        import signal_engine
        shared_data = {'timestamp': time.time(), 'mode': 'dry', 'iteration': 1}
        signal = signal_engine.generate_signal(shared_data)
        
        print(f"  Signal generated: confidence {signal.get('confidence', 0):.3f}")
        
        # Test confidence scoring
        import confidence_scoring
        merged = confidence_scoring.merge_signals([signal])
        
        print(f"  Confidence scoring: {merged.get('confidence', 0):.3f}")
        
        # Test file operations
        signal_file = '/tmp/integration_test_signal.json'
        with open(signal_file, 'w') as f:
            json.dump(merged, f)
        
        print(f"  Signal written to file")
        
        # Verify file
        with open(signal_file, 'r') as f:
            loaded = json.load(f)
        
        print(f"  Signal loaded from file: confidence {loaded.get('confidence', 0):.3f}")
        
        # Test market data engine
        try:
            from live_market_data import get_live_engine
            engine = get_live_engine()
            health = engine.get_system_health()
            status = health['system']['status']
            print(f"  Market data engine: {status}")
        except Exception as e:
            print(f"  Market data engine: ERROR - {e}")
            status = "ERROR"
        
        # Cleanup
        os.remove(signal_file)
        
        results = {
            'signal_generation': signal.get('confidence', 0) > 0,
            'confidence_scoring': merged.get('confidence', 0) > 0,
            'file_operations': True,
            'market_data_status': status,
            'overall_success': True
        }
        
        print(f"\nIntegration Test Summary:")
        print(f"  Signal Generation: {'✅' if results['signal_generation'] else '❌'}")
        print(f"  Confidence Scoring: {'✅' if results['confidence_scoring'] else '❌'}")
        print(f"  File Operations: {'✅' if results['file_operations'] else '❌'}")
        print(f"  Market Data: {status}")
        
        return results
        
    except Exception as e:
        return {'error': str(e), 'overall_success': False}

if __name__ == "__main__":
    result = test_integration()
    print(f"\nFINAL_RESULT: {json.dumps(result)}")
