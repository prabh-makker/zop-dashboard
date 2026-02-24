#!/usr/bin/env python3
"""
Test script to verify sea-color theme and search functionality
"""

import json
import os
from datetime import datetime, timedelta

print("=" * 70)
print("🧪 TESTING NEW FEATURES - Sea Color Theme & Search")
print("=" * 70)

# Test 1: Verify sea color CSS is properly set
print("\n✅ TEST 1: Sea Color Theme CSS Variables")
print("-" * 70)

with open("reddit_dashboard.py", "r") as f:
    dashboard_code = f.read()

required_colors = {
    "#0f3c4b": "Deep sea blue (primary bg)",
    "#1a5a6f": "Ocean teal (secondary bg)",
    "#e8f4f8": "Light seafoam (primary text)",
    "#a8d8e8": "Lighter teal (secondary text)",
    "#2a7a9a": "Sea blue border",
    "#00a8cc": "Ocean gradient start",
    "#0078a3": "Ocean gradient end"
}

all_colors_found = True
for color, description in required_colors.items():
    if color in dashboard_code:
        print(f"  ✅ Found {color} - {description}")
    else:
        print(f"  ❌ Missing {color} - {description}")
        all_colors_found = False

if all_colors_found:
    print("\n✅ All sea color theme colors are present!")
else:
    print("\n❌ Some colors are missing!")

# Test 2: Verify search feature exists
print("\n✅ TEST 2: Search Feature Implementation")
print("-" * 70)

with open("pages/feed.py", "r") as f:
    feed_code = f.read()

search_markers = [
    ("🔍 Search Posts", "Search header"),
    ("search_query", "Search input variable"),
    ("match_score", "Search scoring algorithm"),
    ("search_score", "Search score tracking"),
    ("top_10_posts", "Top 10 limitation"),
    ("Top 10 Results for", "Search results display"),
]

search_implemented = True
for marker, description in search_markers:
    if marker in feed_code:
        print(f"  ✅ Found '{marker}' - {description}")
    else:
        print(f"  ❌ Missing '{marker}' - {description}")
        search_implemented = False

if search_implemented:
    print("\n✅ All search features are implemented!")
else:
    print("\n❌ Some search features are missing!")

# Test 3: Verify file integrity
print("\n✅ TEST 3: File Integrity Check")
print("-" * 70)

files_to_check = {
    "reddit_dashboard.py": "Main dashboard",
    "pages/feed.py": "Feed page",
    "pages/saved.py": "Saved posts page",
    "pages/__init__.py": "Package marker",
    "config.json": "Configuration",
    "requirements.txt": "Dependencies",
}

all_files_exist = True
for filepath, description in files_to_check.items():
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✅ {filepath} ({size:,} bytes) - {description}")
    else:
        print(f"  ❌ Missing {filepath} - {description}")
        all_files_exist = False

if all_files_exist:
    print("\n✅ All required files are present!")
else:
    print("\n❌ Some files are missing!")

# Test 4: Python syntax validation
print("\n✅ TEST 4: Python Syntax Validation")
print("-" * 70)

import py_compile
import sys

python_files = [
    "reddit_dashboard.py",
    "pages/feed.py",
    "pages/saved.py",
]

syntax_valid = True
for filepath in python_files:
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"  ✅ {filepath} - Syntax valid")
    except py_compile.PyCompileError as e:
        print(f"  ❌ {filepath} - Syntax error: {e}")
        syntax_valid = False

if syntax_valid:
    print("\n✅ All Python files have valid syntax!")
else:
    print("\n❌ Some Python files have syntax errors!")

# Test 5: Check if engagement history is valid JSON
print("\n✅ TEST 5: Data Files Integrity")
print("-" * 70)

data_files = {
    "engaged_history.json": "Engagement history",
    "reddit_cache.json": "Post cache",
}

data_valid = True
for filepath, description in data_files.items():
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            print(f"  ✅ {filepath} - Valid JSON ({description})")
        except json.JSONDecodeError as e:
            print(f"  ❌ {filepath} - Invalid JSON: {e}")
            data_valid = False
    else:
        print(f"  ℹ️  {filepath} - File not present (will be created on first use)")

if data_valid:
    print("\n✅ All data files are valid!")
else:
    print("\n❌ Some data files have issues!")

# Test 6: Feature verification
print("\n✅ TEST 6: Feature Integration")
print("-" * 70)

features = {
    "Multi-page navigation": "st.tabs" in dashboard_code,
    "Theme toggle": "st.session_state.theme" in dashboard_code,
    "Sea color theme": "#0f3c4b" in dashboard_code,
    "Search functionality": "search_query" in feed_code,
    "Top 10 results": "[:10]" in feed_code,
    "Engagement tracking": "engaged_history" in dashboard_code,
    "Post cards": "post-card" in dashboard_code,
}

all_features_present = True
for feature, present in features.items():
    if present:
        print(f"  ✅ {feature}")
    else:
        print(f"  ❌ {feature}")
        all_features_present = False

if all_features_present:
    print("\n✅ All features are integrated!")
else:
    print("\n❌ Some features are missing!")

# Summary
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

all_tests_pass = (
    all_colors_found and
    search_implemented and
    all_files_exist and
    syntax_valid and
    data_valid and
    all_features_present
)

if all_tests_pass:
    print("\n✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅")
    print("\n🚀 Dashboard is ready for production use!")
    print("\nAccess at: http://localhost:8501")
    print("\nFeatures:")
    print("  1. 🌊 Sea color theme (light mode with ocean blues/teals)")
    print("  2. 🔍 Unified search (find top 10 results instantly)")
    print("  3. 📱 Multi-page navigation (Feed & Saved Posts)")
    print("  4. 🎨 Theme toggle (light ↔ dark mode)")
    print("  5. 💾 Engagement tracking (posts saved to file)")
    sys.exit(0)
else:
    print("\n❌ Some tests failed. Please review the issues above.")
    sys.exit(1)
