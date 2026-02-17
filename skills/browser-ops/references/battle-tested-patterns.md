# Battle-Tested Browser Patterns

Patterns extracted from 15-task browser autonomy benchmark (Feb 11-12, 2026). Every pattern below was validated end-to-end on real websites.

Terminology used in this file:
- **SPA:** Single-page application; content updates in JavaScript without full page reloads.
- **OAuth:** Redirect-based login/authorization protocol (for example, "Sign in with GitHub").
- **DOM:** Document Object Model, the browser's tree of page elements.
- **a11y tree:** Accessibility tree used by snapshot tools and assistive technologies.

---

## Pattern 1: Standard Login Flow

**Proven on:** saucedemo.com (Task 1), quotes.toscrape.com (Task 9)

```text
browser_navigate(url="https://site.com/login")
browser_snapshot()                              # find form refs
browser_fill(ref="@eN", text="username")        # username/email field
browser_fill(ref="@eM", text="password")        # password field
browser_click(ref="@eK")                        # submit button
browser_wait(target=".dashboard")               # wait for redirect
browser_snapshot()                              # verify logged in
```

**Key learnings:**
- Always snapshot AFTER login to verify success before proceeding
- Some login forms use Enter key instead of submit button -- use `browser_press(key="Enter")` as fallback
- Session cookies persist within a browser session -- subsequent navigations stay authenticated

---

## Pattern 2: Multi-Field Registration (11-Step Flow)

**Proven on:** automationexercise.com (Task 7), demo.automationtesting.in (Task 2)

```text
1. browser_navigate(url="https://site.com/signup")
2. browser_snapshot()                           # get form refs
3. browser_fill(ref="@eN", text="name")
4. browser_fill(ref="@eM", text="email")
5. browser_fill(ref="@eK", text="password")
6. browser_click(ref="@eJ")                    # gender radio button
7. browser_check(ref="@eI")                    # terms checkbox
8. browser_fill(ref="@eH", text="address")     # additional fields
9. browser_select(ref="@eG", value="US")       # dropdown
10. browser_click(ref="@eF")                   # submit
11. browser_snapshot()                          # verify registration
```

**Key learnings:**
- Radio buttons: use `browser_click`, not `browser_check`
- Native `<select>` dropdowns: use `browser_select(ref, value)`
- Custom dropdowns (React Select, MUI): `browser_click` to open, then `browser_click` on option
- Always verify account creation by checking for success message or dashboard state
- Account deletion (cleanup): navigate to account settings, find delete button, confirm

---

## Pattern 3: Complex Form Widgets

**Proven on:** demoqa.com (Task 3)

### Date Picker
```text
browser_click(ref="@eN")                       # open date picker
browser_snapshot()                              # see calendar widget
browser_click(ref="@eM")                        # select date
browser_snapshot()                              # verify date selected
```

### Autocomplete/Search-as-you-type
```text
browser_type(ref="@eN", text="partial")        # type triggers suggestions
browser_wait(target=".suggestions")            # wait for dropdown
browser_snapshot()                              # see suggestions
browser_click(ref="@eM")                        # select suggestion
```

**Key:** Use `browser_type` (character-by-character) for autocomplete fields, not `browser_fill` (which replaces value instantly without triggering keystrokes).

### File Upload
```text
browser_fill(ref="@eN", text="/path/to/file")  # input[type=file]
```

---

## Pattern 4: SaaS Signup with Email OTP (Notion Flow)

**Proven on:** notion.so (Task 12) -- the standout benchmark task.

This is the most complex validated pattern: real SaaS product, real anti-abuse measures, multi-step with email verification.

```text
# Step 1: Create AgentMail inbox
# (Use agentmail CLI -- see scripts/agentmail.sh)
agentmail create browser-task-01

# Step 2: Navigate to signup
browser_navigate(url="https://www.notion.so/signup")
browser_snapshot()

# Step 3: Enter email from AgentMail
browser_fill(ref="@eN", text="your-mailbox@agentmail.to")
browser_click(ref="@eM")                       # "Continue" or submit

# Step 4: Poll for verification email
agentmail poll your-mailbox@agentmail.to --timeout 120

# Step 5: Extract OTP code from email
agentmail extract <inbox_id> <message_id>
# Returns: { "otp": "123456" } or { "link": "https://..." }

# Step 6: Enter OTP in browser
browser_fill(ref="@eN", text="123456")
browser_click(ref="@eM")                       # submit OTP

# Step 7: Complete onboarding
browser_snapshot()                              # see onboarding form
browser_fill(ref="@eN", text="Agent Workspace")
browser_click(ref="@eM")                       # next
# ... repeat for each onboarding step

# Step 8: Verify dashboard reached
browser_snapshot()                              # should show dashboard
browser_screenshot(path="/tmp/notion-success.png")

# Step 9: Create content (prove full access)
browser_click(ref="@eN")                       # "New page" button
browser_type(ref="@eM", text="Created by agent")
browser_screenshot(path="/tmp/notion-page.png")

# Step 10: Cleanup
browser_close()
```

