# 🔧 Advanced Configuration & Customization

## Configuration File

Edit `config.json` to customize the dashboard without touching Python code.

### Structure Overview

```json
{
  "zop_profile": { ... },      // Company & product info
  "target_subreddits": [ ... ], // Monitored communities
  "settings": { ... }           // Performance & scoring parameters
}
```

## Customizing Keywords

### Primary Keywords (High Weight: +10 points)

Edit the `primary` array in `config.json`:

```json
"primary": [
  "FinOps",
  "AWS cost",
  "my-custom-keyword",
  "another-important-term"
]
```

### Secondary Keywords (Medium Weight: +3 points)

Edit the `secondary` array:

```json
"secondary": [
  "cloud",
  "infrastructure",
  "my-medium-importance-keyword"
]
```

### Product Bonuses

Currently hard-coded in `reddit_dashboard.py`. To modify:

1. Open `reddit_dashboard.py`
2. Find the `calculate_relevance_score()` function
3. Modify these lines:

```python
# Bonus for product mentions
if "idp" in combined_text or "internal developer platform" in combined_text:
    score += 15  # Change 15 to your desired bonus
if "finops" in combined_text or "cost optimization" in combined_text:
    score += 15  # Change 15 to your desired bonus
```

## Modifying Scoring Weights

In `config.json`, adjust `relevance_score`:

```json
"relevance_score": {
  "primary_keyword_weight": 10,      // Points per primary keyword
  "secondary_keyword_weight": 3,     // Points per secondary keyword
  "product_mention_bonus": 15,       // Points for product mentions
  "max_score": 100                   // Score cap
}
```

**Example**: To make primary keywords worth more:

```json
"primary_keyword_weight": 15  // Changed from 10
```

## Adding/Removing Subreddits

Edit `target_subreddits` array in `config.json`:

```json
"target_subreddits": [
  "existing_subreddit",
  "another_subreddit",
  "new_subreddit_to_monitor"
]
```

**Remove** a subreddit by deleting its entry:

```json
// Before
["aws", "kubernetes", "unwanted_subreddit"]

// After
["aws", "kubernetes"]
```

## Adjusting Cache Duration

In `config.json`:

```json
"settings": {
  "cache_duration_minutes": 30  // Change to desired minutes
}
```

**Examples**:
- `5` = Cache refreshes every 5 minutes (more API calls, fresher data)
- `60` = Cache refreshes every hour (fewer API calls, potentially stale data)
- `0` = Never cache (not recommended, rate limit risk)

## Post Freshness Window

Control how old posts can be before being filtered:

```json
"post_freshness_days": 7  // Posts older than 7 days ignored
```

**Examples**:
- `1` = Only today's posts
- `7` = Last week's posts (default)
- `30` = Last month's posts

## API Request Tuning

### Request Timeout

```json
"request_timeout_seconds": 10  // Seconds to wait for response
```

**Adjust if**:
- Getting timeouts → Increase to 15-20
- Connections hanging → Decrease to 5-8

### Request Delay

```json
"request_delay_seconds": 0.5  // Delay between subreddit requests
```

**Adjust for**:
- Rate limiting issues → Increase to 1.0-2.0
- Faster performance → Decrease to 0.2-0.3

## Advanced: Custom Relevance Algorithm

To implement custom scoring logic:

1. Open `reddit_dashboard.py`
2. Find `calculate_relevance_score(post: Dict) -> int`
3. Replace logic:

```python
def calculate_relevance_score(post: Dict) -> int:
    """Custom relevance scoring."""
    title = post.get("title", "").lower()
    content = post.get("content", "").lower()

    # Your custom logic here
    score = 0

    # Example: Boost based on engagement
    if post["num_comments"] > 50:
        score += 20

    # Example: Boost based on subreddit
    if post["subreddit"] == "aws":
        score += 10

    return min(100, score)
```

## Multi-Profile Support

To track different companies/products:

1. **Duplicate** `reddit_dashboard.py` → `reddit_dashboard_company2.py`
2. Edit `ZOP_PROFILE` in the new file:

```python
ZOP_PROFILE = {
    "company": "Company2",
    "products": ["Product1", "Product2"],
    "keywords": { ... }
}
```

3. Run multiple dashboards simultaneously:

```bash
# Terminal 1
streamlit run reddit_dashboard.py

# Terminal 2
streamlit run reddit_dashboard_company2.py --server.port 8502
```

## Engagement History Management

### Export Engagement Data

```python
import json

with open("engaged_history.json", "r") as f:
    data = json.load(f)
    post_ids = data["engaged_posts"]
    print(f"Total engaged posts: {len(post_ids)}")
```

### Batch Import

```python
import json

new_posts = ["abc123def", "xyz789uvw", "post_id_3"]

with open("engaged_history.json", "r") as f:
    data = json.load(f)

data["engaged_posts"].extend(new_posts)

with open("engaged_history.json", "w") as f:
    json.dump(data, f, indent=2)
```

### Clear by Date Range

```python
# Only keeps engagement from last 30 days
# (requires enhanced storage with timestamps)
# See "Time-Based History Tracking" below
```

