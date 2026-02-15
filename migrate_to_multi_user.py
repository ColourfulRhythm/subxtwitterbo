#!/usr/bin/env python3
"""
Migration Script - Convert single-user bot data to multi-user format
"""

import json
import shutil
from pathlib import Path
from user_manager import UserManager
from credentials import CredentialManager
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    """Migrate existing single-user data to multi-user format"""
    print("🔄 Starting migration to multi-user format...")
    
    # Create users directory
    users_dir = Path('users')
    users_dir.mkdir(exist_ok=True)
    
    # Default user ID
    default_user_id = "default_user"
    default_user_dir = users_dir / default_user_id
    default_user_dir.mkdir(exist_ok=True)
    
    # Migrate bot_data.json
    old_bot_data = Path('bot_data.json')
    new_bot_data = default_user_dir / 'bot_data.json'
    if old_bot_data.exists() and not new_bot_data.exists():
        print(f"📦 Migrating bot_data.json...")
        shutil.copy(old_bot_data, new_bot_data)
        print(f"✅ Migrated bot_data.json to users/{default_user_id}/bot_data.json")
    elif new_bot_data.exists():
        print(f"ℹ️  Bot data already exists for default user")
    
    # Migrate tweet_queue.json
    old_queue = Path('tweet_queue.json')
    new_queue = default_user_dir / 'tweet_queue.json'
    if old_queue.exists() and not new_queue.exists():
        print(f"📦 Migrating tweet_queue.json...")
        shutil.copy(old_queue, new_queue)
        print(f"✅ Migrated tweet_queue.json to users/{default_user_id}/tweet_queue.json")
    elif new_queue.exists():
        print(f"ℹ️  Tweet queue already exists for default user")
    
    # Create default user account
    user_manager = UserManager()
    if not user_manager.get_user(default_user_id):
        print(f"👤 Creating default user account...")
        user_manager.create_user(
            user_id=default_user_id,
            username="@default_user",
            email=None
        )
        print(f"✅ Created default user account: {default_user_id}")
    else:
        print(f"ℹ️  Default user account already exists")
    
    # Migrate Twitter credentials if they exist in .env
    print(f"🔐 Checking for Twitter credentials...")
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    access_token = os.getenv('ACCESS_TOKEN')
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('BEARER_TOKEN')
    
    if all([api_key, api_secret, access_token, access_token_secret, bearer_token]):
        cred_manager = CredentialManager(default_user_id)
        if not cred_manager.has_credentials():
            print(f"🔐 Migrating Twitter credentials...")
            cred_manager.save_credentials({
                'api_key': api_key,
                'api_secret': api_secret,
                'access_token': access_token,
                'access_token_secret': access_token_secret,
                'bearer_token': bearer_token
            })
            user_manager.set_twitter_connected(default_user_id, True)
            print(f"✅ Migrated Twitter credentials (encrypted)")
        else:
            print(f"ℹ️  Credentials already exist for default user")
    else:
        print(f"⚠️  Twitter credentials not found in .env file")
        print(f"   You can add them later via the web dashboard")
    
    print("\n✅ Migration complete!")
    print(f"\n📝 Next steps:")
    print(f"   1. Start the Flask app: python app.py")
    print(f"   2. Login with Twitter OAuth or use the default user")
    print(f"   3. Connect your Twitter account if not already done")
    print(f"   4. Start your bot from the dashboard")

if __name__ == "__main__":
    migrate()


