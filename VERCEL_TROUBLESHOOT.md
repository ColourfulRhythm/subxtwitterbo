# Vercel Deployment Troubleshooting

## Current Issue: 404 Not Found

## Quick Fix Steps

1. **Commit and push the fixes:**
```bash
git add api/index.py vercel.json
git commit -m "Fix Vercel Flask app export"
git push origin main
```

2. **Check Vercel Build Logs:**
   - Go to Vercel Dashboard → Your Project
   - Click on the latest deployment
   - Check "Build Logs" for errors
   - Check "Function Logs" for runtime errors

3. **Verify Environment Variables:**
   Make sure all these are set in Vercel:
   - `API_KEY`
   - `API_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
   - `API_SECRET_KEY`

## Common Issues

### Issue 1: Build Fails
**Symptom:** Build logs show import errors
**Fix:** Check that `requirements.txt` includes all dependencies

### Issue 2: Function Not Found
**Symptom:** 404 on all routes
**Fix:** 
- Verify `vercel.json` routes point to `api/index.py`
- Check that `api/index.py` exists and exports `app`

### Issue 3: Import Errors
**Symptom:** Runtime errors about missing modules
**Fix:** 
- Ensure all dependencies in `requirements.txt`
- Check Vercel is using Python 3.11 (add to `vercel.json` if needed)

### Issue 4: Environment Variables Not Set
**Symptom:** 500 errors or authentication failures
**Fix:** Add all required env vars in Vercel dashboard

## Test After Fix

```bash
# Health check
curl https://subxtwitterbo.vercel.app/health

# Should return:
# {"status":"ok","service":"Twitter API",...}

# API endpoint
curl https://subxtwitterbo.vercel.app/api/post-tweet

# Should return API documentation (GET request)
```

## Alternative: Use Railway Instead

If Vercel continues to have issues, Railway is better for Python Flask apps:

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. Add environment variables
5. Set start command: `python3 twitter_api.py`
6. Deploy!

Railway advantages:
- Better Python support
- No cold starts
- More predictable for Flask apps
- Easier debugging

