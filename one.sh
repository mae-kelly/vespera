#!/bin/bash

# Complete build and test pipeline for HFT system
# Builds Rust executor and runs comprehensive tests

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

BUILD_LOG="/tmp/hft_build_$(date +%s).log"
TOTAL_STEPS=0
COMPLETED_STEPS=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$BUILD_LOG"
}

step() {
    TOTAL_STEPS=$((TOTAL_STEPS + 1))
    echo -e "${CYAN}📋 Step $TOTAL_STEPS: $1${NC}"
}

complete_step() {
    COMPLETED_STEPS=$((COMPLETED_STEPS + 1))
    echo -e "${GREEN}✅ Step $COMPLETED_STEPS completed${NC}"
    echo ""
}

fail_step() {
    echo -e "${RED}❌ Step $COMPLETED_STEPS failed: $1${NC}"
    echo -e "${YELLOW}💡 Check build log: $BUILD_LOG${NC}"
    exit 1
}

print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   HFT BUILD & TEST PIPELINE                 ║"
    echo "║            Complete System Build and Validation             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    log "Starting HFT build and test pipeline"
}

check_prerequisites() {
    step "Checking Prerequisites"
    
    # Check if we're in the right directory
    if [[ ! -f "Cargo.toml" ]] || [[ ! -f "main.py" ]]; then
        fail_step "Not in HFT project directory (missing Cargo.toml or main.py)"
    fi
    
    # Check Rust installation
    if ! command -v cargo &> /dev/null; then
        fail_step "Cargo not found. Please install Rust: https://rustup.rs/"
    fi
    
    # Check Python installation
    if ! command -v python3 &> /dev/null; then
        fail_step "Python 3 not found. Please install Python 3.8+"
    fi
    
    # Check Git (for version info)
    if command -v git &> /dev/null && git rev-parse --git-dir &> /dev/null; then
        local git_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        log "Git commit: $git_hash"
    fi
    
    log "Prerequisites check completed successfully"
    complete_step
}

install_python_dependencies() {
    step "Installing Python Dependencies"
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        log "pip3 not found, trying pip"
        if ! command -v pip &> /dev/null; then
            fail_step "pip not found. Please install pip"
        fi
        local pip_cmd="pip"
    else
        local pip_cmd="pip3"
    fi
    
    # Install basic dependencies
    log "Installing Python dependencies..."
    if ! $pip_cmd install torch requests pandas websocket-client >> "$BUILD_LOG" 2>&1; then
        fail_step "Failed to install Python dependencies"
    fi
    
    # Verify GPU support
    log "Checking GPU support..."
    python3 -c "
import torch
import sys

if torch.cuda.is_available():
    print('CUDA GPU detected:', torch.cuda.get_device_name(0))
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print('Apple MPS GPU detected')
else:
    print('No GPU acceleration available')
    sys.exit(1)
" >> "$BUILD_LOG" 2>&1 || fail_step "GPU acceleration not available"
    
    log "Python dependencies installed successfully"
    complete_step
}

build_rust_components() {
    step "Building Rust Components"
    
    # Clean previous builds
    log "Cleaning previous builds..."
    if ! cargo clean >> "$BUILD_LOG" 2>&1; then
        log "Warning: cargo clean failed, continuing..."
    fi
    
    # Build in release mode
    log "Building Rust executor in release mode..."
    if ! cargo build --release >> "$BUILD_LOG" 2>&1; then
        fail_step "Rust build failed"
    fi
    
    # Verify binary was created
    if [[ ! -f "./target/release/hft_executor" ]]; then
        fail_step "Rust binary not found after build"
    fi
    
    # Copy binary to project root
    log "Copying binary to project root..."
    cp "./target/release/hft_executor" "./hft_executor"
    chmod +x "./hft_executor"
    
    # Get binary info
    local binary_size=$(ls -lh "./hft_executor" | awk '{print $5}')
    log "Rust executor built successfully (size: $binary_size)"
    
    complete_step
}

verify_python_modules() {
    step "Verifying Python Modules"
    
    local modules=("config" "signal_engine" "confidence_scoring" "entropy_meter" "laggard_sniper" "relief_trap" "notifier_elegant" "logger")
    
    for module in "${modules[@]}"; do
        log "Testing import: $module"
        if ! python3 -c "import $module; print(f'✅ {module} imported successfully')" >> "$BUILD_LOG" 2>&1; then
            fail_step "Failed to import $module"
        fi
    done
    
    log "All Python modules verified"
    complete_step
}