**Key learnings:**
- OTP emails can take 5-30 seconds to arrive. Always poll with timeout.
- Some services detect `agentmail.to` domain -- have backup strategy.
- OTP codes expire. Extract and submit promptly.
- Notion's onboarding has multiple steps (name, workspace type, team size). Snapshot between each to navigate correctly.
- Screenshot at key milestones for evidence.

---

## Pattern 5: Paginated Scraping with Session

**Proven on:** quotes.toscrape.com (Task 9) -- 50 quotes across 5 pages

```text
browser_navigate(url="https://site.com/page1")
browser_snapshot(mode="compact")               # need text content, not just interactive
# Extract data from snapshot...

# Page 2
browser_click(ref="@eN")                       # "Next" button
browser_snapshot(mode="compact")
# Extract...

# Repeat for pages 3-5
# Session cookies persist across all pages

browser_close()
```

**Key learnings:**
- Use `mode="compact"` for scraping (includes text content). `interactive` mode omits text.
- Session persists automatically -- no need to re-login between pages
- Check for "Next" button existence before clicking (may be last page)

---

## Pattern 6: OAuth Redirect Flow

**Proven on:** dashboard.render.com (Task 13) -- GitHub OAuth

```text
browser_navigate(url="https://site.com/login")
browser_snapshot()
browser_click(ref="@eN")                       # "Sign in with GitHub"

# Browser follows redirect chain automatically
browser_wait(target="2000")                    # wait for redirect
browser_snapshot()                              # should be on GitHub OAuth page

# Fill GitHub credentials (if not already logged in)
browser_fill(ref="@eN", text="github_user")
browser_fill(ref="@eM", text="github_pass")
browser_click(ref="@eK")                       # sign in

# Authorize the app
browser_snapshot()                              # consent screen
browser_click(ref="@eN")                       # "Authorize" button

# Wait for redirect back to original site
browser_wait(target=".dashboard")
browser_snapshot()                              # verify authenticated
```

**Key learnings:**
- Redirect chains are automatic -- browser follows them
- OAuth flows cross domains (site.com -> github.com -> site.com). Refs reset at each navigation.
- Always snapshot after each redirect to re-acquire refs
- Without actual GitHub credentials, the flow stops at the login page (documented as expected behavior)

---

## Pattern 7: Error Recovery

**Proven on:** the-internet.herokuapp.com (Task 14)

### Form Validation Recovery
```text
# Submit incomplete form (intentional)
browser_click(ref="@eN")                       # submit with empty fields
browser_snapshot()                              # see validation errors

# Read error messages, fix each field
browser_fill(ref="@eM", text="corrected value")
browser_click(ref="@eN")                       # resubmit
browser_snapshot()                              # verify success
```

### JavaScript Alert/Confirm/Prompt
```text
# Alerts are handled automatically by agent-browser
browser_click(ref="@eN")                       # triggers alert
# Alert auto-dismissed, continue
browser_snapshot()

# For prompts that need input, use browser_evaluate:
browser_evaluate(script="window.prompt = () => 'agent response'")
browser_click(ref="@eN")                       # triggers prompt
```

### Iframe Content Extraction
```text
browser_snapshot()                              # shows iframe refs
browser_click(ref="@eN")                       # click into iframe
browser_snapshot()                              # now inside iframe context
browser_get_text(ref="@eM")                    # extract iframe content
```

---

## Pattern 8: Multi-Site Autonomous Flow

**Proven on:** Task 15 -- automationexercise.com + quotes.toscrape.com in single session

```text
# Site 1: Full account lifecycle
browser_navigate(url="https://site1.com/signup")
# ... registration flow (Pattern 2) ...
# ... perform authenticated action ...
browser_screenshot(path="/tmp/site1-evidence.png")

# Site 2: Different action
browser_navigate(url="https://site2.com/login")
# ... login flow (Pattern 1) ...
# ... scrape data (Pattern 5) ...
browser_screenshot(path="/tmp/site2-evidence.png")

# Report results from both
browser_close()
```

**Key learnings:**
- Single browser session can visit multiple sites
- Cookies are domain-scoped -- site1 cookies don't affect site2
- Screenshot at each milestone for evidence
- Close browser only once at the very end

---

## Pattern 9: Google Flights SPA Navigation

**Proven on:** google.com/travel/flights (Task 11) -- complex JS-rendered SPA

```text
browser_navigate(url="https://www.google.com/travel/flights")
browser_snapshot()

# Change to one-way
browser_click(ref="@eN")                       # trip type dropdown
browser_snapshot()
browser_click(ref="@eM")                       # "One way" option

# Set departure
browser_click(ref="@eN")                       # "From" field
browser_type(ref="@eM", text="LAX")            # type triggers autocomplete
browser_wait(target="1000")                    # wait for suggestions
browser_snapshot()
browser_click(ref="@eK")                       # select LAX suggestion

# Set destination (same pattern)
browser_click(ref="@eN")                       # "To" field
browser_type(ref="@eM", text="JFK")
browser_wait(target="1000")
browser_snapshot()
browser_click(ref="@eK")

# Set date
browser_click(ref="@eN")                       # date field
browser_snapshot()                              # calendar widget
browser_click(ref="@eM")                       # select date
browser_click(ref="@eK")                       # "Done"

# Search
browser_click(ref="@eN")                       # "Search" button
browser_wait(target=".result-list")            # wait for results
browser_snapshot(mode="compact")               # extract flight data
```

