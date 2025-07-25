#!/bin/bash

set -e

echo "🔧 FIXING CUPY IMPORT ISSUES - FINAL FIX"
echo "========================================"

echo "📋 Current import issues detected in signal_engine.py"
echo "Checking all Python files for cupy imports..."

# Create backup
BACKUP_DIR="cupy_fix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Find all Python files with cupy imports
echo "🔍 Scanning for cupy imports..."
for file in *.py; do
    if [[ -f "$file" ]] && grep -q "import cupy" "$file" 2>/dev/null; then
        echo "Found cupy import in: $file"
        cp "$file" "$BACKUP_DIR/"
    fi
done

echo ""
echo "🔧 FIXING ALL CUPY IMPORTS"
echo "=========================="

# Fix signal_engine.py specifically
echo "Fixing signal_engine.py..."
if [[ -f "signal_engine.py" ]]; then
    sed -i.tmp 's/import cupy as cp/import cupy_fallback as cp/g' signal_engine.py
    sed -i.tmp 's/import cupy$/import cupy_fallback as cupy/g' signal_engine.py
    rm -f signal_engine.py.tmp
    echo "✅ Fixed signal_engine.py"
fi

# Fix all other Python files
for file in *.py; do
    if [[ -f "$file" ]] && [[ "$file" != "cupy_fallback.py" ]]; then
        if grep -q "import cupy" "$file" 2>/dev/null; then
            echo "Fixing $file..."
            sed -i.tmp 's/import cupy as cp/import cupy_fallback as cp/g' "$file"
            sed -i.tmp 's/import cupy$/import cupy_fallback as cupy/g' "$file"
            sed -i.tmp 's/^cupy/cupy_fallback/g' "$file"
            rm -f "$file.tmp"
            echo "✅ Fixed $file"
        fi
    fi
done

echo ""
echo "🧪 TESTING IMPORTS"
echo "=================="

# Test each file individually
echo "Testing signal_engine.py import..."
python3 -c "
try:
    import signal_engine
    print('✅ signal_engine.py imports successfully')
except Exception as e:
    print(f'❌ signal_engine.py import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "Testing all modules..."
python3 -c "
import sys
modules = ['config', 'signal_engine', 'entropy_meter', 'laggard_sniper', 'relief_trap', 'confidence_scoring', 'notifier', 'logger']
failed = []

for module in modules:
    try:
        exec(f'import {module}')
        print(f'✅ {module}')
    except Exception as e:
        print(f'❌ {module}: {e}')
        failed.append(module)

if not failed:
    print('🎉 ALL MODULES IMPORT SUCCESSFULLY!')
else:
    print(f'❌ Failed modules: {failed}')
    sys.exit(1)
"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🚀 TESTING SYSTEM STARTUP"
    echo "=========================="
    
    # Create a simple test script
    cat > test_startup.py << 'EOF'
#!/usr/bin/env python3
import time
import sys

def test_system():
    try:
        print("🧪 Testing system startup...")
        
        # Import all modules
        import config
        import signal_engine
        import entropy_meter
        import laggard_sniper
        import relief_trap
        import confidence_scoring
        print("✅ All modules imported")
        
        # Start signal feed
        signal_engine.feed.start_feed()
        print("✅ Signal feed started")
        
        # Wait for initialization
        time.sleep(3)
        
        # Test signal generation
        shared_data = {
            "timestamp": time.time(),
            "mode": "dry",
            "iteration": 1,
            "gpu_available": False
        }
        
        signal = signal_engine.generate_signal(shared_data)
        confidence = signal.get('confidence', 0)
        print(f"✅ Signal generated: confidence={confidence:.3f}")
        
        if confidence > 0:
            print("🎉 SYSTEM WORKING PERFECTLY!")
        else:
            print("⚠️ System working but no high-confidence signals yet")
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_system():
        print("\n🎉 SUCCESS! System is ready to run")
        print("✅ You can now run: python3 main.py --mode=dry")
        print("✅ Or run: ./init_pipeline.sh dry")
    else:
        print("\n❌ System still has issues")
        sys.exit(1)
EOF

    chmod +x test_startup.py
    python3 test_startup.py
    
    if [[ $? -eq 0 ]]; then
        echo ""
        echo "🎉 CUPY IMPORT ISSUES FIXED!"
        echo "============================"
        echo "✅ All cupy imports replaced with cupy_fallback"
        echo "✅ All modules import successfully"
        echo "✅ System startup test passed"
        echo ""
        echo "🚀 READY TO RUN:"
        echo "• python3 main.py --mode=dry"
        echo "• ./init_pipeline.sh dry"
        echo "• python3 test_startup.py"
        echo ""
        echo "📦 Backup created: $BACKUP_DIR"
    else
        echo "❌ System startup test failed"
    fi
else
    echo ""
    echo "❌ IMPORT ISSUES STILL EXIST"
    echo "============================"
    echo "Check the error messages above"
    echo "Backup available: $BACKUP_DIR"
fi

echo ""
echo "🔧 ADDITIONAL DIAGNOSTICS"
echo "========================="
echo "Checking for any remaining cupy imports:"
grep -r "import cupy" *.py 2>/dev/null || echo "✅ No more cupy imports found"

echo ""
echo "Current imports in signal_engine.py:"
head -15 signal_engine.py | grep import