test_signal_generation() {
    step "Testing Signal Generation"
    
    log "Testing signal engine..."
    python3 -c "
import signal_engine
import confidence_scoring
import time
import json

# Test signal generation
shared_data = {
    'timestamp': time.time(),
    'mode': 'dry',
    'iteration': 1,
    'gpu_available': True
}

print('Testing signal engine...')
signal = signal_engine.generate_signal(shared_data)

if not signal or signal.get('confidence', 0) <= 0:
    print('❌ Signal generation failed')
    exit(1)

print(f'✅ Signal generated with confidence: {signal[\"confidence\"]:.3f}')

# Test confidence scoring
print('Testing confidence scoring...')
merged = confidence_scoring.merge_signals([signal])

if not merged or merged.get('confidence', 0) <= 0:
    print('❌ Confidence scoring failed')
    exit(1)

print(f'✅ Merged signal confidence: {merged[\"confidence\"]:.3f}')

# Write test signal
with open('/tmp/test_signal.json', 'w') as f:
    json.dump(merged, f, indent=2)

print('✅ Signal generation test completed')
" >> "$BUILD_LOG" 2>&1 || fail_step "Signal generation test failed"
    
    log "Signal generation test completed"
    complete_step
}

test_rust_executor() {
    step "Testing Rust Executor"
    
    # Ensure we have a test signal
    if [[ ! -f "/tmp/test_signal.json" ]]; then
        log "Creating test signal for Rust executor..."
        cat > /tmp/test_signal.json << 'EOF'
{
  "timestamp": 1234567890,
  "confidence": 0.85,
  "best_signal": {
    "asset": "BTC",
    "entry_price": 67500,
    "stop_loss": 68512.5,
    "take_profit_1": 66487.5,
    "confidence": 0.85,
    "reason": "test_signal"
  }
}
EOF
    fi
    
    # Copy test signal to expected location
    cp /tmp/test_signal.json /tmp/signal.json
    
    # Set environment for dry run
    export MODE=dry
    export RUST_LOG=info
    
    # Test Rust executor
    log "Testing Rust executor (10 second test)..."
    timeout 10 ./hft_executor >> "$BUILD_LOG" 2>&1 || {
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log "Rust executor test completed (timeout as expected)"
        else
            fail_step "Rust executor failed with exit code $exit_code"
        fi
    }
    
    # Check if fills were generated
    if [[ -f "/tmp/fills.json" ]] && grep -q "simulated_fill\|filled" /tmp/fills.json; then
        local fill_count=$(grep -o '"status"' /tmp/fills.json | wc -l)
        log "Rust executor generated $fill_count fills"
    else
        fail_step "Rust executor did not generate any fills"
    fi
    
    log "Rust executor test completed"
    complete_step
}

run_integration_test() {
    step "Running Integration Test"
    
    # Clean up old files
    rm -f /tmp/signal.json /tmp/fills.json
    
    # Set environment
    export MODE=dry
    export RUST_LOG=warn
    export PYTHONUNBUFFERED=1
    
    log "Starting integration test..."
    
    # Start Python system
    python3 main.py --mode=dry >> "$BUILD_LOG" 2>&1 &
    local python_pid=$!
    
    sleep 3
    
    # Start Rust executor
    timeout 15 ./hft_executor >> "$BUILD_LOG" 2>&1 &
    local rust_pid=$!
    
    sleep 10
    
    # Stop processes
    kill $python_pid 2>/dev/null || true
    kill $rust_pid 2>/dev/null || true
    wait $python_pid 2>/dev/null || true
    wait $rust_pid 2>/dev/null || true
    
    # Check results
    local signals_generated=0
    local fills_generated=0
    
    if [[ -f "/tmp/signal.json" ]]; then
        signals_generated=1
        log "✅ Signal file generated"
    else
        log "❌ No signal file generated"
    fi
    
    if [[ -f "/tmp/fills.json" ]]; then
        fills_generated=$(grep -o '"status"' /tmp/fills.json 2>/dev/null | wc -l || echo "0")
        log "✅ Generated $fills_generated fills"
    else
        log "❌ No fills file generated"
    fi
    
    if [[ $signals_generated -eq 1 ]] && [[ $fills_generated -gt 0 ]]; then
        log "Integration test passed: Signal→Fill pipeline working"
    else
        fail_step "Integration test failed: Signal→Fill pipeline broken"
    fi
    
    complete_step
}

