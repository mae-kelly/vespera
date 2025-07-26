#!/bin/bash
# Strip all comments, docstrings, and emojis from the codebase

set -e

RD='[;m'
GRN='[;m'
YLLOW='[;m'
NC='[m'

ACKUP_DIR="backup_before_strip_$(date +%Y%m%d_%H%M%S)"
TMP_DIR="/tmp/strip_processing"

echo "🔧 STRIPPING COMMNTS, DOCSTRINGS, AND MOJIS"
echo "=============================================="

create_backup() 
    echo "Creating backup..."
    mkdir -p "$ACKUP_DIR"
    
    # ind all Python files and copy to backup
    find . -name "*.py" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        cp "$file" "$ACKUP_DIR/"
    done
    
    # ind all shell scripts and copy to backup
    find . -name "*.sh" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        cp "$file" "$ACKUP_DIR/"
    done
    
    # ind all Rust files and copy to backup
    find . -name "*.rs" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        cp "$file" "$ACKUP_DIR/"
    done
    
    echo "ackup created in: $ACKUP_DIR"


strip_python_file() 
    local file="$"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    python -c "
import ast
import sys

def strip_python_code(source_code):
    try:
        tree = ast.parse(source_code)
        
        # Remove docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.unctionDef, ast.ClassDef, ast.AsyncunctionDef)):
                if (node.body and 
                    isinstance(node.body[], ast.pr) and 
                    isinstance(node.body[].value, ast.Constant) and 
                    isinstance(node.body[].value.value, str)):
                    node.body.pop()
            elif isinstance(node, ast.Module):
                if (node.body and 
                    isinstance(node.body[], ast.pr) and 
                    isinstance(node.body[].value, ast.Constant) and 
                    isinstance(node.body[].value.value, str)):
                    node.body.pop()
        
        # Convert back to source
        import astor if 'astor' in sys.modules else None
        if 'astor' not in sys.modules:
            # allback method
            lines = source_code.split('n')
            result = []
            in_multiline_string = alse
            string_delimiter = None
            
            for line in lines:
                stripped_line = line.strip()
                
                # Skip empty lines and comments
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                
                # Handle multiline strings/docstrings
                if not in_multiline_string:
                    if ('"""' in line or "'''" in line):
                        if line.count('"""') ==  or line.count("'''") == :
                            # Single line docstring, skip it
                            continue
                        else:
                            # Start of multiline docstring
                            in_multiline_string = True
                            string_delimiter = '"""' if '"""' in line else "'''"
                            continue
                    else:
                        # Remove inline comments
                        if '#' in line:
                            # Check if # is inside a string
                            in_string = alse
                            quote_char = None
                            for i, char in enumerate(line):
                                if char in ['"', "'"] and (i ==  or line[i-] != ''):
                                    if not in_string:
                                        in_string = True
                                        quote_char = char
                                    elif char == quote_char:
                                        in_string = alse
                                        quote_char = None
                                elif char == '#' and not in_string:
                                    line = line[:i].rstrip()
                                    break
                        
                        if line.strip():
                            result.append(line)
                else:
                    # Inside multiline string
                    if string_delimiter in line:
                        in_multiline_string = alse
                        string_delimiter = None
                    continue
            
            return 'n'.join(result)
        else:
            return astor.to_source(tree)
    
    ecept ception as e:
        # If parsing fails, do basic comment removal
        lines = source_code.split('n')
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Remove inline comments (basic)
                if '#' in line and not ('"' in line or "'" in line):
                    line = line.split('#')[].rstrip()
                if line.strip():
                    result.append(line)
        return 'n'.join(result)

with open('$file', 'r', encoding='utf-') as f:
    content = f.read()

stripped = strip_python_code(content)

# Remove emojis and Unicode symbols
import re
emoji_pattern = re.compile(
    '['
    'U-U'  # emoticons
    'U-U'  # symbols & pictographs
    'U-U'  # transport & map symbols
    'U-U'  # flags (iOS)
    'U-U'  # Dingbats
    'UC-U'
    'U9-U9'  # Supplemental Symbols and Pictographs
    'UA-UA'  # Symbols and Pictographs tended-A
    ']+', 
    flags=re.UNICOD
)

stripped = emoji_pattern.sub('', stripped)

# Remove common emoji-like patterns
stripped = re.sub(r'[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]', '', stripped)

# Clean up multiple newlines
stripped = re.sub(r'ns*ns*n', 'nn', stripped)

