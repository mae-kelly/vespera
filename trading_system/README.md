# Unified Trading System

Combines HFT Shorting + Wallet Mimic strategies into one system.

## Quick Start

1. **Setup**: `bash setup.sh`
2. **Configure**: Edit `config/.env` with your API keys
3. **Test**: `python test_system.py`
4. **Run**: `bash start.sh`

## Features

- ✅ HFT crypto shorting signals
- ✅ Wallet mimic following
- ✅ Paper trading mode
- ✅ Risk management
- ✅ Real-time market data

## Safety

- **Paper Trading**: Start with `MODE=paper` in config/.env
- **Risk Limits**: Position sizing and drawdown controls
- **Emergency Stop**: Ctrl+C to stop immediately

## Structure

```
trading_system/
├── core/              # Core trading components
├── bots/              # Trading strategies
├── config/            # Configuration
├── data/              # Logs and data
├── tools/             # Utilities
└── tests/             # Test suites
```

## Configuration

Edit `config/.env`:
- Set your OKX API credentials
- Choose trading mode (paper/live)
- Adjust position sizes and limits

## Support

- Start with paper trading
- Monitor logs carefully
- Use small position sizes initially
