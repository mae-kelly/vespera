import sys
import json
import time
sys.path.append('.')

def test_signal_generation():
    try:
        import signal_engine
        
        shared_data = {
            "timestamp": time.time(),
            "mode": "dry",
            "iteration": 1
        }
        
        signal = signal_engine.generate_signal(shared_data)
        
        required_fields = ['confidence', 'source']
        for field in required_fields:
            if field not in signal:
                return {'success': False, 'error': f'Missing field: {field}'}
        
        confidence = signal.get('confidence', 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            return {'success': False, 'error': f'Invalid confidence: {confidence}'}
        
        return {
            'success': True,
            'confidence': confidence,
            'source': signal.get('source'),
            'has_signal_data': 'signal_data' in signal
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    result = test_signal_generation()
    print(json.dumps(result))
