import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Dict

# Import utility functions from main module
import sys
sys.path.append("..")

from reddit_dashboard import (
    load_engaged_history, save_engaged_history, get_all_posts,
    filter_and_score_posts, format_time, TARGET_SUBREDDITS, calculate_relevance_score
)

def get_relevance_badge(score: int) -> tuple:
    """Get badge HTML and class for relevance score."""
    if score >= 75:
        badge_html = f'<span class="relevance-badge relevance-high">🔥 HIGH — {score}%</span>'
        css_class = "high-relevance"
    elif score >= 50:
        badge_html = f'<span class="relevance-badge relevance-medium">✅ MEDIUM — {score}%</span>'
        css_class = "medium-relevance"
    else:
        badge_html = f'<span class="relevance-badge relevance-low">📌 LOW — {score}%</span>'
        css_class = "low-relevance"
    return badge_html, css_class

def display_feed_post_card(post: Dict, relevance_score: int):
    """Display a professional post card with separate Engage and Open Link buttons."""

    # Get relevance badge
    badge_html, css_class = get_relevance_badge(relevance_score)

    # Post preview text
    preview = post["content"]
    if preview and len(preview) > 250:
        preview = preview[:250] + "..."

    # Create the card HTML
    preview_html = f'<div class="post-preview">{preview}</div>' if preview else ""

    card_html = f"""
    <div class="post-card {css_class}">
        {badge_html}
        <div class="post-title">{post['title']}</div>
        <div class="post-meta">
            <span class="post-meta-item">📍 r/{post['subreddit']}</span>
            <span class="post-meta-item">👤 {post['author']}</span>
            <span class="post-meta-item">📅 {format_time(post['created_utc'])}</span>
            <span class="post-meta-item">⬆️ {post['score']:,}</span>
            <span class="post-meta-item">💬 {post['num_comments']:,}</span>
        </div>
        {preview_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # Buttons in a row - Engage and Open Link
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        if st.button(
            "🔗 Open Link",
            key=f"link_{post['id']}",
            use_container_width=True,
            help="Open post on Reddit in new tab"
        ):
            st.link_button(
                "View on Reddit",
                f"https://www.reddit.com{post['permalink']}",
                use_container_width=True
            )

    with col3:
        if st.button(
            "✓ Engage",
            key=f"engage_{post['id']}",
            use_container_width=True,
            help="Save this post to Saved Posts"
        ):
            engaged_history = load_engaged_history()
            engaged_history.add(post["id"])
            save_engaged_history(engaged_history)
            st.success("✓ Post saved to Saved Posts!")
            time.sleep(0.5)
            st.rerun()

    st.divider()


def show_feed_page():
    """Show the main feed page with all posts."""

    # Create a container for the feed
    st.markdown('<div class="feed-container">', unsafe_allow_html=True)

    # Top control bar with refresh button
    col_title, col_refresh = st.columns([0.9, 0.1])
    with col_title:
        st.markdown("### 🔍 Top 10 Zop.dev Relevant Posts (Last 7 Days)")
    with col_refresh:
        if st.button("🔄 Refresh", help="Reload posts from Reddit"):
            st.cache_data.clear()
            st.rerun()

    # Default search for Zop.dev keywords in last 7 days
    default_search = "FinOps OR AWS cost OR cloud optimization OR infrastructure"
    search_query = st.text_input(
        "Search for posts",
        default_search,
        placeholder="Search keywords (default: Zop.dev relevant topics)...",
        help="Find top 10 posts relevant to Zop.dev from the last 7 days"
    )

    # Initialize session state for filters
    if "filter_min_relevance" not in st.session_state:
        st.session_state.filter_min_relevance = 0
    if "filter_time_window" not in st.session_state:
        st.session_state.filter_time_window = "7d"
    if "filter_subreddits" not in st.session_state:
        st.session_state.filter_subreddits = []
    if "filter_keyword" not in st.session_state:
        st.session_state.filter_keyword = ""

    # Filter section - collapsible
    with st.expander("⚙️ Advanced Filters", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            min_relevance = st.slider(
                "Minimum Relevance Score",
                0, 100, st.session_state.filter_min_relevance,
                help="Show only posts with at least this relevance score",
                key="slider_min_relevance",
                on_change=lambda: st.session_state.update({"filter_min_relevance": st.session_state.slider_min_relevance})
            )

        with col2:
            time_window = st.radio(
                "Time Window",
                ["7d", "3d", "24h", "30d"],
                index=["7d", "3d", "24h", "30d"].index(st.session_state.filter_time_window),
                horizontal=True,
                help="Show posts from this time period",
                key="radio_time_window",
                on_change=lambda: st.session_state.update({"filter_time_window": st.session_state.radio_time_window})
            )

        col3, col4 = st.columns(2)

        with col3:
            selected_subreddits = st.multiselect(
                "Subreddits",
                TARGET_SUBREDDITS,
                default=st.session_state.filter_subreddits,
                help="Filter by specific communities",
                key="multiselect_subreddits",
                on_change=lambda: st.session_state.update({"filter_subreddits": st.session_state.multiselect_subreddits})
            )

        with col4:
            search_keyword = st.text_input(
                "Search Keywords",
                value=st.session_state.filter_keyword,
                help="Filter posts containing these words",
                key="text_keyword",
                on_change=lambda: st.session_state.update({"filter_keyword": st.session_state.text_keyword})
            )

    # Load all posts
    with st.spinner("🔄 Loading posts..."):
        all_posts = get_all_posts()
        engaged_history = load_engaged_history()

    # If unified search query exists, show top 10 results from last 7 days
    if search_query.strip():
        st.markdown("---")
        st.markdown(f"### 📊 Top 10 Results for: *'{search_query}'*")

        # Filter posts from last 7 days
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)

        # Score posts based on search query match
        scored_posts = []
        query_lower = search_query.lower().split()

        for post in all_posts:
            if post["id"] in engaged_history:
                continue

            # Filter by 7-day window
            post_created = post.get("created_utc", 0)
            if post_created < seven_days_ago:
                continue

            # Calculate search relevance score
            title_lower = post.get("title", "").lower()
            content_lower = post.get("content", "").lower()
            subreddit_lower = post.get("subreddit", "").lower()

            match_score = 0
            for query_term in query_lower:
                if query_term in title_lower:
                    match_score += 10
                if query_term in content_lower:
                    match_score += 5
                if query_term in subreddit_lower:
                    match_score += 3

            if match_score > 0:
                post_data = post.copy()
                post_data["search_score"] = match_score
                scored_posts.append(post_data)

        # Sort by search score and get top 10
        scored_posts.sort(key=lambda x: (-x["search_score"], -x.get("score", 0)))
        top_10_posts = scored_posts[:10]

        if top_10_posts:
            st.success(f"✅ Found {len(scored_posts)} matching posts - showing top 10")

            # Display top 10 results
            for idx, post in enumerate(top_10_posts, 1):
                relevance_score = calculate_relevance_score(post)

                # Create visual ranking
                col1, col2 = st.columns([0.5, 9.5])
                with col1:
                    st.markdown(f"### #{idx}")
                with col2:
                    st.markdown(f"**Match Score**: {post.get('search_score', 0)} | **Relevance**: {relevance_score}%")

                display_feed_post_card(
                    {
                        "id": post["id"],
                        "title": post["title"],
                        "content": post["content"],
                        "author": post["author"],
                        "subreddit": post["subreddit"],
                        "score": post["score"],
                        "num_comments": post["num_comments"],
                        "created_utc": post["created_utc"],
                        "url": post["url"],
                        "permalink": post["permalink"],
                        "is_self": post["is_self"]
                    },
                    relevance_score
                )
        else:
            st.warning(f"❌ No posts found matching '{search_query}'. Try different keywords!")

        st.markdown("---")
        return  # Stop here, don't show full feed

    # Build filters dict for advanced filtering (use session state)
    filters = {
        "min_relevance": st.session_state.filter_min_relevance,
        "time_window": st.session_state.filter_time_window,
        "selected_subreddits": st.session_state.filter_subreddits if st.session_state.filter_subreddits else None,
        "search_keyword": st.session_state.filter_keyword if st.session_state.filter_keyword else None
    }

    # Filter and score posts
    df_posts = filter_and_score_posts(all_posts, engaged_history, filters)

    # Show active filters
    active_filters = []
    if filters["min_relevance"] > 0:
        active_filters.append(f"🎯 Relevance: {filters['min_relevance']}%")
    if filters["selected_subreddits"]:
        active_filters.append(f"📍 Subreddits: {len(filters['selected_subreddits'])} selected")
    if filters["time_window"] != "7d":
        active_filters.append(f"📅 Time: {filters['time_window']}")
    if filters["search_keyword"]:
        active_filters.append(f"🔍 Keyword: {filters['search_keyword']}")

    if active_filters:
        st.info("🔽 Active Filters: " + " | ".join(active_filters))

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    total_posts = len(all_posts)
    available_posts = len(df_posts)
    engaged_posts = len(engaged_history)
    high_relevance = len(df_posts[df_posts["relevance_score"] >= 75]) if len(df_posts) > 0 else 0

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Available</div>
            <div class="metric-value">{total_posts}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Posts</div>
            <div class="metric-value">{available_posts}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔥 High Relevance</div>
            <div class="metric-value">{high_relevance}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_relevance = int(df_posts["relevance_score"].mean()) if len(df_posts) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value">{avg_relevance}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr style="margin: 30px 0;">', unsafe_allow_html=True)

    # Display posts
    if len(df_posts) > 0:
        st.markdown(f"### Showing {len(df_posts)} of {len(all_posts)} posts")

        for idx, row in df_posts.iterrows():
            post_data = {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "author": row["author"],
                "subreddit": row["subreddit"],
                "score": row["score"],
                "num_comments": row["num_comments"],
                "created_utc": row["created_utc"],
                "url": row["url"],
                "permalink": row["permalink"],
                "is_self": row["is_self"]
            }
            display_feed_post_card(post_data, int(row["relevance_score"]))
    else:
        st.markdown("""
        <div class="empty-state">
            <h2>📭 No posts found</h2>
            <p>Try adjusting your filters or check back later for new content.</p>
        </div>
        """, unsafe_allow_html=True)

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh Posts (Clear Cache)", use_container_width=True):
            import os
            if os.path.exists("reddit_cache.json"):
                os.remove("reddit_cache.json")
            st.success("Cache cleared! Fetching fresh posts...")
            time.sleep(0.5)
            st.rerun()

    with col2:
        if st.button("🗑️ Clear Engagement History", use_container_width=True):
            if st.session_state.get("confirm_clear"):
                save_engaged_history(set())
                st.session_state.confirm_clear = False
                st.success("History cleared! All posts restored.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all engagement history")

    st.markdown('</div>', unsafe_allow_html=True)
