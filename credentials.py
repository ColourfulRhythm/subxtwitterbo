#!/usr/bin/env python3
"""
Credential Management - Secure storage and retrieval of Twitter API credentials
Uses Fernet symmetric encryption for credential storage
"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from dotenv import load_dotenv

load_dotenv()

# Get encryption key from environment or generate one
def get_or_create_key():
    """Get encryption key from environment or generate a new one"""
    key_env = os.getenv('ENCRYPTION_KEY')
    if key_env:
        # If key is provided, use it (should be base64 encoded)
        try:
            return base64.urlsafe_b64decode(key_env.encode())
        except:
            # If not base64, treat as password and derive key
            return derive_key_from_password(key_env)
    else:
        # Generate a key file
        key_file = Path('.encryption_key')
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Add to .gitignore
            gitignore = Path('.gitignore')
            if gitignore.exists():
                with open(gitignore, 'r') as f:
                    if '.encryption_key' not in f.read():
                        with open(gitignore, 'a') as f:
                            f.write('\n.encryption_key\n')
            else:
                with open(gitignore, 'w') as f:
                    f.write('.encryption_key\n')
            return key

def derive_key_from_password(password: str):
    """Derive a key from a password using PBKDF2"""
    password_bytes = password.encode()
    salt = b'fixed_salt_for_twitter_bot'  # In production, use random salt per user
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key

class CredentialManager:
    """Manages encrypted storage of Twitter API credentials"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_dir = Path('users') / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.credential_file = self.user_dir / 'credentials.enc'
        
        # Get or create encryption key
        key = get_or_create_key()
        self.cipher = Fernet(key)
    
    def save_credentials(self, credentials: dict):
        """
        Save encrypted Twitter credentials
        
        Args:
            credentials: Dict with keys: api_key, api_secret, access_token, 
                        access_token_secret, bearer_token
        """
        # Validate required fields
        required = ['api_key', 'api_secret', 'access_token', 'access_token_secret', 'bearer_token']
        for field in required:
            if field not in credentials:
                raise ValueError(f"Missing required credential: {field}")
        
        # Encrypt credentials
        credentials_json = json.dumps(credentials)
        encrypted_data = self.cipher.encrypt(credentials_json.encode())
        
        # Save to file
        with open(self.credential_file, 'wb') as f:
            f.write(encrypted_data)
    
    def load_credentials(self) -> dict:
        """Load and decrypt Twitter credentials"""
        if not self.credential_file.exists():
            raise FileNotFoundError(f"No credentials found for user {self.user_id}")
        
        # Read encrypted file
        with open(self.credential_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            return credentials
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {e}")
    
    def has_credentials(self) -> bool:
        """Check if credentials exist for this user"""
        return self.credential_file.exists()
    
    def delete_credentials(self):
        """Delete stored credentials"""
        if self.credential_file.exists():
            self.credential_file.unlink()
    
    def save_oauth_tokens(self, oauth_token: str, oauth_token_secret: str, 
                         api_key: str = None, api_secret: str = None):
        """
        Save OAuth tokens (alternative to manual API keys)
        
        Args:
            oauth_token: OAuth access token
            oauth_token_secret: OAuth access token secret
            api_key: Optional API key (consumer key)
            api_secret: Optional API secret (consumer secret)
        """
        credentials = {
            'access_token': oauth_token,
            'access_token_secret': oauth_token_secret,
            'bearer_token': '',  # OAuth doesn't provide bearer token directly
        }
        
        if api_key:
            credentials['api_key'] = api_key
        if api_secret:
            credentials['api_secret'] = api_secret
        
        self.save_credentials(credentials)


