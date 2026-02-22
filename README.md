# 🚀 Zop.dev Reddit Lead Discovery Dashboard

**Real-time intelligence platform** to discover high-intent discussions about FinOps, cloud optimization, and infrastructure across 10 Reddit communities.

## Features

✅ **Intelligent Post Discovery**
- Scans 10 subreddits: AWS, DevOps, Kubernetes, Cloud Computing, FinOps, Startup, SaaS, Cloud, Optimization, Fintech
- 300+ posts per cycle (5-minute cache)
- Relevance scoring based on 11 ZOP keywords

✅ **Advanced Filtering**
- **Time Window**: 24h, 3d, 7d, 30d (hour-level precision)
- **Subreddit Selection**: Single or multi-select isolation
- **Search**: Case-insensitive, multi-word OR matching
- **Relevance Score**: 0-100% with keyword tagging

✅ **Lead Management**
- Save/bookmark high-value discussions
- Persistent storage (JSON)
- Separate "Saved Leads" tab for follow-up

✅ **Production-Ready UI/UX**
- Dark slate hero header with decorative gradients
- Metric cards with live counts
- Professional post cards with animations
- Responsive design (desktop/tablet/mobile)
- Google Fonts (Inter) typography

## Testing

✅ **208/208 Tests Passed**
- Server stability & health checks
- Reddit API integration (all 10 subs)
- Relevance scoring algorithm
- All filter combinations
- Engagement persistence
- Code quality & security
- UI/UX component verification
- End-to-end data pipeline

## Deployment

### Local Development
```bash
cd "/Users/zopdev/ research"
source venv/bin/activate
streamlit run reddit_dashboard.py
```

Visit: http://localhost:8501

### Production (Streamlit Cloud)
1. Push to GitHub: https://github.com/your-username/reddit-dashboard
2. Go to https://streamlit.io/cloud
3. Click "New app" → Select this repo
4. Watch it deploy automatically!

## Architecture

- **Backend**: Streamlit 1.28.1
- **Reddit API**: Public JSON endpoints (no auth needed)
- **Caching**: 5-minute TTL with manual refresh button
- **Storage**: JSON files (no database needed)
- **Security**: XSS protection, rate limiting, timeout controls

## Relevance Keywords

FinOps, AWS, cost optimization, infrastructure, cloud, DevOps, Kubernetes, platform engineering, automation, deployment, scaling

## Browser Support

Modern browsers (Chrome, Firefox, Safari, Edge)

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **Last Updated**: 2026-02-22
