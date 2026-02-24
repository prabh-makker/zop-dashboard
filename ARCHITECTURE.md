# 🏗️ Architecture & Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD (Streamlit)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User Interface                                      │  │
│  │  - Post cards with relevance scores                │  │
│  │  - Interactive buttons (Visit, Engaged)            │  │
│  │  - Sidebar stats & controls                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  CORE APPLICATION (Python)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Fetching                                       │  │
│  │  - 36 target subreddits                             │  │
│  │  - Reddit JSON API (public endpoints)              │  │
│  │  - 7-day freshness filter                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Processing & Scoring                          │  │
│  │  - Keyword matching (primary/secondary)             │  │
│  │  - Relevance calculation (0-100%)                   │  │
│  │  - Sorting & filtering                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Engagement Tracking                                │  │
│  │  - Load engaged_history.json                        │  │
│  │  - Filter already-seen posts                        │  │
│  │  - Save new engagement data                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL FILE STORAGE                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  engaged_history.json         reddit_cache.json     │  │
│  │  {"engaged_posts": [...]}     {"timestamp": "...",  │  │
│  │                                "posts": [...]}      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
START
  │
  ├─→ Load Configuration
  │    └─→ Read keywords, subreddits, weights
  │
  ├─→ Load Engagement History
  │    └─→ Read engaged_history.json
  │
  ├─→ Check Cache
  │    ├─→ If fresh (< 30 min): USE CACHE → Skip to Filtering
  │    └─→ If stale: FETCH NEW DATA
  │         │
  │         ├─→ For Each Subreddit (36 total)
  │         │    │
  │         │    ├─→ HTTP GET reddit.com/r/{subreddit}/new.json
  │         │    ├─→ Filter posts > 7 days old
  │         │    ├─→ Extract: title, content, score, comments, etc.
  │         │    └─→ Rate limit: wait 0.5s
  │         │
  │         └─→ Combine all posts
  │              └─→ Save to reddit_cache.json
  │
  ├─→ Score Each Post
  │    │
  │    ├─→ For Each Post
  │    │    │
  │    │    ├─→ Extract title + content (lowercase)
  │    │    ├─→ Score = 0
  │    │    │
  │    │    ├─→ Primary Keywords (Zop.dev aligned)
  │    │    │    └─→ Each match: +10 points
  │    │    │
  │    │    ├─→ Secondary Keywords
  │    │    │    └─→ Each match: +3 points
  │    │    │
  │    │    ├─→ Product Mentions
  │    │    │    ├─→ "IDP" mention: +15
  │    │    │    └─→ "FinOps" mention: +15
  │    │    │
  │    │    └─→ Normalize: min(score, 100)
  │    │
  │    └─→ Add "relevance_score" field to each post
  │
  ├─→ Filter Engaged Posts
  │    │
  │    ├─→ Load engaged_history.json
  │    └─→ Remove posts with ID in engaged_posts set
  │
  ├─→ Sort by Relevance
  │    │
  │    └─→ Sort by relevance_score DESC, then score DESC
  │
  ├─→ Display Dashboard
  │    │
  │    ├─→ Show sidebar stats:
  │    │    ├─→ Posts engaged
  │    │    └─→ Active posts
  │    │
  │    ├─→ Show main stats:
  │    │    ├─→ Total posts
  │    │    ├─→ High relevance count
  │    │    ├─→ Medium relevance count
  │    │    └─→ Average relevance %
  │    │
  │    └─→ For Each Post:
  │         ├─→ Display relevance badge (🔥/✅/📌)
  │         ├─→ Display title, metadata, preview
  │         ├─→ Show 🔗 Visit button → reddit.com/...
  │         └─→ Show ✓ Engaged button → on_click:
  │              │
  │              ├─→ Load engaged_history.json
  │              ├─→ Add post ID to set
  │              ├─→ Save engaged_history.json
  │              └─→ Rerun dashboard (refresh)
  │
  └─→ END
```

---

## Relevance Scoring Algorithm

```
Input: Post object {title, content, subreddit, ...}
Output: relevance_score (0-100)

╔════════════════════════════════════════════════════════════════╗
║                  RELEVANCE SCORING ALGORITHM                  ║
╚════════════════════════════════════════════════════════════════╝

1. PREPARE TEXT
   combined_text = (title + content).lowercase()

2. PRIMARY KEYWORD MATCHING
   For each keyword in ["FinOps", "AWS cost", "cloud optimization", ...]:
       If keyword found in combined_text:
           score += 10

