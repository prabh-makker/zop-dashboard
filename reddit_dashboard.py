import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import time
import html as html_lib

# =====================================================================
# CONFIG
# =====================================================================

st.set_page_config(
    page_title="Zop.dev | Reddit Lead Discovery",
    page_icon="https://zop.dev/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# CONSTANTS
# =====================================================================

ENGAGED_FILE = "engaged_history.json"

TARGET_SUBREDDITS = [
    "aws", "devops", "kubernetes", "cloudcomputing", "FinOps",
    "startup", "SaaS", "Cloud", "optimization", "fintech"
]

ZOP_KEYWORDS = [
    "FinOps", "AWS", "cost optimization", "infrastructure",
    "cloud", "DevOps", "Kubernetes", "platform engineering",
    "automation", "deployment", "scaling"
]

# =====================================================================
# SESSION STATE
# =====================================================================

if "engaged" not in st.session_state:
    st.session_state.engaged = set()
    if os.path.exists(ENGAGED_FILE):
        try:
            with open(ENGAGED_FILE) as f:
                st.session_state.engaged = set(json.load(f).get("posts", []))
        except Exception:
            pass

if "min_score" not in st.session_state:
    st.session_state.min_score = 0

if "time_filter" not in st.session_state:
    st.session_state.time_filter = "7d"

if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = False

# =====================================================================
# FETCH POSTS
# =====================================================================

@st.cache_resource
def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    return s

@st.cache_data(ttl=300)
def fetch_reddit_posts():
    """Fetch posts from all target subreddits."""
    all_posts = []
    errors = []
    successful_subs = 0

    for subreddit in TARGET_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=30"
            resp = get_session().get(url, timeout=15)

            if resp.status_code != 200:
                errors.append(f"r/{subreddit}: HTTP {resp.status_code}")
                continue

            data = resp.json()
            sub_posts = 0
            for item in data.get("data", {}).get("children", []):
                post = item.get("data", {})
                if not post.get("id") or not post.get("created_utc"):
                    continue
                created = datetime.fromtimestamp(post["created_utc"])
                if datetime.now() - created > timedelta(days=30):
                    continue
                all_posts.append({
                    "id": post.get("id"),
                    "title": post.get("title", ""),
                    "content": post.get("selftext", "")[:300],
                    "author": post.get("author", "Unknown"),
                    "subreddit": post.get("subreddit", ""),
                    "score": post.get("score", 0),
                    "comments": post.get("num_comments", 0),
                    "created_utc": post.get("created_utc", 0),
                    "url": post.get("permalink", ""),
                    "upvote_ratio": post.get("upvote_ratio", 0),
                })
                sub_posts += 1
            if sub_posts > 0:
                successful_subs += 1
            time.sleep(0.3)
        except Exception as e:
            errors.append(f"r/{subreddit}: {str(e)[:50]}")
            continue

    return all_posts

# =====================================================================
# RELEVANCE SCORING
# =====================================================================

def get_relevance(post: Dict) -> int:
    """Calculate relevance score 0-100."""
    text = (post.get("title", "") + " " + post.get("content", "")).lower()
    score = 0
    matched = []
    for keyword in ZOP_KEYWORDS:
        if keyword.lower() in text:
            score += 20
            matched.append(keyword)
    if score == 0:
        return 0, []
    return min(100, score), matched

# =====================================================================
# FILTER POSTS
# =====================================================================

def filter_posts(posts: List[Dict], search: str, sub_filter: list = None) -> List[Dict]:
    """Filter and score posts."""
    result = []
    for post in posts:
        if post["id"] in st.session_state.engaged:
            continue
        score, matched = get_relevance(post)
        if score < st.session_state.min_score:
            continue
        age = datetime.now() - datetime.fromtimestamp(post["created_utc"])
        hours = age.total_seconds() / 3600
        tf = st.session_state.time_filter
        if tf == "24h" and hours > 24:
            continue
        elif tf == "3d" and hours > 72:
            continue
        elif tf == "7d" and hours > 168:
            continue
        if sub_filter and post["subreddit"] not in sub_filter:
            continue
        if search:
            search_lower = search.lower()
            text = (post["title"] + " " + post["content"] + " " + post["subreddit"]).lower()
            if not any(term in text for term in search_lower.split()):
                continue
        result.append({"relevance": score, "matched_keywords": matched, **post})
    result.sort(key=lambda x: (-x["relevance"], -x["score"]))
    return result

# =====================================================================
# HELPER: TIME AGO
# =====================================================================

def time_ago(utc_ts):
    diff = datetime.now() - datetime.fromtimestamp(utc_ts)
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        m = seconds // 60
        return f"{m}m ago"
    elif seconds < 86400:
        h = seconds // 3600
        return f"{h}h ago"
    else:
        d = seconds // 86400
        return f"{d}d ago"

# =====================================================================
# PROFESSIONAL DECORATIVE CSS
# =====================================================================

st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Reset & Base ── */
    *, *::before, *::after { box-sizing: border-box; }
    html, body, .stApp {
        background: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Hide Streamlit chrome */
    [data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .block-container { padding-top: 1rem !important; max-width: 1200px !important; }

    /* ── Hero Header ── */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #334155 100%);
        border-radius: 20px;
        padding: 48px 56px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-content { position: relative; z-index: 2; }
    .hero-brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
    }
    .hero-logo {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        margin: 0;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1rem;
        color: #94a3b8 !important;
        margin: 8px 0 0 0;
        font-weight: 400;
        line-height: 1.5;
    }
    .hero-stats {
        display: flex;
        gap: 32px;
        margin-top: 24px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.08);
    }
    .hero-stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0 !important;
    }
    .hero-stat-label {
        font-size: 0.75rem;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* ── Metric Cards ── */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }
    .metric-card:nth-child(1)::before { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
    .metric-card:nth-child(2)::before { background: linear-gradient(90deg, #06b6d4, #22d3ee); }
    .metric-card:nth-child(3)::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .metric-card:nth-child(4)::before { background: linear-gradient(90deg, #10b981, #34d399); }
    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .metric-icon-purple { background: #eef2ff; }
    .metric-icon-cyan { background: #ecfeff; }
    .metric-icon-amber { background: #fffbeb; }
    .metric-icon-green { background: #ecfdf5; }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a !important;
        line-height: 1;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #64748b !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Section Header ── */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 2px solid #e2e8f0;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0f172a !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-count {
        background: #6366f1;
        color: #ffffff !important;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
    }

    /* ── Post Card ── */
    .post-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
    }
    .post-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 4px;
        border-radius: 4px 0 0 4px;
    }
    .post-card.relevance-high::before {
        background: linear-gradient(180deg, #f59e0b, #d97706);
    }
    .post-card.relevance-medium::before {
        background: linear-gradient(180deg, #10b981, #059669);
    }
    .post-card.relevance-low::before {
        background: linear-gradient(180deg, #6366f1, #4f46e5);
    }
    .post-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.08);
        border-color: #c7d2fe;
    }

    /* Post Header */
    .post-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 12px;
    }

    /* Badges */
    .relevance-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 14px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 700;
        white-space: nowrap;
        letter-spacing: 0.3px;
    }
    .badge-hot {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
    }
    .badge-warm {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46 !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);
    }
    .badge-cool {
        background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
        color: #3730a3 !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
    }

    /* Subreddit chip */
    .sub-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        background: #f1f5f9;
        color: #475569 !important;
        border: 1px solid #e2e8f0;
    }

    /* Post Title */
    .post-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a !important;
        line-height: 1.5;
        margin-bottom: 10px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Post Meta */
    .post-meta {
        display: flex;
        align-items: center;
        gap: 16px;
        font-size: 0.8rem;
        color: #94a3b8 !important;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }
    .post-meta-item {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #94a3b8 !important;
    }
    .post-meta-item.upvotes { color: #f59e0b !important; font-weight: 600; }
    .post-meta-item.comments { color: #6366f1 !important; font-weight: 600; }

    /* Post Preview */
    .post-preview {
        background: #f8fafc;
        border: 1px solid #f1f5f9;
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.88rem;
        color: #475569 !important;
        line-height: 1.65;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Keyword Tags */
    .keyword-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 14px;
    }
    .keyword-tag {
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        background: linear-gradient(135deg, #eef2ff, #e0e7ff);
        color: #4338ca !important;
        border: 1px solid #c7d2fe;
    }

    /* ── Empty State ── */
    .empty-state {
        text-align: center;
        padding: 64px 24px;
        background: #ffffff;
        border-radius: 20px;
        border: 2px dashed #e2e8f0;
    }
    .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }
    .empty-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a !important;
        margin-bottom: 8px;
    }
    .empty-desc {
        font-size: 0.9rem;
        color: #94a3b8 !important;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Saved Posts ── */
    .saved-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 20px 0 16px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 24px;
    }
    .saved-count-badge {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #ffffff !important;
        padding: 6px 16px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    /* ── Streamlit Widget Overrides ── */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        background: #ffffff !important;
        transition: all 0.2s !important;
        color: #0f172a !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
    }
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        border: 2px solid #e2e8f0 !important;
        background: #ffffff !important;
        color: #374151 !important;
        transition: all 0.2s !important;
        font-size: 0.85rem !important;
    }
    .stButton > button:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #ffffff;
        border-radius: 14px;
        padding: 6px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    div[data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 600;
        color: #374151;
    }
    .stSlider > div > div > div > div {
        background: #6366f1 !important;
    }
    .stMultiSelect > div > div {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
    }

    /* ── Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .post-card { animation: fadeInUp 0.4s ease forwards; }
    .post-card:nth-child(2) { animation-delay: 0.05s; }
    .post-card:nth-child(3) { animation-delay: 0.1s; }
    .post-card:nth-child(4) { animation-delay: 0.15s; }
    .post-card:nth-child(5) { animation-delay: 0.2s; }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .hero { padding: 32px 24px; border-radius: 16px; }
        .hero-title { font-size: 1.5rem; }
        .hero-stats { flex-wrap: wrap; gap: 16px; }
        .metrics-grid { grid-template-columns: repeat(2, 1fr); }
        .post-card { padding: 20px; }
        .post-header { flex-direction: column; }
        .post-meta { flex-wrap: wrap; }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# MAIN UI
# =====================================================================

# ── Refresh Button ──
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.force_refresh = True
        st.rerun()

# ── Fetch Data ──
with st.spinner("📡 Fetching Reddit posts..."):
    all_posts = fetch_reddit_posts()

total_subs_active = len(set(p["subreddit"] for p in all_posts))

# Debug info (hidden by default)
if len(all_posts) == 0:
    st.error("⚠️ No posts fetched from Reddit!")
    st.warning("🔄 SOLUTION: Click the 'Refresh Data' button above to clear cache and retry")
    st.info("This clears Streamlit's cached results and forces a fresh fetch from Reddit API")

# ── Hero Header ──
st.markdown(f"""
<div class="hero">
    <div class="hero-content">
        <div class="hero-brand">
            <div class="hero-logo">Z</div>
            <div>
                <div class="hero-title">Reddit Lead Discovery</div>
                <div class="hero-subtitle">Real-time intelligence from {total_subs_active} subreddits &mdash; find high-intent discussions about FinOps, cloud, and infrastructure</div>
            </div>
        </div>
        <div class="hero-stats">
            <div>
                <div class="hero-stat-value">{len(all_posts):,}</div>
                <div class="hero-stat-label">Posts Scanned</div>
            </div>
            <div>
                <div class="hero-stat-value">{total_subs_active}</div>
                <div class="hero-stat-label">Subreddits</div>
            </div>
            <div>
                <div class="hero-stat-value">{len(st.session_state.engaged)}</div>
                <div class="hero-stat-label">Saved Leads</div>
            </div>
            <div>
                <div class="hero-stat-value">5m</div>
                <div class="hero-stat-label">Cache TTL</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──
tab1, tab2 = st.tabs(["  Feed  ", "  Saved Leads  "])

# =====================================================================
# FEED TAB
# =====================================================================

with tab1:
    # Controls row
    col_search, col_time, col_refresh = st.columns([0.6, 0.2, 0.2])
    with col_search:
        search = st.text_input(
            "Search", "",
            label_visibility="collapsed",
            placeholder="Search posts... e.g. FinOps, AWS cost, Kubernetes"
        )
    with col_time:
        st.session_state.time_filter = st.selectbox(
            "Time", ["24h", "3d", "7d", "30d"],
            index=2, label_visibility="collapsed"
        )
    with col_refresh:
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Advanced filters
    with st.expander("Advanced Filters"):
        fc1, fc2 = st.columns(2)
        with fc1:
            st.session_state.min_score = st.slider("Minimum Relevance Score", 0, 100, 0)
        with fc2:
            subreddit_filter = st.multiselect(
                "Filter by Subreddit",
                sorted(set(p["subreddit"] for p in all_posts)),
                default=[]
            )

    # Filter posts
    filtered = filter_posts(all_posts, search, subreddit_filter if subreddit_filter else None)

    # Metrics
    high_count = len([p for p in filtered if p.get("relevance", 0) >= 75])
    avg_rel = sum(p.get("relevance", 0) for p in filtered) / len(filtered) if filtered else 0

    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon metric-icon-purple">📊</div>
            <div class="metric-value">{len(all_posts):,}</div>
            <div class="metric-label">Total Posts</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon metric-icon-cyan">🎯</div>
            <div class="metric-value">{len(filtered):,}</div>
            <div class="metric-label">Matching</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon metric-icon-amber">🔥</div>
            <div class="metric-value">{high_count}</div>
            <div class="metric-label">High Relevance</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon metric-icon-green">📈</div>
            <div class="metric-value">{avg_rel:.0f}%</div>
            <div class="metric-label">Avg Relevance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Section header
    display_count = min(len(filtered), 15)
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">Top Results</div>
        <span class="section-count">Showing {display_count} of {len(filtered)}</span>
    </div>
    """, unsafe_allow_html=True)

    # Display posts
    if filtered:
        for i, post in enumerate(filtered[:15]):
            rel = post.get("relevance", 0)
            matched_kw = post.get("matched_keywords", [])
            safe_title = html_lib.escape(post.get("title", ""))
            safe_content = html_lib.escape(post.get("content", ""))

            # Relevance class & badge
            if rel >= 75:
                rel_class = "relevance-high"
                badge_html = f'<span class="relevance-badge badge-hot">🔥 {rel}% &mdash; High</span>'
            elif rel >= 40:
                rel_class = "relevance-medium"
                badge_html = f'<span class="relevance-badge badge-warm">✅ {rel}% &mdash; Medium</span>'
            else:
                rel_class = "relevance-low"
                badge_html = f'<span class="relevance-badge badge-cool">📌 {rel}%</span>'

            # Keyword tags
            kw_html = ""
            if matched_kw:
                tags = "".join(f'<span class="keyword-tag">{html_lib.escape(k)}</span>' for k in matched_kw[:5])
                kw_html = f'<div class="keyword-tags">{tags}</div>'

            # Preview
            preview_html = ""
            if safe_content.strip():
                preview_html = f'<div class="post-preview">{safe_content}</div>'

            st.markdown(f"""
            <div class="post-card {rel_class}">
                <div class="post-header">
                    {badge_html}
                    <span class="sub-chip">r/{html_lib.escape(post.get('subreddit', ''))}</span>
                </div>
                <div class="post-title">{safe_title}</div>
                <div class="post-meta">
                    <span class="post-meta-item">👤 {html_lib.escape(post.get('author', 'Unknown'))}</span>
                    <span class="post-meta-item">🕒 {time_ago(post.get('created_utc', 0))}</span>
                    <span class="post-meta-item upvotes">⬆ {post.get('score', 0):,}</span>
                    <span class="post-meta-item comments">💬 {post.get('comments', 0):,}</span>
                </div>
                {preview_html}
                {kw_html}
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            spacer, btn_link, btn_save = st.columns([3, 1, 1])
            with btn_link:
                reddit_url = f"https://reddit.com{post.get('url', '')}"
                st.link_button("Open in Reddit", reddit_url, use_container_width=True)
            with btn_save:
                if st.button("Save Lead", key=f"save_{post['id']}", use_container_width=True):
                    st.session_state.engaged.add(post["id"])
                    with open(ENGAGED_FILE, "w") as f:
                        json.dump({"posts": list(st.session_state.engaged)}, f)
                    st.toast(f"Lead saved!", icon="✅")
                    time.sleep(0.3)
                    st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <div class="empty-title">No matching posts found</div>
            <div class="empty-desc">Try adjusting your search terms, changing the time window, or lowering the minimum relevance score.</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# SAVED LEADS TAB
# =====================================================================

with tab2:
    if st.session_state.engaged:
        saved = [p for p in all_posts if p["id"] in st.session_state.engaged]
        for p in saved:
            rel, matched = get_relevance(p)
            p["relevance"] = rel
            p["matched_keywords"] = matched
        saved.sort(key=lambda x: (-x["relevance"], -x["score"]))

        st.markdown(f"""
        <div class="saved-header">
            <div class="section-title">Your Saved Leads</div>
            <span class="saved-count-badge">{len(saved)} lead{'s' if len(saved) != 1 else ''}</span>
        </div>
        """, unsafe_allow_html=True)

        for post in saved:
            rel = post.get("relevance", 0)
            matched_kw = post.get("matched_keywords", [])
            safe_title = html_lib.escape(post.get("title", ""))
            safe_content = html_lib.escape(post.get("content", ""))

            if rel >= 75:
                rel_class = "relevance-high"
                badge_html = f'<span class="relevance-badge badge-hot">🔥 {rel}% &mdash; High</span>'
            elif rel >= 40:
                rel_class = "relevance-medium"
                badge_html = f'<span class="relevance-badge badge-warm">✅ {rel}% &mdash; Medium</span>'
            else:
                rel_class = "relevance-low"
                badge_html = f'<span class="relevance-badge badge-cool">📌 {rel}%</span>'

            kw_html = ""
            if matched_kw:
                tags = "".join(f'<span class="keyword-tag">{html_lib.escape(k)}</span>' for k in matched_kw[:5])
                kw_html = f'<div class="keyword-tags">{tags}</div>'

            preview_html = ""
            if safe_content.strip():
                preview_html = f'<div class="post-preview">{safe_content}</div>'

            st.markdown(f"""
            <div class="post-card {rel_class}">
                <div class="post-header">
                    {badge_html}
                    <span class="sub-chip">r/{html_lib.escape(post.get('subreddit', ''))}</span>
                </div>
                <div class="post-title">{safe_title}</div>
                <div class="post-meta">
                    <span class="post-meta-item">👤 {html_lib.escape(post.get('author', 'Unknown'))}</span>
                    <span class="post-meta-item">🕒 {time_ago(post.get('created_utc', 0))}</span>
                    <span class="post-meta-item upvotes">⬆ {post.get('score', 0):,}</span>
                    <span class="post-meta-item comments">💬 {post.get('comments', 0):,}</span>
                </div>
                {preview_html}
                {kw_html}
            </div>
            """, unsafe_allow_html=True)

            spacer, btn_view, btn_remove = st.columns([3, 1, 1])
            with btn_view:
                reddit_url = f"https://reddit.com{post.get('url', '')}"
                st.link_button("Open in Reddit", reddit_url, use_container_width=True)
            with btn_remove:
                if st.button("Remove", key=f"rm_{post['id']}", use_container_width=True):
                    st.session_state.engaged.discard(post["id"])
                    with open(ENGAGED_FILE, "w") as f:
                        json.dump({"posts": list(st.session_state.engaged)}, f)
                    st.toast("Lead removed", icon="🗑️")
                    time.sleep(0.3)
                    st.rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📌</div>
            <div class="empty-title">No saved leads yet</div>
            <div class="empty-desc">Go to the Feed tab and click "Save Lead" on any post to start building your collection of high-value discussions.</div>
        </div>
        """, unsafe_allow_html=True)
