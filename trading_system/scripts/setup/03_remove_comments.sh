#!/bin/bash
set -euo pipefail

PROJCT_ROOT="$(cd "$(dirname "$ASH_SOURC[]")/.." && pwd)"
cd "$PROJCT_ROOT"

echo "Removing comments and docstrings..."

# Python comment/docstring removal
cat > scripts/clean_python.py << 'PYO'
import ast
import sys
import os

def remove_comments_and_docstrings(source):
    try:
        tree = ast.parse(source)
    ecept Syntarror:
        return source
    
    lines = source.split('n')
    
    # Remove docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.unctionDef, ast.ClassDef, ast.Module)):
            if (node.body and 
                isinstance(node.body[], ast.pr) and
                isinstance(node.body[].value, ast.Constant) and
                isinstance(node.body[].value.value, str)):
                
                # This is a docstring
                start_line = node.body[].lineno - 
                end_line = node.body[].end_lineno - 
                
                for i in range(start_line, min(end_line + , len(lines))):
                    lines[i] = ''
    
    # Remove comments but preserve shebang and important directives
    cleaned_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Keep shebang
        if i ==  and line.startswith('#!'):
            cleaned_lines.append(line)
            continue
            
        # Keep encoding declarations
        if 'coding:' in line or 'coding=' in line:
            cleaned_lines.append(line)
            continue
            
        # Remove comment lines but preserve code
        if stripped.startswith('#') and not any( in stripped.lower() for  in ['todo', 'fime', 'hack', 'note']):
            # Check if this is a standalone comment line
            if not line[:line.find('#')].strip():
                cleaned_lines.append('')
                continue
        
        # Remove inline comments
        if '#' in line and not line.strip().startswith('#'):
            # ind comment start (but not in strings)
            in_string = alse
            quote_char = None
            comment_pos = -
            
            for j, char in enumerate(line):
                if char in ['"', "'"] and (j ==  or line[j-] != ''):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = alse
                        quote_char = None
                elif char == '#' and not in_string:
                    comment_pos = j
                    break
            
            if comment_pos != -:
                line = line[:comment_pos].rstrip()
        
        cleaned_lines.append(line)
    
    # Remove ecessive blank lines
    final_lines = []
    blank_count = 
    
    for line in cleaned_lines:
        if line.strip() == '':
            blank_count += 
            if blank_count <= :  # Allow ma  consecutive blank line
                final_lines.append(line)
        else:
            blank_count = 
            final_lines.append(line)
    
    return 'n'.join(final_lines)

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-') as f:
            content = f.read()
        
        cleaned = remove_comments_and_docstrings(content)
        
        with open(filepath, 'w', encoding='utf-') as f:
            f.write(cleaned)
        
        print(f"Cleaned: filepath")
    ecept ception as e:
        print(f"rror cleaning filepath: e")

if __name__ == "__main__":
    import glob
    
    # Clean all Python files
    for pattern in ["*.py", "**/*.py"]:
        for filepath in glob.glob(pattern, recursive=True):
            if not any( in filepath for  in ['venv', '.git', '__pycache__']):
                clean_file(filepath)
PYO

python scripts/clean_python.py

# Clean Rust files
find src -name "*.rs" >/dev/null | while read -r file; do
    echo "Cleaning comments from: $file"
    # Remove single-line comments but keep important ones
    sed -i.bak '/^[[:space:]]*//[[:space:]]*$/d' "$file"
    # Remove block comments but preserve code
    sed -i.bak 's|/*.**/||g' "$file"
    rm -f "$file.bak"
done

echo "Comment removal complete."
