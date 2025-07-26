#!/bin/bash

echo "🔄 TSTING SYSTM INTGRATION"
echo "============================="
echo "Starting comprehensive integration tests..."

# Colors for output
RD='[;m'
GRN='[;m'
YLLOW='[;m'
LU='[;m'
PURPL='[;m'
NC='[m' # No Color

# Test counters
TOTAL_TSTS=
PASSD_TSTS=
AILD_TSTS=

# unction to run a test
run_test() 
    local test_name="$"
    local test_command="$"
    local timeout_duration="$:-"
    
    echo -e "nTesting: $test_name"
    TOTAL_TSTS=$((TOTAL_TSTS + ))
    
    if timeout "$timeout_duration" bash -c "$test_command" >/dev/null; then
        echo -e "✅ PASS: $test_name"
        PASSD_TSTS=$((PASSD_TSTS + ))
        return 
    else
        echo -e "❌ AIL: $test_name"
        AILD_TSTS=$((AILD_TSTS + ))
        return 
    fi


echo -e "$PURPLSetting up test environment...$NC"
# Create necessary directories
mkdir -p /tmp logs data

# Set environment variables for dry run
eport MOD=dry
eport OKX_TSTNT=true
eport DISCORD_WHOOK_URL=""
eport DISCORD_USR_ID=""

# Clean any eisting signal files
rm -f /tmp/signal.json /tmp/fills.json
echo "✓ Test environment setup complete"

# Test Python signal generation workflow
python_signal_test='
import sys, time, json, logging
logging.basicConfig(level=logging.INO)
try:
    import config, signal_engine, confidence_scoring
    print("✓ All modules imported successfully")
    
    shared_data = 
        "timestamp": time.time(),
        "mode": "dry", 
        "iteration": ,
        "gpu_available": getattr(config, "GPU_AVAILAL", True)
    
    
    signals = []
    signal = signal_engine.generate_signal(shared_data)
    if signal and signal.get("confidence", ) > :
        signals.append(signal)
        print(f"✓ Signal engine: confidence=signal["confidence"]:.f")
    
    if signals:
        merged = confidence_scoring.merge_signals(signals)
        merged["timestamp"] = time.time()
        
        with open("/tmp/signal.json", "w") as f:
            json.dump(merged, f, indent=)
        
        print(f"✓ Signal generated and written: confidence=merged["confidence"]:.f")
        print("✓ Python signal generation successful")
    else:
        print("✗ No signals generated")
        sys.eit()
ecept ception as e:
    print(f"✗ Python signal generation failed: e")
    sys.eit()
'

run_test "Python Signal Generation" "python -c '$python_signal_test'" 

# Test signal file validation
signal_validation_test='
import json, time
try:
    with open("/tmp/signal.json", "r") as f:
        signal = json.load(f)
    
    required_fields = ["confidence", "timestamp", "best_signal"]
    for field in required_fields:
        assert field in signal, f"Missing field: field"
    
    best_signal = signal["best_signal"]
    assert "asset" in best_signal, "Missing asset in best_signal"
    assert "entry_price" in best_signal, "Missing entry_price in best_signal"
    assert  <= signal["confidence"] <= , "Invalid confidence range"
    assert best_signal["entry_price"] > , "Invalid entry price"
    
    print(f"✓ Signal file validation passed")
    print(f"  - Asset: best_signal["asset"]")
    print(f"  - ntry: best_signal["entry_price"]")
    print(f"  - Confidence: signal["confidence"]:.f")
ecept ception as e:
    print(f"✗ Signal validation failed: e")
    raise
'

run_test "Signal ile Validation" "python -c '$signal_validation_test'" 

