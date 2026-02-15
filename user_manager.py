#!/usr/bin/env python3
"""
User Management - Handles user accounts and authentication
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from credentials import CredentialManager

class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, users_file: str = 'users.json'):
        self.users_file = Path(users_file)
        self.users = self._load_users()
    
    def _load_users(self) -> dict:
        """Load users from JSON file"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def create_user(self, user_id: str, username: str, email: str = None, 
                   twitter_id: str = None) -> Dict:
        """
        Create a new user account
        
        Args:
            user_id: Unique user identifier (e.g., Twitter user ID)
            username: Username (e.g., Twitter handle)
            email: Optional email address
            twitter_id: Optional Twitter ID
            
        Returns:
            User data dictionary
        """
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'twitter_id': twitter_id,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'twitter_connected': False,
            'bot_active': False,
            'bot_config': self._get_default_config()
        }
        
        self.users[user_id] = user_data
        self._save_users()
        
        # Create user directory
        user_dir = Path('users') / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user data by user_id"""
        return self.users.get(user_id)
    
    def update_user(self, user_id: str, **kwargs):
        """Update user data"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        for key, value in kwargs.items():
            if key in self.users[user_id]:
                self.users[user_id][key] = value
        
        self._save_users()
    
    def set_twitter_connected(self, user_id: str, connected: bool = True):
        """Mark user's Twitter account as connected"""
        self.update_user(user_id, twitter_connected=connected)
    
    def set_bot_active(self, user_id: str, active: bool):
        """Set bot active status for user"""
        self.update_user(user_id, bot_active=active)
    
    def get_user_by_twitter_id(self, twitter_id: str) -> Optional[Dict]:
        """Find user by Twitter ID"""
        for user in self.users.values():
            if user.get('twitter_id') == twitter_id:
                return user
        return None
    
    def list_users(self) -> list:
        """List all users"""
        return list(self.users.values())
    
    def _get_default_config(self) -> dict:
        """Get default bot configuration"""
        return {
            'tweets_per_day': 6,
            'posting_times': ['16:00', '20:00', '00:00', '04:00', '08:00', '12:00'],
            'engagement_interval': 15,  # minutes
            'max_replies_per_hour': 5,
            'keywords': {
                'betting': [
                    'betting loss Nigeria',
                    'lost money betting',
                    'stop betting',
                    'gambling addiction',
                    'bet9ja losses',
                    'sports betting',
                    'sports betting waste',
                    'betking loss',
                    'sportybet loss',
                    'bet9ja regret'
                ],
                'investment': [
                    'how to invest Nigeria',
                    'passive income Nigeria',
                    'investment opportunities',
                    'investment opportunities Nigeria',
                    'where to invest',
                    'where to invest Nigeria',
                    'wealth building',
                    'small money investment'
                ],
                'land': [
                    'buy land Lagos',
                    'buy land Abeokuta',
                    'land ownership Nigeria',
                    'affordable land',
                    'affordable land Nigeria',
                    'land investment',
                    'real estate Lagos',
                    'farmland Nigeria',
                    'real estate investment Nigeria',
                    'property investment Nigeria'
                ],
                'co_ownership': [
                    'fractional ownership',
                    'fractional ownership Nigeria',
                    'co-ownership property',
                    'shared ownership',
                    'shared ownership real estate',
                    'real estate syndication',
                    'group land purchase'
                ]
            }
        }
    
    def get_user_config(self, user_id: str) -> dict:
        """Get user's bot configuration"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user.get('bot_config', self._get_default_config())
    
    def update_user_config(self, user_id: str, config: dict):
        """Update user's bot configuration"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Merge with existing config
        current_config = user.get('bot_config', {})
        current_config.update(config)
        self.update_user(user_id, bot_config=current_config)
    
    def get_user_credentials(self, user_id: str) -> Optional[dict]:
        """Get user's Twitter credentials (decrypted)"""
        try:
            cred_manager = CredentialManager(user_id)
            if cred_manager.has_credentials():
                return cred_manager.load_credentials()
        except Exception as e:
            print(f"Error loading credentials for {user_id}: {e}")
        return None


