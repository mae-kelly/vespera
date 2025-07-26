#!/bin/bash
echo "🔄 TESTING SYSTEM INTEGRATION"
echo "============================="

# Setup
mkdir -p /tmp logs
export MODE=dry

echo "Testing Python signal generation..."
python3 -c "
import signal_engine
import confidence_scoring  
import json
import time

# Generate signal
shared_data = {'timestamp': time.time(), 'mode': 'dry'}
signal = signal_engine.generate_signal(shared_data)
merged = confidence_scoring.merge_signals([signal])

# Write signal file
with open('/tmp/signal.json', 'w') as f:
    json.dump(merged, f)

print('✅ Signal generation successful')
print(f'Confidence: {merged[\"confidence\"]:.3f}')
"

echo "Testing signal file validation..."
python3 -c "
import json
with open('/tmp/signal.json') as f:
    signal = json.load(f)
assert 'confidence' in signal
assert 'best_signal' in signal
print('✅ Signal validation successful')
"

echo "✅ Integration tests completed"
