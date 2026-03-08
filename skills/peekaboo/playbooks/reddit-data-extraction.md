---
status: validated
validated: 2026-02-22
domain: browser-automation
---
# Reddit Authenticated Data Extraction

## When to Use
Extract post analytics (views, upvotes, ratio, country breakdown) from Reddit Post Insights panel. This data is only available to the post author via the UI, not via API.

## Prerequisites
- Logged into Reddit as the post author (see `reddit-login.md`)
- Post URL or ability to navigate to user profile
- VLM available for `see --analyze` (stats are visual, not in DOM)

## Flow

1. Navigate to the post (direct URL or via user profile):
   ```bash
   peekaboo-safe.sh open "https://www.reddit.com/user/USERNAME" --app Safari --wait-until-ready
   sleep 3
   ```

2. If navigating from profile, find and click into the target post:
   ```bash
   peekaboo-safe.sh see --analyze "Can I see a list of posts? Which post matches TITLE?" --app Safari
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 3
   ```

3. Locate and click the Insights button (typically below the post, near share/save):
   ```bash
   peekaboo-safe.sh see --analyze "Is there an Insights button or analytics icon below the post?" --app Safari
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 2
   ```

4. Extract stats via VLM analysis (data is rendered visually, not in DOM text nodes):
   ```bash
   peekaboo-safe.sh see --analyze "Read all statistics shown: total views, upvotes, upvote ratio, comments, shares, and any country/region breakdown. Report exact numbers." --app Safari
   ```

5. Scroll for additional stats if needed:
   ```bash
   peekaboo-safe.sh scroll --direction down --amount 3 --app Safari
   sleep 1
   peekaboo-safe.sh see --analyze "Are there additional statistics below? Read any country breakdown, traffic sources, or time-series data." --app Safari
   ```

## Key Patterns

- **Post Insights is author-only.** Not available via Reddit API, not visible to other users. Must be logged in as the post author.
- **Stats are visual, not DOM-accessible.** The Insights panel renders charts and numbers as styled components. `see --analyze` with a specific question is the extraction method, not JS querySelector.
- **VLM as structured data reader.** Ask specific questions: "What is the exact view count?" gets better results than "What do you see?"
- **Profile navigation path:** User profile -> Posts tab -> Click post -> Insights button. Each step needs a fresh `see` for coordinates.

## Known Issues

- Insights button may not appear immediately after posting (Reddit delays analytics by a few hours).
- Country breakdown may not show for posts with low view counts.
- If the Insights panel uses a modal/overlay, scrolling may dismiss it — extract all data before scrolling.
- VLM may misread numbers in charts (e.g., "1.2K" vs "12K") — cross-verify with upvote count visible on the post itself.

## Evidence
- Validated Feb 22, 2026 on Safari
- Successfully extracted views, upvotes, ratio, and country breakdown from live posts