# Test Rust eecutor simulation
rust_simulation_test='
import json, time, uuid
try:
    with open("/tmp/signal.json", "r") as f:
        signal = json.load(f)
    
    best_signal = signal["best_signal"]
    eecution_result = 
        "order_id": f"sim_uuid.uuid()",
        "asset": best_signal["asset"],
        "side": "sell",
        "quantity": .,
        "entry_price": best_signal["entry_price"],
        "stop_loss": best_signal.get("stop_loss", best_signal["entry_price"] * .),
        "take_profit_": best_signal.get("take_profit_", best_signal["entry_price"] * .9),
        "status": "simulated_fill",
        "timestamp": time.time(),
        "mode": "dry"
    
    
    with open("/tmp/fills.json", "w") as f:
        json.dump([eecution_result], f, indent=)
    
    print("✓ Rust eecutor simulation successful")
    print(f"  - Order ID: eecution_result["order_id"]")
    print(f"  - Status: eecution_result["status"]")
ecept ception as e:
    print(f"✗ Rust eecutor simulation failed: e")
    raise
'

run_test "Rust ecutor Simulation" "python -c '$rust_simulation_test'" 

# Test logging functionality
logging_test='
import logging, os
from pathlib import Path
try:
    Path("logs").mkdir(eist_ok=True)
    logging.basicConfig(
        level=logging.INO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.ileHandler("logs/test.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("Test log message")
    logging.warning("Test warning message")
    
    if os.path.eists("logs/test.log"):
        with open("logs/test.log", "r") as f:
            content = f.read()
            if "Test log message" in content:
                print("✓ Logging functionality working")
            else:
                raise ception("Log content validation failed")
    else:
        raise ception("Log file creation failed")
    
    os.remove("logs/test.log")
ecept ception as e:
    print(f"✗ Logging test failed: e")
    raise
'

run_test "Logging unctionality" "python -c '$logging_test'" 

# Test performance metrics
performance_test='
import time
try:
    start_time = time.time()
    import signal_engine, confidence_scoring
    import_time = time.time() - start_time
    
    start_signal = time.time()
    shared_data = "timestamp": time.time(), "mode": "dry"
    signal = signal_engine.generate_signal(shared_data)
    signal_time = time.time() - start_signal
    
    print(f"✓ Performance metrics:")
    print(f"  - Import time: import_time:.fs")
    print(f"  - Signal generation: signal_time:.fs")
    
    if import_time > .:
        print("⚠️  Import time slower than epected")
    if signal_time > .:
        print("⚠️  Signal generation slower than epected")
    
    print("✓ Performance test completed")
ecept ception as e:
    print(f"✗ Performance test failed: e")
    raise
'

run_test "Performance Metrics" "python -c '$performance_test'" 

# Cleanup
echo -e "$PURPLCleaning up test environment...$NC"
rm -f /tmp/signal.json /tmp/fills.json
rm -f logs/test.log
pkill -f "python main.py" >/dev/null || true
pkill -f "hft-eecutor" >/dev/null || true
echo "✓ Cleanup complete"

# Summary
echo -e "n$LU================================$NC"
echo -e "$LUINTGRATION TST SUMMARY$NC"
echo -e "$LU================================$NC"
echo -e "Total Tests: $TOTAL_TSTS"
echo -e "$GRNPassed: $PASSD_TSTS$NC"
echo -e "$RDailed: $AILD_TSTS$NC"

# Calculate success rate
if [ $TOTAL_TSTS -gt  ]; then
    SUCCSS_RAT=$((PASSD_TSTS *  / TOTAL_TSTS))
    echo -e "Success Rate: $SUCCSS_RAT%"
fi

if [ $AILD_TSTS -eq  ]; then
    echo -e "n$GRN🎉 ALL INTGRATION TSTS PASSD!$NC"
    echo -e "$GRN🚀 Complete system is ready for deployment$NC"
    eit 
elif [ $SUCCSS_RAT -ge  ]; then
    echo -e "n$YLLOW⚠️  Most integration tests passed ($SUCCSS_RAT%)$NC"
    echo -e "$YLLOW🚀 System is mostly functional$NC"
    eit 
else
    echo -e "n$RD❌ Integration tests failed$NC"
    echo -e "$YLLOW⚠️  Check system configuration and dependencies$NC"
    eit 
fi