3. SECONDARY KEYWORD MATCHING
   For each keyword in ["cloud", "infrastructure", "deployment", ...]:
       If keyword found in combined_text:
           score += 3

4. PRODUCT MENTION BONUS
   If "idp" OR "internal developer platform" found:
       score += 15
   If "finops" OR "cost optimization" found:
       score += 15

5. NORMALIZE
   score = MIN(score, 100)

6. COLOR CODING
   If score >= 75:
       badge = "🔥 HIGH RELEVANCE"
   Elif score >= 50:
       badge = "✅ MEDIUM RELEVANCE"
   Else:
       badge = "📌 LOW RELEVANCE"

OUTPUT: score (0-100)

═════════════════════════════════════════════════════════════════

EXAMPLE WALKTHROUGH:

Post Title: "AWS Cost Optimization Using Lambda Scheduling"
Post Content: "We're implementing FinOps practices for cloud..."

1. combined_text = "aws cost optimization using lambda scheduling we're implementing finops practices for cloud..."

2. PRIMARY KEYWORD MATCHES:
   - "aws cost" found → score += 10 (score = 10)
   - "cost optimization" found → score += 10 (score = 20)
   - "FinOps" found → (in content) (skip, handled in step 4)

3. SECONDARY KEYWORD MATCHES:
   - "scheduling" found → score += 3 (score = 23)
   - "cloud" found → score += 3 (score = 26)

4. PRODUCT MENTION BONUS:
   - "finops" found → score += 15 (score = 41)

5. NORMALIZE:
   - score = min(41, 100) = 41

6. COLOR:
   - score 41 < 50 → "📌 LOW RELEVANCE"

FINAL SCORE: 41%
```

---

## File Storage Schema

### engaged_history.json
```json
{
  "engaged_posts": [
    "abc123def",     ← Reddit post ID
    "xyz789uvw",
    "post_id_3",
    ...
  ]
}
```

**Purpose**: Track posts you've already reviewed
**Access**: Load on startup, save on button click
**Lifetime**: Persistent until cleared

### reddit_cache.json
```json
{
  "timestamp": "2026-02-20T14:27:00",  ← When fetched
  "posts": [
    {
      "id": "abc123",
      "title": "Post Title",
      "content": "Post body text...",
      "author": "username",
      "subreddit": "aws",
      "score": 250,
      "num_comments": 45,
      "created_utc": 1708967820,
      "url": "https://...",
      "permalink": "/r/aws/comments/abc123/...",
      "is_self": true
    },
    ...
  ]
}
```

**Purpose**: Cache posts for 30 minutes to reduce API calls
**Access**: Load on startup, save after fetch, clear on refresh
**Lifetime**: Auto-expires after 30 minutes

### config.json
```json
{
  "zop_profile": {
    "keywords": {
      "primary": [...],      ← +10 points each
      "secondary": [...]     ← +3 points each
    }
  },
  "target_subreddits": [...], ← 36 communities
  "settings": {
    "cache_duration_minutes": 30,
    "post_freshness_days": 7,
    "request_timeout_seconds": 10,
    "request_delay_seconds": 0.5,
    "relevance_score": {
      "primary_keyword_weight": 10,
      "secondary_keyword_weight": 3,
      "product_mention_bonus": 15,
      "max_score": 100
    }
  }
}
```

**Purpose**: Configuration file (currently embedded in code, config.json is template)
**Access**: Read at startup
**Lifetime**: Persistent

---

## Component Interaction Diagram

```
┌──────────────────┐
│  STREAMLIT UI    │
│  (User Interface)│
└────────┬─────────┘
         │
    ┌────┴─────┐
    │           │
    ↓           ↓
┌─────────┐  ┌──────────────┐
│  Buttons│  │  Display     │
│ (Visit, │  │  Posts       │
│Engaged) │  │              │
└────┬────┘  └──────┬───────┘
     │               │
     │               ↓
     │         ┌──────────────┐
     │         │ REDDIT_DATA  │
     │         │ (Fetched &   │
     │         │  Scored)     │
     │         └──────┬───────┘
     │                │
     └────────┬───────┘
              ↓
      ┌──────────────────┐
      │ CORE LOGIC       │
      │ (calculate_      │
      │  relevance_score)│
      └────────┬─────────┘
               │
         ┌─────┴────────────────────┐
         │                          │
         ↓                          ↓
    ┌──────────────┐        ┌──────────────────┐
    │ LOCAL FILES  │        │ REDDIT API       │
    │              │        │ (HTTP requests)  │
    ├──────────────┤        └──────────────────┘
    │engaged_      │
    │history.json  │
    │              │
    │reddit_       │
    │cache.json    │
    └──────────────┘
