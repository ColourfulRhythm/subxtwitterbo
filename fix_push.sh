#!/bin/bash
# Fix push timeout by creating a fresh, clean repository

echo "🔧 Fixing push timeout issue..."
echo ""

# Step 1: Backup current .git (just in case)
echo "📦 Step 1: Backing up current git history..."
if [ -d .git ]; then
    mv .git .git.backup
    echo "✅ Backed up to .git.backup"
fi

# Step 2: Initialize fresh repository
echo ""
echo "📦 Step 2: Creating fresh git repository..."
git init
git branch -M main

# Step 3: Add remote
echo ""
echo "📦 Step 3: Setting up remote..."
git remote add origin https://github.com/ColourfulRhythm/subxtwitterbo.git

# Step 4: Stage only necessary files
echo ""
echo "📦 Step 4: Staging files (respects .gitignore)..."
git add .

# Step 5: Check what will be committed
echo ""
echo "📦 Step 5: Files to be committed:"
git status --short | head -20
echo "..."

# Step 6: Commit
echo ""
echo "📦 Step 6: Creating initial commit..."
git commit -m "Initial commit: Twitter API service with Vercel deployment"

# Step 7: Push
echo ""
echo "📦 Step 7: Pushing to GitHub..."
echo "⚠️  This will create a fresh repository with only necessary files"
read -p "Continue? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    git push -u origin main --force
    echo ""
    echo "✅ Push complete!"
    echo ""
    echo "🗑️  Old git history backed up to .git.backup (you can delete it if everything works)"
else
    echo "⏭️  Cancelled. Run again when ready."
fi

