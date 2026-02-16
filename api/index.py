"""
Vercel Serverless Function for Twitter API
This wraps twitter_api.py for Vercel deployment
"""
import sys
import os

# Add parent directory to path to import twitter_api
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    # Import the Flask app
    from twitter_api import app
    
    # Vercel expects the Flask app to be accessible
    # This is what Vercel's Python runtime will use
    handler = app
except Exception as e:
    # If import fails, create a minimal error handler
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return {
            'error': 'Failed to initialize Twitter API',
            'message': str(e),
            'path': path
        }, 500
    
    handler = error_app
