# Deploying Flask Web App (Multi-User Bot)

## Why Firebase Hosting Won't Work

Firebase Hosting is for **static websites** (HTML/CSS/JS). Your Flask app is a **Python web server** that needs to run continuously. Use one of these options instead:

---

## Option 1: Railway (Recommended - Free Tier)

### Steps:

1. **Push to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Flask multi-user bot"
   git remote add origin https://github.com/YOUR_USERNAME/subx-twitter-bot.git
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Go to https://railway.app
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `subx-twitter-bot` repository
   - Railway auto-detects Python and installs dependencies

3. **Add Environment Variables**:
   In Railway dashboard → Your project → Variables tab:
   ```
   FLASK_SECRET_KEY=your_secret_key_here
   TWITTER_OAUTH_API_KEY=your_oauth_api_key
   TWITTER_OAUTH_API_SECRET=your_oauth_api_secret
   PORT=5000
   FLASK_DEBUG=False
   ```

4. **Set Public URL**:
   - Railway gives you a public URL automatically
   - Update your Twitter OAuth callback URL to: `https://YOUR_APP.railway.app/auth/callback`

5. **Deploy**:
   - Railway auto-deploys on every push
   - Check logs to verify it's running

---

## Option 2: Render (Free Tier)

### Steps:

1. **Push to GitHub** (same as Railway)

2. **Create Render Account**:
   - Go to https://render.com
   - Sign up with GitHub

3. **New Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - Configure:
     - **Name:** subx-twitter-bot
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `python app.py`
     - **Plan:** Free

4. **Add Environment Variables**:
   ```
   FLASK_SECRET_KEY=your_secret_key_here
   TWITTER_OAUTH_API_KEY=your_oauth_api_key
   TWITTER_OAUTH_API_SECRET=your_oauth_api_secret
   PORT=5000
   FLASK_DEBUG=False
   ```

5. **Update Twitter OAuth Callback**:
   - Render gives you: `https://YOUR_APP.onrender.com`
   - Update callback URL to: `https://YOUR_APP.onrender.com/auth/callback`

---

## Option 3: Heroku

### Steps:

1. **Install Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku  # macOS
   ```

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create App**:
   ```bash
   heroku create subx-twitter-bot
   ```

4. **Set Environment Variables**:
   ```bash
   heroku config:set FLASK_SECRET_KEY=your_secret_key
   heroku config:set TWITTER_OAUTH_API_KEY=your_key
   heroku config:set TWITTER_OAUTH_API_SECRET=your_secret
   heroku config:set PORT=5000
   heroku config:set FLASK_DEBUG=False
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

6. **Update Twitter OAuth Callback**:
   - Heroku gives you: `https://subx-twitter-bot.herokuapp.com`
   - Update callback URL to: `https://subx-twitter-bot.herokuapp.com/auth/callback`

---

## Option 4: VPS (DigitalOcean, Linode, AWS)

### Steps:

1. **Create VPS** (Ubuntu 22.04)

2. **SSH into Server**:
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Dependencies**:
   ```bash
   apt update && apt upgrade -y
   apt install python3 python3-pip python3-venv git nginx -y
   ```

4. **Clone & Setup**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/subx-twitter-bot.git
   cd subx-twitter-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create Systemd Service**:
   ```bash
   sudo nano /etc/systemd/system/subx-bot.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=SubX Twitter Bot Flask App
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/subx-twitter-bot
   Environment="PATH=/root/subx-twitter-bot/venv/bin"
   ExecStart=/root/subx-twitter-bot/venv/bin/python app.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable subx-bot
   sudo systemctl start subx-bot
   ```

6. **Setup Nginx Reverse Proxy**:
   ```bash
   sudo nano /etc/nginx/sites-available/subx-bot
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/subx-bot /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Important: Update Twitter OAuth Callback URL

After deploying, you **MUST** update your Twitter app's callback URL:

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Select your app
3. Go to "App Settings" → "Callback URLs"
4. Add your deployment URL:
   - Railway: `https://YOUR_APP.railway.app/auth/callback`
   - Render: `https://YOUR_APP.onrender.com/auth/callback`
   - Heroku: `https://YOUR_APP.herokuapp.com/auth/callback`
   - VPS: `http://YOUR_DOMAIN/auth/callback`

---

## Environment Variables Needed

Make sure these are set in your deployment platform:

```
FLASK_SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_hex(32))"
TWITTER_OAUTH_API_KEY=your_twitter_oauth_api_key
TWITTER_OAUTH_API_SECRET=your_twitter_oauth_api_secret
PORT=5000
FLASK_DEBUG=False
```

---

## Testing Deployment

1. Visit your deployment URL
2. You should see the login page
3. Click "Login with Twitter"
4. Complete OAuth flow
5. You should be redirected to dashboard

---

## Troubleshooting

### "Callback URL not approved"
- Make sure you added the callback URL in Twitter Developer Portal
- URL must match exactly (including http/https)

### "Module not found"
- Check that `requirements.txt` is up to date
- Railway/Render auto-install, but VPS needs manual install

### App crashes on startup
- Check logs for errors
- Verify all environment variables are set
- Make sure PORT is set correctly

---

## Next Steps

After deployment:
1. Test login flow
2. Connect Twitter account
3. Add tweets to queue
4. Set keywords
5. Start bot from dashboard

