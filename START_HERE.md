# 🚀 START HERE - Zop.dev Reddit Lead Discovery Dashboard

Welcome! This document guides you through the Reddit Lead Discovery Dashboard for Zop.dev.

---

## ⏱️ 30-Second Summary

**What is this?**
A dashboard that finds and scores relevant posts from 36 Reddit communities related to FinOps, cloud infrastructure, and infrastructure automation—automatically matching against Zop.dev's products (ZopDay IDP and ZopNight FinOps tool).

**How does it work?**
1. Fetches recent posts from target subreddits
2. Scores each post based on relevance to Zop.dev (0-100%)
3. Shows highest-scoring leads first
4. Track which posts you've engaged with

**How do I run it?**
```bash
cd /Users/zopdev/\ research
bash setup.sh
streamlit run reddit_dashboard.py
```

**That's it!** The dashboard opens in your browser.

---

## 📚 Documentation Guide

### 🟢 **I want to get started RIGHT NOW**
→ Read: `QUICKSTART.md` (3 minutes)
- 30-second setup
- Key actions
- Common commands

### 🟡 **I want to understand what this does**
→ Read: `README.md` (10 minutes)
- Complete feature overview
- How it works
- Configuration basics
- Troubleshooting

### 🔵 **I want the technical details**
→ Read: `PROJECT_SUMMARY.md` (5 minutes)
- Architecture overview
- File structure
- Specifications
- Usage workflow

### 🟣 **I want to customize/modify it**
→ Read: `ADVANCED.md` (15 minutes)
- Custom keywords
- Scoring adjustments
- Subreddit management
- Performance optimization
- Database integration
- Deployment options

---

## 🎯 Choose Your Path

### Path 1: "Just Get It Running"
1. Open `QUICKSTART.md`
2. Run `bash setup.sh`
3. Run `streamlit run reddit_dashboard.py`
4. Start reviewing leads!

**Time**: 5 minutes

