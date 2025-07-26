#!/bin/bash
set -euo pipefail

echo "🔧 Fixing dangerous defaults for safety..."

# Fix config.py - Force dry mode as default
sed -i 's/MODE = "live"/MODE = "dry"/' config.py
sed -i 's/LIVE_MODE = True/LIVE_MODE = False/' config.py

# Add safety checks to config.py
cat >> config.py << 'EOF'

# SAFETY ENFORCEMENT
import os
import sys

def enforce_safety_checks():
    """Enforce safety for production deployment"""
    
    # Never default to live mode without explicit confirmation
    if MODE == "live" and not os.getenv("CONFIRMED_LIVE_MODE"):
        print("❌ SAFETY: Live mode requires CONFIRMED_LIVE_MODE=true")
        print("Set environment variable: export CONFIRMED_LIVE_MODE=true")
        sys.exit(1)
    
    # Require API keys for live mode
    if MODE == "live":
        required_keys = ["OKX_API_KEY", "OKX_SECRET_KEY", "OKX_PASSPHRASE"]
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            print(f"❌ SAFETY: Missing API keys for live mode: {missing_keys}")
            sys.exit(1)
    
    # Warn about GPU requirements
    if not GPU_AVAILABLE and MODE == "live":
        print("⚠️  WARNING: No GPU acceleration in live mode")
        response = input("Continue without GPU optimization? (yes/no): ")
        if response.lower() != "yes":
            sys.exit(1)

# Run safety checks on import
try:
    enforce_safety_checks()
    print(f"✅ Safety checks passed - Mode: {MODE}")
except KeyboardInterrupt:
    print("\n❌ User cancelled")
    sys.exit(1)
EOF

# Fix Rust main.rs - Remove forced live mode
sed -i 's/std::env::set_var("MODE", "live");//' src/main.rs
sed -i 's/let confidence_threshold = 0.75;/let confidence_threshold = 0.85;/' src/main.rs

# Add safety header to main.rs
sed -i '1i\
// SAFETY: Default to dry mode unless explicitly configured\
use std::env;\
\
fn check_safety_mode() {\
    let mode = env::var("MODE").unwrap_or_else(|_| "dry".to_string());\
    if mode == "live" {\
        let confirmed = env::var("CONFIRMED_LIVE_MODE").unwrap_or_else(|_| "false".to_string());\
        if confirmed != "true" {\
            eprintln!("❌ SAFETY: Live mode requires CONFIRMED_LIVE_MODE=true");\
            std::process::exit(1);\
        }\
        println!("🔴 LIVE MODE CONFIRMED - Real trading enabled");\
    } else {\
        println!("🟡 DRY MODE - Simulation only");\
    }\
}' src/main.rs

# Add safety check to main function
sed -i '/async fn main()/a\    check_safety_mode();' src/main.rs

# Create safety wrapper script
cat > safe_start.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "🔒 HFT System Safety Wrapper"
echo "============================="

# Check current mode
MODE=${MODE:-dry}
echo "Current mode: $MODE"

if [[ "$MODE" == "live" ]]; then
    echo ""
    echo "⚠️  WARNING: LIVE TRADING MODE REQUESTED"
    echo "This will execute REAL trades with REAL money!"
    echo ""
    echo "Required confirmations:"
    echo "1. API keys are configured"
    echo "2. Risk limits are appropriate"
    echo "3. You understand the risks"
    echo ""
    
    read -p "Type 'I UNDERSTAND THE RISKS' to continue: " confirmation
    if [[ "$confirmation" != "I UNDERSTAND THE RISKS" ]]; then
        echo "❌ Confirmation failed - exiting"
        exit 1
    fi
    
    export CONFIRMED_LIVE_MODE=true
    echo "✅ Live mode confirmed"
else
    echo "✅ Dry mode - safe simulation"
fi

echo ""
echo "Starting system in $MODE mode..."
./init_pipeline.sh
EOF

chmod +x safe_start.sh

# Update .env template to be safe by default
if [[ -f ".env" ]]; then
    # Backup existing .env
    cp .env .env.backup
fi

cat > .env.template << 'EOF'
# HFT Trading System Configuration
# SAFETY: Defaults to dry mode for protection

# Trading Mode (dry/live)
MODE=dry
CONFIRMED_LIVE_MODE=false

# OKX API Configuration (required for live mode)
OKX_API_KEY=
OKX_SECRET_KEY=
OKX_PASSPHRASE=
OKX_TESTNET=true

# Discord Notifications (optional)
DISCORD_WEBHOOK_URL=
DISCORD_USER_ID=

# Risk Management
MAX_POSITION_SIZE=1000
MAX_DAILY_TRADES=10
MAX_DRAWDOWN_PERCENT=5.0

# System Configuration
LOG_LEVEL=INFO
PYTHONPATH=.
EOF

echo "✅ Safety defaults implemented:"
echo "  - Default mode: DRY (safe)"
echo "  - Live mode requires explicit confirmation"
echo "  - API key validation for live mode"
echo "  - Use ./safe_start.sh for guided startup"