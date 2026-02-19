#!/usr/bin/env python3
"""
Generate a secure API_SECRET_KEY for Vercel
NOTE: This is NOT a Twitter credential - it's a custom secret for your API
"""
import secrets
import string

# Generate a secure random string (32-64 characters is good)
# You can make it any length you want
key_length = 32  # Change this to whatever length you prefer
alphabet = string.ascii_letters + string.digits + '-_'
api_key = ''.join(secrets.choice(alphabet) for _ in range(key_length))

print("=" * 60)
print("🔐 API_SECRET_KEY Generator")
print("=" * 60)
print()
print("⚠️  IMPORTANT: This is NOT a Twitter credential!")
print("   This is a custom secret key for authenticating API requests.")
print("   It can be any length you want (recommended: 32-64 characters).")
print()
print("Generated API Key:")
print(api_key)
print(f"Length: {len(api_key)} characters")
print()
print("=" * 60)
print("📋 Next Steps:")
print("=" * 60)
print()
print("1. Copy the API key above")
print("2. Go to Vercel Dashboard → Your Project → Settings → Environment Variables")
print("3. Add or update API_SECRET_KEY with the value above")
print("   (This is separate from Twitter credentials like BEARER_TOKEN)")
print("4. Redeploy your project")
print()
print("5. Use this key in your webapp when calling the API:")
print(f'   headers: {{ "X-API-Key": "{api_key}" }}')
print()
print("=" * 60)
