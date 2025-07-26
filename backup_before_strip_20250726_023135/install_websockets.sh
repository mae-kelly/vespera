#!/bin/bash
# Install WebSocket dependencies for live market data

echo "📦 Installing WebSocket dependencies..."

pip install websocket-client>=..
pip install websockets>=..

echo "✅ WebSocket dependencies installed"
echo "🔴 Ready for live market data feeds"
