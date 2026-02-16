#!/usr/bin/env python3
"""
Simple Twitter API Service
Post tweets from your webapp when users make purchases or other events occur.

Usage:
1. Set up .env file with Twitter credentials
2. Set API_SECRET_KEY in .env for authentication
3. Run: python3 twitter_api.py
4. Call POST /api/post-tweet from your webapp

Example webhook call:
POST /api/post-tweet
Headers: X-API-Key: your_secret_key
Body: {
    "tweet": "🎉 New purchase! User just bought land at 2 Seasons!"
}
"""

import os
import tweepy
import traceback
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Twitter API credentials (from .env file)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# API authentication key (set this in .env)
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'change-this-to-a-random-string')

# Initialize Twitter client
try:
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True
    )
    logger.info("✅ Twitter client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Twitter client: {e}")
    client = None


def verify_api_key():
    """Verify API key from request headers"""
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not api_key:
        logger.warning("❌ No API key provided in request headers")
        return False
    if api_key != API_SECRET_KEY:
        logger.warning(f"❌ API key mismatch. Provided: {api_key[:10]}... (length: {len(api_key)}), Expected length: {len(API_SECRET_KEY) if API_SECRET_KEY else 0}")
        return False
    return True


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'ok',
            'service': 'Twitter API',
            'timestamp': datetime.now().isoformat(),
            'twitter_configured': client is not None,
            'env_vars_set': all([
                bool(API_KEY),
                bool(API_SECRET),
                bool(ACCESS_TOKEN),
                bool(ACCESS_TOKEN_SECRET),
                bool(BEARER_TOKEN)
            ])
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc() if hasattr(traceback, 'format_exc') else 'N/A'
        }), 500


@app.route('/api/post-tweet', methods=['POST'])
def post_tweet():
    """
    Post a tweet to Twitter
    
    Request body (JSON):
    {
        "tweet": "Your tweet text here"  (required)
    }
    
    OR for purchase notifications:
    {
        "purchase": {
            "user_name": "John Doe",
            "product": "Land at 2 Seasons",
            "amount": "₦500,000",
            "location": "Abeokuta"
        },
        "custom_message": "Optional custom prefix"
    }
    """
    
    # Verify API key
    if not verify_api_key():
        return jsonify({
            'success': False,
            'error': 'Unauthorized. Invalid or missing API key.'
        }), 401
    
    # Check if Twitter client is configured
    if not client:
        return jsonify({
            'success': False,
            'error': 'Twitter client not configured. Check your .env file.'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Handle direct tweet text
        if 'tweet' in data:
            tweet_text = data['tweet']
        
        # Handle purchase notification
        elif 'purchase' in data:
            purchase = data['purchase']
            custom_msg = data.get('custom_message', '🎉')
            
            # Build tweet from purchase data
            user_name = purchase.get('user_name', 'A customer')
            product = purchase.get('product', 'a product')
            amount = purchase.get('amount', '')
            location = purchase.get('location', '')
            
            tweet_parts = [custom_msg]
            
            if user_name:
                tweet_parts.append(f"{user_name} just purchased")
            else:
                tweet_parts.append("New purchase!")
            
            tweet_parts.append(product)
            
            if amount:
                tweet_parts.append(f"({amount})")
            
            if location:
                tweet_parts.append(f"in {location}")
            
            tweet_text = ' '.join(tweet_parts)
            
            # Add hashtags if space allows
            if len(tweet_text) < 240:
                tweet_text += " #RealEstate #Investment"
        
        else:
            return jsonify({
                'success': False,
                'error': 'Missing "tweet" or "purchase" field in request body'
            }), 400
        
        # Validate tweet length
        if not tweet_text or len(tweet_text.strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'Tweet text cannot be empty'
            }), 400
        
        if len(tweet_text) > 280:
            return jsonify({
                'success': False,
                'error': f'Tweet too long ({len(tweet_text)} chars). Max 280 characters.'
            }), 400
        
        # Post tweet
        response = client.create_tweet(text=tweet_text)
        
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        
        logger.info(f"✅ Tweet posted successfully: {tweet_id}")
        
        return jsonify({
            'success': True,
            'tweet_id': tweet_id,
            'tweet_text': tweet_text,
            'tweet_url': tweet_url,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except tweepy.Unauthorized as e:
        logger.error(f"❌ Unauthorized (401): {e}")
        return jsonify({
            'success': False,
            'error': 'Twitter API credentials are invalid or expired. Check your .env file.'
        }), 401
    
    except tweepy.Forbidden as e:
        logger.error(f"❌ Forbidden (403): {e}")
        return jsonify({
            'success': False,
            'error': 'Twitter app does not have write permissions. Check app settings.'
        }), 403
    
    except tweepy.TooManyRequests as e:
        logger.error(f"❌ Rate limit exceeded: {e}")
        return jsonify({
            'success': False,
            'error': 'Twitter API rate limit exceeded. Please try again later.'
        }), 429
    
    except Exception as e:
        logger.error(f"❌ Error posting tweet: {e}")
        return jsonify({
            'success': False,
            'error': f'Error posting tweet: {str(e)}'
        }), 500


@app.route('/api/post-tweet', methods=['GET'])
def post_tweet_info():
    """Get API documentation"""
    return jsonify({
        'endpoint': '/api/post-tweet',
        'method': 'POST',
        'authentication': 'X-API-Key header or Authorization: Bearer <key>',
        'examples': {
            'direct_tweet': {
                'body': {
                    'tweet': 'Your tweet text here'
                }
            },
            'purchase_notification': {
                'body': {
                    'purchase': {
                        'user_name': 'John Doe',
                        'product': 'Land at 2 Seasons',
                        'amount': '₦500,000',
                        'location': 'Abeokuta'
                    },
                    'custom_message': '🎉'
                }
            }
        }
    }), 200


if __name__ == '__main__':
    # Check if credentials are set
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
        logger.error("❌ Missing Twitter API credentials in .env file")
        logger.error("Required: API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN")
        exit(1)
    
    if API_SECRET_KEY == 'change-this-to-a-random-string':
        logger.warning("⚠️  WARNING: Using default API_SECRET_KEY. Set a secure key in .env!")
    
    # Get port from environment or use default
    port = int(os.getenv('API_PORT', 5001))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting Twitter API service on {host}:{port}")
    logger.info(f"📝 Health check: http://{host}:{port}/health")
    logger.info(f"📝 API endpoint: http://{host}:{port}/api/post-tweet")
    
    app.run(host=host, port=port, debug=False)

