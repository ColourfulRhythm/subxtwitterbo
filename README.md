# SubX Twitter Bot 🤖

Automated Twitter bot for scheduling tweets and engaging with relevant conversations about land ownership, co-ownership, and anti-betting content.

## Features

✅ **Automated Tweet Scheduling** - Posts 3x daily at optimal times (8 AM, 2 PM, 7 PM WAT)  
✅ **Keyword Monitoring** - Tracks conversations about betting, investing, land ownership  
✅ **Smart Auto-Replies** - Engages with relevant tweets automatically  
✅ **Rate Limiting** - Respects Twitter API limits to avoid suspension  
✅ **Analytics Tracking** - Monitors performance and engagement  
✅ **Persistent Storage** - Remembers state between restarts  

## Quick Start

### 1. Get Twitter API Credentials

**CRITICAL: Regenerate your credentials since they were exposed!**

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new project/app (or select existing)
3. Go to "Keys and tokens" tab
4. **Regenerate ALL keys and tokens**
5. Save them securely (you'll need them in step 3)

**Required credentials:**
- API Key (Consumer Key)
- API Secret (Consumer Secret)
- Access Token
- Access Token Secret
- Bearer Token

### 2. Install Dependencies

```bash
# Install Python 3.8+ if not installed
python3 --version

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit .env and add your credentials
nano .env  # or use any text editor
```

**Your .env file should look like:**
```
API_KEY=xxxxxxxxxxxxxxxxxxx
API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ACCESS_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxx
BEARER_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**IMPORTANT:** Never commit `.env` to Git! It's already in `.gitignore`.

### 4. Test the Bot

```bash
# Run once to verify everything works
python3 bot.py
```

You should see:
```
🤖 SubX Twitter Bot Started
📅 Scheduled tweets: ['08:00', '14:00', '19:00']
🔍 Engagement scans: Every 15 minutes
💬 Max replies/hour: 5

📊 BOT STATISTICS
==================
Total tweets posted: 0
Total replies sent: 0
...
```

Press `Ctrl+C` to stop.

## Running the Bot 24/7

### Option A: Deploy to Railway (Recommended - Free)

1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your GitHub account
4. Push this code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```
5. In Railway:
   - Select your repo
   - Add environment variables (from your .env file)
   - Deploy!

### Option B: Deploy to Render

1. Create account at https://render.com
2. Click "New +" → "Background Worker"
3. Connect GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. Add environment variables
6. Deploy!

### Option C: Run on VPS (DigitalOcean, Linode, etc.)

```bash
# SSH into your server
ssh user@your-server-ip

# Clone repo
git clone YOUR_REPO_URL
cd subx-twitter-bot

# Install dependencies
pip3 install -r requirements.txt

# Set up environment variables
cp .env.template .env
nano .env  # Add your credentials

# Run with nohup (keeps running after logout)
nohup python3 bot.py > bot.log 2>&1 &

# Check logs
tail -f bot.log
```

### Option D: Use systemd (Linux servers)

Create a service file:

```bash
sudo nano /etc/systemd/system/subx-bot.service
```

Add:
```ini
[Unit]
Description=SubX Twitter Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/subx-twitter-bot
ExecStart=/usr/bin/python3 /path/to/subx-twitter-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable subx-bot
sudo systemctl start subx-bot
sudo systemctl status subx-bot

# View logs
sudo journalctl -u subx-bot -f
```

## Configuration

Edit `bot.py` to customize:

```python
CONFIG = {
    'tweets_per_day': 3,  # Number of scheduled tweets
    'posting_times': ['08:00', '14:00', '19:00'],  # When to post (24hr format)
    'engagement_interval': 15,  # Minutes between engagement scans
    'max_replies_per_hour': 5,  # Rate limit for replies
}
```

## Tweet Queue Management

Edit `tweet_queue.json` to:
- Add new tweets
- Remove tweets
- Reorder tweets
- Update messaging

The bot loops through the queue automatically.

## Monitoring

### View Statistics

The bot prints stats:
- Every time it runs an action
- Daily at 11:59 PM
- When you stop it (Ctrl+C)

### Check bot_data.json

```bash
cat bot_data.json
```

Shows:
- Current tweet index
- Total tweets posted
- Total replies sent
- Daily statistics
- Replied tweet IDs (to avoid duplicates)

## Customization

### Add New Keywords

Edit `KEYWORDS` in `bot.py`:

```python
KEYWORDS = {
    'betting': ['betting loss', 'lost money betting', ...],
    'investment': ['how to invest', 'passive income', ...],
    # Add your own categories
    'your_category': ['keyword1', 'keyword2', ...]
}
```

### Add New Reply Templates

Edit `REPLY_TEMPLATES` in `bot.py`:

```python
REPLY_TEMPLATES = {
    'betting': [
        "Your custom reply here...",
        "Another reply option...",
    ],
    # Match your keyword categories
}
```

### Change Posting Schedule

```python
CONFIG['posting_times'] = ['06:00', '12:00', '18:00']  # 3x daily
# Or
CONFIG['posting_times'] = ['08:00', '11:00', '14:00', '17:00', '20:00']  # 5x daily
```

## Safety Features

✅ **Rate Limiting** - Respects Twitter API limits  
✅ **Duplicate Prevention** - Never replies to same tweet twice  
✅ **Error Handling** - Continues running even if API calls fail  
✅ **Graceful Shutdown** - Saves state before stopping  
✅ **Daily Limits** - Max 120 replies/day (5/hour * 24)  

## Troubleshointing

### "Authentication Error"
- Check your API credentials in `.env`
- Make sure you regenerated them (they were exposed)
- Verify Bearer Token is correct

### "Rate Limit Exceeded"
- Bot automatically waits and retries
- Reduce `max_replies_per_hour` if needed
- Twitter free tier: 500k tweets/month read, 1.7k/month write

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Bot stops responding
- Check if process is still running: `ps aux | grep bot.py`
- Check logs: `tail -f bot.log`
- Restart: `python3 bot.py`

## Best Practices

1. **Monitor daily** - Check stats and engagement
2. **Update tweets weekly** - Keep content fresh
3. **Adjust keywords** - Based on what works
4. **Review replies** - Ensure quality engagement
5. **Track conversions** - Use UTM parameters in links

## Security

🔒 **Never share your API credentials**  
🔒 **Never commit `.env` to Git**  
🔒 **Regenerate tokens if exposed**  
🔒 **Use environment variables in production**  

## Support

Questions? Issues?
- Check logs: `tail -f bot.log`
- Review bot_data.json for state
- Test manually: `python3 bot.py`

## License

Private use for SubX only.

---

**Built with ❤️ for SubX - Democratizing Land Ownership in Nigeria** 🚀
