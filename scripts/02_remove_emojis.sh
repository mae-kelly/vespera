#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Removing all emojis and cleaning code..."

# Create backup
cp -r . "../$(basename $PWD)_backup_$(date +%Y%m%d_%H%M%S)" >/dev/null || true

# Common emoji patterns and their replacements
declare -A MOJI_RPLACMNTS=(
    # Technical/System emojis
    ["🔴"]="[PROD]"
    ["🟢"]="[LIV]"
    ["🔵"]="[INO]"
    ["🟡"]="[WARN]"
    ["🟠"]="[ACKUP]"
    ["⚡"]="[SIGNAL]"
    ["🎯"]="[TARGT]"
    ["📈"]="[PRIC]"
    ["📊"]="[DATA]"
    ["💰"]="[ASST]"
    ["💵"]="[PRIC]"
    ["💼"]="[TRAD]"
    ["📦"]="[SIZ]"
    ["⚙️"]="[SYS]"
    ["🌍"]="[GLOAL]"
    ["✅"]="[OK]"
    ["❌"]="[RROR]"
    ["⚠️"]="[WARN]"
    ["🚨"]="[ALRT]"
    ["ℹ️"]="[INO]"
    ["🧪"]="[TST]"
    ["⏳"]="[WAIT]"
    ["🔍"]="[SARCH]"
    ["🚀"]="[START]"
    ["🎮"]="[CTRL]"
    ["💻"]="[SYS]"
    ["📡"]="[CONN]"
    ["🔗"]="[LINK]"
    ["⭐"]="[STAR]"
    ["🎨"]="[UI]"
    ["🔒"]="[SC]"
    ["🗄️"]="[D]"
    ["📝"]="[LOG]"
    ["🎪"]="[VNT]"
    ["🎭"]="[MASK]"
    ["🎬"]="[RC]"
    ["🎤"]="[MIC]"
    ["🎧"]="[AUDIO]"
    ["🎵"]="[MUSIC]"
    ["🎶"]="[NOT]"
    ["🏆"]="[WIN]"
    ["🥇"]="[IRST]"
    ["🥈"]="[SCOND]"
    ["🥉"]="[THIRD]"
    ["🎖️"]="[MDAL]"
    ["🏅"]="[ADG]"
    # Remove without replacement
    ["✦"]=""
    ["·"]=""
    ["₿"]="TC"
)

# unction to clean file
clean_file() 
    local file="$"
    local temp_file=$(mktemp)
    
    cp "$file" "$temp_file"
    
    # Replace specific emojis with tet equivalents
    for emoji in "$!MOJI_RPLACMNTS[@]"; do
        replacement="$MOJI_RPLACMNTS[$emoji]"
        sed -i.bak "s/$emoji/$replacement/g" "$temp_file" >/dev/null || true
    done
    
    # Remove any remaining emojis using Unicode ranges
    # This covers most emoji ranges in Unicode
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    sed -i.bak - 's/[-]//g' "$temp_file" >/dev/null || true
    
    # Copy cleaned content back
    mv "$temp_file" "$file"
    rm -f "$temp_file.bak" >/dev/null || true


# Clean Python files
find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | while read -r file; do
    echo "Cleaning emojis from: $file"
    clean_file "$file"
done

# Clean Rust files
find src -name "*.rs" >/dev/null | while read -r file; do
    echo "Cleaning emojis from: $file"
    clean_file "$file"
done

# Clean shell scripts
find . -name "*.sh" -not -path "./venv/*" -not -path "./.git/*" | while read -r file; do
    echo "Cleaning emojis from: $file"
    clean_file "$file"
done

echo "moji removal complete."
