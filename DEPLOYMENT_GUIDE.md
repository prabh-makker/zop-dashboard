# 🚀 Streamlit Cloud Deployment Guide

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `reddit-dashboard` (or your preference)
3. Description: "Reddit Lead Discovery Dashboard for Zop.dev"
4. Make it **PUBLIC** (Streamlit Cloud needs public repos)
5. Click "Create repository"

## Step 2: Push Code to GitHub

```bash
cd "/Users/zopdev/ research"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/reddit-dashboard.git

# Rename to main if needed
git branch -M main

# Push
git push -u origin main
```

## Step 3: Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign up" (or sign in if you have account)
   - Use GitHub for easiest auth
3. Click "New app"
4. Select:
   - Repository: `YOUR_USERNAME/reddit-dashboard`
   - Branch: `main`
   - Main file path: `reddit_dashboard.py`
5. Click "Deploy"

**That's it!** Streamlit will deploy automatically.

## Step 4: Access Your Dashboard

Wait 2-3 minutes for deployment. You'll get a URL like:
```
https://reddit-dashboard-[unique-id].streamlit.app
```

Share this URL with your team!

## Configuration

### Custom Domain (Optional)
- Streamlit Cloud allows custom domains
- Dashboard settings → Custom domain
- Point your DNS to Streamlit's servers

### Secrets (Optional - Not needed for this app)
- Settings → Secrets
- No API keys required for Reddit public API

## Monitoring

Streamlit Cloud dashboard shows:
- Deployment status
- CPU/Memory usage
- Error logs
- Traffic analytics

## Troubleshooting

### "Memory limit exceeded"
- Streamlit Cloud free tier: 1GB RAM
- Dashboard uses ~50-100MB, should be fine

### "App crashed"
- Check logs in Streamlit Cloud console
- Common: Network timeout (increase `timeout=15`)

### "Slow performance"
- Free tier ~10 concurrent users
- Upgrade to Pro tier if needed

## Performance Notes

- **Reddit API**: 5-minute cache (respects rate limits)
- **First load**: 5-10 seconds (fetches 300 posts)
- **Refresh**: Instant (uses cache) unless you click "Refresh Data"
- **Filter operations**: <1 second

## Security

✅ No API keys stored
✅ XSS protected (html.escape)
✅ HTTPS by default
✅ No user data collected
✅ Reddit API is read-only (public posts)

## Next Steps

1. Test all features:
   - Search
   - Time filter (24h/3d/7d)
   - Subreddit filter
   - Save/Remove posts

2. Share with team

3. Monitor performance & user feedback

4. (Optional) Upgrade to Pro tier for higher limits

---

**Dashboard is now LIVE! 🎉**
