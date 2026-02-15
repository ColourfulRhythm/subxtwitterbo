#!/usr/bin/env python3
"""
Flask Web Application - Multi-user Twitter Bot Dashboard
Handles authentication, user management, and bot control
"""

import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_session import Session
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
from user_manager import UserManager
from credentials import CredentialManager
from bot_manager import BotManager
import json
from pathlib import Path
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './sessions'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

Session(app)

# Initialize managers
user_manager = UserManager()
bot_manager = BotManager()

# Twitter OAuth configuration
TWITTER_API_KEY = os.getenv('TWITTER_OAUTH_API_KEY') or os.getenv('API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_OAUTH_API_SECRET') or os.getenv('API_SECRET')
TWITTER_BASE_URL = 'https://api.twitter.com'
REQUEST_TOKEN_URL = f'{TWITTER_BASE_URL}/oauth/request_token'
AUTHORIZE_URL = f'{TWITTER_BASE_URL}/oauth/authorize'
ACCESS_TOKEN_URL = f'{TWITTER_BASE_URL}/oauth/access_token'

# Ensure sessions directory exists
Path('./sessions').mkdir(exist_ok=True)


def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    """Landing page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/auth/twitter')
def auth_twitter():
    """Initiate Twitter OAuth flow"""
    if not TWITTER_API_KEY or not TWITTER_API_SECRET:
        flash('Twitter OAuth not configured. Please set TWITTER_OAUTH_API_KEY and TWITTER_OAUTH_API_SECRET.', 'error')
        return redirect(url_for('login'))
    
    try:
        # Create OAuth session
        oauth = OAuth1Session(
            TWITTER_API_KEY,
            client_secret=TWITTER_API_SECRET,
            callback_uri=url_for('auth_callback', _external=True)
        )
        
        # Get request token
        fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
        
        # Store in session
        session['oauth_token'] = fetch_response.get('oauth_token')
        session['oauth_token_secret'] = fetch_response.get('oauth_token_secret')
        
        # Redirect to authorization
        authorization_url = oauth.authorization_url(AUTHORIZE_URL)
        return redirect(authorization_url)
    
    except Exception as e:
        flash(f'Error initiating OAuth: {str(e)}', 'error')
        return redirect(url_for('login'))


@app.route('/auth/callback')
def auth_callback():
    """Handle Twitter OAuth callback"""
    oauth_token = session.get('oauth_token')
    oauth_token_secret = session.get('oauth_token_secret')
    oauth_verifier = request.args.get('oauth_verifier')
    
    if not oauth_token or not oauth_verifier:
        flash('OAuth verification failed', 'error')
        return redirect(url_for('login'))
    
    try:
        # Create OAuth session with request token
        oauth = OAuth1Session(
            TWITTER_API_KEY,
            client_secret=TWITTER_API_SECRET,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=oauth_verifier
        )
        
        # Get access token
        oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        
        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')
        user_id = oauth_tokens.get('user_id')
        screen_name = oauth_tokens.get('screen_name')
        
        # Get user info
        user_info = oauth.get(f'{TWITTER_BASE_URL}/1.1/account/verify_credentials.json').json()
        
        # Create or get user
        user = user_manager.get_user_by_twitter_id(str(user_id))
        if not user:
            user = user_manager.create_user(
                user_id=f"twitter_{user_id}",
                username=f"@{screen_name}",
                twitter_id=str(user_id)
            )
        
        # Save credentials
        cred_manager = CredentialManager(user['user_id'])
        cred_manager.save_oauth_tokens(
            access_token,
            access_token_secret,
            TWITTER_API_KEY,
            TWITTER_API_SECRET
        )
        
        # Update user
        user_manager.set_twitter_connected(user['user_id'], True)
        
        # Set session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        
        # Clear OAuth tokens from session
        session.pop('oauth_token', None)
        session.pop('oauth_token_secret', None)
        
        flash('Successfully logged in!', 'success')
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        flash(f'Error completing OAuth: {str(e)}', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    user = user_manager.get_user(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Get bot status
    bot_status = bot_manager.get_bot_status(user_id)
    
    # Load bot data for stats
    bot_data_file = Path('users') / user_id / 'bot_data.json'
    bot_data = {}
    if bot_data_file.exists():
        with open(bot_data_file, 'r') as f:
            bot_data = json.load(f)
    
    return render_template('dashboard.html', 
                         user=user, 
                         bot_status=bot_status,
                         bot_data=bot_data)


@app.route('/connect-twitter', methods=['GET', 'POST'])
@login_required
def connect_twitter():
    """Connect Twitter account (OAuth or manual)"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        method = request.form.get('method')
        
        if method == 'oauth':
            # Redirect to OAuth
            return redirect(url_for('auth_twitter'))
        
        elif method == 'manual':
            # Manual credential entry
            api_key = request.form.get('api_key')
            api_secret = request.form.get('api_secret')
            access_token = request.form.get('access_token')
            access_token_secret = request.form.get('access_token_secret')
            bearer_token = request.form.get('bearer_token')
            
            if not all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
                flash('Please fill in all credential fields', 'error')
                return render_template('connect_twitter.html', user_id=user_id)
            
            try:
                cred_manager = CredentialManager(user_id)
                cred_manager.save_credentials({
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'access_token': access_token,
                    'access_token_secret': access_token_secret,
                    'bearer_token': bearer_token
                })
                
                user_manager.set_twitter_connected(user_id, True)
                flash('Twitter credentials saved successfully!', 'success')
                return redirect(url_for('dashboard'))
            
            except Exception as e:
                flash(f'Error saving credentials: {str(e)}', 'error')
                return render_template('connect_twitter.html', user_id=user_id)
    
    return render_template('connect_twitter.html', user_id=user_id)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Bot configuration settings"""
    user_id = session['user_id']
    user = user_manager.get_user(user_id)
    
    if request.method == 'POST':
        # Update configuration
        config = {
            'tweets_per_day': int(request.form.get('tweets_per_day', 6)),
            'posting_times': request.form.get('posting_times', '').split(','),
            'engagement_interval': int(request.form.get('engagement_interval', 15)),
            'max_replies_per_hour': int(request.form.get('max_replies_per_hour', 5))
        }
        
        # Clean posting times
        config['posting_times'] = [t.strip() for t in config['posting_times'] if t.strip()]
        
        user_manager.update_user_config(user_id, config)
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings'))
    
    config = user_manager.get_user_config(user_id)
    return render_template('settings.html', user=user, config=config)


@app.route('/stats')
@login_required
def stats():
    """Detailed statistics view"""
    user_id = session['user_id']
    
    # Load bot data
    bot_data_file = Path('users') / user_id / 'bot_data.json'
    bot_data = {}
    if bot_data_file.exists():
        with open(bot_data_file, 'r') as f:
            bot_data = json.load(f)
    
    return render_template('stats.html', bot_data=bot_data)


@app.route('/api/bot/start', methods=['POST'])
@login_required
def api_bot_start():
    """API endpoint to start bot"""
    user_id = session['user_id']
    
    # Check if Twitter is connected
    user = user_manager.get_user(user_id)
    if not user.get('twitter_connected'):
        return jsonify({'success': False, 'error': 'Twitter account not connected'}), 400
    
    # Check if credentials exist
    cred_manager = CredentialManager(user_id)
    if not cred_manager.has_credentials():
        return jsonify({'success': False, 'error': 'Twitter credentials not found'}), 400
    
    try:
        bot_manager.start_bot(user_id)
        user_manager.set_bot_active(user_id, True)
        return jsonify({'success': True, 'message': 'Bot started successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bot/stop', methods=['POST'])
@login_required
def api_bot_stop():
    """API endpoint to stop bot"""
    user_id = session['user_id']
    
    try:
        bot_manager.stop_bot(user_id)
        user_manager.set_bot_active(user_id, False)
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bot/status', methods=['GET'])
@login_required
def api_bot_status():
    """API endpoint to get bot status"""
    user_id = session['user_id']
    status = bot_manager.get_bot_status(user_id)
    return jsonify(status)


@app.route('/keywords', methods=['GET', 'POST'])
@login_required
def keywords():
    """Manage keywords for monitoring and reply templates"""
    user_id = session['user_id']
    user = user_manager.get_user(user_id)
    config = user_manager.get_user_config(user_id)
    keywords = config.get('keywords', {})
    
    # Load reply templates
    reply_templates_file = Path('users') / user_id / 'reply_templates.json'
    if reply_templates_file.exists():
        with open(reply_templates_file, 'r') as f:
            reply_templates = json.load(f)
    else:
        # Initialize with default templates from bot_core
        from bot_core import REPLY_TEMPLATES
        reply_templates = REPLY_TEMPLATES.copy()
        with open(reply_templates_file, 'w') as f:
            json.dump(reply_templates, f, indent=2)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            category = request.form.get('category')
            keyword = request.form.get('keyword', '').strip()
            
            if category and keyword:
                if category not in keywords:
                    keywords[category] = []
                if keyword not in keywords[category]:
                    keywords[category].append(keyword)
                    user_manager.update_user_config(user_id, {'keywords': keywords})
                    flash('Keyword added successfully!', 'success')
        
        elif action == 'remove':
            category = request.form.get('category')
            keyword = request.form.get('keyword')
            
            if category in keywords and keyword in keywords[category]:
                keywords[category].remove(keyword)
                user_manager.update_user_config(user_id, {'keywords': keywords})
                flash('Keyword removed successfully!', 'success')
        
        elif action == 'add_category':
            new_category = request.form.get('new_category', '').strip()
            if new_category and new_category not in keywords:
                keywords[new_category] = []
                if new_category not in reply_templates:
                    reply_templates[new_category] = []
                user_manager.update_user_config(user_id, {'keywords': keywords})
                with open(reply_templates_file, 'w') as f:
                    json.dump(reply_templates, f, indent=2)
                flash('Category added successfully!', 'success')
        
        elif action == 'add_reply':
            category = request.form.get('category')
            reply_text = request.form.get('reply_text', '').strip()
            
            if category and reply_text:
                if category not in reply_templates:
                    reply_templates[category] = []
                reply_templates[category].append(reply_text)
                with open(reply_templates_file, 'w') as f:
                    json.dump(reply_templates, f, indent=2)
                flash('Reply template added!', 'success')
        
        elif action == 'remove_reply':
            category = request.form.get('category')
            reply_index = int(request.form.get('reply_index'))
            
            if category in reply_templates and 0 <= reply_index < len(reply_templates[category]):
                reply_templates[category].pop(reply_index)
                with open(reply_templates_file, 'w') as f:
                    json.dump(reply_templates, f, indent=2)
                flash('Reply template removed!', 'success')
        
        return redirect(url_for('keywords'))
    
    return render_template('keywords.html', keywords=keywords, reply_templates=reply_templates, user=user)


@app.route('/tweets', methods=['GET', 'POST'])
@login_required
def tweets():
    """Manage tweet queue and scheduled tweets"""
    user_id = session['user_id']
    user = user_manager.get_user(user_id)
    
    # Load tweet queue
    queue_file = Path('users') / user_id / 'tweet_queue.json'
    if queue_file.exists():
        with open(queue_file, 'r') as f:
            tweet_queue = json.load(f)
    else:
        # Fallback to default queue
        default_queue = Path('tweet_queue.json')
        if default_queue.exists():
            with open(default_queue, 'r') as f:
                tweet_queue = json.load(f)
        else:
            tweet_queue = []
    
    # Load scheduled tweets
    scheduled_file = Path('users') / user_id / 'scheduled_tweets.json'
    if scheduled_file.exists():
        with open(scheduled_file, 'r') as f:
            scheduled_tweets = json.load(f)
    else:
        scheduled_tweets = []
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            tweet_text = request.form.get('tweet_text', '').strip()
            if tweet_text and len(tweet_text) <= 280:
                tweet_queue.append(tweet_text)
                with open(queue_file, 'w') as f:
                    json.dump(tweet_queue, f, indent=2)
                flash('Tweet added to queue!', 'success')
            else:
                flash('Tweet must be between 1 and 280 characters', 'error')
        
        elif action == 'schedule':
            tweet_text = request.form.get('tweet_text', '').strip()
            schedule_time = request.form.get('schedule_time', '').strip()
            schedule_date = request.form.get('schedule_date', '').strip()
            
            if tweet_text and len(tweet_text) <= 280 and schedule_time and schedule_date:
                scheduled_tweet = {
                    'tweet': tweet_text,
                    'datetime': f"{schedule_date} {schedule_time}",
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'pending'
                }
                scheduled_tweets.append(scheduled_tweet)
                # Sort by datetime
                scheduled_tweets.sort(key=lambda x: x['datetime'])
                with open(scheduled_file, 'w') as f:
                    json.dump(scheduled_tweets, f, indent=2)
                flash('Tweet scheduled successfully!', 'success')
            else:
                flash('Please fill in all fields correctly', 'error')
        
        elif action == 'remove':
            try:
                index = int(request.form.get('index'))
                if 0 <= index < len(tweet_queue):
                    tweet_queue.pop(index)
                    with open(queue_file, 'w') as f:
                        json.dump(tweet_queue, f, indent=2)
                    flash('Tweet removed from queue!', 'success')
            except (ValueError, IndexError):
                flash('Invalid tweet index', 'error')
        
        elif action == 'remove_scheduled':
            try:
                index = int(request.form.get('index'))
                if 0 <= index < len(scheduled_tweets):
                    scheduled_tweets.pop(index)
                    with open(scheduled_file, 'w') as f:
                        json.dump(scheduled_tweets, f, indent=2)
                    flash('Scheduled tweet removed!', 'success')
            except (ValueError, IndexError):
                flash('Invalid scheduled tweet index', 'error')
        
        return redirect(url_for('tweets'))
    
    return render_template('tweets.html', tweet_queue=tweet_queue, scheduled_tweets=scheduled_tweets, user=user)


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)


