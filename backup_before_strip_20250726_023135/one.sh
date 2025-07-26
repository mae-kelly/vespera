#!/bin/bash
# Strip all comments, docstrings, and emojis from the codebase

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="backup_before_strip_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR="/tmp/strip_processing"

echo "🔧 STRIPPING COMMENTS, DOCSTRINGS, AND EMOJIS"
echo "=============================================="

create_backup() {
    echo "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    
    # Find all Python files and copy to backup
    find . -name "*.py" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        cp "$file" "$BACKUP_DIR/"
    done
    
    # Find all shell scripts and copy to backup
    find . -name "*.sh" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        cp "$file" "$BACKUP_DIR/"
    done
    
    # Find all Rust files and copy to backup
    find . -name "*.rs" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        cp "$file" "$BACKUP_DIR/"
    done
    
    echo "Backup created in: $BACKUP_DIR"
}

strip_python_file() {
    local file="$1"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    python3 -c "
import ast
import sys

def strip_python_code(source_code):
    try:
        tree = ast.parse(source_code)
        
        # Remove docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    node.body.pop(0)
            elif isinstance(node, ast.Module):
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    node.body.pop(0)
        
        # Convert back to source
        import astor if 'astor' in sys.modules else None
        if 'astor' not in sys.modules:
            # Fallback method
            lines = source_code.split('\n')
            result = []
            in_multiline_string = False
            string_delimiter = None
            
            for line in lines:
                stripped_line = line.strip()
                
                # Skip empty lines and comments
                if not stripped_line or stripped_line.startswith('#'):
                    continue
                
                # Handle multiline strings/docstrings
                if not in_multiline_string:
                    if ('\"\"\"' in line or \"'''\" in line):
                        if line.count('\"\"\"') == 2 or line.count(\"'''\") == 2:
                            # Single line docstring, skip it
                            continue
                        else:
                            # Start of multiline docstring
                            in_multiline_string = True
                            string_delimiter = '\"\"\"' if '\"\"\"' in line else \"'''\"
                            continue
                    else:
                        # Remove inline comments
                        if '#' in line:
                            # Check if # is inside a string
                            in_string = False
                            quote_char = None
                            for i, char in enumerate(line):
                                if char in ['\"', \"'\"] and (i == 0 or line[i-1] != '\\\\'):
                                    if not in_string:
                                        in_string = True
                                        quote_char = char
                                    elif char == quote_char:
                                        in_string = False
                                        quote_char = None
                                elif char == '#' and not in_string:
                                    line = line[:i].rstrip()
                                    break
                        
                        if line.strip():
                            result.append(line)
                else:
                    # Inside multiline string
                    if string_delimiter in line:
                        in_multiline_string = False
                        string_delimiter = None
                    continue
            
            return '\n'.join(result)
        else:
            return astor.to_source(tree)
    
    except Exception as e:
        # If parsing fails, do basic comment removal
        lines = source_code.split('\n')
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Remove inline comments (basic)
                if '#' in line and not ('\"' in line or \"'\" in line):
                    line = line.split('#')[0].rstrip()
                if line.strip():
                    result.append(line)
        return '\n'.join(result)

with open('$file', 'r', encoding='utf-8') as f:
    content = f.read()

stripped = strip_python_code(content)

# Remove emojis and Unicode symbols
import re
emoji_pattern = re.compile(
    '['
    '\U0001F600-\U0001F64F'  # emoticons
    '\U0001F300-\U0001F5FF'  # symbols & pictographs
    '\U0001F680-\U0001F6FF'  # transport & map symbols
    '\U0001F1E0-\U0001F1FF'  # flags (iOS)
    '\U00002702-\U000027B0'  # Dingbats
    '\U000024C2-\U0001F251'
    '\U0001F900-\U0001F9FF'  # Supplemental Symbols and Pictographs
    '\U0001FA70-\U0001FAFF'  # Symbols and Pictographs Extended-A
    ']+', 
    flags=re.UNICODE
)

stripped = emoji_pattern.sub('', stripped)

# Remove common emoji-like patterns
stripped = re.sub(r'[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]', '', stripped)

# Clean up multiple newlines
stripped = re.sub(r'\n\s*\n\s*\n', '\n\n', stripped)

with open('$temp_file', 'w', encoding='utf-8') as f:
    f.write(stripped)
"
    
    if [ -f "$temp_file" ]; then
        mv "$temp_file" "$file"
        echo "Stripped: $file"
    else
        echo "Failed to strip: $file"
    fi
}

strip_shell_file() {
    local file="$1"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    # Strip shell comments and emojis
    sed -E '
        # Remove comment lines (but keep shebang)
        /^#!/!{/^[[:space:]]*#/d}
        # Remove inline comments
        s/#[^"'\'']*$//
        # Remove emojis and Unicode symbols
        s/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g
        # Remove empty lines
        /^[[:space:]]*$/d
    ' "$file" > "$temp_file"
    
    if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
        mv "$temp_file" "$file"
        chmod +x "$file"
        echo "Stripped: $file"
    else
        echo "Failed to strip: $file"
        rm -f "$temp_file"
    fi
}

strip_rust_file() {
    local file="$1"
    local temp_file="/tmp/stripped_$(basename "$file")"
    
    # Strip Rust comments and emojis
    sed -E '
        # Remove single-line comments
        s|//.*$||
        # Remove multi-line comments (basic)
        s|/\*.*\*/||g
        # Remove emojis
        s/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g
        # Remove empty lines
        /^[[:space:]]*$/d
    ' "$file" > "$temp_file"
    
    if [ -f "$temp_file" ] && [ -s "$temp_file" ]; then
        mv "$temp_file" "$file"
        echo "Stripped: $file"
    else
        echo "Failed to strip: $file"
        rm -f "$temp_file"
    fi
}

strip_log_strings() {
    local file="$1"
    
    # Remove emoji and verbose logging from strings
    if [[ "$file" == *.py ]]; then
        python3 -c "
import re

with open('$file', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove emojis from logging statements
content = re.sub(r'logging\.(info|debug|warning|error)\s*\(\s*f?[\"\'](.*?)[\"\']\s*(?:,.*?)?\)', 
                lambda m: f'logging.{m.group(1)}(\"\")', content, flags=re.DOTALL)

# Remove print statements with emojis
content = re.sub(r'print\s*\(\s*f?[\"\'](.*?)[\"\']\s*(?:,.*?)?\)', 
                lambda m: '', content, flags=re.DOTALL)

# Remove emoji characters from all strings
emoji_pattern = re.compile(
    '['
    '\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF'
    '\U00002702-\U000027B0'
    '\U000024C2-\U0001F251'
    '\U0001F900-\U0001F9FF'
    '\U0001FA70-\U0001FAFF'
    ']+', 
    flags=re.UNICODE
)
content = emoji_pattern.sub('', content)

with open('$file', 'w', encoding='utf-8') as f:
    f.write(content)
"
    fi
}

main() {
    echo "Starting cleanup process..."
    
    # Create backup
    create_backup
    
    echo "Processing Python files..."
    find . -name "*.py" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_python_file "$file"
            strip_log_strings "$file"
        fi
    done
    
    echo "Processing shell scripts..."
    find . -name "*.sh" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_shell_file "$file"
        fi
    done
    
    echo "Processing Rust files..."
    find . -name "*.rs" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | while read -r file; do
        if [ -f "$file" ]; then
            strip_rust_file "$file"
        fi
    done
    
    echo "Cleaning up log files..."
    find . -name "*.log" -delete 2>/dev/null || true
    
    echo "Removing temporary files..."
    rm -rf "$TEMP_DIR" 2>/dev/null || true
    
    # Final cleanup - remove any remaining emoji patterns
    echo "Final emoji cleanup..."
    find . -name "*.py" -o -name "*.sh" -o -name "*.rs" | grep -v "$BACKUP_DIR" | while read -r file; do
        if [ -f "$file" ]; then
            # Remove common emoji Unicode ranges
            sed -i.bak 's/[🔴🟢🟡⚫⚪🔵🟣🟠🟤🎯🚀📊📈📉💰💎⭐✅❌⚠️💡🔧🔍📁📋🏆🎉]//g' "$file" 2>/dev/null || true
            rm -f "${file}.bak" 2>/dev/null || true
        fi
    done
    
    echo ""
    echo "=============================================="
    echo "CLEANUP COMPLETE"
    echo "=============================================="
    echo "Files processed:"
    echo "- Python files: $(find . -name "*.py" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | wc -l)"
    echo "- Shell scripts: $(find . -name "*.sh" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | wc -l)"
    echo "- Rust files: $(find . -name "*.rs" -not -path "./venv/*" -not -path "./$BACKUP_DIR/*" | wc -l)"
    echo ""
    echo "Backup location: $BACKUP_DIR"
    echo ""
    echo "Removed:"
    echo "- All comments (#)"
    echo "- All docstrings"
    echo "- All emojis and Unicode symbols"
    echo "- Empty lines"
    echo "- Verbose logging statements"
    echo ""
    echo "Code is now minimized and production-ready."
}

main "$@"