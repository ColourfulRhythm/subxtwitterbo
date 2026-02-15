# Twitter API Service - Quick Setup Guide

A simple API service that posts tweets to X (Twitter) when triggered from your webapp.

## 🚀 Quick Start

### 1. Set up `.env` file

Add these variables to your `.env` file:

```env
# Twitter API Credentials (required)
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
ACCESS_TOKEN=your_access_token_here
ACCESS_TOKEN_SECRET=your_access_token_secret_here
BEARER_TOKEN=your_bearer_token_here

# API Security (required - change this!)
API_SECRET_KEY=your-random-secret-key-here

# Optional: Server configuration
API_PORT=5001
API_HOST=0.0.0.0
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the API service

```bash
python3 twitter_api.py
```

The API will start on `http://localhost:5001` (or your configured port).

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns service status.

### Post Tweet
```
POST /api/post-tweet
Headers:
  X-API-Key: your_secret_key
  Content-Type: application/json
```

**Request Body Options:**

#### Option 1: Direct Tweet Text
```json
{
  "tweet": "🎉 New purchase! User just bought land at 2 Seasons!"
}
```

#### Option 2: Purchase Notification (auto-formatted)
```json
{
  "purchase": {
    "user_name": "John Doe",
    "product": "Land at 2 Seasons",
    "amount": "₦500,000",
    "location": "Abeokuta"
  },
  "custom_message": "🎉"
}
```

**Response:**
```json
{
  "success": true,
  "tweet_id": "1234567890",
  "tweet_text": "🎉 John Doe just purchased Land at 2 Seasons (₦500,000) in Abeokuta #RealEstate #Investment",
  "tweet_url": "https://twitter.com/i/web/status/1234567890",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔗 Integration Examples

### JavaScript/Node.js
```javascript
async function postPurchaseTweet(purchaseData) {
  const response = await fetch('http://localhost:5001/api/post-tweet', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_secret_key'
    },
    body: JSON.stringify({
      purchase: {
        user_name: purchaseData.customerName,
        product: purchaseData.productName,
        amount: purchaseData.amount,
        location: purchaseData.location
      },
      custom_message: '🎉'
    })
  });
  
  const result = await response.json();
  console.log('Tweet posted:', result);
}
```

### Python
```python
import requests

def post_purchase_tweet(purchase_data):
    url = 'http://localhost:5001/api/post-tweet'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'your_secret_key'
    }
    
    payload = {
        'purchase': {
            'user_name': purchase_data['customer_name'],
            'product': purchase_data['product_name'],
            'product': purchase_data['amount'],
            'location': purchase_data['location']
        },
        'custom_message': '🎉'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    print('Tweet posted:', result)
    return result
```

### PHP
```php
function postPurchaseTweet($purchaseData) {
    $url = 'http://localhost:5001/api/post-tweet';
    $headers = [
        'Content-Type: application/json',
        'X-API-Key: your_secret_key'
    ];
    
    $payload = [
        'purchase' => [
            'user_name' => $purchaseData['customer_name'],
            'product' => $purchaseData['product_name'],
            'amount' => $purchaseData['amount'],
            'location' => $purchaseData['location']
        ],
        'custom_message' => '🎉'
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}
```

## 🔒 Security

1. **Change `API_SECRET_KEY`** in `.env` to a strong random string
2. **Use HTTPS** in production
3. **Keep your `.env` file secure** - never commit it to git
4. **Rate limiting**: The API respects Twitter's rate limits automatically

## 🐳 Deployment

### Using systemd (Linux)
Create `/etc/systemd/system/twitter-api.service`:

```ini
[Unit]
Description=Twitter API Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/subx-twitter-bot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python3 twitter_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable twitter-api
sudo systemctl start twitter-api
```

### Using Docker
Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY twitter_api.py .
COPY .env .

EXPOSE 5001
CMD ["python3", "twitter_api.py"]
```

### Using Railway/Render/Heroku
1. Add `twitter_api.py` to your project
2. Set environment variables in your platform's dashboard
3. Update `Procfile` or start command to run `python3 twitter_api.py`

## 📝 Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `400` - Bad request (missing/invalid data)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (Twitter app permissions issue)
- `429` - Rate limit exceeded
- `500` - Server error

## 🧪 Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:5001/health

# Post a tweet
curl -X POST http://localhost:5001/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_key" \
  -d '{"tweet": "Test tweet from API!"}'

# Post purchase notification
curl -X POST http://localhost:5001/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_secret_key" \
  -d '{
    "purchase": {
      "user_name": "Test User",
      "product": "Land at 2 Seasons",
      "amount": "₦500,000",
      "location": "Abeokuta"
    }
  }'
```

## 🎯 Use Cases

- **Purchase notifications**: Automatically tweet when users buy products
- **Milestone celebrations**: Post when you hit sales targets
- **Event announcements**: Trigger tweets from your webapp
- **Status updates**: Post system notifications to Twitter
- **Integration with any webhook**: Connect to payment processors, CRM systems, etc.

## 📞 Support

If you encounter issues:
1. Check that all `.env` variables are set correctly
2. Verify Twitter API credentials are valid
3. Ensure your Twitter app has "Read and Write" permissions
4. Check the logs for detailed error messages

