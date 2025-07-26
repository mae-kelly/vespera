Complete dual-language system for high-speed crypto asset shorting simulation with GPU-accelerated signal processing and low-latency execution.
- **Signal Engine**: RSI, VWAP, volume anomaly detection
- **Entropy Meter**: Shannon entropy decay monitoring  
- **Laggard Sniper**: Cross-asset correlation analysis
- **Relief Trap Detector**: False bounce identification
- **Confidence Scoring**: Multi-signal fusion with softmax weighting
- **OKX-Style Trading**: Market/limit orders with stop-loss laddering
- **Position Management**: Real-time PnL tracking and breakeven logic
- **Risk Engine**: Drawdown limits, cooldown periods, exposure controls
- **Data Feed**: WebSocket price monitoring with simulation fallback
```bash
cp .env.template .env
chmod +x init_pipeline.sh
./init_pipeline.sh dry
./init_pipeline.sh live
```
**Python Dependencies:**
- torch (A100 GPU support)
- cupy-cuda12x
- cudf  
- websocket-client
- python-telegram-bot
- requests
- pandas
**Rust Dependencies:**
- tokio (async runtime)
- reqwest (HTTP client)
- ring (HMAC signing)
- tokio-tungstenite (WebSocket)
- serde_json (JSON handling)
The system monitors multiple signal sources:
1. **Technical Indicators**: RSI < 30, price below VWAP, volume spikes
2. **Entropy Analysis**: Shannon entropy decay over 60-sample windows  
3. **Cross-Asset Signals**: BTC weakness triggering alt-coin shorts
4. **Relief Trap Detection**: Failed bounces with RSI divergence
Signals are merged using confidence-weighted scoring and written to `/tmp/signal.json`.
When confidence > 0.7:
1. **Risk Validation**: Position limits, drawdown checks, cooldown periods
2. **Order Placement**: Market short with 1.5% stop-loss
3. **Take Profit Laddering**: 50% @ 1.5%, 30% @ 2.5%, 20% @ 4.0%
4. **Breakeven Management**: Move stop to entry after first TP hit
5. **Trailing Stops**: Dynamic adjustment in profitable positions
```
/tmp/signal.json    # Python → Rust communication
/tmp/fills.json     # Rust → Python trade log
logs/trade_log.csv  # Comprehensive signal history
logs/execution_log.csv # Trade execution details
logs/engine.log     # System operational logs
```
Key settings in `config.py`:
- `SIGNAL_CONFIDENCE_THRESHOLD = 0.7`
- `MAX_DRAWDOWN_PERCENT = 10.0`
- `COOLDOWN_MINUTES = 5`
- `POSITION_SIZE_PERCENT = 2.0`
The system provides:
- Real-time signal confidence scoring
- Position PnL tracking
- Risk metric monitoring  
- Telegram notifications (optional)
- CSV logging for backtesting
**Dry-Run Default**: All orders simulated unless explicitly set to live mode
**Risk Limits**: Maximum 3 open positions, 10% daily drawdown limit
**Cooldown Logic**: 5-minute minimum between same-asset signals
**Position Sizing**: 2% account risk per trade with dynamic sizing
- **Signal Generation**: ~1ms per cycle (GPU-accelerated)
- **Order Execution**: <50ms latency (simulated)
- **Memory Usage**: ~2GB (including GPU buffers)
- **CPU Usage**: ~15% (multi-threaded processing)
Built for A100 GPU environments but gracefully falls back to CPU. Optimized for Google Colab Pro+ and production VPS deployment.