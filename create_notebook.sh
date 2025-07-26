#!/bin/bash

# NUCLEAR Mac Cleanup Script - Maximum space recovery
# WARNING: This is extremely aggressive and removes many files
# Run with: chmod +x nuclear_cleanup.sh && ./nuclear_cleanup.sh

echo "☢️  NUCLEAR MAC CLEANUP STARTING..."
echo "This script will aggressively remove files system-wide for maximum space recovery."
echo "Press Ctrl+C within 3 seconds to cancel..."
sleep 3
echo ""

# Function to display file sizes in human readable format
display_size() {
    if [ -d "$1" ] || [ -f "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        echo "0B"
    fi
}

echo "📊 Current disk usage:"
df -h /
echo ""

# 1. Nuclear trash cleanup
echo "☢️ NUCLEAR trash cleanup..."
sudo rm -rf ~/.Trash/* 2>/dev/null
sudo rm -rf /Volumes/*/.Trashes/* 2>/dev/null
sudo rm -rf /private/var/folders/*/T/* 2>/dev/null
echo "   Nuclear trash cleared"
echo ""

# 2. Massive cache cleanup
echo "💣 MASSIVE cache cleanup..."
sudo rm -rf /Library/Caches/* 2>/dev/null
sudo rm -rf /System/Library/Caches/* 2>/dev/null
rm -rf ~/Library/Caches/* 2>/dev/null
sudo rm -rf /var/folders/* 2>/dev/null
echo "   All system caches nuked"
echo ""

# 3. Browser nuclear option
echo "🌐 BROWSER NUCLEAR CLEANUP..."
pkill -f "Google Chrome" 2>/dev/null
pkill -f "Safari" 2>/dev/null
pkill -f "Firefox" 2>/dev/null
sleep 2

# Chrome complete removal
rm -rf ~/Library/Caches/Google 2>/dev/null
rm -rf ~/Library/Application\ Support/Google/Chrome/*/History* 2>/dev/null
rm -rf ~/Library/Application\ Support/Google/Chrome/*/Cache* 2>/dev/null
rm -rf ~/Library/Application\ Support/Google/Chrome/*/Code\ Cache 2>/dev/null
rm -rf ~/Library/Application\ Support/Google/Chrome/*/GPUCache 2>/dev/null
rm -rf ~/Library/Application\ Support/Google/Chrome/*/Session* 2>/dev/null

# Safari complete removal
rm -rf ~/Library/Caches/com.apple.Safari 2>/dev/null
rm -rf ~/Library/Safari/History.db* 2>/dev/null
rm -rf ~/Library/Safari/TopSites.plist 2>/dev/null
rm -rf ~/Library/Safari/CloudHistory.db* 2>/dev/null

# Firefox complete removal
rm -rf ~/Library/Caches/Firefox 2>/dev/null
rm -rf ~/Library/Application\ Support/Firefox/Profiles/*/cache2 2>/dev/null

echo "   All browsers completely cleaned"
echo ""

# 4. Development environment nuclear cleanup
echo "⚙️  DEVELOPMENT NUCLEAR CLEANUP..."

# Find and nuke ALL node_modules directories system-wide
echo "   💥 Nuking ALL node_modules (this may take a while)..."
find /Users -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null &

# Python nuclear cleanup
find /Users -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /Users -name "*.pyc" -type f -delete 2>/dev/null
find /Users -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null
find /Users -name ".tox" -type d -exec rm -rf {} + 2>/dev/null
pip cache purge 2>/dev/null
python3 -m pip cache purge 2>/dev/null

# Virtual environments nuclear option
find /Users -name "venv" -type d -exec rm -rf {} + 2>/dev/null
find /Users -name ".venv" -type d -exec rm -rf {} + 2>/dev/null
find /Users -name "env" -type d -path "*/python*" -exec rm -rf {} + 2>/dev/null

# npm/yarn nuclear cleanup
rm -rf ~/.npm 2>/dev/null
rm -rf ~/.yarn 2>/dev/null
if command -v npm &> /dev/null; then
    npm cache clean --force 2>/dev/null
fi
if command -v yarn &> /dev/null; then
    yarn cache clean --all 2>/dev/null
fi

echo "   Development environments nuked"
echo ""

# 5. Docker nuclear option
if command -v docker &> /dev/null; then
    echo "🐳 DOCKER NUCLEAR CLEANUP..."
    docker system prune -af --volumes 2>/dev/null
    docker builder prune -af 2>/dev/null
    docker volume prune -f 2>/dev/null
    docker network prune -f 2>/dev/null
    echo "   Docker completely nuked"
    echo ""
fi

# 6. Homebrew nuclear cleanup
if command -v brew &> /dev/null; then
    echo "🍺 HOMEBREW NUCLEAR CLEANUP..."
    brew cleanup --prune=all 2>/dev/null
    brew autoremove 2>/dev/null
    rm -rf $(brew --cache) 2>/dev/null
    rm -rf /usr/local/Homebrew/Library/Caches 2>/dev/null
    rm -rf ~/Library/Caches/Homebrew 2>/dev/null
    echo "   Homebrew nuked"
    echo ""
fi

# 7. Application nuclear cleanup
echo "📱 APPLICATION NUCLEAR CLEANUP..."

# Xcode nuclear option
rm -rf ~/Library/Developer/Xcode/DerivedData 2>/dev/null
rm -rf ~/Library/Developer/Xcode/Archives 2>/dev/null
rm -rf ~/Library/Developer/Xcode/iOS\ DeviceSupport 2>/dev/null
rm -rf ~/Library/Developer/CoreSimulator 2>/dev/null
rm -rf ~/Library/Caches/com.apple.dt.Xcode 2>/dev/null

# Adobe nuclear cleanup
rm -rf ~/Library/Caches/Adobe 2>/dev/null
rm -rf ~/Library/Application\ Support/Adobe/*/Cache 2>/dev/null
rm -rf ~/Library/Application\ Support/Adobe/Common/Media\ Cache* 2>/dev/null

# VS Code nuclear cleanup
rm -rf ~/Library/Caches/com.microsoft.VSCode 2>/dev/null
rm -rf ~/.vscode/extensions/*/node_modules 2>/dev/null

# Other app caches
rm -rf ~/Library/Caches/com.spotify.client 2>/dev/null
rm -rf ~/Library/Caches/com.tinyspeck.slackmacgap 2>/dev/null
rm -rf ~/Library/Caches/com.apple.iTunes 2>/dev/null
rm -rf ~/Library/Caches/com.apple.Music 2>/dev/null

echo "   All application caches nuked"
echo ""

# 8. iOS backups nuclear option
echo "📱 iOS NUCLEAR CLEANUP..."
backups_dir="$HOME/Library/Application Support/MobileSync/Backup"
if [ -d "$backups_dir" ]; then
    backup_size=$(display_size "$backups_dir")
    echo "   💥 NUKING ALL iOS BACKUPS: $backup_size"
    rm -rf "$backups_dir"/* 2>/dev/null
fi
echo ""

# 9. System logs nuclear cleanup
echo "📋 SYSTEM LOGS NUCLEAR CLEANUP..."
sudo rm -rf /var/log/* 2>/dev/null
sudo rm -rf /Library/Logs/* 2>/dev/null
rm -rf ~/Library/Logs/* 2>/dev/null
sudo rm -rf /Library/Application\ Support/CrashReporter/* 2>/dev/null
rm -rf ~/Library/Application\ Support/CrashReporter/* 2>/dev/null
echo "   All logs nuked"
echo ""

# 10. Downloads nuclear cleanup
echo "📥 DOWNLOADS NUCLEAR CLEANUP..."
# Remove all .dmg files
find ~/Downloads -name "*.dmg" -delete 2>/dev/null
# Remove all .zip files older than 3 days
find ~/Downloads -name "*.zip" -mtime +3 -delete 2>/dev/null
# Remove all .pkg files
find ~/Downloads -name "*.pkg" -delete 2>/dev/null
# Remove duplicate files
find ~/Downloads -name "* (1).*" -delete 2>/dev/null
find ~/Downloads -name "*copy*" -delete 2>/dev/null
echo "   Downloads nuked"
echo ""

# 11. Time Machine nuclear option
echo "⏰ TIME MACHINE NUCLEAR CLEANUP..."
sudo tmutil listlocalsnapshotdates / 2>/dev/null | while read -r snapshot; do
    if [ -n "$snapshot" ]; then
        sudo tmutil deletelocalsnapshots "$snapshot" 2>/dev/null
        echo "   💥 Nuked snapshot: $snapshot"
    fi
done
sudo rm -rf /.DocumentRevisions-V100 2>/dev/null
echo ""

# 12. Large file hunter and destroyer
echo "🎯 LARGE FILE HUNTER..."
echo "   Scanning for files >500MB..."
large_files=$(find ~/Desktop ~/Documents ~/Downloads ~/Movies ~/Pictures -size +500M -type f 2>/dev/null)
if [ ! -z "$large_files" ]; then
    echo "   💣 LARGE FILES FOUND:"
    echo "$large_files" | while read -r file; do
        size=$(display_size "$file")
        echo "     $size: $file"
    done
    echo "   ⚠️  Review these files manually and delete if unneeded"
else
    echo "   No large files >500MB found"
fi
echo ""

# 13. Project-specific nuclear cleanup
echo "🗂️  PROJECT NUCLEAR CLEANUP..."
current_dir=$(pwd)
echo "   Current directory: $current_dir"

# Remove ALL backup directories
if ls backup_* 1> /dev/null 2>&1; then
    backup_total=$(du -sh backup_* 2>/dev/null | awk '{s+=$1} END {print s""}')
    echo "   💥 NUKING all backup_* directories: $backup_total"
    rm -rf backup_* 2>/dev/null
fi

# Remove git objects if too large
if [ -d ".git" ]; then
    git_size=$(display_size .git)
    echo "   Git repository size: $git_size"
    git gc --aggressive --prune=now 2>/dev/null
    git repack -ad 2>/dev/null
fi

# Remove common dev artifacts
rm -rf .pytest_cache __pycache__ *.pyc .coverage 2>/dev/null
rm -rf node_modules 2>/dev/null
rm -rf target 2>/dev/null  # Rust build artifacts
rm -rf build 2>/dev/null   # General build artifacts

echo "   Project cleaned"
echo ""

# 14. System maintenance nuclear option
echo "🔧 SYSTEM MAINTENANCE NUCLEAR OPTION..."
sudo /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user 2>/dev/null
sudo atsutil databases -remove 2>/dev/null
sudo dscacheutil -flushcache 2>/dev/null
sudo purge 2>/dev/null
echo "   System maintenance complete"
echo ""

# Wait for background processes
echo "⏳ Waiting for nuclear cleanup to complete..."
wait
echo ""

# Final assessment
echo "☢️  NUCLEAR CLEANUP COMPLETE!"
echo ""
echo "📊 Final disk usage:"
df -h /
echo ""
echo "💥 NUCLEAR CLEANUP SUMMARY:"
echo "   • ALL caches nuked"
echo "   • ALL browser data destroyed"
echo "   • ALL development environments cleaned"
echo "   • ALL node_modules removed"
echo "   • ALL iOS backups deleted"
echo "   • ALL logs cleared"
echo "   • ALL temporary files destroyed"
echo "   • ALL backup directories removed"
echo ""
echo "⚠️  NUCLEAR AFTERMATH - You may need to:"
echo "   • Re-login to all websites"
echo "   • Reinstall npm packages (npm install) in projects"
echo "   • Reconfigure development environments"
echo "   • Re-download browser extensions"
echo "   • Restore iOS device backups if needed"
echo "   • Re-setup application preferences"
echo ""
echo "🎯 If you need more space, manually review and delete:"
echo "   • Large video files in ~/Movies"
echo "   • Large photo libraries"
echo "   • Old virtual machines"
echo "   • Unused applications in /Applications"