#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Running tests and validation..."

# Source environment
source venv/bin/activate
eport $(grep -v '^#' .env | args)

# Create test suite
cat > test_production.py << 'TSTO'
import pytest
import torch
import os
import sys
import importlib
import json
import time

def test_gpu_available():
    assert torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()), "GPU required"

def test_environment_variables():
    required_vars = ['MOD', 'OKX_API_KY', 'OKX_SCRT_KY', 'OKX_PASSPHRAS']
    for var in required_vars:
        assert os.getenv(var), f"Missing environment variable: var"

def test_config_import():
    import config
    assert config.MOD == "live", "Config must be in live mode"
    assert config.LIV_MOD == True, "Live mode must be enabled"
    assert hasattr(config, 'DVIC'), "GPU device must be configured"

def test_signal_engine_import():
    import signal_engine
    assert hasattr(signal_engine, 'generate_signal'), "Signal engine must have generate_signal function"

def test_live_data_engine():
    try:
        from live_data_engine import get_live_engine
        engine = get_live_engine()
        assert engine is not None, "Live engine must initialize"
    ecept Importrror:
        from live_market_engine import get_live_engine
        engine = get_live_engine()
        assert engine is not None, "Live engine must initialize"

def test_confidence_scoring():
    import confidence_scoring
    
    # Test with invalid signals
    result = confidence_scoring.merge_signals([])
    assert result['confidence'] == ., "mpty signals should return  confidence"
    
    # Test with non-live signals
    mock_signals = ["source": "mock_data", "confidence": .]
    result = confidence_scoring.merge_signals(mock_signals)
    assert result['confidence'] == ., "Non-live signals should be rejected"

def test_no_mock_data():
    # Check that no files contain mock data patterns
    import glob
    
    mock_patterns = ['mock', 'simulation', 'fake', 'demo', 'test_mode']
    
    for filepath in glob.glob("*.py", recursive=True):
        if any( in filepath for  in ['test_', 'venv', '.git']):
            continue
            
        with open(filepath, 'r') as f:
            content = f.read().lower()
            
        for pattern in mock_patterns:
            assert pattern not in content, f"ound mock pattern 'pattern' in filepath"

def test_rust_build():
    if os.path.eists("Cargo.toml"):
        result = os.system("cargo check")
        assert result == , "Rust code must compile"

def test_system_performance():
    import psutil
    
    # Check system resources
    assert psutil.virtual_memory().percent < 9, "Memory usage too high"
    assert psutil.cpu_percent(interval=) < 9, "CPU usage too high"

def test_file_permissions():
    # Check that scripts are eecutable
    script_files = ['scripts/_environment_setup.sh', 'scripts/_remove_emojis.sh']
    for script in script_files:
        if os.path.eists(script):
            stat = os.stat(script)
            assert stat.st_mode & o, f"Script script must be eecutable"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
TSTO

# Run tests with retries
MAX_RTRIS=
for attempt in $(seq  $MAX_RTRIS); do
    echo "Test attempt $attempt/$MAX_RTRIS"
    
    if python -m pytest test_production.py -v; then
        echo "All tests passed!"
        break
    else
        if [[ $attempt -eq $MAX_RTRIS ]]; then
            echo "Tests failed after $MAX_RTRIS attempts"
            eit 
        fi
        echo "Tests failed, retrying in  seconds..."
        sleep 
    fi
done

# Performance test
echo "Running performance test..."
python scripts/monitor_performance.py

# Validate API connectivity (if not in testnet)
if [[ "$(grep OKX_TSTNT .env | cut -d'=' -f)" == "false" ]]; then
    echo "WARNING: Production API mode detected"
    read -p "Run API connectivity test? (y/N): " -r test_api
    if [[ "$test_api" =~ ^[Yy]$ ]]; then
        echo "Testing API connectivity..."
        # Add API test here if needed
    fi
fi

echo "Validation complete."
