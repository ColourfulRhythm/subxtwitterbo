#!/bin/bash
# Deployment script for GitHub and Vercel

echo "🚀 Starting deployment process..."

# Step 1: Update git remote
echo "📝 Step 1: Updating git remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/ColourfulRhythm/subxtwitterbo.git
echo "✅ Remote updated"

# Step 2: Check git status
echo ""
echo "📝 Step 2: Checking git status..."
git status

# Step 3: Stage files
echo ""
echo "📝 Step 3: Staging files..."
git add .

# Step 4: Commit
echo ""
echo "📝 Step 4: Committing changes..."
read -p "Enter commit message (or press Enter for default): " commit_msg
commit_msg=${commit_msg:-"Add Twitter API service with Vercel deployment support"}
git commit -m "$commit_msg"

# Step 5: Push to GitHub
echo ""
echo "📝 Step 5: Pushing to GitHub..."
echo "⚠️  If the repository is empty, use: git push -u origin main --force"
echo "⚠️  If the repository has content, use: git push -u origin main"
read -p "Push to GitHub now? (y/n): " push_now

if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
    # Try to pull first (in case repo has content)
    git pull origin main --allow-unrelated-histories 2>/dev/null || true
    
    # Push
    git push -u origin main || git push -u origin main --force
    echo "✅ Pushed to GitHub!"
else
    echo "⏭️  Skipped push. Run manually:"
    echo "   git push -u origin main"
fi

echo ""
echo "✅ Deployment script complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Click 'Add New Project'"
echo "3. Import repository: ColourfulRhythm/subxtwitterbo"
echo "4. Add environment variables (see DEPLOY_VERCEL.md)"
echo "5. Deploy!"
echo ""
echo "📖 See DEPLOY_VERCEL.md for detailed Vercel setup instructions"

