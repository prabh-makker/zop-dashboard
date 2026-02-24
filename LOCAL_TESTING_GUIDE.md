# Local Testing Guide - Reddit Dashboard Refresh Fix

## Quick Test (2 minutes)

### 1. Start the Server
```bash
cd "/Users/zopdev/ research"
python3 app.py
```

The server will start on `http://localhost:8080`

### 2. Open in Browser
Visit: **http://localhost:8080/feed**

### 3. Test the Refresh Button
1. Look at the posts displayed
2. Click the **"🔄 Refresh Posts"** button
3. Notice the alert: "✅ Posts refreshed! 6 new posts loaded"
4. **IMPORTANT**: Observe that the posts on the page **CHANGE** to different ones
5. Click refresh again - different posts appear again!

### 4. Verify Randomization
- Each click should show completely different posts
- Posts should come from different subreddits
- Post titles, scores, and authors should all be different

---

## API Testing (Command Line)

### Test the Refresh Endpoint Directly

```bash
# Single refresh request
curl http://localhost:8080/api/refresh | python3 -m json.tool | head -20

# Multiple refreshes to verify randomization
for i in 1 2 3; do
  echo "Refresh #$i:"
  curl -s http://localhost:8080/api/refresh | python3 -c "import sys, json; data=json.load(sys.stdin); print([p['id'] for p in data])"
  sleep 0.5
done
```

**Expected Output**: Each refresh returns different post IDs

---

## What to Look For

### ✅ Correct Behavior
- Click refresh → Different posts appear
- Refresh #1: Posts A, B, C, D, E, F
- Refresh #2: Posts G, H, I, J, K, L (completely different)
- Refresh #3: Posts M, N, O, P, Q, R (different again)
- Engaged posts don't reappear
- All posts are from the 7-day window

### ❌ Wrong Behavior (If you see this, something's wrong)
- Click refresh → Same posts appear (no change)
- All refreshes show identical post lists
- Posts show dates older than 7 days
- Engaged posts still appear

---

## Testing Checklist

### Functionality Tests
- [ ] Page loads without errors
- [ ] 6 posts visible on initial load
- [ ] Refresh button is clickable
- [ ] Alert shows when refresh is clicked
- [ ] Posts change after refresh
- [ ] Each refresh shows different posts
- [ ] Engage button works (saves posts)
- [ ] Saved posts don't reappear on refresh

### Visual Tests
- [ ] Header displays correctly
- [ ] Posts are formatted nicely
- [ ] Theme toggle button works (if you want)
- [ ] Mobile view is responsive (if you want to test)
- [ ] All text is readable

### API Tests
- [ ] `/api/refresh` returns 6 posts
- [ ] `/api/refresh` returns different posts each call
- [ ] Posts have all required fields (id, title, score, etc.)
- [ ] Relevance scores are present
- [ ] URLs are valid

---

## Stopping the Server

```bash
# Kill the Flask server
pkill -f "python3 app.py"

# Or press Ctrl+C if running in foreground
```

---

## Troubleshooting

### Server Won't Start
```
Error: Address already in use
```
**Solution**: Kill existing Flask process
```bash
lsof -i :8080
kill -9 <PID>
```

### No Posts Display
**Likely Cause**: Network unavailable, no cache
**Solution**:
- Check internet connection
- Ensure cache file exists: `posts_cache.json`
- Restart server

### Posts Don't Change on Refresh
**Likely Cause**: Randomization not working (shouldn't happen)
**Solution**:
- Check that `import random` is in app.py line 13
- Verify `/api/refresh` has `random.shuffle(posts)`
- Restart Flask server

### Same Posts Keep Appearing
**This is expected behavior**: If Reddit API returns same posts (limited new content), the shuffle will randomize which ones are selected. You may see some repeated posts across multiple refreshes if Reddit doesn't have much new content.

---

## Performance Notes

- Initial page load: ~1-2 seconds
- Refresh button response: ~0.5-1 second
- Cache timeout: 5 minutes (then fetches fresh data)
- No database queries (all in-memory with JSON cache)

---

## What's New (Commit 135381e)

The main change is in the `/api/refresh` endpoint:

```python
# Added this line before returning posts
random.shuffle(posts)

# This randomizes which 6 posts are shown from all available posts
# Results in different posts on each refresh instead of same top 6
```

---

## Contact

For issues or questions, refer to:
- `README_REFRESH_FIX.md` - User-friendly guide
- `CHANGES_SUMMARY.md` - Technical details
- `REFRESH_FIX_COMPLETE.md` - Full documentation
- `SESSION_COMPLETE.txt` - Complete session report

---

**Status**: ✅ Ready for testing
**Last Updated**: February 23, 2026
