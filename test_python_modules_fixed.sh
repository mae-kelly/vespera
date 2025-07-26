#!/bin/bash
echo "🧪 TSTING PYTHON MODULS"
echo "=========================="

TOTAL_TSTS=
PASSD_TSTS=
AILD_TSTS=

run_test() 
    echo -e "nTesting: $"
    TOTAL_TSTS=$((TOTAL_TSTS + ))
    
    if eval "$" >/dev/null >&; then
        echo -e "✅ PASS: $"
        PASSD_TSTS=$((PASSD_TSTS + ))
    else
        echo -e "❌ AIL: $"
        AILD_TSTS=$((AILD_TSTS + ))
    fi


# ied tests
run_test "Config Module Import" "python -c 'import config'"
run_test "Signal ngine Import" "python -c 'import signal_engine'"
run_test "Confidence Scoring Import" "python -c 'import confidence_scoring'"
run_test "Signal Generation" "python -c 'import signal_engine, time; s=signal_engine.generate_signal("timestamp":time.time(),"mode":"dry"); print(f"Confidence: s.get("confidence",)")'"

echo -e "nPython Tests: $PASSD_TSTS/$TOTAL_TSTS passed"
