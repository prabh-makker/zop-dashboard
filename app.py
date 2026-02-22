#!/usr/bin/env python3
"""
Reddit Lead Discovery Dashboard - Multi-Page UI Redesign
Professional dashboard with Feed, Saved Posts, and theme toggle
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
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

def load_engaged():
    """Load engaged posts from JSON"""
    if os.path.exists(ENGAGED_FILE):
        try:
            with open(ENGAGED_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get("engaged_posts", []))
        except:
            return set()
    return set()

def save_engaged(engaged_set):
    """Save engaged posts to JSON"""
    with open(ENGAGED_FILE, 'w') as f:
        json.dump({"engaged_posts": list(engaged_set)}, f)

def get_demo_posts():
    """Return sample posts for development/testing when Reddit API unavailable"""
    now = datetime.now()
    base_time = now - timedelta(days=2)

    demo_posts = [
        {
            "id": "demo1",
            "title": "How we optimized AWS costs by 45% using FinOps practices",
            "content": "In our Kubernetes cluster, we implemented cloud resource optimization through DevOps automation. Our infrastructure cost reduction came from analyzing AWS spending patterns and implementing deployment strategies.",
            "author": "finops_expert",
            "subreddit": "aws",
            "score": 2847,
            "comments": 156,
            "created_utc": int(base_time.timestamp()),
            "url": "https://reddit.com/r/aws/comments/demo1",
            "upvote_ratio": 0.95,
        },
        {
            "id": "demo2",
            "title": "DevOps automation at scale: Kubernetes deployment pipeline",
            "content": "We scaled our platform engineering team by implementing Infrastructure automation through Kubernetes. Our deployment process now handles cloud scaling automatically using platform engineering best practices.",
            "author": "devops_lead",
            "subreddit": "devops",
            "score": 1923,
            "comments": 89,
            "created_utc": int((base_time + timedelta(hours=2)).timestamp()),
            "url": "https://reddit.com/r/devops/comments/demo2",
            "upvote_ratio": 0.92,
        },
        {
            "id": "demo3",
            "title": "Cost optimization in cloud infrastructure using FinOps",
            "content": "FinOps is transforming how we manage cloud costs. Through proper cloud infrastructure planning and AWS cost analysis, teams can achieve significant savings in their deployment strategy.",
            "author": "cloud_architect",
            "subreddit": "cloudcomputing",
            "score": 1654,
            "comments": 123,
            "created_utc": int((base_time + timedelta(hours=4)).timestamp()),
            "url": "https://reddit.com/r/cloudcomputing/comments/demo3",
            "upvote_ratio": 0.90,
        },
        {
            "id": "demo4",
            "title": "Kubernetes platform engineering: Automating deployments",
            "content": "Our automation framework for Kubernetes deployments reduced deployment time by 70%. Platform engineering practices combined with infrastructure as code enable rapid scaling and cost optimization.",
            "author": "platform_eng",
            "subreddit": "kubernetes",
            "score": 2156,
            "comments": 145,
            "created_utc": int((base_time + timedelta(hours=6)).timestamp()),
            "url": "https://reddit.com/r/kubernetes/comments/demo4",
            "upvote_ratio": 0.93,
        },
        {
            "id": "demo5",
            "title": "Infrastructure automation: DevOps tools comparison",
            "content": "Comparing Kubernetes, Docker, and cloud platform solutions for infrastructure automation. DevOps automation reduces manual deployment tasks and improves scaling capabilities.",
            "author": "devops_tester",
            "subreddit": "devops",
            "score": 1432,
            "comments": 98,
            "created_utc": int((base_time + timedelta(hours=8)).timestamp()),
            "url": "https://reddit.com/r/devops/comments/demo5",
            "upvote_ratio": 0.88,
        },
        {
            "id": "demo6",
            "title": "AWS optimization patterns for FinOps teams",
            "content": "Implementing FinOps practices on AWS requires understanding cost drivers. Our team saved millions through infrastructure optimization and cloud resource planning.",
            "author": "aws_specialist",
            "subreddit": "aws",
            "score": 1876,
            "comments": 112,
            "created_utc": int((base_time + timedelta(hours=10)).timestamp()),
            "url": "https://reddit.com/r/aws/comments/demo6",
            "upvote_ratio": 0.91,
        },
        {
            "id": "demo7",
            "title": "Scaling microservices: Kubernetes and cloud deployment",
            "content": "Microservices architecture on Kubernetes enables automatic scaling. Our platform engineering approach uses cloud-native deployment patterns for optimal resource utilization.",
            "author": "k8s_master",
            "subreddit": "kubernetes",
            "score": 1645,
            "comments": 134,
            "created_utc": int((base_time + timedelta(hours=12)).timestamp()),
            "url": "https://reddit.com/r/kubernetes/comments/demo7",
            "upvote_ratio": 0.89,
        },
        {
            "id": "demo8",
            "title": "Cloud infrastructure cost reduction through automation",
            "content": "Automation is key to infrastructure cost reduction. Using DevOps and FinOps principles, we automated our deployment process and reduced cloud spending significantly.",
            "author": "infra_manager",
            "subreddit": "cloudcomputing",
            "score": 1523,
            "comments": 87,
            "created_utc": int((base_time + timedelta(hours=14)).timestamp()),
            "url": "https://reddit.com/r/cloudcomputing/comments/demo8",
            "upvote_ratio": 0.87,
        },
        {
            "id": "demo9",
            "title": "FinOps and cost optimization: Real-world case study",
            "content": "Our FinOps journey: implementing cost optimization across AWS and Kubernetes infrastructure. DevOps automation helps enforce cost governance in cloud deployments.",
            "author": "finops_practitioner",
            "subreddit": "FinOps",
            "score": 1734,
            "comments": 156,
            "created_utc": int((base_time + timedelta(hours=16)).timestamp()),
            "url": "https://reddit.com/r/FinOps/comments/demo9",
            "upvote_ratio": 0.92,
        },
        {
            "id": "demo10",
            "title": "Platform engineering best practices for cloud deployment",
            "content": "Platform engineering enables teams to deploy applications efficiently. Using Kubernetes, we built an internal developer platform that automates deployment and reduces infrastructure overhead.",
            "author": "platform_builder",
            "subreddit": "devops",
            "score": 1891,
            "comments": 167,
            "created_utc": int((base_time + timedelta(hours=18)).timestamp()),
            "url": "https://reddit.com/r/devops/comments/demo10",
            "upvote_ratio": 0.94,
        },
        {
            "id": "demo11",
            "title": "Scaling AWS infrastructure with cost optimization",
            "content": "Scaling on AWS requires careful cost planning. Our infrastructure scaling strategy combines automation with cost governance to maintain efficiency.",
            "author": "aws_scaler",
            "subreddit": "aws",
            "score": 1567,
            "comments": 95,
            "created_utc": int((base_time + timedelta(hours=20)).timestamp()),
            "url": "https://reddit.com/r/aws/comments/demo11",
            "upvote_ratio": 0.90,
        },
        {
            "id": "demo12",
            "title": "Kubernetes deployment strategies and platform engineering",
            "content": "Our Kubernetes platform enables seamless deployment across infrastructure. Platform engineering automation reduces deployment time and improves cloud resource utilization.",
            "author": "k8s_deployer",
            "subreddit": "kubernetes",
            "score": 1432,
            "comments": 102,
            "created_utc": int((base_time + timedelta(hours=22)).timestamp()),
            "url": "https://reddit.com/r/kubernetes/comments/demo12",
            "upvote_ratio": 0.88,
        },
    ]

    return demo_posts

def fetch_reddit_posts():
    """Fetch REAL posts from Reddit, or demo posts if Reddit unavailable"""
    # Try to fetch from Reddit first
    all_posts = []

    for subreddit in TARGET_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=30"
            resp = get_session().get(url, timeout=3)

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

    # If no posts fetched from Reddit, use demo data for testing
    if not all_posts:
        print("[INFO] Reddit API unreachable - using demo data for UI testing")
        all_posts = get_demo_posts()

    return all_posts

def get_relevance(post):
    """Score post by ZOP keywords"""
    text = (post.get("title", "") + " " + post.get("content", "")).lower()
    score = 0
    for keyword in ZOP_KEYWORDS:
        if keyword.lower() in text:
            score += 20
    return min(100, score)

def get_base_template(content):
    """Base HTML template with shared styles and scripts"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reddit Lead Discovery - Zop.dev</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {{
                --bg-primary: #ffffff;
                --bg-secondary: #f8fafc;
                --text-primary: #0f172a;
                --text-secondary: #475569;
                --text-tertiary: #64748b;
                --border-color: #e2e8f0;
                --card-shadow: rgba(0, 0, 0, 0.08);
            }}

            body.dark-mode {{
                --bg-primary: #1a1f2e;
                --bg-secondary: #0f172a;
                --text-primary: #f1f5f9;
                --text-secondary: #cbd5e1;
                --text-tertiary: #94a3b8;
                --border-color: #334155;
                --card-shadow: rgba(0, 0, 0, 0.3);
            }}

            * {{ margin: 0; padding: 0; box-sizing: border-box; }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: var(--bg-secondary);
                color: var(--text-primary);
                transition: background-color 0.3s, color 0.3s;
            }}

            .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}

            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .header-left h1 {{ font-size: 1.8em; margin-bottom: 5px; }}
            .header-left p {{ font-size: 0.95em; opacity: 0.95; }}

            .header-right {{
                display: flex;
                gap: 15px;
                align-items: center;
            }}

            .theme-toggle {{
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1.2em;
                transition: background 0.3s;
            }}

            .theme-toggle:hover {{ background: rgba(255, 255, 255, 0.3); }}

            .nav-tabs {{
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                border-bottom: 2px solid var(--border-color);
            }}

            .nav-tab {{
                padding: 12px 20px;
                background: none;
                border: none;
                border-bottom: 3px solid transparent;
                cursor: pointer;
                font-size: 1em;
                color: var(--text-tertiary);
                transition: all 0.3s;
                font-weight: 500;
                text-decoration: none;
            }}

            .nav-tab.active {{
                color: #667eea;
                border-bottom-color: #667eea;
            }}

            .nav-tab:hover {{
                color: var(--text-primary);
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}

            .stat {{
                background: var(--bg-primary);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 2px 8px var(--card-shadow);
                border-left: 4px solid #667eea;
            }}

            .stat-value {{ font-size: 1.8em; font-weight: 700; margin-bottom: 5px; }}
            .stat-label {{ font-size: 0.85em; color: var(--text-tertiary); }}

            .posts {{
                display: grid;
                gap: 20px;
            }}

            .post {{
                background: var(--bg-primary);
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 12px var(--card-shadow);
                border-left: 4px solid #667eea;
                transition: all 0.3s;
            }}

            .post:hover {{
                box-shadow: 0 8px 24px var(--card-shadow);
                transform: translateY(-2px);
            }}

            .post-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 12px;
            }}

            .post-title {{
                font-size: 1.15em;
                font-weight: 600;
                color: var(--text-primary);
                flex: 1;
                margin-right: 15px;
            }}

            .relevance-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 700;
                white-space: nowrap;
            }}

            .post-meta {{
                display: flex;
                gap: 20px;
                font-size: 0.9em;
                color: var(--text-tertiary);
                margin-bottom: 12px;
                flex-wrap: wrap;
            }}

            .post-meta span {{
                display: flex;
                align-items: center;
                gap: 5px;
            }}

            .post-content {{
                color: var(--text-secondary);
                margin-bottom: 15px;
                line-height: 1.6;
                font-size: 0.95em;
            }}

            .post-actions {{
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }}

            .btn {{
                padding: 10px 18px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.95em;
                font-weight: 600;
                transition: all 0.3s;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}

            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}

            .btn-secondary {{
                background: var(--bg-secondary);
                color: var(--text-primary);
                border: 2px solid var(--border-color);
            }}

            .btn-secondary:hover {{
                border-color: #667eea;
                color: #667eea;
            }}

            .no-posts {{
                background: var(--bg-primary);
                padding: 60px 40px;
                text-align: center;
                border-radius: 12px;
                color: var(--text-tertiary);
                box-shadow: 0 2px 12px var(--card-shadow);
            }}

            .no-posts h2 {{ font-size: 1.5em; margin-bottom: 10px; color: var(--text-primary); }}

            .refresh-btn {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                margin-bottom: 25px;
                border: none;
                cursor: pointer;
                font-size: 0.95em;
                font-weight: 600;
                transition: all 0.3s;
            }}

            .refresh-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}

            @media (max-width: 768px) {{
                .header {{ flex-direction: column; text-align: center; }}
                .header-right {{ margin-top: 15px; }}
                .post-meta {{ font-size: 0.85em; }}
                .post-actions {{ flex-direction: column; }}
                .btn {{ width: 100%; justify-content: center; }}
                .nav-tabs {{ gap: 5px; }}
                .nav-tab {{ padding: 10px 15px; font-size: 0.9em; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {content}
        </div>
        <script>
            function initTheme() {{
                const savedTheme = localStorage.getItem('theme') || 'light';
                document.body.classList.toggle('dark-mode', savedTheme === 'dark');
                updateThemeButton(savedTheme);
            }}

            function toggleTheme() {{
                const isDark = document.body.classList.toggle('dark-mode');
                const theme = isDark ? 'dark' : 'light';
                localStorage.setItem('theme', theme);
                updateThemeButton(theme);
            }}

            function updateThemeButton(theme) {{
                const btn = document.getElementById('theme-btn');
                if (btn) {{
                    btn.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
                }}
            }}

            initTheme();
        </script>
    </body>
    </html>
    """

@app.route('/')
def index():
    return redirect(url_for('feed'))

@app.route('/feed')
def feed():
    """Main feed page"""
    posts = fetch_reddit_posts()
    engaged = load_engaged()

    for post in posts:
        post['relevance'] = get_relevance(post)

    posts = [p for p in posts if p['id'] not in engaged]
    posts.sort(key=lambda x: (-x['relevance'], -x['score']))

    high_relevance = sum(1 for p in posts if p['relevance'] >= 80)

    posts_html = ""
    if posts:
        for post in posts[:50]:
            posts_html += f"""
            <div class="post">
                <div class="post-header">
                    <div class="post-title">{post['title']}</div>
                    <div class="relevance-badge">💡 {post['relevance']}%</div>
                </div>
                <div class="post-meta">
                    <span>🔗 r/{post['subreddit']}</span>
                    <span>👤 {post['author']}</span>
                    <span>⬆️ {post['score']}</span>
                    <span>💬 {post['comments']}</span>
                </div>
                <div class="post-content">{post['content']}</div>
                <div class="post-actions">
                    <a href="{post['url']}" target="_blank" class="btn btn-secondary">🔗 Open Link</a>
                    <a href="/engage/{post['id']}" class="btn btn-primary">✓ Engage</a>
                </div>
            </div>
            """
    else:
        posts_html = '<div class="no-posts"><h2>📭 No Posts Found</h2><p>Try adjusting filters or come back later</p></div>'

    content = f"""
    <div class="header">
        <div class="header-left">
            <h1>🔍 Reddit Lead Discovery</h1>
            <p>Real-time intelligence from your communities</p>
        </div>
        <div class="header-right">
            <button id="theme-btn" class="theme-toggle" onclick="toggleTheme()">🌙 Dark</button>
        </div>
    </div>

    <div class="nav-tabs">
        <button class="nav-tab active">📰 Feed</button>
        <a href="/saved" class="nav-tab">📌 Saved Posts ({len(engaged)})</a>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value">{len(posts)}</div>
            <div class="stat-label">Posts Available</div>
        </div>
        <div class="stat">
            <div class="stat-value">{high_relevance}</div>
            <div class="stat-label">High Relevance</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(set(p['subreddit'] for p in posts))}</div>
            <div class="stat-label">Subreddits</div>
        </div>
        <div class="stat">
            <div class="stat-value">LIVE</div>
            <div class="stat-label">Status</div>
        </div>
    </div>

    <a href="/feed" class="refresh-btn">🔄 Refresh Posts</a>

    <div class="posts">
        {posts_html}
    </div>
    """

    return get_base_template(content)

@app.route('/saved')
def saved():
    """Saved posts page"""
    # Load engaged posts first to filter early
    engaged = load_engaged()

    if not engaged:
        # No saved posts yet - return empty state quickly
        posts = []
    else:
        posts = fetch_reddit_posts()
        for post in posts:
            post['relevance'] = get_relevance(post)
        posts = [p for p in posts if p['id'] in engaged]
        posts.sort(key=lambda x: (-x['relevance'], -x['score']))

    posts_html = ""
    if posts:
        for post in posts:
            posts_html += f"""
            <div class="post">
                <div class="post-header">
                    <div class="post-title">{post['title']}</div>
                    <div class="relevance-badge">💡 {post['relevance']}%</div>
                </div>
                <div class="post-meta">
                    <span>🔗 r/{post['subreddit']}</span>
                    <span>👤 {post['author']}</span>
                    <span>⬆️ {post['score']}</span>
                    <span>💬 {post['comments']}</span>
                </div>
                <div class="post-content">{post['content']}</div>
                <div class="post-actions">
                    <a href="{post['url']}" target="_blank" class="btn btn-secondary">🔗 Open Link</a>
                    <a href="/unsave/{post['id']}" class="btn btn-primary">🗑️ Unsave</a>
                </div>
            </div>
            """
    else:
        posts_html = '<div class="no-posts"><h2>📭 No Saved Posts Yet</h2><p>Engage with posts to save them here</p></div>'

    content = f"""
    <div class="header">
        <div class="header-left">
            <h1>📌 Saved Posts</h1>
            <p>Your engaged and saved content</p>
        </div>
        <div class="header-right">
            <button id="theme-btn" class="theme-toggle" onclick="toggleTheme()">🌙 Dark</button>
        </div>
    </div>

    <div class="nav-tabs">
        <a href="/feed" class="nav-tab">📰 Feed</a>
        <button class="nav-tab active">📌 Saved Posts ({len(posts)})</button>
    </div>

    <div class="stats">
        <div class="stat">
            <div class="stat-value">{len(posts)}</div>
            <div class="stat-label">Saved Posts</div>
        </div>
        <div class="stat">
            <div class="stat-value">{len(set(p['subreddit'] for p in posts))}</div>
            <div class="stat-label">From Subreddits</div>
        </div>
        <div class="stat">
            <div class="stat-value">{round(sum(p['relevance'] for p in posts) / len(posts), 0) if posts else 0}%</div>
            <div class="stat-label">Avg Relevance</div>
        </div>
        <div class="stat">
            <div class="stat-value">✓</div>
            <div class="stat-label">Curated</div>
        </div>
    </div>

    <div class="posts">
        {posts_html}
    </div>
    """

    return get_base_template(content)

@app.route('/engage/<post_id>')
def engage(post_id):
    """Mark post as engaged"""
    engaged = load_engaged()
    engaged.add(post_id)
    save_engaged(engaged)
    return redirect(url_for('feed'))

@app.route('/unsave/<post_id>')
def unsave(post_id):
    """Remove post from saved"""
    engaged = load_engaged()
    engaged.discard(post_id)
    save_engaged(engaged)
    return redirect(url_for('saved'))

@app.route('/api/posts')
def api_posts():
    """API endpoint for JSON posts"""
    posts = fetch_reddit_posts()
    for post in posts:
        post['relevance'] = get_relevance(post)
    posts.sort(key=lambda x: (-x['relevance'], -x['score']))
    return jsonify(posts[:100])

@app.route('/top10')
def top10():
    """Get top 10 most relevant posts - fresh data each time"""
    posts = fetch_reddit_posts()

    for post in posts:
        post['relevance'] = get_relevance(post)

    # Sort by relevance (descending) then by score
    posts.sort(key=lambda x: (-x['relevance'], -x['score']))

    # Get top 10
    top_posts = posts[:10]

    # Create HTML response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Top 10 Posts - Reddit Lead Discovery</title>
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            }}
            .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
            .posts {{ display: grid; gap: 20px; }}
            .post {{
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.08);
                border-left: 4px solid #667eea;
            }}
            .rank {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 700;
                margin-bottom: 12px;
                font-size: 0.9em;
            }}
            .post-title {{
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 12px;
                color: #0f172a;
            }}
            .post-meta {{
                display: flex;
                gap: 20px;
                font-size: 0.9em;
                color: #64748b;
                margin-bottom: 12px;
                flex-wrap: wrap;
            }}
            .post-content {{
                color: #475569;
                margin-bottom: 15px;
                line-height: 1.6;
            }}
            .post-footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
            }}
            .relevance {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .reddit-link {{
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }}
            .reddit-link:hover {{ text-decoration: underline; }}
            .refresh {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                margin-bottom: 25px;
                font-weight: 600;
                transition: all 0.3s;
            }}
            .refresh:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔥 Top 10 Most Relevant Posts</h1>
                <p>Real-time Reddit intelligence - Fresh data on every search</p>
            </div>

            <a href="/top10" class="refresh">🔄 Refresh (Get Latest Data)</a>

            <div class="posts">
    """

    for rank, post in enumerate(top_posts, 1):
        html += f"""
                <div class="post">
                    <div class="rank">#{rank} - {post['relevance']}% Match</div>
                    <div class="post-title">{post['title']}</div>
                    <div class="post-meta">
                        <span>🔗 r/{post['subreddit']}</span>
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
        """

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
