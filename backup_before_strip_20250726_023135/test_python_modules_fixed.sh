#!/bin/bash
echo "🧪 TESTING PYTHON MODULES"
echo "=========================="

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    echo -e "\nTesting: $1"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$2" >/dev/null 2>&1; then
        echo -e "✅ PASS: $1"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "❌ FAIL: $1"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Fixed tests
run_test "Config Module Import" "python3 -c 'import config'"
run_test "Signal Engine Import" "python3 -c 'import signal_engine'"
run_test "Confidence Scoring Import" "python3 -c 'import confidence_scoring'"
run_test "Signal Generation" "python3 -c 'import signal_engine, time; s=signal_engine.generate_signal({\"timestamp\":time.time(),\"mode\":\"dry\"}); print(f\"Confidence: {s.get(\"confidence\",0)}\")'"

echo -e "\nPython Tests: $PASSED_TESTS/$TOTAL_TESTS passed"
