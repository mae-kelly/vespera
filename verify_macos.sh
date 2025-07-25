#!/bin/bash

echo "🔍 VERIFYING macOS COMPLIANCE"
echo "============================="

echo "📱 System Information:"
echo "OS: $(uname -s) $(uname -r)"
echo "Arch: $(uname -m)"
echo "Python: $(python3 --version)"

echo -e "\n🧪 Running quick test..."
python3 quick_test.py

echo -e "\n🔬 Running full macOS compliance test..."
python3 test_macos_compliance.py

echo -e "\n📊 Checking file structure..."
critical_files=(
    "main.py"
    "signal_engine.py"
    "config.py"
    "cupy_fallback.py"
    "init_pipeline.sh"
)

for file in "${critical_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo -e "\n✅ macOS verification complete!"
