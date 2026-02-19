# Test Your Vercel Deployment

## Build Status: ✅ SUCCESS

Your deployment built successfully! Now let's test it.

## Quick Tests

### 1. Health Check
```bash
curl https://subxtwitterbo.vercel.app/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "Twitter API",
  "timestamp": "2024-01-15T08:30:00",
  "twitter_configured": true,
  "env_vars_set": true
}
```

### 2. API Endpoint (GET - Documentation)
```bash
curl https://subxtwitterbo.vercel.app/api/post-tweet
```

**Expected Response:**
```json
{
  "endpoint": "/api/post-tweet",
  "method": "POST",
  "authentication": "X-API-Key header or Authorization: Bearer <key>",
  "examples": {...}
}
```

### 3. Test Posting a Tweet (POST)
```bash
curl -X POST https://subxtwitterbo.vercel.app/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: agKghFPEBXRL6WDuQWtNYLCrZgzDy18bzcKxepYyxzlT9QyG36" \
  -d '{"tweet": "🧪 Test tweet from Vercel!"}'
```

**Expected Response:**
```json
{
  "success": true,
  "tweet_id": "1234567890",
  "tweet_text": "🧪 Test tweet from Vercel!",
  "tweet_url": "https://twitter.com/i/web/status/1234567890",
  "timestamp": "2024-01-15T08:30:00"
}
```

## Troubleshooting

### If Health Check Shows `env_vars_set: false`
**Problem:** Environment variables not set in Vercel

**Fix:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add all required variables:
   - `API_KEY`
   - `API_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
   - `API_SECRET_KEY`
3. Redeploy (or wait for auto-redeploy)

### If Health Check Shows `twitter_configured: false`
**Problem:** Twitter client failed to initialize (likely missing/invalid credentials)

**Fix:**
1. Verify all Twitter credentials are correct in Vercel
2. Check Twitter Developer Portal to ensure app has "Read and Write" permissions
3. Regenerate tokens if needed

### If You Get 401 Unauthorized
**Problem:** `API_SECRET_KEY` doesn't match

**Fix:**
1. Check `API_SECRET_KEY` in Vercel environment variables
2. Use the same key in your API requests
3. Generate a new one if needed: `python3 -c "import secrets; print(secrets.token_hex(32))"`

### If You Get 500 Error
**Problem:** Check Vercel Function Logs

**Fix:**
1. Go to Vercel Dashboard → Your Project → Deployments
2. Click latest deployment → "Function Logs"
3. Look for error messages
4. The new error handling should show detailed error info

## Integration Test

Once health check passes, test from your webapp:

```javascript
// JavaScript example
const response = await fetch('https://subxtwitterbo.vercel.app/api/post-tweet', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your_api_secret_key'
  },
  body: JSON.stringify({
    purchase: {
      user_name: 'Test User',
      product: 'Land at 2 Seasons',
      amount: '₦500,000',
      location: 'Abeokuta'
    }
  })
});

const result = await response.json();
console.log(result);
```

## Success Indicators

✅ Health check returns `status: "ok"`  
✅ Health check shows `env_vars_set: true`  
✅ Health check shows `twitter_configured: true`  
✅ POST request returns `success: true`  
✅ Tweet appears on Twitter