```

---

## Request/Response Flow

### Example: Fetch from r/aws

```
CLIENT REQUEST:
────────────────
GET /r/aws/new.json HTTP/1.1
Host: reddit.com
User-Agent: ZopDevLeadDiscovery/1.0


SERVER RESPONSE:
────────────────
{
  "kind": "Listing",
  "data": {
    "children": [
      {
        "kind": "t3",
        "data": {
          "id": "abc123def",
          "title": "AWS Cost Optimization",
          "selftext": "We're implementing FinOps...",
          "author": "user123",
          "score": 250,
          "num_comments": 45,
          "created_utc": 1708967820,
          "url": "...",
          "permalink": "/r/aws/comments/abc123/...",
          "is_self": true
        }
      },
      ...
    ]
  }
}


PROCESSING:
───────────
1. Extract relevant fields
2. Filter by created_utc (last 7 days)
3. Add to posts list
4. Rate-limit delay (0.5s)


REPEAT: For each of 36 subreddits
───────
Then: Cache all posts + score them
```

---

## Performance Characteristics

### Time Complexity
- **Fetching**: O(n) where n = subreddits (36)
  - Each request ~500ms-1s
  - Total: ~20-40 seconds initially
  - Cached: ~1 second

- **Scoring**: O(n × m) where n = posts, m = keywords
  - Typical: 50-200 posts
  - ~100 keywords total
  - Each post scored in <1ms
  - Total: <500ms

- **Filtering**: O(n × log n) sorting
  - Total: <100ms

### Space Complexity
- **Memory**: ~50MB typical (posts in RAM)
- **Disk**: ~5MB for engaged_history.json (scales with engagement)
- **Disk**: ~10MB for reddit_cache.json (30-min rolling window)

### Network
- **Requests**: 36 (one per subreddit) + user refresh requests
- **Bandwidth**: ~500KB per full fetch
- **Rate Limit**: Friendly (0.5s delays between requests)

---

## Error Handling Flow

```
Try: Fetch from subreddit
  │
  ├─→ Success
  │    └─→ Parse, filter, continue
  │
  └─→ RequestException
       │
       ├─→ Timeout (>10s)
       │    └─→ Log warning, skip subreddit, continue
       │
       ├─→ HTTP Error (404, 500, etc)
       │    └─→ Log warning, skip subreddit, continue
       │
       └─→ Connection Error
            └─→ Log warning, skip subreddit, continue


Try: Save files
  │
  ├─→ Success
  │    └─→ Continue
  │
  └─→ IOError
       └─→ Show user notification, continue without saving
```

---

## Deployment Architecture

### Local Execution
```
Development Machine
├── Python 3.8+
├── Streamlit Server (Port 8501)
├── Browser (User Interface)
└── Local Files
    ├── reddit_dashboard.py
    ├── engaged_history.json
    └── reddit_cache.json
```

### Scale-Out Options (See ADVANCED.md)
```
1. Multi-User Shared Server
   - Streamlit Server on central machine
   - Multiple browsers connect
   - Shared engagement database

2. Cloud Deployment
   - Deploy to Heroku/AWS/GCP
   - Global access
   - Persistent database backend

3. Scheduled Tasks
   - Run as cron job
   - Cache posts automatically
   - Email digest of top leads
```

---

## Security Model

```
Data Protection:
├─ Local storage only ✅
├─ No credentials stored ✅
├─ No sensitive data ✅
└─ User has full control ✅

Network:
├─ Public Reddit API only ✅
├─ No authentication required ✅
├─ HTTPS to Reddit ✅
└─ No data sent to external servers ✅

Access Control:
├─ No user authentication ✅
├─ Local file system permissions ✅
└─ Single-machine deployment ✅
```

---

## Configuration Customization Path

```
User wants to customize
        │
        ├─→ Keywords → Edit config.json (EASY)
        │
        ├─→ Scoring weights → Edit config.json (EASY)
        │
        ├─→ Subreddits → Edit config.json (EASY)
        │
        ├─→ Cache duration → Edit config.json (EASY)
        │
        ├─→ Algorithm → Edit reddit_dashboard.py (MEDIUM)
        │
        ├─→ Database backend → Modify code (HARD)
        │
        └─→ Multi-profile → Duplicate script (MEDIUM)
```

---

**End of Architecture Documentation**

For implementation details, see `reddit_dashboard.py`
For configuration details, see `config.json`
For usage details, see `README.md`
