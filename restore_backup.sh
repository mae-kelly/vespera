#!/bin/bash
echo "🔄 Restoring from backup..."
BACKUP_DIR=$(ls -d backup_* | tail -1)
if [[ -d "$BACKUP_DIR" ]]; then
    for file in "$BACKUP_DIR"/*; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            cp "$file" "$filename"
        fi
    done
    echo "✅ Backup restored from $BACKUP_DIR"
else
    echo "❌ No backup found"
fi
