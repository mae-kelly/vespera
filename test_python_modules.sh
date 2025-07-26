#!/bin/bash

echo "🧪 TSTING PYTHON MODULS"
echo "=========================="
echo "Starting comprehensive Python module tests..."

# Colors for output
RD='[;m'
GRN='[;m'
YLLOW='[;m'
LU='[;m'
NC='[m' # No Color

# Test counters
TOTAL_TSTS=
PASSD_TSTS=
AILD_TSTS=

# unction to run a test
run_test() 
    local test_name="$"
    local test_command="$"
    
    echo -e "nTesting: $test_name"
    TOTAL_TSTS=$((TOTAL_TSTS + ))
    
    if eval "$test_command" >/dev/null >&; then
        echo -e "✅ PASS: $test_name"
        PASSD_TSTS=$((PASSD_TSTS + ))
        return 
    else
        echo -e "❌ AIL: $test_name"
        AILD_TSTS=$((AILD_TSTS + ))
        return 
    fi


# Core module import tests
run_test "Config Module Import" "python -c 'import config'"
run_test "Signal ngine Import" "python -c 'import signal_engine'"
run_test "Confidence Scoring Import" "python -c 'import confidence_scoring'"
run_test "ntropy Meter Import" "python -c 'import entropy_meter'"
run_test "CuPy allback Import" "python -c 'import cupy_fallback'"

# GPU detection test
run_test "GPU Detection" "python -c 'import torch; print("MPS available" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "CUDA available" if torch.cuda.is_available() else "CPU only")'"

# Config validation test
run_test "Config Module Validation" "python -c 'import config; assert hasattr(config, "DVIC"); assert hasattr(config, "ASSTS"); print(f"Config valid - Device: config.DVIC")'"

# Signal generation test
run_test "Signal Generation" "python -c 'import signal_engine, time; shared_data="timestamp": time.time(), "mode": "dry", "gpu_available": True; signal=signal_engine.generate_signal(shared_data); assert signal.get("confidence", ) > ; print(f"Signal generated with confidence: signal["confidence"]:.f")'"

# Confidence scoring test
run_test "Confidence Scoring" "python -c 'import confidence_scoring; signals=["confidence": ., "source": "test", "priority": ]; result=confidence_scoring.merge_signals(signals); assert result["confidence"] > ; print(f"Confidence merging successful: result["confidence"]:.f")'"

# ntropy calculation test
run_test "ntropy Calculation" "python -c 'import entropy_meter, time; shared_data="timestamp": time.time(), "mode": "dry"; result=entropy_meter.calculate_entropy_signal(shared_data); assert "entropy" in result; print(f"ntropy calculation successful: result["entropy"]:.f")'"

# ile operations test
run_test "ile Operations" "python -c 'import json, time, os; os.makedirs("/tmp", eist_ok=True); test_signal="timestamp": time.time(), "confidence": .; json.dump(test_signal, open("/tmp/test_signal.json", "w")); loaded=json.load(open("/tmp/test_signal.json")); assert loaded["confidence"] == .; os.remove("/tmp/test_signal.json"); print("ile operations successful")'"

# Optional modules
echo -e "n$YLLOWTesting optional modules...$NC"
run_test "Laggard Sniper Import" "python -c 'import laggard_sniper'" || true
run_test "Relief Trap Import" "python -c 'import relief_trap'" || true
run_test "Logger Import" "python -c 'import logger'" || true

# Summary
echo -e "n$LU================================$NC"
echo -e "$LUTST SUMMARY$NC"
echo -e "$LU================================$NC"
echo -e "Total Tests: $TOTAL_TSTS"
echo -e "$GRNPassed: $PASSD_TSTS$NC"
echo -e "$RDailed: $AILD_TSTS$NC"

if [ $AILD_TSTS -eq  ]; then
    echo -e "n$GRN🎉 ALL PYTHON MODUL TSTS PASSD!$NC"
    echo -e "$GRN🚀 Python system is ready$NC"
    eit 
else
    echo -e "n$RD❌ Some tests failed$NC"
    echo -e "$YLLOW⚠️  Check error messages above$NC"
    eit 
fi
