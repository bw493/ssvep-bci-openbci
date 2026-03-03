#!/bin/bash
# Bash script to push project to GitHub
# Run this from the project root directory

set -e  # Exit on error

echo "=================================="
echo "SSVEP BCI - GitHub Push Script"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed!"
    echo "Install Git from: https://git-scm.com/"
    exit 1
fi

echo "✓ Git found: $(git --version)"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo "✓ Git initialized"
else
    echo "✓ Git repository already exists"
fi

echo ""

# Add all files
echo "Adding files to Git..."
git add .
echo "✓ Files added"

echo ""

# Create commit
echo "Creating commit..."
COMMIT_MSG="Complete SSVEP BCI implementation with collected OpenBCI data"
git commit -m "$COMMIT_MSG" || echo "Nothing to commit or already committed"
echo "✓ Commit ready"

echo ""

# Add remote (if not exists)
REMOTE_URL="https://github.com/bw493/ssvep-bci-openbci.git"

if git remote get-url origin &> /dev/null; then
    echo "Remote 'origin' already exists"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "Current remote: $CURRENT_REMOTE"
    
    if [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
        read -p "Update remote URL? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git remote set-url origin "$REMOTE_URL"
            echo "✓ Remote URL updated"
        fi
    fi
else
    echo "Adding remote repository..."
    git remote add origin "$REMOTE_URL"
    echo "✓ Remote added"
fi

echo ""

# Pull any existing content
echo "Checking remote repository..."
if git pull origin main --allow-unrelated-histories &> /dev/null; then
    echo "✓ Pulled existing content"
else
    echo "No existing content to pull (or remote doesn't exist yet)"
fi

echo ""

# Push to GitHub
echo "Pushing to GitHub..."
echo ""

if git push -u origin main; then
    PUSHED=true
else
    echo ""
    echo "⚠️  Normal push failed"
    echo "This usually means the remote has different history"
    echo ""
    read -p "Force push? This will OVERWRITE remote content (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Force pushing..."
        if git push -u origin main --force; then
            PUSHED=true
            FORCE_USED=true
        else
            PUSHED=false
        fi
    else
        PUSHED=false
    fi
fi

echo ""
echo "=================================="

if [ "$PUSHED" = true ]; then
    echo "✅ SUCCESS!"
    echo ""
    echo "Your code is now on GitHub!"
    echo "View it at: https://github.com/bw493/ssvep-bci-openbci"
    
    if [ "$FORCE_USED" = true ]; then
        echo ""
        echo "⚠️  Note: Used force push - remote history was overwritten"
    fi
else
    echo "❌ Push failed"
    echo ""
    echo "Troubleshooting:"
    echo "1. Make sure you're logged in to GitHub"
    echo "2. Check your internet connection"
    echo "3. Verify repository URL is correct"
    echo "4. See GITHUB_SETUP.md for detailed instructions"
    echo ""
    echo "For authentication, you may need a Personal Access Token:"
    echo "Create one at: https://github.com/settings/tokens"
fi

echo "=================================="
echo ""
