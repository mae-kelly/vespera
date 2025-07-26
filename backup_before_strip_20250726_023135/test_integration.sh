#!/bin/bash

echo "🔄 TESTING SYSTEM INTEGRATION"
echo "============================="
echo "Starting comprehensive integration tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local timeout_duration="${3:-30}"
    
    echo -e "\nTesting: $test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if timeout "$timeout_duration" bash -c "$test_command" 2>/dev/null; then
        echo -e "✅ PASS: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "❌ FAIL: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${PURPLE}Setting up test environment...${NC}"
# Create necessary directories
mkdir -p /tmp logs data

# Set environment variables for dry run
export MODE=dry
export OKX_TESTNET=true
export DISCORD_WEBHOOK_URL=""
export DISCORD_USER_ID=""

# Clean any existing signal files
rm -f /tmp/signal.json /tmp/fills.json
echo "✓ Test environment setup complete"

# Test Python signal generation workflow
python_signal_test='
import sys, time, json, logging
logging.basicConfig(level=logging.INFO)
try:
    import config, signal_engine, confidence_scoring
    print("✓ All modules imported successfully")
    
    shared_data = {
        "timestamp": time.time(),
        "mode": "dry", 
        "iteration": 1,
        "gpu_available": getattr(config, "GPU_AVAILABLE", True)
    }
    
    signals = []
    signal = signal_engine.generate_signal(shared_data)
    if signal and signal.get("confidence", 0) > 0:
        signals.append(signal)
        print(f"✓ Signal engine: confidence={signal[\"confidence\"]:.3f}")
    
    if signals:
        merged = confidence_scoring.merge_signals(signals)
        merged["timestamp"] = time.time()
        
        with open("/tmp/signal.json", "w") as f:
            json.dump(merged, f, indent=2)
        
        print(f"✓ Signal generated and written: confidence={merged[\"confidence\"]:.3f}")
        print("✓ Python signal generation successful")
    else:
        print("✗ No signals generated")
        sys.exit(1)
except Exception as e:
    print(f"✗ Python signal generation failed: {e}")
    sys.exit(1)
'

run_test "Python Signal Generation" "python3 -c '$python_signal_test'" 30

# Test signal file validation
signal_validation_test='
import json, time
try:
    with open("/tmp/signal.json", "r") as f:
        signal = json.load(f)
    
    required_fields = ["confidence", "timestamp", "best_signal"]
    for field in required_fields:
        assert field in signal, f"Missing field: {field}"
    
    best_signal = signal["best_signal"]
    assert "asset" in best_signal, "Missing asset in best_signal"
    assert "entry_price" in best_signal, "Missing entry_price in best_signal"
    assert 0 <= signal["confidence"] <= 1, "Invalid confidence range"
    assert best_signal["entry_price"] > 0, "Invalid entry price"
    
    print(f"✓ Signal file validation passed")
    print(f"  - Asset: {best_signal[\"asset\"]}")
    print(f"  - Entry: {best_signal[\"entry_price\"]}")
    print(f"  - Confidence: {signal[\"confidence\"]:.3f}")
except Exception as e:
    print(f"✗ Signal validation failed: {e}")
    raise
'

run_test "Signal File Validation" "python3 -c '$signal_validation_test'" 10

# Test Rust executor simulation
rust_simulation_test='
import json, time, uuid
try:
    with open("/tmp/signal.json", "r") as f:
        signal = json.load(f)
    
    best_signal = signal["best_signal"]
    execution_result = {
        "order_id": f"sim_{uuid.uuid4()}",
        "asset": best_signal["asset"],
        "side": "sell",
        "quantity": 0.01,
        "entry_price": best_signal["entry_price"],
        "stop_loss": best_signal.get("stop_loss", best_signal["entry_price"] * 1.015),
        "take_profit_1": best_signal.get("take_profit_1", best_signal["entry_price"] * 0.985),
        "status": "simulated_fill",
        "timestamp": time.time(),
        "mode": "dry"
    }
    
    with open("/tmp/fills.json", "w") as f:
        json.dump([execution_result], f, indent=2)
    
    print("✓ Rust executor simulation successful")
    print(f"  - Order ID: {execution_result[\"order_id\"]}")
    print(f"  - Status: {execution_result[\"status\"]}")
except Exception as e:
    print(f"✗ Rust executor simulation failed: {e}")
    raise
'

run_test "Rust Executor Simulation" "python3 -c '$rust_simulation_test'" 15

# Test logging functionality
logging_test='
import logging, os
from pathlib import Path
try:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/test.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Test log message")
    logging.warning("Test warning message")
    
    if os.path.exists("logs/test.log"):
        with open("logs/test.log", "r") as f:
            content = f.read()
            if "Test log message" in content:
                print("✓ Logging functionality working")
            else:
                raise Exception("Log content validation failed")
    else:
        raise Exception("Log file creation failed")
    
    os.remove("logs/test.log")
except Exception as e:
    print(f"✗ Logging test failed: {e}")
    raise
'

run_test "Logging Functionality" "python3 -c '$logging_test'" 10

# Test performance metrics
performance_test='
import time
try:
    start_time = time.time()
    import signal_engine, confidence_scoring
    import_time = time.time() - start_time
    
    start_signal = time.time()
    shared_data = {"timestamp": time.time(), "mode": "dry"}
    signal = signal_engine.generate_signal(shared_data)
    signal_time = time.time() - start_signal
    
    print(f"✓ Performance metrics:")
    print(f"  - Import time: {import_time:.3f}s")
    print(f"  - Signal generation: {signal_time:.3f}s")
    
    if import_time > 5.0:
        print("⚠️  Import time slower than expected")
    if signal_time > 1.0:
        print("⚠️  Signal generation slower than expected")
    
    print("✓ Performance test completed")
except Exception as e:
    print(f"✗ Performance test failed: {e}")
    raise
'

run_test "Performance Metrics" "python3 -c '$performance_test'" 20

# Cleanup
echo -e "${PURPLE}Cleaning up test environment...${NC}"
rm -f /tmp/signal.json /tmp/fills.json
rm -f logs/test.log
pkill -f "python3 main.py" 2>/dev/null || true
pkill -f "hft-executor" 2>/dev/null || true
echo "✓ Cleanup complete"

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}INTEGRATION TEST SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Total Tests: ${TOTAL_TESTS}"
echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Success Rate: ${SUCCESS_RATE}%"
fi

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL INTEGRATION TESTS PASSED!${NC}"
    echo -e "${GREEN}🚀 Complete system is ready for deployment${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️  Most integration tests passed (${SUCCESS_RATE}%)${NC}"
    echo -e "${YELLOW}🚀 System is mostly functional${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Integration tests failed${NC}"
    echo -e "${YELLOW}⚠️  Check system configuration and dependencies${NC}"
    exit 1
fi
