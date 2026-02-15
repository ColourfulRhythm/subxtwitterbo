#!/usr/bin/env python3
"""
Quick script to post a tweet
"""
import os
import sys
from dotenv import load_dotenv
import tweepy

# Load environment variables
load_dotenv()

# Twitter API credentials
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# Get tweet text from command line or use default
tweet_text = sys.argv[1] if len(sys.argv) > 1 else "Val with M 26"

# Initialize Twitter client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

try:
    # Post tweet
    response = client.create_tweet(text=tweet_text)
    print(f"✅ Tweet posted successfully!")
    print(f"   Tweet ID: {response.data['id']}")
    print(f"   Text: {tweet_text}")
    print(f"   URL: https://twitter.com/i/web/status/{response.data['id']}")
except tweepy.Unauthorized as e:
    print(f"❌ Unauthorized (401): Your Twitter API credentials are invalid or expired.")
    print(f"   Please check your .env file and regenerate credentials if needed.")
except tweepy.Forbidden as e:
    print(f"❌ Forbidden (403): Your app may not have write permissions.")
    print(f"   Check your app settings at https://developer.twitter.com/en/portal/dashboard")
except Exception as e:
    print(f"❌ Error posting tweet: {e}")

