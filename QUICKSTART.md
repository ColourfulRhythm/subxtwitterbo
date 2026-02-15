# SubX Twitter Bot - Quick Start ⚡

## 🚨 CRITICAL FIRST STEP

**Your Twitter credentials were exposed in the chat!**

**DO THIS NOW:**
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Regenerate ALL keys and tokens
3. Save them securely

---

## What This Bot Does

✅ Posts 3 tweets daily (8 AM, 2 PM, 7 PM WAT)  
✅ Monitors Twitter for keywords (betting, investing, land ownership)  
✅ Auto-replies to relevant conversations  
✅ Tracks performance with analytics  
✅ 90 pre-written tweets ready to go  

---

## Fastest Setup (5 Minutes)

### 1. Get New Twitter API Credentials

Required:
- API Key
- API Secret
- Access Token
- Access Token Secret
- Bearer Token

Get them: https://developer.twitter.com/en/portal/dashboard → "Keys and tokens" → "Regenerate"

### 2. Deploy to Railway (Free)

```bash
# 1. Sign up: https://railway.app
# 2. Click "New Project" → "Deploy from GitHub repo"
# 3. Connect this repository
# 4. Add environment variables (your 5 credentials)
# 5. Deploy!
```

**That's it!** Bot runs 24/7 for free.

---

## What's Included

### Files:
- `bot.py` - Main bot (scheduling + engagement)
- `tweet_queue.json` - 90 pre-written tweets
- `dashboard.py` - View stats & manage bot
- `requirements.txt` - Python dependencies
- `.env.template` - Credentials template

### Features:
- **Smart scheduling** - Optimal posting times
- **Auto-engagement** - Replies to relevant tweets
- **Rate limiting** - Respects Twitter limits
- **Analytics** - Tracks all activity
- **Persistent storage** - Remembers state

---

## View Statistics

```bash
python3 dashboard.py
```

Shows:
- Total tweets posted
- Total replies sent
- Daily performance
- Next scheduled tweet

---

## Customize

### Change Tweet Times
Edit `bot.py`:
```python
CONFIG['posting_times'] = ['08:00', '14:00', '19:00']
```

### Add/Edit Tweets
Edit `tweet_queue.json`:
```json
[
  "Your custom tweet here...",
  "Another tweet...",
]
```

### Change Keywords
Edit `bot.py` → `KEYWORDS` section

---

## Monitor

### Railway/Render
- Check dashboard logs
- View deployment status
- Monitor uptime

### Local/VPS
```bash
# View logs
tail -f bot.log

# Check stats
python3 dashboard.py stats
```

---

## Tweet Examples (From Queue)

1. "Most Nigerians think ₦1M is too small to invest in real estate. That's why most Nigerians will never own land..."

2. "You spend ₦5k on betting weekly. That's ₦240k yearly. Enough to own 48 sqm in 2 Seasons..."

3. "Co-ownership isn't 'sharing' land like splitting rice. It's owning a legal fraction with documented rights..."

**90 total tweets ready!**

---

## Need Help?

1. **README.md** - Full documentation
2. **DEPLOYMENT.md** - Detailed deployment guide
3. **Dashboard** - `python3 dashboard.py` for diagnostics

---

## Warning Signs

❌ "Authentication failed" → Regenerate credentials  
❌ "Rate limit exceeded" → Bot auto-handles this  
❌ Bot not posting → Check scheduled times (WAT)  

---

## Success Checklist

✅ Credentials regenerated (NOT the exposed ones!)  
✅ Bot deployed to Railway/Render/VPS  
✅ Environment variables added  
✅ First tweet posted successfully  
✅ Engagement scan running  
✅ Dashboard shows activity  

---

**You're all set! Bot will:**
- Post at 8 AM, 2 PM, 7 PM WAT daily
- Reply to ~50 relevant tweets daily
- Track all activity automatically

**Monitor weekly and adjust as needed.** 🚀

---

Questions? Check DEPLOYMENT.md for detailed guides.