**Key learnings:**
- SPAs require `browser_type` for autocomplete fields (not `browser_fill`)
- Add waits between interactions for dynamic content to load
- Use compact mode for extraction (need text content)
- Sort/filter interactions follow the same click-snapshot-click pattern

---

## Pattern 10: Targeted DOM Extraction (Tier 3)

**Proven on:** Yandex Market (anti-bot workaround)

When a11y tree doesn't show the data you need, or you know exactly where it is:

```text
browser_navigate(url="https://known-site.com/product")

# Extract JSON-LD structured data (bypasses many anti-bot measures)
browser_evaluate(script="document.querySelector('script[type=\"application/ld+json\"]')?.textContent")

# Extract specific element text
browser_evaluate(script="document.querySelector('.price-display').textContent")

# Extract multiple items
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.item')).map(e => ({name: e.querySelector('.name').textContent, price: e.querySelector('.price').textContent})))")

browser_close()
```

**Key learnings:**
- JSON-LD is available on many e-commerce sites without needing interaction
- `browser_evaluate` returns raw text -- parse JSON results in the agent
- Can often get data from page source without any clicking or form filling
- Some sites (Yandex Market) can be scraped entirely via JSON-LD without browser interaction

---

## Pattern 11: Post-Search Verification & Recovery Loop

**Proven on:** Booking.com -- homepage search redirects to city template that strips dates

After submitting any search form, immediately snapshot the results page and verify:
1. Date/filter fields still show selected values
2. URL contains expected parameters
3. Prices are date-specific, not generic "from $X"

```text
# Submit search
browser_click(ref="@eN")                       # search button
browser_wait(target="2000")
browser_snapshot()                              # VERIFY results page

# Check: did the site strip our parameters?
# Signs of param stripping:
#   - Date picker shows "Check-in / Check-out" instead of selected dates
#   - URL is a city template (e.g. /city/my/sandakan.html) not a search results page
#   - Prices show "from $X" instead of per-night rates

# If verification fails — RECOVERY:
# Re-enter parameters using the RESULTS PAGE search bar (not homepage)
browser_click(ref="@eM")                       # date field on results/city page
browser_snapshot()                              # calendar widget
# ... select dates again (Pattern 12) ...
browser_click(ref="@eK")                       # search again from results page

# Second search from results/city page typically preserves params
browser_wait(target="2000")
browser_snapshot()                              # verify date-locked pricing
```

**Key learnings:**
- Server-side redirect only hits the first search from homepage -- second search from city/results page preserves params
- Max 2 recovery attempts before logging as site-level anti-bot pattern
- Always verify prices are date-specific (per-night) not generic ("from $X") before extracting data
- This pattern applies to any travel/booking site, not just Booking.com

---

## Pattern 12: Calendar Widget Protocol

**Proven on:** Booking.com -- calendar clicks worked perfectly, typing would have failed

Never type dates into travel site date fields -- they are often read-only or get overwritten by the calendar widget.

```text
# Step 1: Open the calendar
browser_click(ref="@eN")                       # click date input field
browser_snapshot()                              # see calendar widget with current month

# Step 2: Navigate to target month
# If target month is not visible, use arrow buttons
browser_click(ref="@eM")                       # forward arrow (next month)
browser_snapshot()                              # verify correct month is now displayed
# Repeat until target month is visible

# Step 3: Click the specific date
browser_click(ref="@eK")                       # click date cell by accessible name
                                                # e.g. "Sa 14 March 2026"

# Step 4: Select end date (if date range)
browser_snapshot()                              # calendar may auto-advance to end date selection
browser_click(ref="@eJ")                       # click checkout/end date

# Step 5: Verify before proceeding
browser_snapshot()                              # date button text should show selected dates
# Only proceed to Search after confirming date display is correct
```

**Key learnings:**
- Travel site date fields are almost never standard text inputs -- they are read-only triggers for calendar widgets
- Use accessible names from the a11y tree to identify specific date cells (e.g. "Sa 14 March 2026")
- Always snapshot after date selection to verify the date button/display updated correctly
- Some calendars auto-advance: after selecting check-in, the widget switches to check-out selection mode
- Navigate month-by-month using arrow buttons -- do not try to type or jump to a month

---

## Anti-Patterns from the Benchmark

| Pattern | What Went Wrong | Fix |
|---------|----------------|-----|
| Parallel browser workers | Session collision -- workers fought over same page | Run browser workers SEQUENTIALLY |
| Browser for static content | 20% Codex quota burned on price lookups | Use WebSearch/WebFetch for static data |
| `snapshot(mode="full")` by default | 15K tokens per page wasted | Default to `interactive` (~1,400 tokens) |
| No screenshot evidence | Can't verify what happened after the fact | Screenshot at key milestones |
| Missing `browser_close()` | Orphaned Chromium process blocks next workers | Always close when done |
| Retry against blocked site | Burns more quota for same result | Check failure-log.md first |
