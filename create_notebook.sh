#!/bin/bash

echo "🔧 FIXING CUPY IMPORT ISSUES"
echo "============================"
echo "Replacing all 'import cupy' with 'import cupy_fallback as cupy'"

# Create backup
BACKUP_DIR="cupy_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Creating backup in $BACKUP_DIR"

# Backup files that will be modified
for file in *.py; do
    if [[ -f "$file" ]] && grep -q "import cupy" "$file"; then
        cp "$file" "$BACKUP_DIR/"
        echo "📝 Backed up $file"
    fi
done

# Fix all Python files to use cupy_fallback
echo "🔧 Fixing import statements..."

# Files to fix
files_to_fix=(
    "signal_engine.py"
    "entropy_meter.py" 
    "laggard_sniper.py"
    "relief_trap.py"
    "confidence_scoring.py"
    "config.py"
    "main.py"
)

for file in "${files_to_fix[@]}"; do
    if [[ -f "$file" ]]; then
        echo "🔧 Fixing $file..."
        
        # Replace 'import cupy as cp' with 'import cupy_fallback as cp'
        sed -i '' 's/import cupy as cp/import cupy_fallback as cp/g' "$file"
        
        # Replace 'import cupy' with 'import cupy_fallback as cupy'
        sed -i '' 's/^import cupy$/import cupy_fallback as cupy/g' "$file"
        
        echo "✅ Fixed $file"
    else
        echo "⚠️ $file not found"
    fi
done

# Also update any files that might have torch.cuda usage to handle MPS
echo "🔧 Adding MPS support checks..."

# Create a simple device detection function and add it to config.py
cat >> config.py << 'EOF'

# Device detection for Apple Silicon
def get_best_device():
    """Get the best available device (MPS, CUDA, or CPU)"""
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return 'mps'
    elif torch.cuda.is_available():
        return 'cuda'
    else:
        return 'cpu'

DEVICE = get_best_device()
print(f"🖥️ Using device: {DEVICE}")
EOF

# Test the fixes
echo "🧪 Testing the fixes..."
python3 -c "
try:
    import cupy_fallback as cp
    print('✅ CuPy fallback import successful')
    
    # Test basic operations
    test_array = cp.array([1, 2, 3, 4, 5])
    result = cp.sum(test_array)
    print(f'✅ CuPy operations working: sum = {result}')
    
    import config
    print('✅ Config import successful')
    
    # Test signal_engine import
    import signal_engine
    print('✅ Signal engine import successful')
    
    print('🎉 ALL IMPORTS FIXED!')
    
except Exception as e:
    print(f'❌ Still have issues: {e}')
    import traceback
    traceback.print_exc()
"

# Create a simple test to verify everything works
cat > test_fixed_imports.py << 'EOF'
#!/usr/bin/env python3
"""Test that all imports work after the fix"""

import sys

def test_all_imports():
    """Test all critical imports"""
    print("🧪 Testing all imports after fix...")
    
    try:
        # Test cupy fallback
        import cupy_fallback as cp
        test_array = cp.array([1, 2, 3])
        result = cp.sum(test_array)
        print(f"✅ CuPy fallback: {result}")
        
        # Test config
        import config
        print(f"✅ Config: Device = {config.DEVICE}")
        
        # Test signal engine
        import signal_engine
        print("✅ Signal engine imported")
        
        # Test other modules
        import entropy_meter
        import laggard_sniper  
        import relief_trap
        import confidence_scoring
        print("✅ All signal modules imported")
        
        # Test that signal generation works
        signal_engine.feed.start_feed()
        import time
        time.sleep(1)
        
        shared_data = {"timestamp": time.time(), "mode": "dry", "iteration": 1}
        signal = signal_engine.generate_signal(shared_data)
        print(f"✅ Signal generation: confidence = {signal.get('confidence', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_imports()
    if success:
        print("\n🎉 ALL IMPORTS WORKING!")
        print("✅ Ready to run the full system")
    else:
        print("\n❌ Still have import issues")
    
    sys.exit(0 if success else 1)
EOF

chmod +x test_fixed_imports.py

echo ""
echo "🎉 CUPY IMPORT FIXES COMPLETE!"
echo "============================="
echo ""
echo "📋 WHAT WAS FIXED:"
echo "✅ Replaced 'import cupy' with 'import cupy_fallback as cupy'"
echo "✅ Replaced 'import cupy as cp' with 'import cupy_fallback as cp'"
echo "✅ Added MPS device detection"
echo "✅ Created import test script"
echo ""
echo "🧪 TESTING:"
echo "1. Run import test: python3 test_fixed_imports.py"
echo "2. Run quick test: python3 quick_test.py" 
echo "3. Run full verification: ./verify_macos.sh"
echo "4. Start system: ./start_macos.sh"
echo ""
echo "💾 Backup created in: $BACKUP_DIR"
echo ""
echo "🚀 The system should now work on macOS with Apple Silicon!"