# SubX Twitter Bot - Deployment Guide

## 🚨 SECURITY FIRST

**YOUR CREDENTIALS WERE EXPOSED!** Before doing ANYTHING:

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Select your app
3. Go to "Keys and tokens"
4. Click "Regenerate" on ALL credentials:
   - API Key & Secret
   - Access Token & Secret
   - Bearer Token
5. Save new credentials securely

---

## Option 1: Railway (Recommended - Free Tier)

### Why Railway?
- Free tier: 500 hours/month (enough for 24/7)
- Auto-deploys from GitHub
- Easy environment variable management
- Built-in logging

### Steps:

1. **Create GitHub Repository**
   ```bash
   cd subx-twitter-bot
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create subx-twitter-bot --private --source=. --remote=origin --push
   # Or manually create repo on GitHub and push
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `subx-twitter-bot` repository
   - Railway auto-detects Python and installs dependencies

3. **Add Environment Variables**
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add each credential:
     ```
     API_KEY=your_regenerated_api_key
     API_SECRET=your_regenerated_api_secret
     ACCESS_TOKEN=your_regenerated_access_token
     ACCESS_TOKEN_SECRET=your_regenerated_access_token_secret
     BEARER_TOKEN=your_regenerated_bearer_token
     ```

4. **Deploy**
   - Click "Deploy"
   - Check logs to verify it's running
   - Bot will post first tweet at next scheduled time (8 AM, 2 PM, or 7 PM WAT)

5. **Monitor**
   - View logs in Railway dashboard
   - Check Twitter to see bot activity
   - Stats saved in persistent storage

---

## Option 2: Render (Free Tier Alternative)

### Steps:

1. **Push to GitHub** (same as Railway step 1)

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **New Background Worker**
   - Click "New +" → "Background Worker"
   - Connect GitHub repo
   - Configure:
     - **Name:** subx-twitter-bot
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python bot.py`
     - **Plan:** Free

4. **Add Environment Variables**
   - In "Environment" tab, add:
     ```
     API_KEY=your_value
     API_SECRET=your_value
     ACCESS_TOKEN=your_value
     ACCESS_TOKEN_SECRET=your_value
     BEARER_TOKEN=your_value
     ```

5. **Deploy**
   - Render automatically builds and deploys
   - Check logs for confirmation

---

## Option 3: VPS (DigitalOcean, Linode, AWS, etc.)

### Best for: Full control, dedicated resources

### Steps:

1. **Create VPS**
   - DigitalOcean Droplet (basic $6/month)
   - Ubuntu 22.04 LTS
   - SSH access enabled

2. **SSH into Server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   apt update && apt upgrade -y
   
   # Install Python
   apt install python3 python3-pip git -y
   
   # Clone repo
   git clone https://github.com/your-username/subx-twitter-bot.git
   cd subx-twitter-bot
   
   # Install Python packages
   pip3 install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.template .env
   nano .env  # Add your credentials
   ```

5. **Run as System Service**
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/subx-bot.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=SubX Twitter Bot
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/subx-twitter-bot
   ExecStart=/usr/bin/python3 /root/subx-twitter-bot/bot.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable subx-bot
   sudo systemctl start subx-bot
   ```

6. **Monitor**
   ```bash
   # Check status
   sudo systemctl status subx-bot
   
   # View logs
   sudo journalctl -u subx-bot -f
   
   # Restart if needed
   sudo systemctl restart subx-bot
   ```

---

## Option 4: Local Development/Testing

### Steps:

1. **Clone/Download Code**
   ```bash
   cd subx-twitter-bot
   ```

2. **Run Setup Script**
   ```bash
   bash setup.sh
   ```

3. **Add Credentials**
   - Edit `.env` file
   - Add your Twitter API credentials

4. **Test Run**
   ```bash
   python3 bot.py
   ```

5. **Keep Running**
   ```bash
   # With nohup (keeps running after terminal closes)
   nohup python3 bot.py > bot.log 2>&1 &
   
   # Check logs
   tail -f bot.log
   
   # Stop bot
   pkill -f bot.py
   ```

---

## Post-Deployment Checklist

✅ **Verify Credentials**
   - All 5 credentials added correctly
   - No placeholder values remaining

✅ **Check Logs**
   - Bot started successfully
   - No authentication errors
   - Scheduled tasks registered

✅ **Test Functionality**
   - Wait for next scheduled time (8 AM, 2 PM, 7 PM WAT)
   - Verify tweet posted to your account
   - Check engagement scan is running

✅ **Monitor Performance**
   - Check dashboard: `python3 dashboard.py`
   - Review daily stats
   - Ensure no rate limit errors

✅ **Customize Content** (optional)
   - Edit `tweet_queue.json` for your brand voice
   - Adjust keywords in `bot.py`
   - Modify reply templates

---

## Monitoring & Maintenance

### View Live Stats
```bash
# Interactive dashboard
python3 dashboard.py

# Quick stats
python3 dashboard.py stats

# View queue
python3 dashboard.py queue

# Export CSV
python3 dashboard.py export
```

### Check Bot Health

**Railway/Render:**
- View logs in dashboard
- Check for errors
- Monitor uptime

**VPS:**
```bash
# Service status
sudo systemctl status subx-bot

# Live logs
sudo journalctl -u subx-bot -f

# Restart if needed
sudo systemctl restart subx-bot
```

### Update Tweet Queue

1. Edit `tweet_queue.json`
2. Add/remove/modify tweets
3. Bot automatically picks up changes

### Update Keywords/Replies

1. Edit `bot.py`
2. Modify `KEYWORDS` or `REPLY_TEMPLATES`
3. Restart bot:
   - Railway/Render: Commit & push (auto-deploys)
   - VPS: `sudo systemctl restart subx-bot`

---

## Troubleshooting

### Bot Not Posting

**Check:**
1. Credentials in `.env` are correct
2. Current time matches scheduled times (8 AM, 2 PM, 7 PM WAT)
3. Tweet queue isn't empty
4. No rate limit errors in logs

### Authentication Errors

**Fix:**
1. Regenerate ALL Twitter API credentials
2. Update `.env` file
3. Restart bot

### "Module not found" Error

**Fix:**
```bash
pip3 install -r requirements.txt --upgrade
```

### Bot Stopped Running

**Railway/Render:**
- Check deployment logs
- Verify environment variables

**VPS:**
```bash
sudo systemctl status subx-bot
sudo systemctl restart subx-bot
```

---

## Best Practices

1. **Monitor Daily**
   - Check stats dashboard
   - Review engagement quality
   - Adjust keywords if needed

2. **Update Content Weekly**
   - Refresh tweet queue
   - Remove underperforming tweets
   - Add trending topics

3. **Track Performance**
   - Export CSV weekly
   - Analyze engagement patterns
   - Optimize posting times

4. **Respect Rate Limits**
   - Don't exceed max_replies_per_hour
   - Keep engagement authentic
   - Quality > quantity

5. **Backup Data**
   - Export `bot_data.json` weekly
   - Save `tweet_queue.json` versions
   - Track successful patterns

---

## Success Metrics

Track these weekly:

- **Tweets Posted:** Should be 21/week (3/day)
- **Replies Sent:** Should be ~350/week (50/day max)
- **Engagement Rate:** Monitor likes/retweets
- **Follower Growth:** Track weekly increase
- **Link Clicks:** Use UTM parameters

---

## Need Help?

1. Check logs first
2. Review README.md
3. Run dashboard for diagnostics
4. Verify credentials haven't expired

---

**Remember:** This bot represents your brand. Monitor it regularly to ensure quality engagement! 🚀
