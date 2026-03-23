# 🚀 Flask Reddit Dashboard - Quick Start Guide

## **Access the Dashboard**
- **URL:** http://localhost:8080/feed
- **Status:** ✅ Running (with auto-restart protection)

## **Features Available**

### 📰 **Feed Page** (`/feed`)
- Shows 6 top-ranked Reddit posts about your target keywords
- Color-coded badges by pitchability:
  - 🎯 **GREEN (HIGH)** - Ready to pitch ZopDev
  - ⭐ **AMBER (MEDIUM)** - Good potential leads
  - 📌 **RED (LOW)** - Not a good fit
- Displays scoring breakdown showing how each post scored
- **Refresh Button** - Get fresh posts with randomized selection
- **Engage Button** - Save post to "Saved Posts" page
- **Open Link** - View original Reddit post

### 📌 **Saved Posts Page** (`/saved`)
- All posts you've engaged with
- Same color-coded scoring display
- **Unsave Button** - Remove from saved posts

### 🌙 **Dark Mode**
- Toggle button in header
- Preference persists across sessions

---

## **Intelligent Scoring System**

Posts are scored on 4 components (max 100 points):

| Component | Weight | What It Detects |
|-----------|--------|-----------------|
| **Keywords** | 40 pts | Brand/product mentions (aws, devops, kubernetes, etc.) |
| **FinOps Pillars** | 15 pts | Cost optimization, rate optimization, workload optimization, governance |
| **Intent Signals** | 35 pts | Cost reduction pain, automation needs, visibility needs |
| **Engagement** | 10 pts | Upvotes and comments (popular posts score higher) |

### Anti-Signals
Posts about "learning", "tutorial", "certification", "study" are **reduced by 40%** (learning content isn't sales-ready)

### Pitchability Tiers
- **HIGH (75-100%)** - Strong fit for ZopDev pitch
- **MEDIUM (50-74%)** - Conditional interest
- **LOW (<50%)** - Not a good prospect

---

## **Managing the App**

### ✅ **Check if App is Running**
```bash
/Users/zopdev/\ research/start_app.sh status
```

### 🔄 **Restart the App**
```bash
/Users/zopdev/\ research/start_app.sh restart
```

### ▶️ **Start the App**
```bash
/Users/zopdev/\ research/start_app.sh start
```

### ⏹️ **Stop the App**
```bash
/Users/zopdev/\ research/start_app.sh stop
```

---

## **Monitoring & Auto-Restart**

A background monitor process automatically restarts the Flask app if it crashes:

### Check Monitor Status
```bash
ps aux | grep monitor_app.sh
```

### View Monitor Logs
```bash
tail -50 /tmp/flask_monitor.log
```

### Restart Monitor (if needed)
```bash
pkill -f monitor_app.sh
nohup /Users/zopdev/\ research/monitor_app.sh > /dev/null 2>&1 &
```

---

## **Logs & Debugging**

### Flask App Logs
```bash
tail -50 /tmp/flask_reddit_dashboard.log
```

### Monitor Logs
```bash
tail -50 /tmp/flask_monitor.log
```

### Check Port Status
```bash
lsof -i :8080
```

---

## **How It Works**

### Scoring Example

**Post:** "How do we reduce our AWS bill by 40%?"

| Component | Score | Reason |
|-----------|-------|--------|
| Keywords | +20 | "AWS" in title (+15) + "reduce" intent signal |
| FinOps Pillar | +15 | "reduce bill" matches cost_management pillar |
| Intent Signal | +20 | "How do we reduce" is cost pain signal |
| Engagement | +5 | 25 upvotes + 12 comments |
| **Total** | **60%** | **MEDIUM** pitchability |

### Scoring Example (Learning Post)

**Post:** "Best resources for learning AWS DevOps"

| Component | Score | Reason |
|-----------|-------|--------|
| Keywords | +25 | "AWS" and "DevOps" in title |
| FinOps Pillar | +0 | No cost/optimization keywords |
| Intent Signal | +0 | Learning intent, not buying intent |
| Engagement | +2 | 8 upvotes + 4 comments |
| **Total** | 27 × 0.6 | **16%** (anti-signal applied) |
| **Final** | **16%** | **LOW** pitchability ❌ |

---

## **Troubleshooting**

### App not responding?
```bash
# Check if it's running
/Users/zopdev/\ research/start_app.sh status

# If not running, restart it
/Users/zopdev/\ research/start_app.sh restart

# Check logs
tail -20 /tmp/flask_reddit_dashboard.log
```

### Scores look wrong?
- Clear cache and refresh:
  ```bash
  # Go to http://localhost:8080/feed?refresh=1 in browser
  ```
- Check Flask logs for errors

### Need to update scoring?
Edit the `get_relevance()` function in `/Users/zopdev/research/app.py` (around line 247)

---

## **API Endpoints**

### Get Posts JSON
```
GET /api/posts
Returns: Top 100 posts with scores as JSON
```

### Refresh Posts
```
GET /api/refresh
Returns: 6 random top-scored posts (skips cache)
```

### Engage with Post
```
POST /engage/{post_id}
Saves post to "Saved Posts" page
```

---

## **Next Steps**

### 🎯 **Coming Soon**
- [ ] Huginn integration for automated post discovery
- [ ] Email notifications for HIGH-pitchability posts
- [ ] Advanced filtering and search
- [ ] Analytics dashboard showing scoring trends
- [ ] Custom keyword configuration UI

---

## **Questions or Issues?**

Check the logs:
- `/tmp/flask_reddit_dashboard.log` - Flask app logs
- `/tmp/flask_monitor.log` - Monitor health checks

Or manually restart:
```bash
/Users/zopdev/\ research/start_app.sh restart
```

---

**Last Updated:** March 23, 2026
**Status:** ✅ Production Ready
