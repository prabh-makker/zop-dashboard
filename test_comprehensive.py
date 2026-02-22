#!/usr/bin/env python3
"""
Comprehensive Test Suite for Reddit Dashboard
Tests all features: API access, data fetching, UI rendering, engagement, theme toggle, etc.
"""

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "http://localhost:8080"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Test Client"})

# Test Results
results = {
    "passed": 0,
    "failed": 0,
    "errors": [],
    "details": []
}

def test_case(name, condition, details=""):
    """Log test result"""
    if condition:
        results["passed"] += 1
        results["details"].append(f"✅ {name}")
        print(f"✅ {name}")
    else:
        results["failed"] += 1
        results["errors"].append(f"❌ {name}: {details}")
        results["details"].append(f"❌ {name}: {details}")
        print(f"❌ {name}: {details}")

def section(title):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ============================================================================
section("1. BASIC ROUTING & SERVER HEALTH")
# ============================================================================

# Test 1.1: Homepage redirects to /feed
resp = SESSION.get(f"{BASE_URL}/")
test_case("1.1 Homepage redirect to /feed", resp.status_code == 200 and "Feed" in resp.text,
          f"Status: {resp.status_code}")

# Test 1.2: Feed page loads
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("1.2 Feed page loads", resp.status_code == 200, f"Status: {resp.status_code}")

# Test 1.3: Saved posts page loads
resp = SESSION.get(f"{BASE_URL}/saved")
test_case("1.3 Saved posts page loads", resp.status_code == 200, f"Status: {resp.status_code}")

# Test 1.4: Top 10 page loads
resp = SESSION.get(f"{BASE_URL}/top10")
test_case("1.4 Top 10 page loads", resp.status_code == 200, f"Status: {resp.status_code}")

# ============================================================================
section("2. DATA FETCHING - REDDIT API")
# ============================================================================

# Test 2.1: Feed page contains posts
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
post_cards = soup.find_all('div', class_='post')
test_case("2.1 Feed contains post cards", len(post_cards) > 0,
          f"Found {len(post_cards)} posts")

# Test 2.2: Posts have required fields
if post_cards:
    first_post = post_cards[0]
    has_title = first_post.find('div', class_='post-title') is not None
    has_meta = first_post.find('div', class_='post-meta') is not None
    has_buttons = first_post.find('div', class_='post-actions') is not None
    test_case("2.2 Posts have title, meta, and actions",
              has_title and has_meta and has_buttons,
              f"Title: {has_title}, Meta: {has_meta}, Actions: {has_buttons}")

# Test 2.3: Posts have relevance badges
if post_cards:
    badges = soup.find_all('span', class_='relevance-badge')
    test_case("2.3 Posts have relevance badges", len(badges) > 0,
              f"Found {len(badges)} badges")

# Test 2.4: Top 10 endpoint returns ranked posts
resp = SESSION.get(f"{BASE_URL}/top10")
soup = BeautifulSoup(resp.text, 'html.parser')
post_cards = soup.find_all('div', class_='post')
test_case("2.4 Top 10 returns posts", len(post_cards) > 0,
          f"Found {len(post_cards)} posts (expecting up to 10)")

# Test 2.5: Top 10 posts have rank badges
if post_cards:
    rank_badges = [p for p in post_cards if p.find('div', class_='relevance-badge') is not None]
    test_case("2.5 Top 10 posts show ranking", len(rank_badges) > 0,
              f"Posts with rankings: {len(rank_badges)}/{len(post_cards)}")

# ============================================================================
section("3. UI RENDERING & LAYOUT")
# ============================================================================

# Test 3.1: Header with gradient background
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("3.1 Header gradient visible", "667eea" in resp.text and "764ba2" in resp.text,
          "Gradient colors not found in CSS")

# Test 3.2: Navigation tabs present
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
nav_tabs = soup.find_all('a', class_='nav-tab')
test_case("3.2 Navigation tabs present", len(nav_tabs) > 0,
          f"Found {len(nav_tabs)} tabs")

# Test 3.3: Theme toggle button present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("3.3 Theme toggle button present", "theme-toggle" in resp.text,
          "Theme toggle button not found")

# Test 3.4: Stats section displays numbers
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
stats = soup.find_all('div', class_='stat')
test_case("3.4 Stats section displays", len(stats) > 0,
          f"Found {len(stats)} stat boxes")

# ============================================================================
section("4. ENGAGEMENT TRACKING")
# ============================================================================

# Test 4.1: Engage button exists
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
engage_buttons = [btn for btn in soup.find_all('a') if 'engage' in btn.get('href', '').lower()]
test_case("4.1 Engage buttons present", len(engage_buttons) > 0,
          f"Found {len(engage_buttons)} engage buttons")

