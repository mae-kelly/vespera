#!/bin/bash
# Install WebSocket dependencies for live market data

echo "📦 Installing WebSocket dependencies..."

pip install websocket-client>=1.6.0
pip install websockets>=11.0.0

echo "✅ WebSocket dependencies installed"
echo "🔴 Ready for live market data feeds"
