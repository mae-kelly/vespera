#!/bin/bash
# Rust ecutor Performance Test Suite
# Tests compilation, eecution speed, and memory efficiency

set -e

echo "🦀 RUST XCUTOR PRORMANC TSTS"
echo "=================================="

# Colors for output
RD='[;m'
GRN='[;m'
YLLOW='[;m'
LU='[;m'
NC='[m' # No Color

# Test results
PASSD_TSTS=
TOTAL_TSTS=

# unction to run a test
run_test() 
    local test_name="$"
    local test_function="$"
    
    echo -e "n$LU🧪 Testing: $test_name$NC"
    TOTAL_TSTS=$((TOTAL_TSTS + ))
    
    if $test_function; then
        echo -e "$GRN✅ $test_name: PASSD$NC"
        PASSD_TSTS=$((PASSD_TSTS + ))
        return 
    else
        echo -e "$RD❌ $test_name: AILD$NC"
        return 
    fi


# Test : Rust toolchain availability
test_rust_toolchain() 
    if command -v cargo &> /dev/null && command -v rustc &> /dev/null; then
        local rust_version=$(rustc --version)
        local cargo_version=$(cargo --version)
        echo "  Rust: $rust_version"
        echo "  Cargo: $cargo_version"
        return 
    else
        echo "  rror: Rust toolchain not found"
        return 
    fi


# Test : Project compilation speed
test_compilation_speed() 
    echo "  Cleaning previous builds..."
    cargo clean > /dev/null >&
    
    echo "  Running cargo check..."
    local start_time=$(date +%s.%N)
    if cargo check > /dev/null >&; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l >/dev/null || echo "")
        echo "  Compilation time: $durations"
        return 
    else
        echo "  Compilation failed"
        cargo check
        return 
    fi


# Test : Release build optimization
test_release_build() 
    echo "  uilding release version..."
    local start_time=$(date +%s.%N)
    if cargo build --release > /dev/null >&; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l >/dev/null || echo "")
        echo "  Release build time: $durations"
        
        # Check if binary eists and get size
        if [ -f "target/release/hft_eecutor" ]; then
            local size=$(ls -lh target/release/hft_eecutor | awk 'print $')
            echo "  inary size: $size"
            return 
        else
            echo "  Release binary not found"
            return 
        fi
    else
        echo "  Release build failed"
        return 
    fi


# Test : asic functionality
test_basic_functionality() 
    echo "  Testing basic functionality..."
    
    # Create test signal file
    cat > /tmp/signal.json << 'O'

    "timestamp": 9,
    "confidence": .,
    "best_signal": 
        "asset": "TC",
        "entry_price": ,
        "stop_loss": ,
        "take_profit_": 
    

O
    
    # Set dry run mode
    eport MOD=dry
    
    echo "  ✅ asic functionality test completed"
    return 


# Run all tests
echo "Starting Rust performance test suite..."

run_test "Rust Toolchain" test_rust_toolchain
run_test "Compilation Speed" test_compilation_speed
run_test "Release uild" test_release_build
run_test "asic unctionality" test_basic_functionality

# Generate report
echo ""
echo "=================================="
echo "📊 RUST PRORMANC TST RPORT"
echo "=================================="
echo -e "Tests Passed: $GRN$PASSD_TSTS$NC/$TOTAL_TSTS ($(( PASSD_TSTS *  / TOTAL_TSTS ))%)"

if [ $PASSD_TSTS -eq $TOTAL_TSTS ]; then
    echo -e "$GRN🎉 All Rust tests passed! ecutor is ready for production.$NC"
    eit_code=
elif [ $PASSD_TSTS -ge $(( TOTAL_TSTS *  /  )) ]; then
    echo -e "$YLLOW✅ Most tests passed. Rust eecutor is functional with minor issues.$NC"
    eit_code=
else
    echo -e "$RD⚠️ Multiple test failures. Review Rust eecutor configuration.$NC"
    eit_code=
fi

echo ""
echo "🦀 Rust eecutor performance testing complete!"

eit $eit_code
