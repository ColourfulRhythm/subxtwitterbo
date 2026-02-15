"""
Example: How to integrate Twitter API with your Python webapp

This shows how to call the API when a user makes a purchase
"""

import requests
import os
from typing import Dict, Optional

# Configuration
TWITTER_API_URL = os.getenv('TWITTER_API_URL', 'http://localhost:5001/api/post-tweet')
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your_secret_key_here')


def post_purchase_tweet(purchase_data: Dict) -> Dict:
    """
    Post a tweet when a user completes a purchase
    
    Args:
        purchase_data: Dictionary with keys:
            - customer_name (str): Name of the customer
            - product_name (str): Name of the product purchased
            - amount (float): Purchase amount
            - currency (str): Currency code (default: NGN)
            - location (str, optional): Location of purchase
    
    Returns:
        Dict with tweet information or error
    """
    try:
        # Format currency
        currency = purchase_data.get('currency', 'NGN')
        amount = purchase_data.get('amount', 0)
        if currency == 'NGN':
            formatted_amount = f"₦{amount:,.0f}"
        else:
            formatted_amount = f"{currency} {amount:,.0f}"
        
        # Prepare payload
        payload = {
            'purchase': {
                'user_name': purchase_data.get('customer_name', 'A customer'),
                'product': purchase_data.get('product_name', 'a product'),
                'amount': formatted_amount,
                'location': purchase_data.get('location', '')
            },
            'custom_message': '🎉'
        }
        
        # Make API request
        response = requests.post(
            TWITTER_API_URL,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': API_SECRET_KEY
            },
            timeout=10
        )
        
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Tweet posted: {result.get('tweet_url')}")
        else:
            print(f"❌ Failed to post tweet: {result.get('error')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Twitter API: {e}")
        return {'success': False, 'error': str(e)}


def post_custom_tweet(tweet_text: str) -> Dict:
    """
    Post a custom tweet
    
    Args:
        tweet_text: The text to tweet
    
    Returns:
        Dict with tweet information or error
    """
    try:
        payload = {'tweet': tweet_text}
        
        response = requests.post(
            TWITTER_API_URL,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': API_SECRET_KEY
            },
            timeout=10
        )
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling Twitter API: {e}")
        return {'success': False, 'error': str(e)}


# Example: Flask integration
"""
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

@app.route('/webhook/purchase', methods=['POST'])
def handle_purchase_webhook():
    data = request.get_json()
    
    # Extract purchase information
    purchase_data = {
        'customer_name': data.get('customer', {}).get('name'),
        'product_name': data.get('product', {}).get('name'),
        'amount': data.get('amount'),
        'currency': data.get('currency', 'NGN'),
        'location': data.get('shipping', {}).get('city', '')
    }
    
    # Post to Twitter in background (don't block the response)
    def post_tweet_async():
        post_purchase_tweet(purchase_data)
    
    thread = threading.Thread(target=post_tweet_async)
    thread.start()
    
    return jsonify({'status': 'ok', 'message': 'Purchase processed'})

if __name__ == '__main__':
    app.run(port=3000)
"""

# Example: Django integration
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import threading

@csrf_exempt
def purchase_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        purchase_data = {
            'customer_name': data.get('customer_name'),
            'product_name': data.get('product_name'),
            'amount': data.get('amount'),
            'currency': data.get('currency', 'NGN'),
            'location': data.get('location', '')
        }
        
        # Post to Twitter in background
        thread = threading.Thread(target=post_purchase_tweet, args=(purchase_data,))
        thread.start()
        
        return JsonResponse({'status': 'ok'})
"""

# Example usage:
if __name__ == '__main__':
    # Test purchase notification
    purchase_data = {
        'customer_name': 'John Doe',
        'product_name': 'Land at 2 Seasons',
        'amount': 500000,
        'currency': 'NGN',
        'location': 'Abeokuta'
    }
    
    result = post_purchase_tweet(purchase_data)
    print(result)

