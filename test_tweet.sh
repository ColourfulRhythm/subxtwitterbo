#!/bin/bash
# Test script to post a tweet via the API
# Usage: ./test_tweet.sh YOUR_API_SECRET_KEY

API_SECRET_KEY="${1:-change-this-to-a-random-string}"
API_URL="https://subxtwitterbo.vercel.app/api/post-tweet"

echo "🧪 Testing Twitter API..."
echo "📍 Endpoint: $API_URL"
echo "📝 Tweet: Join the challenge! 🚀"
echo ""

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_SECRET_KEY" \
  -d '{
    "tweet": "Join the challenge! 🚀"
  }' \
  -w "\n\n📊 HTTP Status: %{http_code}\n" \
  -s | jq '.' 2>/dev/null || cat

echo ""
echo "✅ Done! Check the response above."

