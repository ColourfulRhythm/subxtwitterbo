#!/bin/bash
# Simple test script for the Twitter API
# Usage: ./test_api.sh YOUR_API_SECRET_KEY

API_SECRET_KEY="${1}"
API_URL="https://subxtwitterbo.vercel.app/api/post-tweet"

if [ -z "$API_SECRET_KEY" ]; then
    echo "❌ Error: Please provide your API_SECRET_KEY"
    echo "Usage: ./test_api.sh YOUR_API_SECRET_KEY"
    echo ""
    echo "Or generate one: python3 generate_api_key.py"
    exit 1
fi

echo "🧪 Testing Twitter API..."
echo "📍 Endpoint: $API_URL"
echo "📝 Tweet: Join the challenge! 🚀"
echo ""

response=$(curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_SECRET_KEY" \
  -d '{"tweet": "Join the challenge! 🚀"}' \
  -w "\nHTTP_STATUS:%{http_code}" \
  -s)

# Split response and status code
body=$(echo "$response" | sed 's/HTTP_STATUS:.*//')
status=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)

echo "Response:"
echo "$body" | jq '.' 2>/dev/null || echo "$body"
echo ""
echo "HTTP Status: $status"
echo ""

if [ "$status" = "200" ]; then
    echo "✅ SUCCESS! Tweet posted!"
    tweet_url=$(echo "$body" | jq -r '.tweet_url' 2>/dev/null)
    if [ "$tweet_url" != "null" ] && [ -n "$tweet_url" ]; then
        echo "🔗 Tweet URL: $tweet_url"
    fi
else
    echo "❌ FAILED"
    error=$(echo "$body" | jq -r '.error' 2>/dev/null)
    if [ "$error" != "null" ] && [ -n "$error" ]; then
        echo "Error: $error"
    fi
fi