create_startup_script() {
    step "Creating Startup Scripts"
    
    # Make init_pipeline.sh executable
    if [[ -f "init_pipeline.sh" ]]; then
        chmod +x init_pipeline.sh
        log "✅ init_pipeline.sh made executable"
    fi
    
    # Create a simple start script
    cat > start_hft.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting HFT System"
echo "======================"

if [[ ! -f "./hft_executor" ]]; then
    echo "❌ hft_executor not found. Run: ./build_and_test.sh"
    exit 1
fi

MODE="${1:-dry}"
echo "Mode: $MODE"

if [[ -f "init_pipeline.sh" ]]; then
    ./init_pipeline.sh "$MODE"
else
    echo "Starting system manually..."
    export MODE="$MODE"
    
    echo "Starting Python cognition layer..."
    python3 main.py --mode="$MODE" &
    PYTHON_PID=$!
    
    sleep 3
    
    echo "Starting Rust executor..."
    ./hft_executor
fi
EOF
    
    chmod +x start_hft.sh
    log "✅ start_hft.sh created"
    
    complete_step
}

generate_build_report() {
    step "Generating Build Report"
    
    local rust_version=$(cargo --version 2>/dev/null || echo "unknown")
    local python_version=$(python3 --version 2>/dev/null || echo "unknown")
    local gpu_info=$(python3 -c "import torch; print('CUDA' if torch.cuda.is_available() else 'MPS' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'CPU')" 2>/dev/null || echo "unknown")
    
    cat > build_report.json << EOF
{
  "build_timestamp": $(date +%s),
  "build_date": "$(date)",
  "build_status": "SUCCESS",
  "components": {
    "rust_executor": "BUILT",
    "python_modules": "VERIFIED",
    "signal_generation": "TESTED",
    "integration": "TESTED"
  },
  "environment": {
    "rust_version": "$rust_version",
    "python_version": "$python_version",
    "gpu_support": "$gpu_info"
  },
  "artifacts": {
    "rust_binary": "./hft_executor",
    "startup_script": "./start_hft.sh",
    "pipeline_script": "./init_pipeline.sh"
  },
  "build_log": "$BUILD_LOG",
  "next_steps": [
    "./quick_validate.sh - Quick system validation",
    "./start_hft.sh dry - Start in dry run mode",
    "./comprehensive_system_test.sh - Full test suite",
    "./stress_test.sh - Performance testing"
  ]
}
EOF
    
    log "Build report generated: build_report.json"
    complete_step
}

cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up test processes...${NC}"
    pkill -f "python3 main.py" 2>/dev/null || true
    pkill -f "./hft_executor" 2>/dev/null || true
}

main() {
    print_header
    
    trap cleanup EXIT
    
    echo -e "${BLUE}Build Configuration:${NC}"
    echo "  Rust: $(cargo --version 2>/dev/null || echo 'Not found')"
    echo "  Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "  Build Log: $BUILD_LOG"
    echo ""
    
    # Run all build and test steps
    check_prerequisites
    install_python_dependencies
    build_rust_components
    verify_python_modules
    test_signal_generation
    test_rust_executor
    run_integration_test
    create_startup_script
    generate_build_report
    
    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}🎉 BUILD & TEST PIPELINE COMPLETED!${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}✅ System successfully built and tested${NC}"
    echo -e "${CYAN}✅ All components verified working${NC}"
    echo -e "${CYAN}✅ Ready for operation${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  ${GREEN}./quick_validate.sh${NC}     - Quick validation"
    echo -e "  ${GREEN}./start_hft.sh dry${NC}      - Start in dry run mode"
    echo -e "  ${GREEN}./stress_test.sh${NC}        - Performance testing"
    echo ""
    echo -e "${BLUE}Build log saved to: $BUILD_LOG${NC}"
    
    return 0
}

main "$@"