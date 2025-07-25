#!/bin/bash

echo "🚀 Starting HFT System on macOS"
echo "==============================="

# Activate virtual environment if it exists
if [[ -d "venv" ]]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Set environment variables
export PYTHONPATH="$PWD:$PYTHONPATH"
export MODE="dry"

echo "📊 System starting in DRY mode..."
echo "Press Ctrl+C to stop"

# Start the Python system
python3 main.py --mode=dry

echo "🔴 System stopped"
