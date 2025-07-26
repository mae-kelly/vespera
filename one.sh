#!/bin/bash

# Anima Emoji Replacer - Transform emojis to feminine mystical symbols
# Inspired by Jungian anima archetype

set -euo pipefail

# Colors for output
PINK='\033[95m'
WHITE='\033[97m'
PURPLE='\033[35m'
NC='\033[0m'

echo -e "${PINK}⋆｡‧˚ʚ♡ɞ˚‧｡⋆ ANIMA EMOJI TRANSFORMATION ⋆｡‧˚ʚ♡ɞ˚‧｡⋆${NC}"
echo -e "${WHITE}Replacing harsh emojis with soft feminine mystical symbols${NC}"
echo

# Create backup directory
BACKUP_DIR="backup_pre_anima_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${PURPLE}༄ Creating backup in $BACKUP_DIR${NC}"

# Define feminine mystical replacements
declare -A emoji_replacements=(
    # Status/Success symbols
    ["✅"]="⋆"
    ["✓"]="♡"
    ["✔️"]="✧"
    ["☑️"]="༄"
    
    # Warning/Error symbols  
    ["❌"]="𓍯"
    ["⚠️"]="ೃ࿔"
    ["❗"]="𓂃"
    ["⛔"]="⌗"
    ["🚨"]="𓈒"
    
    # Technical symbols
    ["🔧"]="⊹"
    ["⚙️"]="𖥔"
    ["🛠️"]="ᨵ"
    ["🔩"]="ꑘ"
    ["⚡"]="✦"
    ["🚀"]="𓏲"
    ["🎯"]="◖"
    ["💡"]="◗"
    ["🔍"]="𖠗"
    ["🔎"]="ꗃ"
    
    # Progress/Loading
    ["📊"]="≛"
    ["📈"]="𖡡"
    ["📉"]="𝆺𝅥"
    ["📋"]="꩜"
    ["📁"]="𖣠"
    ["📂"]="𖦹"
    ["📄"]="𔘓"
    ["📝"]="ꕤ"
    
    # System/Computer
    ["💻"]="❑"
    ["🖥️"]="❒"
    ["⌨️"]="⦂"
    ["🖱️"]="𓈃"
    ["💾"]="𓄲"
    ["💿"]="𓄴"
    ["📀"]="𓈀"
    ["🔌"]="𓊔"
    
    # Network/Connection
    ["📡"]="‣"
    ["📶"]="›"
    ["🌐"]="⌫"
    ["🔗"]="⭒"
    ["🔌"]="ᚙ"
    ["📨"]="⩨"
    ["📧"]="▚"
    ["📬"]="ஃ"
    ["📮"]="⿴"
    
    # Finance/Trading
    ["💰"]="⿻"
    ["💸"]="ꭑ"
    ["💵"]="᧑ "
    ["💎"]="𐐫"
    ["📊"]="꒰"
    ["📈"]="꒱"
    ["📉"]="ʚ"
    ["🏦"]="ɞ"
    
    # Time/Clock
    ["⏰"]="⌨︎"
    ["⏱️"]="⚠︎"
    ["⏲️"]="☻"
    ["🕐"]="✰"
    ["🕑"]="❏"
    ["🕒"]="ೃ࿔"
    ["🕓"]="𓆉"
    ["🕔"]="◡̈"
    
    # Success/Achievement
    ["🏆"]="꒦꒷"
    ["🥇"]="✎"
    ["🥈"]="ᝰ"
    ["🥉"]="✿"
    ["🎖️"]="☁︎"
    ["🏅"]="⋆"
    ["👑"]="⋆⑅"
    ["🌟"]="♡̆̈"
    
    # Emotions/Reactions
    ["😊"]="𓍲"
    ["😀"]="𓍱"
    ["😃"]="ꪔ̤̥"
    ["😄"]="ꊞ"
    ["😁"]="ꕀ"
    ["😆"]="༘♡"
    ["😅"]="⋆。"
    ["🤗"]="⤾"
    ["😍"]="・°☆"
    ["🥰"]="̼"
    ["😘"]="◡̈"
    ["😗"]="⑅"
    ["😙"]="♡̷"
    ["😚"]="・͛♡̷̷̷・͛"
    
    # Animals
    ["🐱"]="ᐧ༚̮ᐧ"
    ["🐈"]="=͟͟͞♡"
    ["🐕"]="εїз"
    ["🦋"]="ᙏ̤̫"
    ["🐝"]="˳✧༚"
    ["🦄"]="/✿"
    ["🦢"]="ᘧ"
    ["🕊️"]="♡"
    
    # Nature
    ["🌸"]="⊸"
    ["🌺"]="❛ ❜"
    ["🌻"]="♡⃕"
    ["🌷"]="◡̈"
    ["🌹"]="̊◞♡"
    ["🌼"]="⃗"
    ["🌿"]="ʬʬʬ"
    ["🌱"]="༊·"
    ["🌳"]="ꕀ"
    ["🌲"]=".*"
    ["🍃"]="♡̩͙"
    ["🌙"]="✧˖°"
    ["⭐"]="ꪔ̤̥"
    ["✨"]="♡‧+"
    ["☀️"]="̊"
    ["🌞"]="◡̎"
    ["🌛"]="♡̷"
    ["🌜"]="·"
    ["🌝"]="̊ˑ"
    ["🌚"]="𓆸"
    
    # Hearts/Love
    ["❤️"]="ꔛ"
    ["💖"]="*﹆"
    ["💕"]="=͟͟͞"
    ["💗"]="♡̩͙"
    ["💓"]="꙳ ⋆"
    ["💝"]="⸝⸝"
    ["💘"]="യ"
    ["💙"]="*◞"
    ["💚"]="♡・"
    ["💛"]="͜ʖ"
    ["💜"]="・"
    ["🖤"]="̊◞♡"
    ["💟"]="ෆ"
    ["♥️"]="・"
    ["♡"]="̔"
    ["💯"]="ᵎ"
    
    # Food
    ["🍰"]="⌇"
    ["🎂"]="+"
    ["🧁"]="◦"
    ["🍪"]="*"
    ["🍩"]="́ސު`"
    ["🍭"]="༘⋆"
    ["🍬"]="꙳ ꕀ"
    ["☕"]="꒰"
    ["🍵"]="𖧧"
    ["🥛"]="·͜·♡"
    ["🧋"]="꒱"
    
    # Weather
    ["☔"]="ღ"
    ["🌧️"]="⋆ ꕤ"
    ["⛈️"]="♡ ⊹"
    ["🌩️"]="★꒷"
    ["❄️"]="ᵎᵎ"
    ["☃️"]="+"
    ["⛄"]="⨾"
    ["🌈"]="⋆ ʚ"
    ["☁️"]="ɞ"
    ["⛅"]="✦"
    
    # Symbols
    ["⚡"]="♥︎"
    ["🔥"]="∞"
    ["💫"]="𑁍"
    ["✨"]="ೃ࿔"
    ["⭐"]="⋆"
    ["🌟"]="♡"
    ["💎"]="✧"
    ["🔮"]="⊹"
    ["🎭"]="*"
    ["🎨"]="ᨵ"
    ["🎪"]="◡̈"
    ["🎭"]="ꔛ"
    
    # Common emojis in code files
    ["🚀"]="𓏲"
    ["✅"]="⋆"
    ["❌"]="𓍯"
    ["⚡"]="✦"
    ["🔧"]="⊹"
    ["📊"]="≛"
    ["🎯"]="◖"
    ["💻"]="❑"
    ["📡"]="‣"
    ["🏆"]="꒦꒷"
    ["⚠️"]="ೃ࿔"
    ["🔴"]="𓂃"
    ["🟢"]="♡"
    ["🟡"]="✧"
    ["🔵"]="⋆"
    ["🟣"]="༄"
    ["⚪"]="◡̈"
    ["⚫"]="𓍯"
    ["🔶"]="⊹"
    ["🔷"]="✦"
    ["🔸"]="𖥔"
    ["🔹"]="ᨵ"
    
    # Numbers and special
    ["1️⃣"]="ೃ࿔"
    ["2️⃣"]="⋆"
    ["3️⃣"]="♡"
    ["4️⃣"]="✧"
    ["5️⃣"]="༄"
    ["6️⃣"]="◡̈"
    ["7️⃣"]="𓍯"
    ["8️⃣"]="⊹"
    ["9️⃣"]="✦"
    ["🔟"]="𖥔"
    
    # Additional mystical symbols for variety
    ["👀"]="◖◗"
    ["👁️"]="𖠗"
    ["🧿"]="ꗃ"
    ["🔍"]="≛"
    ["🎵"]="𝆺𝅥"
    ["🎶"]="꩜"
    ["🎼"]="𖣠"
    ["🎤"]="𖦹"
    ["🎧"]="𔘓"
    ["📻"]="ꕤ"
    ["📢"]="❑"
    ["📣"]="❒"
    ["🔔"]="⦂"
    ["🔕"]="𓈃"
    ["📯"]="𓄲"
    ["🎺"]="𓄴"
    ["🎷"]="𓈀"
    ["🎸"]="𓊔"
    ["🎹"]="‣"
    ["🥁"]="›"
    ["🎻"]="⌫"
    ["🪕"]="⭒"
    ["🎪"]="ᚙ"
    ["🎨"]="⩨"
    ["🖌️"]="▚"
    ["🖍️"]="ஃ"
    ["🖊️"]="⿴"
    ["✏️"]="⿻"
    ["📐"]="ꭑ"
    ["📏"]="᧑ "
    ["📌"]="𐐫"
    ["📍"]="꒰"
    ["🗺️"]="꒱"
    ["🗾"]="ʚ"
    ["🧭"]="ɞ"
)