with open('$temp_file', 'w', encoding='utf-') as f:
    f.write(stripped)
"
    
    if [ -f "$temp_file" ]; then
        mv "$temp_file" "$file"
        echo "Stripped: $file"
    else
        echo "ailed to strip: $file"
    fi


strip_shell_file() 
    local file="$"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    # Strip shell comments and emojis
    sed - '
        # Remove comment lines (but keep shebang)
        /^#!/!/^[[:space:]]*#/d
        # Remove inline comments
        s/#[^"''']*$//
        # Remove emojis and Unicode symbols
        s/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g
        # Remove empty lines
        /^[[:space:]]*$/d
    ' "$file" > "$temp_file"
    
    if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
        mv "$temp_file" "$file"
        chmod + "$file"
        echo "Stripped: $file"
    else
        echo "ailed to strip: $file"
        rm -f "$temp_file"
    fi


strip_rust_file() 
    local file="$"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    # Strip Rust comments and emojis
    sed - '
        # Remove single-line comments
        s|//.*$||
        # Remove multi-line comments (basic)
        s|/*.**/||g
        # Remove emojis
        s/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g
        # Remove empty lines
        /^[[:space:]]*$/d
    ' "$file" > "$temp_file"
    
    if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
        mv "$temp_file" "$file"
        echo "Stripped: $file"
    else
        echo "ailed to strip: $file"
        rm -f "$temp_file"
    fi


strip_log_strings() 
    local file="$"
    
    # Remove emoji and verbose logging from strings
    if [[ "$file" == *.py ]]; then
        python -c "
import re

with open('$file', 'r', encoding='utf-') as f:
    content = f.read()

# Remove emojis from logging statements
content = re.sub(r'logging.(info|debug|warning|error)s*(s*f?["'](.*?)["']s*(?:,.*?)?)', 
                lambda m: f'logging.m.group()("")', content, flags=re.DOTALL)

# Remove print statements with emojis
content = re.sub(r'prints*(s*f?["'](.*?)["']s*(?:,.*?)?)', 
                lambda m: '', content, flags=re.DOTALL)

# Remove emoji characters from all strings
emoji_pattern = re.compile(
    '['
    'U-U'
    'U-U'
    'U-U'
    'U-U'
    'U-U'
    'UC-U'
    'U9-U9'
    'UA-UA'
    ']+', 
    flags=re.UNICOD
)
content = emoji_pattern.sub('', content)

with open('$file', 'w', encoding='utf-') as f:
    f.write(content)
"
    fi


main() 
    echo "Starting cleanup process..."
    
    # Create backup
    create_backup
    
    echo "Processing Python files..."
    find . -name "*.py" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_python_file "$file"
            strip_log_strings "$file"
        fi
    done
    
    echo "Processing shell scripts..."
    find . -name "*.sh" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_shell_file "$file"
        fi
    done
    
    echo "Processing Rust files..."
    find . -name "*.rs" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_rust_file "$file"
        fi
    done
    
    echo "Cleaning up log files..."
    find . -name "*.log" -delete >/dev/null || true
    
    echo "Removing temporary files..."
    rm -rf "$TMP_DIR" >/dev/null || true
    
    # inal cleanup - remove any remaining emoji patterns
    echo "inal emoji cleanup..."
    find . -name "*.py" -o -name "*.sh" -o -name "*.rs" | grep -v "$ACKUP_DIR" | while read -r file; do
        if [ -f "$file" ]; then
            # Remove common emoji Unicode ranges
            sed -i.bak 's/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g' "$file" >/dev/null || true
            rm -f "$file.bak" >/dev/null || true
        fi
    done
    
    echo ""
    echo "=============================================="
    echo "CLANUP COMPLT"
    echo "=============================================="
    echo "iles processed:"
    echo "- Python files: $(find . -name "*.py" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | wc -l)"
    echo "- Shell scripts: $(find . -name "*.sh" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | wc -l)"
    echo "- Rust files: $(find . -name "*.rs" -not -path "./venv/*" -not -path "./$ACKUP_DIR/*" | wc -l)"
    echo ""
    echo "ackup location: $ACKUP_DIR"
    echo ""
    echo "Removed:"
    echo "- All comments (#)"
    echo "- All docstrings"
    echo "- All emojis and Unicode symbols"
    echo "- mpty lines"
    echo "- Verbose logging statements"
    echo ""
    echo "Code is now minimized and production-ready."


main "$@"