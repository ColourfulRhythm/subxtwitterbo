# 🚀 Quick Deploy Guide

## Option 1: Use the Deployment Script (Easiest)

```bash
./deploy.sh
```

Follow the prompts. The script will:
1. Update git remote
2. Stage all files
3. Commit changes
4. Push to GitHub

## Option 2: Manual Steps

### 1. Update Git Remote
```bash
git remote remove origin
git remote add origin https://github.com/ColourfulRhythm/subxtwitterbo.git
git remote -v  # Verify
```

### 2. Stage and Commit
```bash
git add .
git commit -m "Add Twitter API service with Vercel deployment"
```

### 3. Push to GitHub
```bash
# If repository is empty:
git push -u origin main --force

# If repository has content:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### 4. Deploy to Vercel

**Via Dashboard:**
1. Go to https://vercel.com/dashboard
2. Click **"Add New Project"**
3. Import: `ColourfulRhythm/subxtwitterbo`
4. Add Environment Variables:
   ```
   API_KEY=your_key
   API_SECRET=your_secret
   ACCESS_TOKEN=your_token
   ACCESS_TOKEN_SECRET=your_secret
   BEARER_TOKEN=your_bearer
   API_SECRET_KEY=your_random_secret
   ```
5. Click **"Deploy"**

**Via CLI:**
```bash
npm i -g vercel
vercel login
vercel
# Follow prompts, then:
vercel env add API_KEY
vercel env add API_SECRET
vercel env add ACCESS_TOKEN
vercel env add ACCESS_TOKEN_SECRET
vercel env add BEARER_TOKEN
vercel env add API_SECRET_KEY
vercel --prod
```

## ✅ Verify Deployment

Test your API:
```bash
curl https://your-app.vercel.app/health
```

## 📚 Full Documentation

- `DEPLOY_VERCEL.md` - Detailed Vercel setup
- `PUSH_TO_GITHUB.md` - GitHub push instructions
- `API_README.md` - API documentation
- `NEXT_STEPS.md` - Integration guide

