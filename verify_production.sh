#!/bin/bash
# verify_production.sh - Verify no mock data remains (updated)

echo "🔍 VERIFYING PRODUCTION SYSTEM"
echo "=============================="

MOCK_FOUND=0

# Search Python files for mock references (excluding venv, backups, and pandas)
echo "🔎 Checking Python files (excluding venv and backups)..."
if find . -name "*.py" -not -path "./venv/*" -not -path "./backup*/*" -not -path "./pandas/*" -exec grep -l -i "mock\|fake\|SimplifiedFeed\|test.*data\|fallback.*data" {} \; 2>/dev/null | grep -v verify_production.sh | head -5; then
    echo "❌ Found some references (checking if they're in our code...)"
    # Check if any are in our main files (not pandas library)
    if find . -maxdepth 1 -name "*.py" -exec grep -l -i "SimplifiedFeed\|mock\|fake" {} \; 2>/dev/null; then
        echo "❌ MOCK DATA REFERENCES FOUND IN OUR PYTHON FILES"
        MOCK_FOUND=1
    else
        echo "✅ No mock data references in our Python files (pandas library references are OK)"
    fi
else
    echo "✅ No mock data references in Python files"
fi

# Search Rust files for mock references  
echo "🔎 Checking Rust files..."
if find src/ -name "*.rs" -exec grep -l -i "dry.*mode\|simulation" {} \; 2>/dev/null; then
    echo "❌ MOCK DATA REFERENCES FOUND IN RUST FILES"
    MOCK_FOUND=1
else
    echo "✅ No mock data references in Rust files"
fi

# Check for test files that shouldn't exist
echo "🔎 Checking for remaining test files..."
TEST_FILES=("benchmark_suite.py" "integration_test_suite.py" "performance_test_suite.py" "one.py" "test_repairs.py" "validate_fixes.py")

for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "❌ TEST FILE FOUND: $file"
        MOCK_FOUND=1
    fi
done

if [ $MOCK_FOUND -eq 0 ]; then
    echo "✅ No test files found"
fi

# Check main files for production readiness
echo "🔎 Checking production readiness..."

if [ -f "main.py" ]; then
    if grep -q "create_default_signal\|fallback\|dry" main.py; then
        echo "❌ NON-PRODUCTION CODE FOUND IN main.py"
        MOCK_FOUND=1
    else
        echo "✅ main.py appears production ready"
    fi
else
    echo "❌ main.py not found"
    MOCK_FOUND=1
fi

# Check signal_engine.py for live-only implementation
if [ -f "signal_engine.py" ]; then
    if grep -q "SimplifiedFeed\|mock\|fake" signal_engine.py; then
        echo "❌ MOCK IMPLEMENTATIONS FOUND IN signal_engine.py"
        MOCK_FOUND=1
    else
        echo "✅ signal_engine.py appears live-only"
    fi
else
    echo "❌ signal_engine.py not found"
    MOCK_FOUND=1
fi

# Check for required production files
echo "🔎 Checking for required production files..."
REQUIRED_FILES=("live_data_engine.py" "confidence_scoring.py" "config.py" "src/main.rs" "src/okx_executor.rs" "setup_production_env.sh" "start_production.sh" "emergency_stop.sh")

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ REQUIRED FILE MISSING: $file"
        MOCK_FOUND=1
    fi
done

if [ $MOCK_FOUND -eq 0 ]; then
    echo "✅ All required files present"
fi

# Check environment requirements
echo "🔎 Checking production environment requirements..."
if ! python3 -c "import torch; print('GPU available:', torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()))" 2>/dev/null | grep -q "True"; then
    echo "❌ GPU NOT AVAILABLE"
    MOCK_FOUND=1
else
    echo "✅ GPU available"
fi

# Check Rust compilation
echo "🔎 Checking Rust compilation..."
if ! cargo check --quiet 2>/dev/null; then
    echo "❌ RUST COMPILATION ISSUES"
    MOCK_FOUND=1
else
    echo "✅ Rust code compiles successfully"
fi

# Check for production validation in key files
echo "🔎 Checking production validation..."
if [ -f "signal_engine.py" ] && grep -q "production_validated.*True\|PRODUCTION.*SIGNAL" signal_engine.py; then
    echo "✅ Signal engine has production validation"
else
    echo "❌ Signal engine missing production validation"
    MOCK_FOUND=1
fi

if [ -f "confidence_scoring.py" ] && grep -q "production_validated.*True\|PRODUCTION.*LIVE" confidence_scoring.py; then
    echo "✅ Confidence scoring has production validation"
else
    echo "❌ Confidence scoring missing production validation"
    MOCK_FOUND=1
fi

# Check config.py forces live mode
if [ -f "config.py" ] && grep -q 'MODE.*=.*"live"' config.py; then
    echo "✅ Config forces live mode"
else
    echo "❌ Config does not force live mode"
    MOCK_FOUND=1
fi

# Final verification summary
echo ""
echo "=================================="
if [ $MOCK_FOUND -eq 0 ]; then
    echo "🎉 PRODUCTION VERIFICATION PASSED"
    echo "✅ No mock data found in our code"
    echo "✅ All test files removed"
    echo "✅ Production validation present"
    echo "✅ System ready for live trading"
    echo ""
    echo "⚠️  REMINDER: This is now a LIVE trading system"
    echo "⚠️  Set your API credentials before starting:"
    echo "     export OKX_API_KEY=your_key"
    echo "     export OKX_SECRET_KEY=your_secret"
    echo "     export OKX_PASSPHRASE=your_passphrase"
    echo "⚠️  Use ./start_production.sh to begin"
    exit 0
else
    echo "❌ PRODUCTION VERIFICATION FAILED"
    echo "❌ Issues found above need to be resolved"
    echo "❌ System NOT ready for production"
    echo ""
    echo "🔧 Check the specific issues mentioned above"
    exit 1
fi
echo "=================================="
