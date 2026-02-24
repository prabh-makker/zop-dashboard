import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict

# Import utility functions from main module
import sys
sys.path.append("..")

from reddit_dashboard import (
    load_engaged_history, save_engaged_history, load_cache,
    format_time, TARGET_SUBREDDITS, calculate_relevance_score
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

def display_saved_post_card(post: Dict, relevance_score: int, post_id: str):
    """Display a saved post card with unsave button."""

    # Get relevance badge
    badge_html, css_class = get_relevance_badge(relevance_score)

    # Post preview text
    preview = post.get("content", "")
    if preview and len(preview) > 250:
        preview = preview[:250] + "..."

    # Create the card HTML
    preview_html = f'<div class="post-preview">{preview}</div>' if preview else ""

    card_html = f"""
    <div class="post-card {css_class}">
        {badge_html}
        <div class="post-title">{post.get('title', 'Untitled')}</div>
        <div class="post-meta">
            <span class="post-meta-item">📍 r/{post.get('subreddit', 'unknown')}</span>
            <span class="post-meta-item">👤 {post.get('author', '[deleted]')}</span>
            <span class="post-meta-item">📅 {format_time(post.get('created_utc', 0))}</span>
            <span class="post-meta-item">⬆️ {post.get('score', 0):,}</span>
            <span class="post-meta-item">💬 {post.get('num_comments', 0):,}</span>
        </div>
        {preview_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # Buttons in a row - View and Unsave
    col1, col2, col3 = st.columns([2, 1, 1])

    with col2:
        if st.button(
            "🔗 View",
            key=f"view_{post_id}",
            use_container_width=True,
            help="Open post on Reddit in new tab"
        ):
            st.link_button(
                "View on Reddit",
                f"https://www.reddit.com{post.get('permalink', '')}",
                use_container_width=True
            )

    with col3:
        if st.button(
            "✖ Unsave",
            key=f"unsave_{post_id}",
            use_container_width=True,
            help="Remove from saved posts"
        ):
            engaged_history = load_engaged_history()
            engaged_history.discard(post_id)
            save_engaged_history(engaged_history)
            st.success("✓ Removed from Saved Posts!")
            time.sleep(0.5)
            st.rerun()

    st.divider()


def show_saved_posts_page():
    """Show the saved posts page."""

    # Create a container for the feed
    st.markdown('<div class="feed-container">', unsafe_allow_html=True)

    # Load saved posts
    engaged_history = load_engaged_history()

    if len(engaged_history) == 0:
        st.markdown("""
        <div class="empty-state">
            <h2>📭 No Saved Posts Yet</h2>
            <p>Posts you engage with from the Feed will appear here.</p>
            <p style="margin-top: 20px; font-size: 0.95em;">👉 Go to the <strong>Feed</strong> tab and click <strong>✓ Engage</strong> to save posts!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Load all posts to match with saved IDs
        cache = load_cache()
        all_posts = cache.get("posts", []) if cache else []

        # Create a map of posts by ID for quick lookup
        posts_by_id = {post.get("id"): post for post in all_posts}

        # Build dataframe of saved posts
        saved_posts_list = []
        for post_id in engaged_history:
            if post_id in posts_by_id:
                post = posts_by_id[post_id]
                post["relevance_score"] = calculate_relevance_score(post)
                saved_posts_list.append(post)

        if len(saved_posts_list) == 0:
            st.markdown("""
            <div class="empty-state">
                <h2>📭 No Cached Data</h2>
                <p>Go to the Feed tab and refresh to fetch posts. Saved posts will appear once you've saved some from the Feed.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Create DataFrame and sort
            df_saved = pd.DataFrame(saved_posts_list)
            df_saved = df_saved.sort_values(by=["relevance_score", "score"], ascending=[False, False])

            # Filter options
            with st.expander("⚙️ Sort & Filter", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    sort_by = st.radio(
                        "Sort by",
                        ["Relevance", "Recent", "Popularity"],
                        horizontal=True
                    )

                with col2:
                    filter_subreddit = st.multiselect(
                        "Filter by Subreddit",
                        df_saved["subreddit"].unique().tolist(),
                        help="Show only posts from selected communities"
                    )

                # Apply sort
                if sort_by == "Recent":
                    df_saved = df_saved.sort_values(by="created_utc", ascending=False)
                elif sort_by == "Popularity":
                    df_saved = df_saved.sort_values(by="score", ascending=False)

                # Apply filter
                if filter_subreddit:
                    df_saved = df_saved[df_saved["subreddit"].isin(filter_subreddit)]

            # Metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Saved</div>
                    <div class="metric-value">{len(engaged_history)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Showing</div>
                    <div class="metric-value">{len(df_saved)}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                high_rel = len(df_saved[df_saved["relevance_score"] >= 75])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">🔥 High Relevance</div>
                    <div class="metric-value">{high_rel}</div>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                avg_rel = int(df_saved["relevance_score"].mean()) if len(df_saved) > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Average Score</div>
                    <div class="metric-value">{avg_rel}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<hr style="margin: 30px 0;">', unsafe_allow_html=True)

            # Display saved posts
            st.markdown(f"### {len(df_saved)} Saved Posts")

            for idx, row in df_saved.iterrows():
                display_saved_post_card(
                    {
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
                    },
                    int(row["relevance_score"]),
                    row["id"]
                )

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Refresh from Feed", use_container_width=True):
                    st.success("Reloading saved posts...")
                    time.sleep(0.3)
                    st.rerun()

            with col2:
                if st.button("🗑️ Clear All Saved", use_container_width=True):
                    if st.session_state.get("confirm_clear_saved"):
                        save_engaged_history(set())
                        st.session_state.confirm_clear_saved = False
                        st.success("All saved posts cleared!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_saved = True
                        st.warning("Click again to confirm clearing all saved posts")

    st.markdown('</div>', unsafe_allow_html=True)
