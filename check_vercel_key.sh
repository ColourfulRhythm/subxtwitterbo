#!/bin/bash
# Check what API_SECRET_KEY is expected by checking the health endpoint
echo "🔍 Checking API configuration..."
echo ""

# Try to get info from health endpoint
response=$(curl -s "https://subxtwitterbo.vercel.app/health")
echo "$response" | jq '.' 2>/dev/null || echo "$response"

echo ""
echo "📋 To find your API_SECRET_KEY:"
echo "1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables"
echo "2. Look for API_SECRET_KEY"
echo "3. Copy its value (it's currently 64 characters)"
echo ""
echo "Then test with:"
echo "./test_api.sh YOUR_64_CHAR_KEY_FROM_VERCEL"

