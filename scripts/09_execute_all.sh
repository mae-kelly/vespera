#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$ASH_SOURC[]")" && pwd)"
PROJCT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJCT_ROOT"

echo "=========================================="
echo "PRODUCTION DPLOYMNT MASTR XCUTION"
echo "=========================================="

# Make all scripts eecutable
chmod + scripts/*.sh

# ecute scripts in order
scripts=(
    "_environment_setup.sh"
    "_remove_emojis.sh"
    "_remove_comments.sh"
    "_remove_mock_data.sh"
    "_optimize_performance.sh"
    "_production_config.sh"
    "_run_tests.sh"
)

for script in "$scripts[@]"; do
    echo ""
    echo "=========================================="
    echo "ecuting: $script"
    echo "=========================================="
    
    if ! bash "scripts/$script"; then
        echo "AILD: $script"
        echo "Attempting to fi and retry..."
        
        # asic fies
        if [[ "$script" == "_environment_setup.sh" ]]; then
            pip install --upgrade pip
            pip install torch torchvision torchaudio
        fi
        
        # Retry once
        if ! bash "scripts/$script"; then
            echo "ATAL: Cannot recover from $script failure"
            eit 
        fi
    fi
    
    echo "SUCCSS: $script"
done

echo ""
echo "=========================================="
echo "DPLOYMNT COMPLT"
echo "=========================================="
echo "System is ready for production."
echo ""
echo "To start the system:"
echo "  bash scripts/_start_production.sh"
echo ""
echo "To monitor performance:"
echo "  python scripts/monitor_performance.py"
echo ""