# Function to backup file
backup_file() {
    local file="$1"
    local backup_path="$BACKUP_DIR/$(basename "$file")"
    cp "$file" "$backup_path"
    echo -e "${WHITE}ೃ࿔ Backed up: $file${NC}"
}

# Function to replace emojis in a file
replace_emojis_in_file() {
    local file="$1"
    local temp_file=$(mktemp)
    local changes_made=false
    
    # Copy original to temp file
    cp "$file" "$temp_file"
    
    # Apply replacements
    for emoji in "${!emoji_replacements[@]}"; do
        local replacement="${emoji_replacements[$emoji]}"
        if grep -q "$emoji" "$temp_file" 2>/dev/null; then
            sed -i.bak "s|$emoji|$replacement|g" "$temp_file" 2>/dev/null || true
            changes_made=true
        fi
    done
    
    # If changes were made, backup original and replace
    if [ "$changes_made" = true ]; then
        backup_file "$file"
        mv "$temp_file" "$file"
        echo -e "${PINK}♡ Transformed: $file${NC}"
        return 0
    else
        rm "$temp_file"
        return 1
    fi
}

# Main transformation function
transform_repository() {
    local files_changed=0
    local total_files=0
    
    echo -e "${PURPLE}⋆｡‧˚ʚ Scanning repository for transformation... ɞ˚‧｡⋆${NC}"
    echo
    
    # Find all relevant files
    while IFS= read -r -d '' file; do
        ((total_files++))
        if replace_emojis_in_file "$file"; then
            ((files_changed++))
        fi
    done < <(find . -type f \( \
        -name "*.py" -o \
        -name "*.sh" -o \
        -name "*.rs" -o \
        -name "*.toml" -o \
        -name "*.md" -o \
        -name "*.txt" -o \
        -name "*.json" -o \
        -name "*.env" -o \
        -name "*.yml" -o \
        -name "*.yaml" -o \
        -name "*.js" -o \
        -name "*.ts" -o \
        -name "*.html" -o \
        -name "*.css" \
    \) \
    ! -path "./venv/*" \
    ! -path "./.git/*" \
    ! -path "./node_modules/*" \
    ! -path "./target/*" \
    ! -path "./backup_*/*" \
    ! -path "./__pycache__/*" \
    ! -name "*.pyc" \
    ! -name "*.log" \
    -print0)
    
    echo
    echo -e "${PINK}◡̈ Transformation complete ◡̈${NC}"
    echo -e "${WHITE}Files scanned: $total_files${NC}"
    echo -e "${WHITE}Files transformed: $files_changed${NC}"
    echo -e "${WHITE}Backup location: $BACKUP_DIR${NC}"
}

