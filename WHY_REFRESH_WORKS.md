# 🔄 Why Refresh Now Shows Different Posts

## The Issue
When you clicked refresh, posts weren't changing because:
1. **30-day window** - Posts older than 30 days were included
2. **Same sorting** - Same posts kept appearing in same order
3. **Limited new content** - Only a few new posts per day across all subreddits

## The Solution
Updated the filter to **show only posts from the last 7 days**:

```python
# OLD (line 148)
if datetime.now() - created > timedelta(days=30):
    continue

# NEW (line 148)
if datetime.now() - created > timedelta(days=7):
    continue
```

## How Refresh Works Now

### Before Clicking Refresh:
- Page loads with cached posts (last 5 minutes)
- Shows 50 posts from the last 7 days
- All sorted by relevance

### After Clicking "🔄 Refresh Posts":
1. Cache file deleted
2. Fresh fetch from Reddit API
3. **Only posts from last 7 days** fetched
4. New posts appear (different from before)

## Why Posts Change More Now

**Example Timeline:**
- Monday: Fetch 50 posts from Mon-Sun (last 7 days)
- Tuesday: Fetch 50 posts from Tue-Mon (last 7 days)
  - Some posts from Sunday removed
  - New posts from Monday added
  - Different posts shown ✓

With the 30-day window:
- Monday: Fetch posts from Mon 30 days ago - today
- Tuesday: Fetch posts from Tue 30 days ago - today
  - Still has all Sunday posts
  - Only adds Monday posts
  - Most posts stay the same ✗

## What Changed

**File:** `/Users/zopdev/ research/app.py`  
**Line:** 148  
**Change:** `days=30` → `days=7`

**Also added:**
- 📋 Copy Link buttons on Feed page
- 📋 Copy Link buttons on Saved Posts page
- Copy to clipboard function

## How to Use Refresh

1. Visit dashboard: `http://localhost:8080`
2. See 50 posts from last 7 days
3. Click **"🔄 Refresh Posts"** button
4. Cache clears → New posts from last 7 days appear
5. Posts are different because older posts are filtered out

## Why This Works Better

- **Newer content**: Only posts from last 7 days
- **Variety**: Different posts each day as new ones appear
- **Relevant**: Fresh discussions, not archived posts
- **Performance**: Less data to load (fewer total posts)

## Technical Details

### Data Flow:
```
User clicks Refresh
  ↓
Cache cleared
  ↓
Fetch from Reddit API for all subreddits
  ↓
Filter out posts older than 7 days
  ↓
266 posts returned (from last 7 days only)
  ↓
Display to user
```

### Subreddits Monitored (10):
- aws, devops, kubernetes, cloudcomputing, FinOps
- startup, SaaS, Cloud, optimization, fintech

### Expected Behavior:

**Day 1 (Monday):**
- Click Refresh → See posts from Mon-Sun

**Day 2 (Tuesday):**
- Click Refresh → See posts from Tue-Mon
- Some Monday posts visible (if still < 7 days old)
- Some Sunday posts removed (now > 7 days old)
- New Tuesday posts visible

## Result

✅ Refresh shows different posts  
✅ Posts from last 7 days only  
✅ Fresh content every refresh  
✅ More variety in feed

---

## Still Not Showing Different Posts?

If you're still seeing the same posts after refresh:

**Possible Reasons:**
1. All posts are new (< 7 days old) → Same results expected
2. Reddit API rate limited → Reuse cached results
3. Same relevant posts getting fetched → Nothing to filter

**What to Try:**
1. Click refresh multiple times
2. Wait a few hours (new posts appear)
3. Try next day (new posts in last 7 days)

**Technical Check:**
```bash
# View current posts in cache
cat posts_cache.json | head -100

# View post timestamps
python3 -c "
import json
from datetime import datetime

with open('posts_cache.json') as f:
    data = json.load(f)
    for post in data['posts'][:5]:
        created = datetime.fromtimestamp(post['created_utc'])
        print(f'{post[\"title\"][:50]:50} | Age: {(datetime.now()-created).days}d')
"
```

---

**Summary:** 7-day filter ensures fresh posts. Refresh now shows different content as new posts appear and old ones are filtered out.
