#!/bin/bash

echo "🤖 SubX Twitter Bot - Quick Setup"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }

# Install dependencies
echo ""
echo "✓ Installing dependencies..."
pip3 install -r requirements.txt || { echo "❌ Failed to install dependencies"; exit 1; }

# Create .env from template
if [ ! -f .env ]; then
    echo ""
    echo "✓ Creating .env file..."
    cp .env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Twitter API credentials!"
    echo "   Get them from: https://developer.twitter.com/en/portal/dashboard"
    echo ""
    echo "   Required credentials:"
    echo "   - API_KEY"
    echo "   - API_SECRET"
    echo "   - ACCESS_TOKEN"
    echo "   - ACCESS_TOKEN_SECRET"
    echo "   - BEARER_TOKEN"
    echo ""
    read -p "Press Enter after you've added credentials to .env..."
else
    echo ""
    echo "✓ .env file already exists"
fi

# Check if credentials are set
if grep -q "your_api_key_here" .env; then
    echo ""
    echo "❌ .env still contains placeholder values!"
    echo "   Please edit .env and add your actual Twitter API credentials."
    echo "   Then run this script again."
    exit 1
fi

# Test bot
echo ""
echo "✓ Testing bot configuration..."
timeout 5 python3 bot.py || true

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review your .env credentials"
echo "2. Customize tweet_queue.json if needed"
echo "3. Run: python3 bot.py"
echo ""
echo "Or view dashboard: python3 dashboard.py"
echo "=================================="
