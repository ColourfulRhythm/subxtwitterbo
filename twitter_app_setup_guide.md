# Twitter App Setup Guide

## Required App Info Fields

When setting up your Twitter app for write permissions, you need to fill in these fields:

### 1. Callback URI / Redirect URL (Required)
**For a bot that doesn't use OAuth (like this one):**
```
http://localhost:3000
```
or
```
https://localhost
```

**Note:** Since this bot uses API keys directly (not OAuth), any valid URL format will work. `http://localhost:3000` is commonly used for bots.

### 2. Website URL (Required)
**You can use:**
```
https://twitter.com
```
or your actual website if you have one, or:
```
https://github.com/yourusername
```

### 3. Organization name (Optional but recommended)
```
Your Name or Company Name
```
Example: `SubX Bot` or `Your Name`

### 4. Organization URL (Optional)
```
https://twitter.com
```
or your website/GitHub profile

### 5. Terms of Service (Optional)
```
https://twitter.com/en/tos
```
or your own terms if you have a website

### 6. Privacy Policy (Optional)
```
https://twitter.com/en/privacy
```
or your own privacy policy if you have a website

---

## Quick Setup (Minimum Required)

**Minimum to get started:**
- **Callback URI:** `http://localhost:3000`
- **Website URL:** `https://twitter.com`

After filling these, save and then:
1. Go to "Settings" → Change "App permissions" to "Read and Write"
2. Save again
3. Go to "Keys and tokens" → Regenerate Access Token and Access Token Secret
4. Update your `.env` file with the new tokens

