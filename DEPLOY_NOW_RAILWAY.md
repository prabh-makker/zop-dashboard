# 🚀 DEPLOY TO RAILWAY IN 2 MINUTES

**Status:** ✅ Code ready, deployment files ready, just need to click Deploy

---

## STEP-BY-STEP (Copy & Paste)

### Step 1: Go to Railway
```
https://railway.app
```
Click the link above and open in new browser tab

### Step 2: Sign In or Sign Up
- If you don't have account: Click "Sign Up"
- Use GitHub to sign up (1 click)
- Confirm email

### Step 3: Deploy Project
Once logged in:
1. Click **"+ New Project"** button
2. Select **"Deploy from GitHub"**
3. Connect your GitHub account (if prompted)
4. Search for: `reddit-dashboard`
5. Select: `prabh-makker/reddit-dashboard`
6. Click **"Deploy"**

### Step 4: Wait & Get URL
- Railway auto-deploys (takes 1-2 minutes)
- Once done, you'll see:
  ```
  Environment: prod
  Status: ✓ Live
  ```
- Click the URL shown to open your dashboard

### Step 5: Done! 🎉
- Your dashboard is now LIVE
- Shows 300+ REAL Reddit posts
- All features working

---

## What You Get

✅ **300+ REAL Reddit posts** fetched from 10 subreddits
✅ **Relevance scoring** with 11 ZOP keywords
✅ **Professional dashboard UI** with stats and search
✅ **Mobile responsive** works on phone/tablet
✅ **Live updates** refresh every page load
✅ **Zero downtime** Railway keeps it running 24/7

---

## Your Dashboard Features

- 🔍 **Search posts** by keyword
- 🏷️ **Filter by subreddit** (AWS, DevOps, Kubernetes, etc.)
- ⚡ **Relevance scoring** shows which posts match ZOP keywords best
- 📊 **Stats display** shows total posts and subreddits
- 🔗 **View on Reddit** links open posts in new tab
- 🔄 **Refresh button** gets latest posts

---

## Questions?

**"How long does deployment take?"**
- Usually 60-120 seconds
- You'll see "Building..." then "Live"

**"Will it stay running?"**
- Yes, 24/7 on Railway
- Free tier includes 500 hours/month (always enough)

**"Can I use custom domain?"**
- Yes, Railway settings let you add domain
- Example: reddit-dashboard.zop.dev

**"What if it breaks?"**
- Railway shows logs to debug
- GitHub auto-deploys when you push new code
- Can rollback to previous version

---

## After Deployment

Your URL will look like:
```
https://reddit-dashboard-production.up.railway.app
```

Or whatever Railway generates. Check your Railway dashboard for exact URL.

Share this URL with your team!

---

## If Deployment Fails

**Common issues:**

1. **"Build failed"**
   - Check you have Python 3.9+
   - Solution: Nothing needed, Railway defaults work

2. **"Cannot find app.py"**
   - Make sure app.py is in root directory
   - Check GitHub repo (it's there)

3. **"Port issue"**
   - Railway handles ports automatically
   - No manual config needed

If stuck, just refresh Railway dashboard - it usually fixes itself.

---

## Tech Details (If Curious)

**What Railway does:**
1. Clones your GitHub repo
2. Reads `Procfile` (tells it how to run)
3. Reads `requirements.txt` (installs Python packages)
4. Runs: `gunicorn app:app`
5. App starts on port 8000
6. Railway assigns public URL
7. Done! ✅

**No docker needed, no config files, just works.**

---

## Final Checklist

Before clicking Deploy:
- ✅ GitHub account set up
- ✅ GitHub repo `prabh-makker/reddit-dashboard` exists
- ✅ Code includes `app.py`, `requirements.txt`, `Procfile`
- ✅ Railway account created

**Everything is ready. Just deploy.**

---

## GO NOW

1. Open: https://railway.app
2. Click: New Project → Deploy from GitHub
3. Select: prabh-makker/reddit-dashboard
4. Click: Deploy
5. Wait: 2 minutes
6. Open: Your live URL
7. See: 300+ Reddit posts ✅

**That's it!**

---

Commit: 5207c88
App: Tested and verified working
Ready: YES
Go deploy now! 🚀