# Test 4.2: Open Link button exists
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
link_buttons = [btn for btn in soup.find_all('a') if 'reddit.com' in btn.get('href', '').lower()]
test_case("4.2 Open Link buttons present", len(link_buttons) > 0,
          f"Found {len(link_buttons)} link buttons")

# Test 4.3: Engagement JSON file exists or can be created
import os
engaged_file = "/Users/zopdev/ research/engaged_history.json"
test_case("4.3 Engagement file exists", os.path.exists(engaged_file),
          "File will be created on first engagement")

# Test 4.4: Engagement workflow - engage a post
if engage_buttons:
    # Get first engage button URL
    first_engage_url = engage_buttons[0].get('href', '')

    # Count posts before engagement
    resp_before = SESSION.get(f"{BASE_URL}/feed")
    posts_before = len(BeautifulSoup(resp_before.text, 'html.parser').find_all('div', class_='post'))

    # Engage a post
    resp_engage = SESSION.get(BASE_URL + first_engage_url, allow_redirects=True)

    # Count posts after engagement
    resp_after = SESSION.get(f"{BASE_URL}/feed")
    posts_after = len(BeautifulSoup(resp_after.text, 'html.parser').find_all('div', class_='post'))

    posts_decreased = posts_after < posts_before
    test_case("4.4 Engagement removes post from feed", posts_decreased,
              f"Before: {posts_before}, After: {posts_after}")

# Test 4.5: Engaged post appears in Saved
resp_saved = SESSION.get(f"{BASE_URL}/saved")
posts_in_saved = len(BeautifulSoup(resp_saved.text, 'html.parser').find_all('div', class_='post'))
test_case("4.5 Saved posts page displays engaged posts", posts_in_saved > 0,
          f"Found {posts_in_saved} saved posts")

# ============================================================================
section("5. THEME TOGGLE")
# ============================================================================

# Test 5.1: Dark mode CSS present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("5.1 Dark mode styles present", "dark-mode" in resp.text,
          "Dark mode CSS not found")

# Test 5.2: CSS variables defined
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("5.2 CSS variables defined", "--bg-primary" in resp.text and "--text-primary" in resp.text,
          "CSS custom properties not found")

# Test 5.3: JavaScript theme handling present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("5.3 Theme JS functions present", "initTheme" in resp.text and "toggleTheme" in resp.text,
          "Theme JavaScript functions not found")

# Test 5.4: LocalStorage reference present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("5.4 LocalStorage integration present", "localStorage" in resp.text,
          "LocalStorage not referenced in code")

# ============================================================================
section("6. RELEVANCE SCORING")
# ============================================================================

# Test 6.1: Posts have relevance percentages
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
badges = soup.find_all('div', class_='relevance-badge')
test_case("6.1 Relevance badges show percentages", len(badges) > 0 and any('%' in b.text for b in badges),
          f"Found {len(badges)} badges, {sum(1 for b in badges if '%' in b.text)} with %")

# Test 6.2: Relevance values are numeric
if badges:
    try:
        percentages = [int(b.text.replace('%', '').strip()) for b in badges if '%' in b.text]
        valid_percentages = all(0 <= p <= 100 for p in percentages)
        test_case("6.2 Relevance values 0-100", valid_percentages,
                  f"Min: {min(percentages) if percentages else 'N/A'}, Max: {max(percentages) if percentages else 'N/A'}")
    except ValueError as e:
        test_case("6.2 Relevance values 0-100", False, str(e))

# Test 6.3: Posts are sorted by relevance
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
posts = soup.find_all('div', class_='post')
if len(posts) >= 2:
    try:
        relevances = []
        for post in posts[:10]:
            badge = post.find('div', class_='relevance-badge')
            if badge and '%' in badge.text:
                rel = int(badge.text.replace('%', '').replace('💡', '').strip())
                relevances.append(rel)

        is_sorted = relevances == sorted(relevances, reverse=True)
        test_case("6.3 Posts sorted by relevance (descending)", is_sorted,
                  f"Relevances: {relevances[:5]}")
    except Exception as e:
        test_case("6.3 Posts sorted by relevance (descending)", False, str(e))

# ============================================================================
section("7. RESPONSIVE DESIGN")
# ============================================================================

# Test 7.1: Viewport meta tag present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("7.1 Responsive viewport tag", "viewport" in resp.text,
          "Viewport meta tag not found")

# Test 7.2: CSS media queries present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("7.2 Mobile media queries present", "@media" in resp.text and "768px" in resp.text,
          "Mobile breakpoint not found")

# Test 7.3: Container has max-width
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("7.3 Container max-width set", "900px" in resp.text or "max-width" in resp.text,
          "Container width constraint not found")

# ============================================================================
section("8. BUTTON STYLING & INTERACTION")
# ============================================================================

# Test 8.1: Primary button styles present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("8.1 Primary button styles", ".btn-primary" in resp.text or "btn-primary" in resp.text,
          "Primary button class not found")

