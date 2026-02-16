# Fix API Key Authentication

## Issue: Unauthorized Error

You're getting:
```json
{"error":"Unauthorized. Invalid or missing API key.","success":false}
```

## Solution

### Step 1: Check Your API_SECRET_KEY in Vercel

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Find `API_SECRET_KEY`
3. Copy the value

### Step 2: Use the Correct Key in Your Request

Make sure you're using the **exact same value** in your curl command:

```bash
curl -X POST https://subxtwitterbo.vercel.app/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ACTUAL_API_SECRET_KEY_FROM_VERCEL" \
  -d '{"tweet": "🧪 Test tweet!"}'
```

### Step 3: Verify the Key is Set

If `API_SECRET_KEY` is not set in Vercel:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Click "Add New"
3. Key: `API_SECRET_KEY`
4. Value: Generate one with:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
5. Save and redeploy

### Step 4: Test Again

After setting/verifying the key, test:

```bash
curl -X POST https://subxtwitterbo.vercel.app/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY_HERE" \
  -d '{"tweet": "🧪 Test!"}'
```

## Common Mistakes

❌ **Wrong:** Using `API_KEY` instead of `API_SECRET_KEY`  
✅ **Correct:** Use `API_SECRET_KEY` (the authentication key for your API)

❌ **Wrong:** Key has extra spaces or quotes  
✅ **Correct:** Copy the exact value, no spaces

❌ **Wrong:** Using Twitter API keys  
✅ **Correct:** `API_SECRET_KEY` is separate from Twitter credentials

## Alternative: Check What Key is Expected

You can also check the API documentation endpoint:

```bash
curl https://subxtwitterbo.vercel.app/api/post-tweet
```

This shows the API structure (but not the actual key value for security).

## For Your Webapp Integration

Make sure you use the same `API_SECRET_KEY` in your webapp:

```javascript
const API_SECRET_KEY = 'your_key_from_vercel'; // Must match Vercel env var
```

```python
API_SECRET_KEY = 'your_key_from_vercel'  # Must match Vercel env var
```

