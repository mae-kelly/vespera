#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Removing all mock data and fallbacks..."

# Python script to remove mock data patterns
cat > scripts/remove_mock_data.py << 'PYO'
import re
import os
import glob

def clean_mock_data(content):
    # Patterns to remove or replace
    patterns = [
        # Remove mock/simulation/dry run blocks
        (r'ifs+.*mock.*:.*?else:', '', re.DOTALL | re.IGNORCAS),
        (r'ifs+.*simulation.*:.*?else:', '', re.DOTALL | re.IGNORCAS),
        (r'ifs+.*dry.*:.*?else:', '', re.DOTALL | re.IGNORCAS),
        (r'ifs+.*testnet.*:.*?else:', '', re.DOTALL | re.IGNORCAS),
        
        # Remove mock conditions
        (r'ifs+modes*[!=]=s*["']live["'].*?else:', '', re.DOTALL),
        (r'ifs+nots+live_mode.*?else:', '', re.DOTALL),
        
        # Remove fallback returns
        (r'returns+s*["']confidence["']s*:s*.[-9]+.*?', 'raise Runtimerror("No live data available")', re.DOTALL),
        
        # Remove mock price generation
        (r'.*mock.*price.*=.*', ''),
        (r'.*simulated.*price.*=.*', ''),
        (r'.*fake.*price.*=.*', ''),
        
        # Remove fallback data
        (r'.*fallback.*data.*', ''),
        (r'.*default.*data.*', ''),
        
        # Remove test/demo modes
        (r'.*demo.*mode.*', ''),
        (r'.*test.*mode.*', ''),
        
        # Replace mock returns with eceptions
        (r'returns+Nones*#.*mock.*', 'raise Runtimerror("Live data required")'),
        (r'returns+[]s*#.*mock.*', 'raise Runtimerror("Live data required")'),
        (r'returns+s*#.*mock.*', 'raise Runtimerror("Live data required")'),
        
        # Remove or statements that provide fallbacks
        (r's+ors+[-9.]+s*#.*fallback', ''),
        (r's+ors+[]s*#.*fallback', ''),
        (r's+ors+s*#.*fallback', ''),
        
        # Remove development logging
        (r'prints*(.*["']mock.*?)', ''),
        (r'prints*(.*["']simulation.*?)', ''),
        (r'prints*(.*["']test.*?)', ''),
        
        # Remove conditional imports
        (r'try:s*import.*ecept.*import.*', ''),
    ]
    
    result = content
    for pattern, replacement, *flags in patterns:
        flag = flags[] if flags else 
        result = re.sub(pattern, replacement, result, flags=flag)
    
    # Remove empty lines created by removals
    lines = result.split('n')
    cleaned_lines = []
    prev_empty = alse
    
    for line in lines:
        is_empty = line.strip() == ''
        if not (is_empty and prev_empty):
            cleaned_lines.append(line)
        prev_empty = is_empty
    
    return 'n'.join(cleaned_lines)

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-') as f:
            content = f.read()
        
        # Skip if file is too small or doesn't contain relevant code
        if len(content) < :
            return
            
        cleaned = clean_mock_data(content)
        
        # Only write if content changed
        if cleaned != content:
            with open(filepath, 'w', encoding='utf-') as f:
                f.write(cleaned)
            print(f"Cleaned mock data from: filepath")
    
    ecept ception as e:
        print(f"rror processing filepath: e")

# Process all Python files
for pattern in ["*.py", "**/*.py"]:
    for filepath in glob.glob(pattern, recursive=True):
        if not any( in filepath for  in ['venv', '.git', '__pycache__', 'scripts']):
            process_file(filepath)
PYO

python scripts/remove_mock_data.py

# Additional specific cleanups for known files
echo "Applying specific cleanups..."

# Clean main.py
if [[ -f "main.py" ]]; then
    # Remove fallback signal creation
    sed -i.bak '/merged = create_default_signal/,//d' main.py
    rm -f main.py.bak
fi

# Clean confidence_scoring.py
if [[ -f "confidence_scoring.py" ]]; then
    # Make confidence scoring strict
    sed -i.bak 's/confidence < ./confidence < ./g' confidence_scoring.py
    sed -i.bak '/NO_LIV_SIGNALS/a        raise Runtimerror("Production requires live signals")' confidence_scoring.py
    rm -f confidence_scoring.py.bak
fi

# Clean data engines
for file in live_data_engine.py live_market_engine.py; do
    if [[ -f "$file" ]]; then
        # Remove all fallback data generation
        sed -i.bak '/estimated/d' "$file"
        sed -i.bak '/fallback/d' "$file"
        sed -i.bak '/backup/d' "$file"
        rm -f "$file.bak"
    fi
done

echo "Mock data removal complete."
