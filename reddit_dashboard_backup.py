import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import List, Dict, Tuple

# Configuration
ENGAGED_HISTORY_FILE = "engaged_history.json"
CACHE_FILE = "reddit_cache.json"
CACHE_DURATION_MINUTES = 30

# Target subreddits
TARGET_SUBREDDITS = [
    "aspirebudgeting", "aws", "AWS_cloud", "AZURE", "books", "booksuggestions",
    "Cloud", "CloudArchitect", "cloudcomputing", "cloudcostoptimization",
    "cloudgovernance", "CloudResearchConnect", "CLOUDS", "cloudstorage",
    "CrealityCloud", "devops", "FinOps", "fintech", "googlecloud", "Heroku",
    "IDP", "kubernetes", "Kubuntu", "literature", "ManagedITSolutions",
    "marketingcloud", "movies", "optimization", "SaaS", "SelfHosting",
    "startup", "suggestmeabook", "sysadmin", "Terraform"
]

# Zop.dev Profile
ZOP_PROFILE = {
    "company": "Zop.dev",
    "products": ["ZopDay", "ZopNight"],
    "descriptions": {
        "ZopDay": "Internal Developer Platform (IDP) for rapid infrastructure provisioning",
        "ZopNight": "FinOps tool for scheduling cloud resource sleep/wake cycles to save costs"
    },
    "keywords": {
        "primary": [
            "FinOps", "AWS cost", "cloud optimization", "infrastructure automation",
            "Kubernetes orchestration", "platform engineering", "cloud governance",
            "resource scheduling", "cost optimization", "cloud infrastructure",
            "infrastructure as code", "DevOps", "cloud cost management"
        ],
        "secondary": [
            "cloud", "infrastructure", "deployment", "automation", "scheduling",
            "resource management", "cost", "optimization", "Kubernetes", "AWS",
            "cloud computing", "platform", "developer tools"
        ]
    }
}


def load_engaged_history() -> set:
    """Load set of post IDs already engaged with."""
    if os.path.exists(ENGAGED_HISTORY_FILE):
        try:
            with open(ENGAGED_HISTORY_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("engaged_posts", []))
        except Exception as e:
            st.warning(f"Error loading history: {e}")
            return set()
    return set()


def save_engaged_history(engaged_posts: set):
    """Save set of engaged post IDs to file."""
    try:
        with open(ENGAGED_HISTORY_FILE, "w") as f:
            json.dump({"engaged_posts": list(engaged_posts)}, f, indent=2)
    except Exception as e:
        st.error(f"Error saving history: {e}")


