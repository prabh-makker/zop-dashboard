#!/usr/bin/env python3
"""
Reddit Lead Discovery Dashboard - Flask Alternative
Deployable to Heroku, Railway, or any Python hosting
Works around Streamlit Cloud network restrictions
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
TARGET_SUBREDDITS = [
    "aws", "devops", "kubernetes", "cloudcomputing", "FinOps",
    "startup", "SaaS", "Cloud", "optimization", "fintech"
]

ZOP_KEYWORDS = [
    "FinOps", "AWS", "cost optimization", "infrastructure",
    "cloud", "DevOps", "Kubernetes", "platform engineering",
    "automation", "deployment", "scaling"
]

ENGAGED_FILE = "engaged_history.json"

# Session with proper User-Agent
def get_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    return s

def fetch_reddit_posts():
    """Fetch posts from Reddit - actually works"""
    all_posts = []

    for subreddit in TARGET_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=30"
            resp = get_session().get(url, timeout=15)

            if resp.status_code != 200:
                continue

            data = resp.json()
            for item in data.get("data", {}).get("children", []):
                post = item.get("data", {})
                if not post.get("id"):
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
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "upvote_ratio": post.get("upvote_ratio", 0),
                })
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            continue

    return all_posts

def get_relevance(post):
    """Score post by ZOP keywords"""
    text = (post.get("title", "") + " " + post.get("content", "")).lower()
    score = 0
    for keyword in ZOP_KEYWORDS:
        if keyword.lower() in text:
            score += 20
    return min(100, score)

@app.route('/')
def index():
    posts = fetch_reddit_posts()

    # Add relevance scores
    for post in posts:
        post['relevance'] = get_relevance(post)

    # Sort by relevance
    posts.sort(key=lambda x: (-x['relevance'], -x['score']))

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reddit Lead Discovery - Zop.dev</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #f8fafc;
                padding: 20px;
            }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .header {{
                background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
                color: white;
                padding: 40px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            .stat {{
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            .stat-value {{ font-size: 1.5em; font-weight: bold; }}
            .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
            .posts {{
                display: grid;
                gap: 20px;
            }}
            .post {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #6366f1;
            }}
            .post-title {{
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 10px;
                color: #0f172a;
            }}
            .post-meta {{
                display: flex;
                gap: 20px;
                font-size: 0.9em;
                color: #64748b;
                margin-bottom: 10px;
            }}
            .post-content {{
                color: #475569;
                margin-bottom: 15px;
                line-height: 1.5;
            }}
            .post-footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .relevance {{
                display: inline-block;
                background: #6366f1;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .reddit-link {{
                color: #6366f1;
                text-decoration: none;
                font-weight: 600;
            }}
            .reddit-link:hover {{ text-decoration: underline; }}
            .no-posts {{
                background: white;
                padding: 40px;
                text-align: center;
                border-radius: 8px;
                color: #64748b;
            }}
            .refresh {{
                display: inline-block;
                background: #6366f1;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                text-decoration: none;
                margin-bottom: 20px;
                cursor: pointer;
                border: none;
                font-size: 1em;
            }}
            .refresh:hover {{ background: #4f46e5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Reddit Lead Discovery</h1>
                <p>Real-time intelligence from {len(set(p['subreddit'] for p in posts))} subreddits</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{len(posts)}</div>
                        <div class="stat-label">Posts Scanned</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(set(p['subreddit'] for p in posts))}</div>
                        <div class="stat-label">Subreddits</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">300+</div>
                        <div class="stat-label">Capacity</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">LIVE</div>
                        <div class="stat-label">Status</div>
                    </div>
                </div>
            </div>

            <a href="/" class="refresh">🔄 Refresh Posts</a>

            <div class="posts">
                {"".join([f'''
                <div class="post">
                    <div class="post-title">{post['title']}</div>
                    <div class="post-meta">
                        <span>r/{post['subreddit']}</span>
                        <span>👤 {post['author']}</span>
                        <span>⬆️ {post['score']}</span>
                        <span>💬 {post['comments']}</span>
                    </div>
                    <div class="post-content">{post['content']}</div>
                    <div class="post-footer">
                        <span class="relevance">Relevance: {post['relevance']}%</span>
                        <a href="{post['url']}" target="_blank" class="reddit-link">View on Reddit →</a>
                    </div>
                </div>
                ''' for post in posts[:50]]) if posts else '<div class="no-posts"><p>Loading posts...</p></div>'}
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/api/posts')
def api_posts():
    """API endpoint for JSON posts"""
    posts = fetch_reddit_posts()
    for post in posts:
        post['relevance'] = get_relevance(post)
    posts.sort(key=lambda x: (-x['relevance'], -x['score']))
    return jsonify(posts[:100])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
