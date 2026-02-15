# Deploy to Vercel - Step by Step Guide

## Prerequisites

1. GitHub account
2. Vercel account (sign up at https://vercel.com)
3. Your Twitter API credentials

## Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add the remote repository
git remote add origin https://github.com/ColourfulRhythm/subxtwitterbo.git

# Stage all relevant files
git add .

# Commit
git commit -m "Initial commit: Twitter API service"

# Push to GitHub
git push -u origin main
```

If the repository already exists and has content:
```bash
git pull origin main --allow-unrelated-histories
# Resolve any conflicts, then:
git push -u origin main
```

## Step 2: Deploy to Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Click **"Add New Project"**
3. Import your GitHub repository: `ColourfulRhythm/subxtwitterbo`
4. Vercel will auto-detect Python
5. **Add Environment Variables:**
   - `API_KEY` - Your Twitter API Key
   - `API_SECRET` - Your Twitter API Secret
   - `ACCESS_TOKEN` - Your Twitter Access Token
   - `ACCESS_TOKEN_SECRET` - Your Twitter Access Token Secret
   - `BEARER_TOKEN` - Your Twitter Bearer Token
   - `API_SECRET_KEY` - Your API authentication key (generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"`)
   - `API_PORT` - Leave empty (Vercel handles this)
   - `API_HOST` - Leave empty (Vercel handles this)

6. Click **"Deploy"**

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name? subx-twitter-api (or your choice)
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add API_KEY
vercel env add API_SECRET
vercel env add ACCESS_TOKEN
vercel env add ACCESS_TOKEN_SECRET
vercel env add BEARER_TOKEN
vercel env add API_SECRET_KEY

# Redeploy with env vars
vercel --prod
```

## Step 3: Test Your Deployment

Once deployed, Vercel will give you a URL like:
`https://subx-twitter-api.vercel.app`

Test it:
```bash
# Health check
curl https://your-app.vercel.app/health

# Test posting (replace YOUR_SECRET_KEY)
curl -X POST https://your-app.vercel.app/api/post-tweet \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_SECRET_KEY" \
  -d '{"tweet": "🧪 Test from Vercel!"}'
```

## Step 4: Update Your Webapp

Update your webapp to use the Vercel URL:

```javascript
// In your webapp
const TWITTER_API_URL = 'https://your-app.vercel.app/api/post-tweet';
```

## Important Notes

⚠️ **Vercel Serverless Functions:**
- Vercel uses serverless functions, so the API runs on-demand
- Cold starts may add ~1-2 seconds on first request
- Free tier has execution time limits (10 seconds)
- For long-running processes, consider Railway or Render

⚠️ **Environment Variables:**
- Never commit `.env` file to GitHub
- Always add env vars in Vercel dashboard
- Each environment (production, preview) needs separate env vars

⚠️ **Rate Limits:**
- Vercel free tier: 100GB bandwidth/month
- Twitter API: Respects rate limits automatically

## Troubleshooting

**Build fails:**
- Check that `requirements.txt` includes all dependencies
- Verify Python version in `vercel.json` (if specified)

**401 Unauthorized:**
- Check environment variables are set correctly in Vercel
- Verify `API_SECRET_KEY` matches what you're sending

**Function timeout:**
- Vercel free tier: 10 seconds max
- If you need longer, upgrade or use Railway/Render

**Import errors:**
- Make sure all dependencies are in `requirements.txt`
- Check that `twitter_api.py` is in the root directory

## Alternative: Deploy to Railway (Better for Long-Running)

If you need a traditional server (not serverless), Railway is better:

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. Add environment variables
5. Set start command: `python3 twitter_api.py`
6. Deploy!

Railway is better for:
- Long-running processes
- No cold starts
- More predictable performance
- Better for the main `bot.py` scheduler

