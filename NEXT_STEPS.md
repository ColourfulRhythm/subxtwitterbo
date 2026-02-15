# 🎯 Next Steps - Twitter API Integration

## Step 1: Configure API Security Key

Add this to your `.env` file:

```env
# Generate a random secret key (you can use: openssl rand -hex 32)
API_SECRET_KEY=your-random-secret-key-here-change-this

# Optional: Change port if 5001 is already in use
API_PORT=5001
```

**Quick way to generate a secure key:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 2: Test the API Locally

### Start the API service:
```bash
python3 twitter_api.py
```

You should see:
```
✅ Twitter client initialized successfully
🚀 Starting Twitter API service on 0.0.0.0:5001
```

### Test it works (in another terminal):
```bash
# Test health check
curl http://localhost:5001/health

# Test posting a tweet (replace YOUR_SECRET_KEY with your actual key)
curl -X POST http://localhost:5001/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_SECRET_KEY" \
  -d '{"tweet": "🧪 Test tweet from API!"}'
```

Or use the test script:
```bash
python3 test_api.py
```

## Step 3: Integrate with Your Webapp

### Option A: JavaScript/Node.js Webapp

1. Copy the code from `example_webapp_integration.js`
2. Update the configuration:
   ```javascript
   const TWITTER_API_URL = 'http://your-api-url:5001/api/post-tweet';
   const API_SECRET_KEY = 'your_secret_key_from_env';
   ```

3. Call it when a purchase happens:
   ```javascript
   // After successful purchase
   await handlePurchaseComplete({
       customerName: purchase.customer_name,
       productName: purchase.product_name,
       amount: purchase.amount,
       currency: 'NGN',
       location: purchase.location
   });
   ```

### Option B: Python Webapp (Flask/Django)

1. Copy the code from `example_webapp_integration.py`
2. Add to your purchase handler:
   ```python
   from example_webapp_integration import post_purchase_tweet
   
   # After successful purchase
   post_purchase_tweet({
       'customer_name': purchase.customer_name,
       'product_name': purchase.product_name,
       'amount': purchase.amount,
       'currency': 'NGN',
       'location': purchase.location
   })
   ```

### Option C: Webhook Integration

If you're using a payment processor (Stripe, PayPal, etc.), add the API call to your webhook handler:

```python
@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    # Process payment...
    
    # Post to Twitter
    post_purchase_tweet(purchase_data)
    
    return {'status': 'ok'}
```

## Step 4: Deploy the API

### Option A: Run on Same Server as Webapp
```bash
# Run in background
nohup python3 twitter_api.py > api.log 2>&1 &
```

### Option B: Use systemd (Linux)
See `API_README.md` for systemd service setup

### Option C: Deploy to Cloud
- **Railway**: Add `twitter_api.py` and set environment variables
- **Render**: Add start command: `python3 twitter_api.py`
- **Heroku**: Update Procfile or use worker dyno

### Option D: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY twitter_api.py .
EXPOSE 5001
CMD ["python3", "twitter_api.py"]
```

## Step 5: Update Your Webapp API URL

Once deployed, update your webapp to point to the production API:

```javascript
// Development
const TWITTER_API_URL = 'http://localhost:5001/api/post-tweet';

// Production
const TWITTER_API_URL = 'https://your-api-domain.com/api/post-tweet';
```

## ✅ Checklist

- [ ] Added `API_SECRET_KEY` to `.env` file
- [ ] Tested API locally with `test_api.py`
- [ ] Integrated API call into your purchase flow
- [ ] Tested end-to-end: purchase → tweet posted
- [ ] Deployed API to production (if needed)
- [ ] Updated webapp to use production API URL
- [ ] Added error handling (don't fail purchases if Twitter API fails)

## 🐛 Troubleshooting

**API won't start:**
- Check that all Twitter credentials are in `.env`
- Verify port 5001 is not in use: `lsof -i :5001`

**401 Unauthorized:**
- Check `API_SECRET_KEY` matches in `.env` and webapp
- Verify you're sending `X-API-Key` header

**403 Forbidden:**
- Twitter app needs "Read and Write" permissions
- Regenerate Access Token after changing permissions

**Tweets not posting:**
- Check API logs for errors
- Verify Twitter credentials are valid
- Check rate limits (Twitter allows limited posts per day)

## 📚 Need More Help?

- See `API_README.md` for full documentation
- Check `example_webapp_integration.js` or `.py` for code examples
- Test with `test_api.py` to verify setup

