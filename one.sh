#!/bin/bash

# Debug script to identify exactly what's failing in the HFT system

echo "🔍 DEBUGGING HFT SYSTEM FAILURES"
echo "================================="

# Function to test and show detailed output
debug_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n🔍 DEBUG: $test_name"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    if eval "$test_command" 2>&1; then
        echo "✅ SUCCESS: $test_name"
    else
        echo "❌ FAILED: $test_name"
        echo "Error details above ↑"
    fi
    echo "----------------------------------------"
}

# 1. Check Python environment
echo -e "\n📋 PYTHON ENVIRONMENT"
debug_test "Python Version" "python3 --version"
debug_test "Current Directory" "pwd && ls -la"
debug_test "Python Path" "python3 -c 'import sys; print(\"\\n\".join(sys.path))'"

# 2. Test individual Python imports with detailed errors
echo -e "\n🐍 PYTHON IMPORTS (with error details)"
debug_test "Config Import" "python3 -c 'import config; print(f\"Config loaded: {config.DEVICE}\")'"
debug_test "Signal Engine Import" "python3 -c 'import signal_engine; print(\"Signal engine loaded\")'"
debug_test "Confidence Scoring Import" "python3 -c 'import confidence_scoring; print(\"Confidence scoring loaded\")'"

# 3. Test signal generation with full error output
echo -e "\n📊 SIGNAL GENERATION (detailed)"
debug_test "Signal Generation" "python3 -c '
import signal_engine
import time
import traceback

try:
    shared_data = {
        \"timestamp\": time.time(),
        \"mode\": \"dry\",
        \"gpu_available\": True,
        \"iteration\": 1
    }
    print(f\"Shared data: {shared_data}\")
    
    signal = signal_engine.generate_signal(shared_data)
    print(f\"Signal result: {signal}\")
    
    confidence = signal.get(\"confidence\", 0)
    print(f\"Confidence: {confidence}\")
    
    if confidence <= 0:
        raise Exception(f\"Invalid confidence: {confidence}\")
    
    print(\"✅ Signal generation successful\")
    
except Exception as e:
    print(f\"❌ Signal generation failed: {e}\")
    traceback.print_exc()
    raise
'"

# 4. Test confidence scoring with detailed output
echo -e "\n🧮 CONFIDENCE SCORING (detailed)"
debug_test "Confidence Scoring" "python3 -c '
import confidence_scoring
import traceback

try:
    # Create test signals
    signals = [
        {
            \"confidence\": 0.6,
            \"source\": \"test_engine\",
            \"priority\": 1,
            \"signal_data\": {
                \"asset\": \"BTC\",
                \"entry_price\": 45000
            }
        }
    ]
    print(f\"Input signals: {signals}\")
    
    result = confidence_scoring.merge_signals(signals)
    print(f\"Merged result: {result}\")
    
    if \"confidence\" not in result:
        raise Exception(\"Missing confidence in result\")
    
    print(\"✅ Confidence scoring successful\")
    
except Exception as e:
    print(f\"❌ Confidence scoring failed: {e}\")
    traceback.print_exc()
    raise
'"

# 5. Test file operations
echo -e "\n📁 FILE OPERATIONS (detailed)"
debug_test "File Write/Read Test" "python3 -c '
import json
import time
import os
import traceback

try:
    # Ensure tmp directory exists
    os.makedirs(\"/tmp\", exist_ok=True)
    print(\"✓ /tmp directory ready\")
    
    # Create test signal
    test_signal = {
        \"timestamp\": time.time(),
        \"confidence\": 0.8,
        \"best_signal\": {
            \"asset\": \"BTC\",
            \"entry_price\": 45000
        }
    }
    print(f\"Test signal: {test_signal}\")
    
    # Write to file
    with open(\"/tmp/test_signal.json\", \"w\") as f:
        json.dump(test_signal, f, indent=2)
    print(\"✓ Signal written to file\")
    
    # Read from file
    with open(\"/tmp/test_signal.json\", \"r\") as f:
        loaded_signal = json.load(f)
    print(f\"Loaded signal: {loaded_signal}\")
    
    # Validate
    if loaded_signal[\"confidence\"] != test_signal[\"confidence\"]:
        raise Exception(\"File content mismatch\")
    
    # Cleanup
    os.remove(\"/tmp/test_signal.json\")
    print(\"✓ Cleanup completed\")
    
    print(\"✅ File operations successful\")
    
except Exception as e:
    print(f\"❌ File operations failed: {e}\")
    traceback.print_exc()
    raise
'"

# 6. Check Rust environment
echo -e "\n🦀 RUST ENVIRONMENT"
debug_test "Rust Installation" "rustc --version && cargo --version"
debug_test "Cargo.toml Check" "[ -f Cargo.toml ] && echo 'Cargo.toml found' && head -10 Cargo.toml"
debug_test "Rust Source Files" "ls -la src/"
debug_test "Target Directory" "ls -la target/ 2>/dev/null || echo 'No target directory'"

# 7. Check for binary
echo -e "\n🔍 BINARY SEARCH"
debug_test "Find HFT Executables" "find . -name '*hft*' -type f 2>/dev/null || echo 'No HFT binaries found'"
debug_test "Find Any Executables" "find . -name '*.exe' -o -name 'hft_executor' -o -name 'main' 2>/dev/null || echo 'No executables found'"

# 8. Test Rust compilation
echo -e "\n🔨 RUST COMPILATION TEST"
debug_test "Cargo Check" "cargo check"
debug_test "Cargo Build Debug" "cargo build"

# 9. Integration test simulation
echo -e "\n🔄 INTEGRATION SIMULATION"
debug_test "Full Integration Chain" "python3 -c '
import signal_engine
import confidence_scoring
import json
import time
import traceback

try:
    print(\"Starting integration test...\")
    
    # Step 1: Generate signal
    shared_data = {\"timestamp\": time.time(), \"mode\": \"dry\"}
    signal = signal_engine.generate_signal(shared_data)
    print(f\"Step 1 - Signal: {signal.get(\"confidence\", 0):.3f}\")
    
    # Step 2: Merge signals
    merged = confidence_scoring.merge_signals([signal])
    print(f\"Step 2 - Merged: {merged.get(\"confidence\", 0):.3f}\")
    
    # Step 3: Write signal file
    with open(\"/tmp/debug_signal.json\", \"w\") as f:
        json.dump(merged, f)
    print(\"Step 3 - File written\")
    
    # Step 4: Validate file
    with open(\"/tmp/debug_signal.json\", \"r\") as f:
        loaded = json.load(f)
    
    if \"confidence\" not in loaded or \"best_signal\" not in loaded:
        raise Exception(\"Invalid signal structure\")
    
    print(f\"Step 4 - Validation successful: {loaded[\"best_signal\"][\"asset\"]}\")
    print(\"✅ Full integration chain working\")
    
except Exception as e:
    print(f\"❌ Integration failed at: {e}\")
    traceback.print_exc()
    raise
'"

echo -e "\n🎯 DEBUGGING COMPLETE"
echo "Check the detailed output above to identify specific failure points."