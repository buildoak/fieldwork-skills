# Reddit Scraping Playbook

**Target:** https://old.reddit.com (NOT reddit.com)
**Tested:** Feb 2026
**Result:** PASS (after retry)
**Stealth:** Layer 1 sufficient for old.reddit.com

## What Works

### Use old.reddit.com exclusively

```
browser_navigate(url="https://old.reddit.com/r/programming")
browser_snapshot()

# If initial page shows "blocked by network security" message:
# Retry with ?sort=hot appended
browser_navigate(url="https://old.reddit.com/r/programming?sort=hot")
browser_wait(target="2000")
browser_snapshot()
```

### Extract data via browser_evaluate (not snapshots)

```
# Extract posts with targeted JS DOM queries
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.thing')).slice(0, 5).map(el => ({title: el.querySelector('a.title')?.textContent, score: el.querySelector('.score.unvoted')?.textContent, comments: el.querySelector('.comments')?.textContent, url: el.querySelector('a.title')?.href})))")

# Extract comments from a thread
browser_navigate(url="https://old.reddit.com/r/programming/comments/<thread_id>")
browser_wait(target="1000")
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.comment .md')).slice(0, 10).map(el => el.textContent.trim()))")

browser_close()
```

### Performance

- 14 tool calls, 25.4 seconds
- 5 posts + 3 comments extracted
- Used `browser_evaluate` with JS DOM queries for structured extraction

## What Doesn't Work

1. **reddit.com (modern SPA).** The modern Reddit SPA has aggressive anti-automation. Client-side rendering with obfuscated DOM, headless browser detection triggers a silent block. Do not use reddit.com for browser automation.

2. **Parsing accessibility snapshots on old.reddit.com.** The a11y tree on Reddit pages is dense and inefficient to parse. Use `browser_evaluate` instead.

3. **First navigation without retry.** old.reddit.com sometimes returns a "blocked by network security" page on the initial request. The retry with `?sort=hot` parameter bypasses this.

## Key Patterns

- **old.reddit.com, always.** Simple HTML version. Clean DOM structure. CSS selectors work predictably. No client-side rendering complexity.
- **`?sort=hot` retry pattern.** If the first navigation to old.reddit.com returns a block page, append `?sort=hot` to the URL and retry. This consistently bypasses the initial block.
- **`browser_evaluate` for extraction.** Do not parse the a11y tree for data extraction on Reddit. Use targeted JS DOM queries via `browser_evaluate`. The selectors on old.reddit.com are stable: `.thing` for posts, `a.title` for post titles, `.score.unvoted` for scores, `.comments` for comment counts, `.comment .md` for comment text.
- **Slice results.** Reddit pages can have many posts. Use `.slice(0, N)` in your evaluate script to limit extraction to what you need.

## Anti-Bot Notes

- **reddit.com is hostile territory.** Modern SPA with aggressive anti-bot detection. Obfuscated DOM, headless browser detection, silent blocking. Do not attempt.
- **old.reddit.com has basic protection only.** Initial "blocked by network security" page is bypassed with the `?sort=hot` retry. No CAPTCHA, no Cloudflare.
- **Layer 1 stealth is sufficient.** Headed mode + custom UA + persistent profile works for old.reddit.com.
- **Consider alternatives first.** For public Reddit data, the Reddit API or WebFetch may be more efficient than browser automation. Use browser only when you need authenticated access or interaction.

## Sample Worker Prompt

```
Scrape the top 5 posts from r/programming on Reddit.

CRITICAL: Use old.reddit.com, NOT reddit.com. The modern Reddit SPA blocks headless browsers.

Steps:
1. Navigate to https://old.reddit.com/r/programming
2. If you see a "blocked by network security" page, retry with https://old.reddit.com/r/programming?sort=hot
3. Use browser_evaluate with JS DOM queries to extract data (do NOT parse accessibility snapshots -- they are too large):
   JSON.stringify(Array.from(document.querySelectorAll('.thing')).slice(0, 5).map(el => ({
     title: el.querySelector('a.title')?.textContent,
     score: el.querySelector('.score.unvoted')?.textContent,
     comments: el.querySelector('.comments')?.textContent,
     url: el.querySelector('a.title')?.href
   })))
4. Navigate to the top post's comment thread
5. Extract the first 3 top-level comments using browser_evaluate
6. Close browser

Report: 5 post titles with scores and comment counts, plus 3 comments from the top thread.
```