## Advanced Features (Code Modifications)

### Time-Based History Tracking

Modify engagement to include timestamps:

```python
# In reddit_dashboard.py, replace load_engaged_history():
def load_engaged_history() -> Dict:
    if os.path.exists(ENGAGED_HISTORY_FILE):
        with open(ENGAGED_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"posts": {}}

# Replace save_engaged_history():
def save_engaged_history(engaged: Dict):
    with open(ENGAGED_HISTORY_FILE, "w") as f:
        json.dump(engaged, f, indent=2)

# In display_post_card(), change:
if st.button("✓ Engaged", key=f"mark_{post['id']}"):
    engaged = load_engaged_history()
    engaged["posts"][post["id"]] = {
        "timestamp": datetime.now().isoformat(),
        "title": post["title"],
        "subreddit": post["subreddit"]
    }
    save_engaged_history(engaged)
```

### Database Integration (SQLite)

Replace JSON with SQLite for better performance:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect("engagement.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engaged_posts (
            post_id TEXT PRIMARY KEY,
            title TEXT,
            subreddit TEXT,
            engaged_at TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def mark_engaged(post_id: str, title: str, subreddit: str):
    conn = sqlite3.connect("engagement.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO engaged_posts VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
        (post_id, title, subreddit)
    )
    conn.commit()
```

### Add Post Filtering UI

```python
# In main(), add filtering section:
st.markdown("## 🔍 Advanced Filters")
col1, col2, col3 = st.columns(3)

with col1:
    min_relevance = st.slider("Min Relevance", 0, 100, 0)

with col2:
    selected_subreddits = st.multiselect(
        "Subreddits",
        TARGET_SUBREDDITS,
        default=TARGET_SUBREDDITS
    )

with col3:
    min_engagement = st.slider("Min Comments", 0, 500, 0)

# Filter dataframe
df = df[df["relevance_score"] >= min_relevance]
df = df[df["subreddit"].isin(selected_subreddits)]
df = df[df["num_comments"] >= min_engagement]
```

## Monitoring & Analytics

### View Engagement Statistics

```python
import json
from collections import Counter

with open("engaged_history.json", "r") as f:
    engaged_ids = set(json.load(f).get("engaged_posts", []))

# Analyze engagement by subreddit
subreddit_counts = Counter()
for post in all_posts:
    if post["id"] in engaged_ids:
        subreddit_counts[post["subreddit"]] += 1

print(subreddit_counts.most_common(10))
```

### Export Engagement Summary

```python
import json
import csv

with open("engaged_history.json", "r") as f:
    engaged_ids = set(json.load(f).get("engaged_posts", []))

# Create CSV with engaged posts
with open("engaged_posts_export.csv", "w") as f:
    writer = csv.DictWriter(f, ["title", "subreddit", "author", "score"])
    writer.writeheader()

    for post in all_posts:
        if post["id"] in engaged_ids:
            writer.writerow({
                "title": post["title"],
                "subreddit": post["subreddit"],
                "author": post["author"],
                "score": post["score"]
            })
```

## Performance Optimization

### Parallel Subreddit Fetching

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_all_posts_parallel() -> List[Dict]:
    all_posts = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_reddit_posts, sub): sub
            for sub in TARGET_SUBREDDITS
        }

        for future in as_completed(futures):
            posts = future.result()
            all_posts.extend(posts)

    return all_posts
```

### In-Memory Caching with TTL

```python
from functools import lru_cache
import time

CACHE_TTL = 30 * 60  # 30 minutes

@lru_cache(maxsize=128)
def fetch_subreddit_cached(subreddit: str, timestamp: int):
    return fetch_reddit_posts(subreddit)

def get_all_posts_cached() -> List[Dict]:
    timestamp = int(time.time() // CACHE_TTL)

    all_posts = []
    for sub in TARGET_SUBREDDITS:
        posts = fetch_subreddit_cached(sub, timestamp)
        all_posts.extend(posts)

    return all_posts
```

## Debugging

### Enable Verbose Logging

Add to top of `reddit_dashboard.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In fetch_reddit_posts():
logger.debug(f"Fetching from r/{subreddit}")
logger.debug(f"Got {len(posts)} posts")
```

### Test Relevance Scoring

```python
# Create test_scoring.py
from reddit_dashboard import calculate_relevance_score

test_posts = [
    {"title": "AWS Cost Optimization Guide", "content": "FinOps strategies..."},
    {"title": "Kubernetes Basics", "content": "Platform engineering..."},
    {"title": "Cat Photos", "content": "Look at my cute cat"},
]

for post in test_posts:
    score = calculate_relevance_score(post)
    print(f"{post['title']}: {score}%")
```

## Deployment

### Run as Background Service (macOS)

Create `com.zopdev.reddit-dashboard.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zopdev.reddit-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/zopdev/ research/venv/bin/python</string>
        <string>-m</string>
        <string>streamlit</string>
        <string>run</string>
        <string>/Users/zopdev/ research/reddit_dashboard.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/zopdev/ research</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.zopdev.reddit-dashboard.plist
```

---

**Questions or Issues?** Check QUICKSTART.md or README.md for more help.
