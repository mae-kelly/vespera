#!/bin/bash

echo "🧪 TESTING PYTHON MODULES"
echo "=========================="
echo "Starting comprehensive Python module tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\nTesting: $test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "✅ PASS: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "❌ FAIL: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Core module import tests
run_test "Config Module Import" "python3 -c 'import config'"
run_test "Signal Engine Import" "python3 -c 'import signal_engine'"
run_test "Confidence Scoring Import" "python3 -c 'import confidence_scoring'"
run_test "Entropy Meter Import" "python3 -c 'import entropy_meter'"
run_test "CuPy Fallback Import" "python3 -c 'import cupy_fallback'"

# GPU detection test
run_test "GPU Detection" "python3 -c 'import torch; print(\"MPS available\" if hasattr(torch.backends, \"mps\") and torch.backends.mps.is_available() else \"CUDA available\" if torch.cuda.is_available() else \"CPU only\")'"

# Config validation test
run_test "Config Module Validation" "python3 -c 'import config; assert hasattr(config, \"DEVICE\"); assert hasattr(config, \"ASSETS\"); print(f\"Config valid - Device: {config.DEVICE}\")'"

# Signal generation test
run_test "Signal Generation" "python3 -c 'import signal_engine, time; shared_data={\"timestamp\": time.time(), \"mode\": \"dry\", \"gpu_available\": True}; signal=signal_engine.generate_signal(shared_data); assert signal.get(\"confidence\", 0) > 0; print(f\"Signal generated with confidence: {signal[\"confidence\"]:.3f}\")'"

# Confidence scoring test
run_test "Confidence Scoring" "python3 -c 'import confidence_scoring; signals=[{\"confidence\": 0.6, \"source\": \"test\", \"priority\": 1}]; result=confidence_scoring.merge_signals(signals); assert result[\"confidence\"] > 0; print(f\"Confidence merging successful: {result[\"confidence\"]:.3f}\")'"

# Entropy calculation test
run_test "Entropy Calculation" "python3 -c 'import entropy_meter, time; shared_data={\"timestamp\": time.time(), \"mode\": \"dry\"}; result=entropy_meter.calculate_entropy_signal(shared_data); assert \"entropy\" in result; print(f\"Entropy calculation successful: {result[\"entropy\"]:.3f}\")'"

# File operations test
run_test "File Operations" "python3 -c 'import json, time, os; os.makedirs(\"/tmp\", exist_ok=True); test_signal={\"timestamp\": time.time(), \"confidence\": 0.8}; json.dump(test_signal, open(\"/tmp/test_signal.json\", \"w\")); loaded=json.load(open(\"/tmp/test_signal.json\")); assert loaded[\"confidence\"] == 0.8; os.remove(\"/tmp/test_signal.json\"); print(\"File operations successful\")'"

# Optional modules
echo -e "\n${YELLOW}Testing optional modules...${NC}"
run_test "Laggard Sniper Import" "python3 -c 'import laggard_sniper'" || true
run_test "Relief Trap Import" "python3 -c 'import relief_trap'" || true
run_test "Logger Import" "python3 -c 'import logger'" || true

# Summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Total Tests: ${TOTAL_TESTS}"
echo -e "${GREEN}Passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}Failed: ${FAILED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL PYTHON MODULE TESTS PASSED!${NC}"
    echo -e "${GREEN}🚀 Python system is ready${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    echo -e "${YELLOW}⚠️  Check error messages above${NC}"
    exit 1
fi
