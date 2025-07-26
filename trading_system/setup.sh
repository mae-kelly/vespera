#!/bin/bash
echo "🔧 Setting up Unified Trading System..."

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo "📝 Edit config/.env with your API keys"
echo "🚀 Then run: bash start.sh"