def load_cache() -> Dict:
    """Load cached Reddit data if fresh."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                if datetime.now() - cache_time < timedelta(minutes=CACHE_DURATION_MINUTES):
                    return cache
        except Exception:
            pass
    return None


def save_cache(data: Dict):
    """Save Reddit data to cache."""
    try:
        cache = {"timestamp": datetime.now().isoformat(), "posts": data}
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        st.warning(f"Cache save failed: {e}")


def fetch_reddit_posts(subreddit: str, limit: int = 25) -> List[Dict]:
    """Fetch recent posts from a subreddit using public JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/new.json"
    headers = {"User-Agent": "ZopDevLeadDiscovery/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        posts = []

        for item in data.get("data", {}).get("children", []):
            post = item.get("data", {})
            created_time = datetime.fromtimestamp(post.get("created_utc", 0))

            # Only include posts from last 7 days
            if datetime.now() - created_time > timedelta(days=7):
                continue

            posts.append({
                "id": post.get("id"),
                "title": post.get("title", ""),
                "content": post.get("selftext", ""),
                "author": post.get("author", "[deleted]"),
                "subreddit": subreddit,
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": post.get("created_utc", 0),
                "url": post.get("url", ""),
                "permalink": post.get("permalink", ""),
                "is_self": post.get("is_self", True)
            })

        return posts

    except requests.exceptions.RequestException as e:
        st.warning(f"Error fetching from r/{subreddit}: {str(e)[:100]}")
        return []


def calculate_relevance_score(post: Dict) -> int:
    """Calculate relevance score (0-100) based on Zop.dev profile."""
    title = post.get("title", "").lower()
    content = post.get("content", "").lower()
    combined_text = f"{title} {content}"

    score = 0

    # Primary keywords: +10 points each
    for keyword in ZOP_PROFILE["keywords"]["primary"]:
        if keyword.lower() in combined_text:
            score += 10

    # Secondary keywords: +3 points each
    for keyword in ZOP_PROFILE["keywords"]["secondary"]:
        if keyword.lower() in combined_text:
            score += 3

    # Bonus for product mentions
    if "idp" in combined_text or "internal developer platform" in combined_text:
        score += 15
    if "finops" in combined_text or "cost optimization" in combined_text:
        score += 15

    # Normalize to 0-100
    return min(100, score)


def get_all_posts() -> List[Dict]:
    """Fetch posts from all target subreddits."""
    # Check cache first
    cache = load_cache()
    if cache:
        st.info("📦 Using cached data (refreshes every 30 minutes)")
        return cache.get("posts", [])

    all_posts = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, subreddit in enumerate(TARGET_SUBREDDITS):
        status_text.text(f"Fetching from r/{subreddit}... ({idx + 1}/{len(TARGET_SUBREDDITS)})")
        posts = fetch_reddit_posts(subreddit)
        all_posts.extend(posts)
        progress_bar.progress((idx + 1) / len(TARGET_SUBREDDITS))
        time.sleep(0.5)  # Rate limit friendly

    progress_bar.empty()
    status_text.empty()

    # Save to cache
    save_cache(all_posts)

    return all_posts


def filter_and_score_posts(posts: List[Dict], engaged_history: set) -> pd.DataFrame:
    """Filter engaged posts and calculate relevance scores."""
    filtered_posts = [p for p in posts if p["id"] not in engaged_history]

    for post in filtered_posts:
        post["relevance_score"] = calculate_relevance_score(post)

    df = pd.DataFrame(filtered_posts)

    if len(df) > 0:
        # Sort by relevance score descending, then by score
        df = df.sort_values(by=["relevance_score", "score"], ascending=[False, False])

    return df


def format_time(timestamp: int) -> str:
    """Format unix timestamp to readable time."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")


def display_post_card(post: Dict, relevance_score: int):
    """Display a professional post card with interactions."""
    # Determine relevance level
    if relevance_score >= 75:
        badge_html = f'<span class="relevance-badge relevance-high">🔥 HIGH RELEVANCE — {relevance_score}%</span>'
    elif relevance_score >= 50:
        badge_html = f'<span class="relevance-badge relevance-medium">✅ MEDIUM RELEVANCE — {relevance_score}%</span>'
    else:
        badge_html = f'<span class="relevance-badge relevance-low">📌 LOW RELEVANCE — {relevance_score}%</span>'

    # Post preview text
    preview = post["content"]
    if preview and len(preview) > 250:
        preview = preview[:250] + "..."

    # Post metadata
    post_meta = f"""
    <div class="post-meta">
        <span class="post-meta-item">📍 r/{post['subreddit']}</span>
        <span class="post-meta-item">👤 {post['author']}</span>
        <span class="post-meta-item">📅 {format_time(post['created_utc'])}</span>
        <span class="post-meta-item">⬆️ {post['score']:,}</span>
        <span class="post-meta-item">💬 {post['num_comments']:,}</span>
    </div>
    """

    preview_section = f"""
    <div class="post-preview">
        {preview if preview else "No content preview available"}
    </div>
    """ if preview else ""

    # Create the card HTML
    card_html = f"""
    <div class="post-card">
        {badge_html}
        <div class="post-title">{post['title']}</div>
        {post_meta}
        {preview_section}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # Buttons in columns
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        reddit_url = f"https://www.reddit.com{post['permalink']}"
        st.link_button("🔗 Visit", reddit_url, use_container_width=True)

    with col3:
        if st.button("✓ Engaged", key=f"mark_{post['id']}", use_container_width=True):
            engaged_history = load_engaged_history()
            engaged_history.add(post["id"])
            save_engaged_history(engaged_history)
            st.success("✓ Marked!")
            time.sleep(0.5)
            st.rerun()

    st.divider()


def main():
    """Main Streamlit app."""
    # Configure Streamlit theme with professional styling
    st.set_page_config(
        page_title="Zop.dev Lead Discovery Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Professional CSS styling
    st.markdown("""
    <style>
    /* Professional color scheme */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00a3ff;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ff9800;
        --dark-bg: #f5f7fa;
        --card-bg: #ffffff;
        --text-primary: #1a1a1a;
        --text-secondary: #666666;
        --border-color: #e0e0e0;
    }

    /* Main container */
    .main-header {
        background: linear-gradient(135deg, #0066cc 0%, #00a3ff 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 102, 204, 0.1);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
    }

    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        opacity: 0.95;
    }

    /* Post card styling */
    .post-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .post-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #0066cc;
    }

    .relevance-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 12px;
        font-size: 0.9em;
    }

    .relevance-high {
        background: #ff4444;
        color: white;
    }

    .relevance-medium {
        background: #ffb84d;
        color: white;
    }

    .relevance-low {
        background: #66bb6a;
        color: white;
    }

    .post-title {
        font-size: 1.2em;
        font-weight: 600;
        color: #1a1a1a;
        margin: 12px 0;
        line-height: 1.4;
    }

    .post-meta {
        display: flex;
        gap: 20px;
        font-size: 0.9em;
        color: #666666;
        margin: 12px 0;
        flex-wrap: wrap;
    }

    .post-meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .post-preview {
        background: #f5f7fa;
        padding: 12px;
        border-left: 4px solid #0066cc;
        border-radius: 4px;
        margin: 12px 0;
        font-size: 0.95em;
        color: #666666;
        line-height: 1.5;
    }

    /* Metrics cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .metric-card.high {
        border-left-color: #ff4444;
    }

    .metric-card.medium {
        border-left-color: #ffb84d;
    }

    .metric-card.low {
        border-left-color: #66bb6a;
    }

    /* Buttons */
    .button-group {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    /* Sidebar styling */
    .sidebar-section {
        background: #f5f7fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .sidebar-section h3 {
        margin-top: 0;
        color: #0066cc;
        font-weight: 600;
    }

    /* Statistics row */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin-bottom: 20px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 600;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #0066cc;
    }
    </style>
    """, unsafe_allow_html=True)

    # Professional header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Zop.dev Lead Discovery Dashboard</h1>
        <p>AI-Powered Reddit Lead Discovery for Infrastructure & FinOps Solutions</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar info
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3>📋 Zop.dev Profile</h3>
            <p><strong>Company:</strong> Zop.dev</p>
            <p><strong>Products:</strong></p>
            <ul style="margin: 8px 0; padding-left: 20px;">
                <li>🏗️ <strong>ZopDay</strong> - Internal Developer Platform</li>
                <li>💰 <strong>ZopNight</strong> - FinOps Cost Optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Stats
        engaged_history = load_engaged_history()
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Dashboard Stats</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("📌 Engaged", len(engaged_history))
        with col2:
            st.metric("✨ Active", "—")

        st.divider()

        # Controls
        st.markdown("""
        <div class="sidebar-section">
            <h3>🎛️ Controls</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True, help="Refresh data from Reddit"):
                if os.path.exists(CACHE_FILE):
                    os.remove(CACHE_FILE)
                st.rerun()

        with col2:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear engagement history"):
                save_engaged_history(set())
                st.success("✓ Cleared!")
                st.rerun()

        st.divider()

        st.markdown("""
        <div style="font-size: 0.85em; color: #666666; line-height: 1.6;">
            <p><strong>📊 Configuration</strong></p>
            <p>Subreddits: <strong>36</strong></p>
            <p>Window: <strong>Last 7 days</strong></p>
            <p>Cache: <strong>30 minutes</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    st.markdown("## 🎯 Filtered & Scored Leads")

    with st.spinner("⏳ Loading Reddit posts from 36 subreddits..."):
        all_posts = get_all_posts()
        engaged_history = load_engaged_history()
        df = filter_and_score_posts(all_posts, engaged_history)

    if len(df) == 0:
        st.info("✅ No new posts! You've engaged with all available leads. Click 🗑️ Clear to see all posts again.")
    else:
        # Professional statistics section
        st.markdown("### 📈 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total Posts", len(df), delta="unreviewed")

        with col2:
            high_relevance = len(df[df["relevance_score"] >= 75])
            st.metric("🔥 High Relevance", high_relevance)

        with col3:
            medium_relevance = len(df[(df["relevance_score"] >= 50) & (df["relevance_score"] < 75)])
            st.metric("✅ Medium Relevance", medium_relevance)

        with col4:
            avg_score = df["relevance_score"].mean()
            st.metric("📈 Avg Score", f"{avg_score:.0f}%")

        st.divider()

        # Display posts with better spacing
        st.markdown("### 🔗 Lead Posts")
        for idx, row in df.iterrows():
            display_post_card(row.to_dict(), row["relevance_score"])


if __name__ == "__main__":
    main()