# Test 8.2: Secondary button styles present
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("8.2 Secondary button styles", ".btn-secondary" in resp.text or "btn-secondary" in resp.text,
          "Secondary button class not found")

# Test 8.3: Button hover effects
resp = SESSION.get(f"{BASE_URL}/feed")
test_case("8.3 Button hover effects", ":hover" in resp.text,
          "Hover styles not found")

# ============================================================================
section("9. CONTENT & METADATA")
# ============================================================================

# Test 9.1: Posts have titles
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
posts = soup.find_all('div', class_='post')
if posts:
    titles = [p.find('div', class_='post-title') for p in posts]
    valid_titles = sum(1 for t in titles if t and t.text.strip())
    test_case("9.1 Posts have titles", valid_titles > 0,
              f"{valid_titles}/{len(posts)} posts have titles")

# Test 9.2: Posts have metadata (author, subreddit, score)
if posts:
    metas = [p.find('div', class_='post-meta') for p in posts]
    valid_metas = sum(1 for m in metas if m and m.text.strip())
    test_case("9.2 Posts have metadata", valid_metas > 0,
              f"{valid_metas}/{len(posts)} posts have metadata")

# Test 9.3: Posts show subreddit
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
test_case("9.3 Subreddit names visible", "r/" in resp.text,
          "Subreddit references not found")

# Test 9.4: Posts show author
resp = SESSION.get(f"{BASE_URL}/feed")
soup = BeautifulSoup(resp.text, 'html.parser')
posts = soup.find_all('div', class_='post')
if posts:
    has_authors = any('u/' in p.text for p in posts)
    test_case("9.4 Author names visible", has_authors,
              "Author references not found")

# ============================================================================
section("10. ERROR HANDLING & EDGE CASES")
# ============================================================================

# Test 10.1: Invalid route returns 404
resp = SESSION.get(f"{BASE_URL}/invalid-route")
test_case("10.1 Invalid route returns 404", resp.status_code == 404,
          f"Status: {resp.status_code}")

# Test 10.2: Empty saved posts handled gracefully
# First clear engagement file if exists
engaged_file = "/Users/zopdev/ research/engaged_history.json"
if os.path.exists(engaged_file):
    os.remove(engaged_file)

resp = SESSION.get(f"{BASE_URL}/saved")
test_case("10.2 Saved page handles no posts", resp.status_code == 200,
          f"Status: {resp.status_code}")

# Test 10.3: Top 10 handles if fewer than 10 posts
resp = SESSION.get(f"{BASE_URL}/top10")
soup = BeautifulSoup(resp.text, 'html.parser')
posts = soup.find_all('div', class_='post')
test_case("10.3 Top 10 works with any post count", resp.status_code == 200,
          f"Status: {resp.status_code}, Posts: {len(posts)}")

# ============================================================================
section("11. API ENDPOINT")
# ============================================================================

# Test 11.1: API endpoint returns JSON
resp = SESSION.get(f"{BASE_URL}/api/posts")
test_case("11.1 API endpoint responds", resp.status_code == 200,
          f"Status: {resp.status_code}")

# Test 11.2: API returns valid JSON
if resp.status_code == 200:
    try:
        data = resp.json()
        test_case("11.2 API returns JSON", isinstance(data, list),
                  f"Type: {type(data)}")
    except:
        test_case("11.2 API returns JSON", False, "Invalid JSON")

# ============================================================================
section("12. PERFORMANCE & STABILITY")
# ============================================================================

# Test 12.1: Page load time acceptable
start = time.time()
resp = SESSION.get(f"{BASE_URL}/feed")
load_time = time.time() - start
test_case("12.1 Feed loads in <5 seconds", load_time < 5,
          f"Load time: {load_time:.2f}s")

# Test 12.2: Multiple page loads don't break state
for i in range(3):
    resp = SESSION.get(f"{BASE_URL}/feed")
    if resp.status_code != 200:
        test_case(f"12.2.{i+1} Repeated page loads stable", False,
                  f"Request {i+1} failed")
        break
else:
    test_case("12.2 Repeated page loads stable", True,
              "3 sequential requests all succeeded")

# ============================================================================
# SUMMARY
# ============================================================================

section("TEST SUMMARY")
print(f"\n📊 Total Tests: {results['passed'] + results['failed']}")
print(f"✅ Passed: {results['passed']}")
print(f"❌ Failed: {results['failed']}")

if results['failed'] > 0:
    print(f"\n🐛 FAILURES:")
    for error in results['errors']:
        print(f"  {error}")

# Save detailed results
with open('/Users/zopdev/ research/test_results.json', 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total': results['passed'] + results['failed'],
        'passed': results['passed'],
        'failed': results['failed'],
        'details': results['details']
    }, f, indent=2)

print(f"\n📄 Full results saved to test_results.json")
print(f"\n{'='*60}")

exit(0 if results['failed'] == 0 else 1)
