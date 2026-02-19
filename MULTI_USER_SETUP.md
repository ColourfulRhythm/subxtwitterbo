# Multi-User Twitter Bot System - Setup Guide

## Overview

The bot has been transformed into a multi-user web application where multiple users can:
- Login with Twitter OAuth
- Connect their Twitter accounts (OAuth or manual credentials)
- Run their own bot instances with isolated data
- Manage bot settings and view statistics via web dashboard

## Architecture

- **Web Application**: Flask-based dashboard (`app.py`)
- **User Management**: JSON-based user accounts (`user_manager.py`)
- **Credential Security**: Encrypted storage (`credentials.py`)
- **Bot Core**: Multi-user bot engine (`bot_core.py`)
- **Bot Manager**: Manages multiple concurrent bot instances (`bot_manager.py`)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migration (if migrating from single-user)

```bash
python migrate_to_multi_user.py
```

This will:
- Migrate existing `bot_data.json` and `tweet_queue.json` to `users/default_user/`
- Create a default user account
- Migrate Twitter credentials from `.env` (if present)

### 3. Configure Environment Variables

Create a `.env` file with:

```env
# Twitter OAuth (for user login)
TWITTER_OAUTH_API_KEY=your_oauth_api_key
TWITTER_OAUTH_API_SECRET=your_oauth_api_secret

# Flask Configuration
FLASK_SECRET_KEY=generate_with_secrets_token_hex_32
FLASK_DEBUG=False
PORT=5000
```

### 4. Start the Web Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 5. Access the Dashboard

1. Open ` http://localhost:5000` in your browser
2. Click "Login with Twitter"
3. Authorize the application
4. Connect your Twitter account (OAuth or manual)
5. Start your bot from the dashboard

## User Flow

### First Time Setup

1. **Login**: User logs in with Twitter OAuth
2. **Connect Twitter**: User connects their Twitter account (for bot to use)
   - Option A: OAuth flow (recommended)
   - Option B: Manual credential entry
3. **Configure**: User sets bot settings (posting times, keywords, etc.)
4. **Start Bot**: User starts their bot instance from dashboard

### Daily Use

- View statistics on dashboard
- Adjust settings as needed
- Start/stop bot as desired
- View detailed statistics

## Data Structure

Each user has their own directory:

```
users/
  {user_id}/
    bot_data.json          # Bot state and statistics
    tweet_queue.json       # User's tweet queue
    credentials.enc         # Encrypted Twitter credentials
    config.json            # User-specific bot configuration (stored in users.json)
```

## API Endpoints

- `GET /` - Landing page (redirects to login or dashboard)
- `GET /login` - Login page
- `GET /auth/twitter` - Initiate Twitter OAuth
- `GET /auth/callback` - OAuth callback handler
- `GET /dashboard` - Main dashboard
- `GET /settings` - Bot configuration
- `GET /stats` - Detailed statistics
- `GET /connect-twitter` - Connect Twitter account
- `POST /api/bot/start` - Start bot instance
- `POST /api/bot/stop` - Stop bot instance
- `GET /api/bot/status` - Get bot status

## Security Features

1. **Credential Encryption**: All Twitter API credentials encrypted at rest using Fernet
2. **Session Security**: Flask sessions with secure cookies
3. **OAuth State Validation**: CSRF protection for OAuth flow
4. **User Isolation**: Strict file path validation
5. **Per-User Rate Limiting**: Each bot instance has its own rate limits

## Deployment

### Railway/Render

Update `Procfile`:
```
web: python app.py
```

Set environment variables:
- `FLASK_SECRET_KEY`
- `TWITTER_OAUTH_API_KEY`
- `TWITTER_OAUTH_API_SECRET`
- `PORT` (usually auto-set)

### Local Development

```bash
export FLASK_DEBUG=True
python app.py
```

## Troubleshooting

### Bot Not Starting

1. Check if Twitter account is connected
2. Verify credentials are valid
3. Check bot logs in console
4. Verify user has proper permissions

### OAuth Not Working

1. Verify `TWITTER_OAUTH_API_KEY` and `TWITTER_OAUTH_API_SECRET` are set
2. Check callback URL is correct in Twitter app settings
3. Ensure app has read/write permissions

### Multiple Bots Interfering

Each bot instance runs in its own thread with isolated data. The schedule library uses a global scheduler, but each bot's methods are bound to its instance, so they operate independently.

## Migration Notes

- Original `bot.py` is preserved for backward compatibility
- Original data files are not deleted during migration
- Default user is created with ID `default_user`
- Existing credentials from `.env` are migrated if present

## Next Steps

1. Customize templates in `templates/` directory
2. Add more bot features in `bot_core.py`
3. Extend user management in `user_manager.py`
4. Add database support (replace JSON files) if needed for scale


