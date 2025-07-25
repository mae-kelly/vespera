#!/bin/bash

echo "🚀 Starting HFT System (Simple Mode)"
echo "===================================="

# Create directories
mkdir -p logs /tmp

# Set environment
export MODE="dry"
export PYTHONPATH="$PWD:$PYTHONPATH"

echo "📊 Testing basic functionality..."

# Test Python script first
python3 -c "
import sys
import os
import time

print('Testing imports...')
try:
    import config
    print(f'✅ Config: Mode={config.MODE}')
    
    import signal_engine
    print('✅ Signal engine imported')
    
    # Start feed
    signal_engine.feed.start_feed()
    print('✅ Feed started')
    
    # Wait for data
    time.sleep(3)
    
    # Test signal generation
    shared_data = {
        'timestamp': time.time(),
        'mode': 'dry',
        'iteration': 1,
        'gpu_available': False
    }
    
    signal = signal_engine.generate_signal(shared_data)
    print(f'✅ Signal generated: confidence={signal.get(\"confidence\", 0):.3f}')
    
    print('✅ Basic test completed successfully')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" 

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 BASIC TEST PASSED"
    echo "===================="
    echo ""
    echo "🚀 Starting full system..."
    
    # Start Python main
    echo "Starting Python cognition layer..."
    python3 main.py --mode=dry &
    PYTHON_PID=$!
    
    echo "Python PID: $PYTHON_PID"
    
    # Wait and check
    sleep 5
    
    if ps -p $PYTHON_PID > /dev/null; then
        echo "✅ Python layer running successfully"
        echo "📄 Check logs/cognition.log for details"
        echo ""
        echo "Press Ctrl+C to stop"
        
        # Keep running
        while ps -p $PYTHON_PID > /dev/null; do
            sleep 5
            if [[ -f "/tmp/signal.json" ]]; then
                echo "📡 Signal file detected"
                break
            fi
        done
        
        # Cleanup
        kill $PYTHON_PID 2>/dev/null || true
        echo "🔴 System stopped"
    else
        echo "❌ Python layer failed to start"
        echo "📄 Check logs for errors:"
        if [[ -f "logs/cognition.log" ]]; then
            tail -20 logs/cognition.log
        fi
    fi
else
    echo "❌ Basic test failed - check errors above"
fi