### Path 2: "I Want to Understand It First"
1. Read this file (you're here!)
2. Read `README.md` (features & setup)
3. Run `bash setup.sh` and start dashboard
4. Customize via `ADVANCED.md` if needed

**Time**: 20 minutes

### Path 3: "Deep Dive / Full Customization"
1. Read `PROJECT_SUMMARY.md` (architecture)
2. Read `README.md` (features)
3. Read `ADVANCED.md` (customization)
4. Modify code/config as needed
5. Deploy and monitor

**Time**: 45 minutes

---

## 📦 What's Included

```
/Users/zopdev/ research/
├── reddit_dashboard.py      ← Main app (don't need to edit)
├── config.json              ← Customizable configuration
├── requirements.txt         ← Python dependencies
├── setup.sh                 ← Automated setup script
│
├── README.md                ← Full documentation
├── QUICKSTART.md           ← Quick start guide
├── ADVANCED.md             ← Advanced customization
├── PROJECT_SUMMARY.md      ← Technical overview
├── START_HERE.md           ← This file
│
└── (Auto-generated on first run)
    ├── engaged_history.json ← Your engagement tracking
    ├── reddit_cache.json    ← Post cache (30 min TTL)
    └── venv/               ← Virtual environment
```

---

## 🎬 Quick Setup (Copy & Paste)

```bash
# Navigate to project directory
cd /Users/zopdev/\ research

# Run automated setup (installs Python packages)
bash setup.sh

# Activate virtual environment
source venv/bin/activate

# Start the dashboard
streamlit run reddit_dashboard.py
```

**Browser opens automatically to:** `http://localhost:8501`

---

## 🎮 Using the Dashboard

### Main View
- **Posts** sorted by relevance score (highest first)
- **Color-coded badges**: 🔥 High | ✅ Medium | 📌 Low
- **Content preview** of each post
- **Metadata**: subreddit, author, upvotes, comments, timestamp

### Actions
- **🔗 Visit** - Opens Reddit thread in new tab
- **✓ Engaged** - Marks as reviewed, hides from dashboard
- **🔄 Refresh** - Fetches new posts (clears cache)
- **🗑️ Clear History** - Shows all posts again

### Sidebar Stats
- Posts engaged (total tracked)
- Active posts (unreviewed)
- Control buttons
- Configuration summary

---

## 🔑 Key Features

✅ **AI Relevance Scoring**
- Automatically scores posts 0-100%
- Based on Zop.dev keywords & products
- Primary keywords: +10 | Secondary: +3 | Products: +15

✅ **36 Monitored Subreddits**
- aws, FinOps, kubernetes, devops, cloud, etc.
- Plus 30 other related communities
- Covers infrastructure, cloud, FinOps topics

✅ **Engagement Memory**
- Tracks posts you've reviewed
- Never shows same post twice
- Persists between sessions
- Easy to reset if needed

✅ **Smart Caching**
- 30-minute cache for efficiency
- Rate-limit friendly
- Graceful error handling

✅ **Professional UI**
- Dark-mode optimized
- Responsive design
- Real-time interactions
- Progress indicators

---

## ⚙️ Customization Quick Links

**Want to change something?** See `ADVANCED.md`:

| Want to... | See... | Difficulty |
|-----------|--------|-----------|
| Add/remove keywords | `ADVANCED.md` → Keywords | Easy |
| Change scoring weights | `ADVANCED.md` → Scoring | Easy |
| Add/remove subreddits | `ADVANCED.md` → Subreddits | Easy |
| Adjust cache duration | `ADVANCED.md` → Cache | Easy |
| Change relevance algorithm | `ADVANCED.md` → Custom Algorithm | Medium |
| Add database backend | `ADVANCED.md` → Database | Hard |
| Deploy as service | `ADVANCED.md` → Deployment | Hard |

---

## ❓ Common Questions

**Q: Do I need a Reddit account?**
A: No! Uses public Reddit API endpoints.

**Q: Will it slow down Reddit?**
A: No. Minimal requests with respectful rate limiting (0.5s delays).

**Q: Does it send data anywhere?**
A: No. Everything is stored locally on your computer.

**Q: Can I customize the keywords?**
A: Yes! Edit `config.json` or `ADVANCED.md` for details.

**Q: How often should I run it?**
A: Daily or whenever you want new leads. Cache refreshes every 30 minutes.

**Q: What if I want different subreddits?**
A: Edit `config.json` to add/remove communities.

---

## 🐛 Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| "Command not found: streamlit" | Run `pip install -r requirements.txt` |
| Port 8501 already in use | Run with `streamlit run reddit_dashboard.py --server.port 8502` |
| No posts showing up | Click 🔄 Refresh to fetch new data |
| Old posts keep reappearing | Click 🗑️ Clear History to reset |
| Slow performance | Reduce subreddit count in `config.json` |

**More help?** See `README.md` or `QUICKSTART.md`

---

## 📊 What Success Looks Like

✅ Dashboard loads with 50-200 posts per session
✅ Posts sorted by relevance (highest % first)
✅ Can click 🔗 Visit to see Reddit threads
✅ Can click ✓ Engaged to track reviews
✅ Sidebar shows engagement statistics
✅ 🔄 Refresh gets new posts
✅ Can customize keywords/subreddits if needed

---

## 🚀 Next Steps

### Option 1: Start Now (5 min)
```bash
cd /Users/zopdev/\ research
bash setup.sh
source venv/bin/activate
streamlit run reddit_dashboard.py
```

### Option 2: Read & Then Start (20 min)
1. Read `README.md` (understand features)
2. Follow Option 1 above
3. Check `ADVANCED.md` if you want customization

### Option 3: Full Deep Dive (45 min)
1. Read `PROJECT_SUMMARY.md` (architecture)
2. Read `README.md` (features)
3. Read `ADVANCED.md` (customization)
4. Follow Option 1 setup
5. Customize as needed

---

## 📞 Need Help?

1. **Getting started?** → `QUICKSTART.md`
2. **Understanding features?** → `README.md`
3. **Want to customize?** → `ADVANCED.md`
4. **Technical details?** → `PROJECT_SUMMARY.md`
5. **Troubleshooting?** → `README.md` or `QUICKSTART.md`

---

## 🎉 You're All Set!

Everything you need is ready to go. Pick your path above and get started.

**Most common next step:**
```bash
cd /Users/zopdev/\ research && bash setup.sh
```

**Then:**
```bash
source venv/bin/activate && streamlit run reddit_dashboard.py
```

---

**Made for Zop.dev** ✨
*February 2026*
