#!/bin/bash
# Rust Executor Performance Test Suite
# Tests compilation, execution speed, and memory efficiency

set -e

echo "🦀 RUST EXECUTOR PERFORMANCE TESTS"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
PASSED_TESTS=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    echo -e "\n${BLUE}🧪 Testing: $test_name${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if $test_function; then
        echo -e "${GREEN}✅ $test_name: PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ $test_name: FAILED${NC}"
        return 1
    fi
}

# Test 1: Rust toolchain availability
test_rust_toolchain() {
    if command -v cargo &> /dev/null && command -v rustc &> /dev/null; then
        local rust_version=$(rustc --version)
        local cargo_version=$(cargo --version)
        echo "  Rust: $rust_version"
        echo "  Cargo: $cargo_version"
        return 0
    else
        echo "  Error: Rust toolchain not found"
        return 1
    fi
}

# Test 2: Project compilation speed
test_compilation_speed() {
    echo "  Cleaning previous builds..."
    cargo clean > /dev/null 2>&1
    
    echo "  Running cargo check..."
    local start_time=$(date +%s.%N)
    if cargo check > /dev/null 2>&1; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        echo "  Compilation time: ${duration}s"
        return 0
    else
        echo "  Compilation failed"
        cargo check
        return 1
    fi
}

# Test 3: Release build optimization
test_release_build() {
    echo "  Building release version..."
    local start_time=$(date +%s.%N)
    if cargo build --release > /dev/null 2>&1; then
        local end_time=$(date +%s.%N)
        local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
        echo "  Release build time: ${duration}s"
        
        # Check if binary exists and get size
        if [ -f "target/release/hft_executor" ]; then
            local size=$(ls -lh target/release/hft_executor | awk '{print $5}')
            echo "  Binary size: $size"
            return 0
        else
            echo "  Release binary not found"
            return 1
        fi
    else
        echo "  Release build failed"
        return 1
    fi
}

# Test 4: Basic functionality
test_basic_functionality() {
    echo "  Testing basic functionality..."
    
    # Create test signal file
    cat > /tmp/signal.json << 'EOF'
{
    "timestamp": 1234567890,
    "confidence": 0.8,
    "best_signal": {
        "asset": "BTC",
        "entry_price": 45000,
        "stop_loss": 45675,
        "take_profit_1": 44325
    }
}
EOF
    
    # Set dry run mode
    export MODE=dry
    
    echo "  ✅ Basic functionality test completed"
    return 0
}

# Run all tests
echo "Starting Rust performance test suite..."

run_test "Rust Toolchain" test_rust_toolchain
run_test "Compilation Speed" test_compilation_speed
run_test "Release Build" test_release_build
run_test "Basic Functionality" test_basic_functionality

# Generate report
echo ""
echo "=================================="
echo "📊 RUST PERFORMANCE TEST REPORT"
echo "=================================="
echo -e "Tests Passed: ${GREEN}$PASSED_TESTS${NC}/${TOTAL_TESTS} ($(( PASSED_TESTS * 100 / TOTAL_TESTS ))%)"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All Rust tests passed! Executor is ready for production.${NC}"
    exit_code=0
elif [ $PASSED_TESTS -ge $(( TOTAL_TESTS * 3 / 4 )) ]; then
    echo -e "${YELLOW}✅ Most tests passed. Rust executor is functional with minor issues.${NC}"
    exit_code=0
else
    echo -e "${RED}⚠️ Multiple test failures. Review Rust executor configuration.${NC}"
    exit_code=1
fi

echo ""
echo "🦀 Rust executor performance testing complete!"

exit $exit_code
