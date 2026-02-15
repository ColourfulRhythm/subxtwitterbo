"""
Vercel Serverless Function for Twitter API
This wraps twitter_api.py for Vercel deployment
"""
import sys
import os

# Add parent directory to path to import twitter_api
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twitter_api import app

# Vercel expects the Flask app directly
# The app variable from twitter_api.py is what Vercel needs

