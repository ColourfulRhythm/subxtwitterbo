#!/bin/bash
# Test script for Vercel API

API_URL="https://subxtwitterbo.vercel.app"
API_KEY="agKghFPEBXRL6WDuQWtNYLCrZgzDy18bzcKxepYyxzlT9QyG36"

echo "🧪 Testing Vercel API..."
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$API_URL/health"
echo ""
echo ""

# Test 2: Post tweet
echo "2️⃣ Testing post tweet endpoint..."
curl -X POST "$API_URL/api/post-tweet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"tweet": "🧪 Test tweet from Vercel API!"}'
echo ""
echo ""

# Test 3: Post purchase notification
echo "3️⃣ Testing purchase notification..."
curl -X POST "$API_URL/api/post-tweet" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "purchase": {
      "user_name": "Test User",
      "product": "Land at 2 Seasons",
      "amount": "₦500,000",
      "location": "Abeokuta"
    },
    "custom_message": "🎉"
  }'
echo ""
echo ""

echo "✅ Tests complete!"

