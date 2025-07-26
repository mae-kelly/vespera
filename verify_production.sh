#!/bin/bash
# verify_production.sh - Verify no mock data remains (updated)

echo "🔍 VRIYING PRODUCTION SYSTM"
echo "=============================="

MOCK_OUND=

# Search Python files for mock references (ecluding venv, backups, and pandas)
echo "🔎 Checking Python files (ecluding venv and backups)..."
if find . -name "*.py" -not -path "./venv/*" -not -path "./backup*/*" -not -path "./pandas/*" -eec grep -l -i "mock|fake|Simplifiedeed|test.*data|fallback.*data"  ; >/dev/null | grep -v verify_production.sh | head -; then
    echo "❌ ound some references (checking if they're in our code...)"
    # Check if any are in our main files (not pandas library)
    if find . -madepth  -name "*.py" -eec grep -l -i "Simplifiedeed|mock|fake"  ; >/dev/null; then
        echo "❌ MOCK DATA RRNCS OUND IN OUR PYTHON ILS"
        MOCK_OUND=
    else
        echo "✅ No mock data references in our Python files (pandas library references are OK)"
    fi
else
    echo "✅ No mock data references in Python files"
fi

# Search Rust files for mock references  
echo "🔎 Checking Rust files..."
if find src/ -name "*.rs" -eec grep -l -i "dry.*mode|simulation"  ; >/dev/null; then
    echo "❌ MOCK DATA RRNCS OUND IN RUST ILS"
    MOCK_OUND=
else
    echo "✅ No mock data references in Rust files"
fi

# Check for test files that shouldn't eist
echo "🔎 Checking for remaining test files..."
TST_ILS=("benchmark_suite.py" "integration_test_suite.py" "performance_test_suite.py" "one.py" "test_repairs.py" "validate_fies.py")

for file in "$TST_ILS[@]"; do
    if [ -f "$file" ]; then
        echo "❌ TST IL OUND: $file"
        MOCK_OUND=
    fi
done

if [ $MOCK_OUND -eq  ]; then
    echo "✅ No test files found"
fi

# Check main files for production readiness
echo "🔎 Checking production readiness..."

if [ -f "main.py" ]; then
    if grep -q "create_default_signal|fallback|dry" main.py; then
        echo "❌ NON-PRODUCTION COD OUND IN main.py"
        MOCK_OUND=
    else
        echo "✅ main.py appears production ready"
    fi
else
    echo "❌ main.py not found"
    MOCK_OUND=
fi

# Check signal_engine.py for live-only implementation
if [ -f "signal_engine.py" ]; then
    if grep -q "Simplifiedeed|mock|fake" signal_engine.py; then
        echo "❌ MOCK IMPLMNTATIONS OUND IN signal_engine.py"
        MOCK_OUND=
    else
        echo "✅ signal_engine.py appears live-only"
    fi
else
    echo "❌ signal_engine.py not found"
    MOCK_OUND=
fi

# Check for required production files
echo "🔎 Checking for required production files..."
RQUIRD_ILS=("live_data_engine.py" "confidence_scoring.py" "config.py" "src/main.rs" "src/ok_eecutor.rs" "setup_production_env.sh" "start_production.sh" "emergency_stop.sh")

for file in "$RQUIRD_ILS[@]"; do
    if [ ! -f "$file" ]; then
        echo "❌ RQUIRD IL MISSING: $file"
        MOCK_OUND=
    fi
done

if [ $MOCK_OUND -eq  ]; then
    echo "✅ All required files present"
fi

# Check environment requirements
echo "🔎 Checking production environment requirements..."
if ! python -c "import torch; print('GPU available:', torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()))" >/dev/null | grep -q "True"; then
    echo "❌ GPU NOT AVAILAL"
    MOCK_OUND=
else
    echo "✅ GPU available"
fi

# Check Rust compilation
echo "🔎 Checking Rust compilation..."
if ! cargo check --quiet >/dev/null; then
    echo "❌ RUST COMPILATION ISSUS"
    MOCK_OUND=
else
    echo "✅ Rust code compiles successfully"
fi

# Check for production validation in key files
echo "🔎 Checking production validation..."
if [ -f "signal_engine.py" ] && grep -q "production_validated.*True|PRODUCTION.*SIGNAL" signal_engine.py; then
    echo "✅ Signal engine has production validation"
else
    echo "❌ Signal engine missing production validation"
    MOCK_OUND=
fi

if [ -f "confidence_scoring.py" ] && grep -q "production_validated.*True|PRODUCTION.*LIV" confidence_scoring.py; then
    echo "✅ Confidence scoring has production validation"
else
    echo "❌ Confidence scoring missing production validation"
    MOCK_OUND=
fi

# Check config.py forces live mode
if [ -f "config.py" ] && grep -q 'MOD.*=.*"live"' config.py; then
    echo "✅ Config forces live mode"
else
    echo "❌ Config does not force live mode"
    MOCK_OUND=
fi

# inal verification summary
echo ""
echo "=================================="
if [ $MOCK_OUND -eq  ]; then
    echo "🎉 PRODUCTION VRIICATION PASSD"
    echo "✅ No mock data found in our code"
    echo "✅ All test files removed"
    echo "✅ Production validation present"
    echo "✅ System ready for live trading"
    echo ""
    echo "⚠️  RMINDR: This is now a LIV trading system"
    echo "⚠️  Set your API credentials before starting:"
    echo "     eport OKX_API_KY=your_key"
    echo "     eport OKX_SCRT_KY=your_secret"
    echo "     eport OKX_PASSPHRAS=your_passphrase"
    echo "⚠️  Use ./start_production.sh to begin"
    eit 
else
    echo "❌ PRODUCTION VRIICATION AILD"
    echo "❌ Issues found above need to be resolved"
    echo "❌ System NOT ready for production"
    echo ""
    echo "🔧 Check the specific issues mentioned above"
    eit 
fi
echo "=================================="
