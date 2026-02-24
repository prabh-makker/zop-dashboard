# ⚡ Quick Start Guide

## 30-Second Setup

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/zopdev/\ research
bash setup.sh
```

Then run:
```bash
source venv/bin/activate
streamlit run reddit_dashboard.py
```

### Option 2: Manual Setup

```bash
cd /Users/zopdev/\ research
pip install -r requirements.txt
streamlit run reddit_dashboard.py
```

## What You'll See

When the dashboard loads:

1. **Header**: "Zop.dev Lead Discovery Dashboard" with app overview
2. **Sidebar**:
   - Zop.dev profile summary
   - Dashboard stats (posts engaged, total active)
   - Control buttons (Refresh, Clear History)
3. **Main Area**:
   - Statistics row (total posts, relevance breakdown)
   - Post cards sorted by relevance score
   - Each post shows: title, subreddit, author, time, upvotes, comments, preview, and action buttons

## Key Actions

### View a Lead
Click **🔗 Visit** → Opens the Reddit thread in a new browser tab

### Mark as Engaged
Click **✓ Engaged** → Hides the post, adds to engagement history

### Refresh All Data
Click **🔄 Refresh** → Fetches latest posts (clears cache)

### Reset Engagement
Click **🗑️ Clear History** → Shows all posts again (for re-evaluation)

## How Relevance Scoring Works

**Example Post**: "AWS Cost Optimization with Lambda Scheduling"

- **Title keywords matched**: "AWS cost" (+10), "cost optimization" (+10) = 20 points
- **FinOps mention**: (+15 bonus) = 35 points
- **Secondary keywords**: "scheduling" (+3) = 38 points
- **Final Score**: **38%** → MEDIUM RELEVANCE ✅

Posts are ranked by this score, so most relevant leads appear first.

## File Location

All files are in: `/Users/zopdev/ research/`

- `reddit_dashboard.py` ← Main app (don't move)
- `engaged_history.json` ← Your engagement data (created on first use)
- `reddit_cache.json` ← Post cache (auto-created, auto-deleted after 30 min)
- `requirements.txt` ← Dependencies
- `setup.sh` ← Setup script

## Common Commands

```bash
# Run dashboard
streamlit run reddit_dashboard.py

# Run with specific port
streamlit run reddit_dashboard.py --server.port 8502

# Clear all cached data
rm reddit_cache.json engaged_history.json

# Deactivate virtual environment
deactivate
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Command not found: streamlit" | Run `pip install -r requirements.txt` |
| Port 8501 already in use | Run with `streamlit run reddit_dashboard.py --server.port 8502` |
| "No module named streamlit" | Activate venv: `source venv/bin/activate` |
| Dashboard shows no posts | Click 🔄 Refresh to fetch new data |
| Posts keep reappearing | Clear history: Click 🗑️ Clear History |

## Next Steps

1. ✅ Run the dashboard
2. 📊 Review the top relevant posts (sorted by %)
3. 🔗 Click to visit interesting leads on Reddit
4. ✓ Mark posts you've engaged with
5. 📈 Track your engagement in the sidebar stats
6. 🔄 Refresh daily for new leads

---

**Happy Lead Hunting! 🚀**
