"""
Vercel Serverless Function for Twitter API
Handles Flask app export for Vercel's Python runtime
"""
import sys
import os
import traceback

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import the Flask app
try:
    from twitter_api import app
    print("✅ Successfully imported Flask app from twitter_api")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    # Create a minimal error app
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def import_error_handler(path):
        return jsonify({
            'error': 'Import Error',
            'message': str(e),
            'traceback': traceback.format_exc(),
            'hint': 'Check that all dependencies are in requirements.txt and environment variables are set'
        }), 500
    
    app = error_app
except Exception as e:
    print(f"❌ Unexpected error importing app: {e}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    # Create error app
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'error': 'Initialization Error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
    app = error_app

# Vercel Python runtime expects 'app' variable
# This is what gets exported to Vercel