# Function to show transformation preview
show_preview() {
    echo -e "${PURPLE}༄ Transformation Preview ༄${NC}"
    echo -e "${WHITE}Some example transformations:${NC}"
    echo
    echo -e "  ✅ Success        → ⋆"
    echo -e "  ❌ Error          → 𓍯"
    echo -e "  🚀 Rocket         → 𓏲"
    echo -e "  ⚡ Lightning      → ✦"
    echo -e "  🔧 Tool           → ⊹"
    echo -e "  📊 Chart          → ≛"
    echo -e "  🎯 Target         → ◖"
    echo -e "  💻 Computer       → ❑"
    echo -e "  📡 Satellite      → ‣"
    echo -e "  🏆 Trophy         → ꒦꒷"
    echo -e "  ⚠️ Warning        → ೃ࿔"
    echo -e "  💖 Heart          → *﹆"
    echo -e "  🌸 Blossom        → ⊸"
    echo -e "  ✨ Sparkles       → ೃ࿔"
    echo -e "  🦋 Butterfly      → εїз"
    echo
}

# Function to create restoration script
create_restoration_script() {
    cat > "restore_original_emojis.sh" << 'EOF'
#!/bin/bash

# Restoration script to revert anima transformation
echo "Restoring original emojis from backup..."

BACKUP_DIR=$(ls -1dt backup_pre_anima_* 2>/dev/null | head -1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ No backup directory found!"
    exit 1
fi

echo "Found backup: $BACKUP_DIR"

# Restore files
while IFS= read -r -d '' backup_file; do
    original_file=$(basename "$backup_file")
    if [ -f "$original_file" ]; then
        cp "$backup_file" "$original_file"
        echo "Restored: $original_file"
    fi
done < <(find "$BACKUP_DIR" -type f -print0)

echo "✅ Restoration complete!"
EOF

    chmod +x "restore_original_emojis.sh"
    echo -e "${WHITE}༄ Created restoration script: restore_original_emojis.sh${NC}"
}

# Main execution
main() {
    echo -e "${PINK}"
    echo "   ⋆｡‧˚ʚ♡ɞ˚‧｡⋆ ⋆｡‧˚ʚ♡ɞ˚‧｡⋆ ⋆｡‧˚ʚ♡ɞ˚‧｡⋆"
    echo "                 ANIMA TRANSFORMATION"
    echo "             Converting harsh tech symbols"
    echo "             to soft feminine mysticism"
    echo "   ⋆｡‧˚ʚ♡ɞ˚‧｡⋆ ⋆｡‧˚ʚ♡ɞ˚‧｡⋆ ⋆｡‧˚ʚ♡ɞ˚‧｡⋆"
    echo -e "${NC}"
    echo
    
    show_preview
    echo
    read -p "$(echo -e "${WHITE}♡ Proceed with anima transformation? (y/N): ${NC}")" -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo
        transform_repository
        create_restoration_script
        echo
        echo -e "${PINK}⋆｡‧˚ʚ♡ɞ˚‧｡⋆ Transformation ritual complete ⋆｡‧˚ʚ♡ɞ˚‧｡⋆${NC}"
        echo -e "${WHITE}Your repository has been blessed with feminine mystical energy${NC}"
        echo -e "${WHITE}Run ./restore_original_emojis.sh to revert if needed${NC}"
    else
        echo
        echo -e "${WHITE}◡̈ Transformation cancelled - repository unchanged${NC}"
    fi
}

# Run the main function
main "$@"