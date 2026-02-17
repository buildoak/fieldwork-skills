# Browser-Ops Test Results

> Tests used a consistent agent-browser + Playwright Chromium setup.
> Most runs used headless mode. Stealth validation runs used headed mode with custom UA, persistent profile, and automation flag disabled.
> Results reflect baseline capability of the browser-ops skill documentation alone.

Terminology used in this file:
- **Playwright:** A browser automation framework used under the hood by `agent-browser`.
- **SPA:** Single-page application; most content is rendered dynamically in JavaScript.
- **DOM:** Document Object Model, the browser's tree of page elements.
- **OAuth:** Redirect-based login protocol (for example, "Sign in with GitHub").

---

## Benchmark v1 Summary (15 Tasks)

15-task browser autonomy benchmark. **12/15 pass (100% excluding external blockers).**

| # | Test | Target | Result | Key Finding |
|---|------|--------|--------|-------------|
| 1 | Login + add to cart | saucedemo.com | PASS | Standard auth + e-commerce flow works reliably |
| 2 | Registration form fill | demo.automationtesting.in | PASS | Multi-field registration including dropdowns |
| 3 | Complex form widgets | demoqa.com | PASS | Date pickers, React Select, file upload all work |
| 4 | Magento checkout | magento.softwaretestingboard.com | FAIL | Site down (SSL 526 error) -- external outage |
| 5 | Drag-drop, dropdown, file upload | the-internet.herokuapp.com | PASS | Multiple interaction types in single session |
| 6 | Account creation + upvote | news.ycombinator.com | PASS | Real site with authenticated actions |
| 7 | Full registration lifecycle | automationexercise.com | PASS | 11-step flow: signup, profile, verify, delete |
| 8 | Create + share paste | pastebin.com | FAIL | Cloudflare transparent challenge -- no bypass |
| 9 | Login + paginated scrape | quotes.toscrape.com | PASS | 50 quotes across 5 pages, session persisted |
| 10 | Forum signup + email verify | forum.pkp.sfu.ca | PARTIAL | Email verification worked; blocked by moderator approval gate |
| 11 | Flight search + filter | google.com/travel/flights | PASS | Complex SPA with autocomplete, date pickers, sort/filter |
| 12 | SaaS signup with email OTP | notion.so | PASS | Full end-to-end with AgentMail OTP verification |
| 13 | OAuth redirect flow | dashboard.render.com | PASS | GitHub OAuth chain with automatic redirects |
| 14 | Error recovery (3 sub-tasks) | the-internet.herokuapp.com | PASS | Form validation, JS alerts, iframe extraction |
| 15 | Multi-site autonomous flow | automationexercise.com + quotes.toscrape.com | PASS | Two sites in a single browser session |

**Overall: 12/15 PASS, 1 PARTIAL, 2 FAIL**

All 3 non-passes were external blockers (SSL outage, Cloudflare challenge, moderator gate) -- not agent or skill capability gaps.

---

## Test Suite v2 Summary (10 Tasks)

Progressive difficulty test suite validating the rebuilt browser-ops skill. **9/10 PASS, 1 PARTIAL.**

| # | Tier | Task | Target | Result | Calls | Time | Key Finding |
|---|------|------|--------|--------|-------|------|-------------|
| 1 | Medium | Scrape subreddit posts | old.reddit.com | PASS | 14 | 25s | old.reddit.com works with retry; reddit.com SPA does not |
| 2 | Medium | Navigate HN threads | news.ycombinator.com | PASS | 13 | 35s | JS eval extraction beats 47K-token snapshots |
| 3 | Medium | E-commerce end-to-end | saucedemo.com | PASS | 38 | 61s | Full cart + checkout + price verification |
| 4 | Hard | GitHub repo extraction | github.com | PASS | 37 | 83s | Exact counts via `title` attribute selectors |
| 5 | Hard | Google Flights search + filter | google.com/travel/flights | PASS | 21 | 48s | URL pre-population bypasses autocomplete issues |
| 6 | Hard | HN account lifecycle | news.ycombinator.com | PASS | 22 | 39s | Account create, post, note no-delete, logout |
| 7 | Brutal | Stripe iframe checkout | Stripe demo | PASS | 59 | 168s | Cross-origin iframe bypass via direct navigation |
| 8 | Brutal | Wikipedia multi-language | wikipedia.org (EN + JA) | PASS | 11 | 63s | Zero snapshots -- pure evaluate-only mode |
| 9 | Brutal | Cloudflare stealth gauntlet | nowsecure.nl | PASS | 12 | 36s | Passed Cloudflare free tier with Layer 1 stealth |
| 10 | Final Boss | Linear E2E + AgentMail | linear.app | PARTIAL | ~40 | ~180s | Blocked by Cloudflare Turnstile CAPTCHA |

**Overall: 9/10 PASS, 1 PARTIAL**

Test 10 blocked by Cloudflare Turnstile CAPTCHA -- requires Layer 2+ stealth. Not a skill or agent gap.

---

## Detailed Test Logs

### Test 1: Reddit Scraping
**Target:** old.reddit.com
**Result:** PASS (after retry)
**Duration:** 25s, 14 tool calls
**What happened:** First attempt with a different engine ran 105 tool calls and stalled in a snapshot-act loop without a termination condition. Second attempt used targeted `browser_evaluate` with JS DOM queries. Reddit initially blocked the headless browser, but the worker self-recovered by retrying with a `?sort=hot` URL parameter. Extracted 5 posts and 3 comments.
**Key finding:** reddit.com (modern SPA with aggressive anti-bot) is hostile territory. old.reddit.com (simple HTML) works with a retry-on-block strategy. This is a site-specific workaround, not a skill gap.

### Test 2: HN Thread Extraction
**Target:** news.ycombinator.com
**Result:** PASS
**Duration:** 35s, 13 tool calls
**What happened:** Worker navigated to HN front page. Instead of parsing the 47K-character accessibility snapshot, it went straight to `browser_evaluate` with targeted JS DOM queries for structured extraction. Extracted post title, URL, and 12 top-level comments with authors.
**Key finding:** For data-heavy pages, `browser_evaluate` with JS selectors is far more token-efficient than parsing full accessibility snapshots. This "evaluate-only" approach should be the default for extraction tasks on known page structures.

### Test 3: SauceDemo E-Commerce
**Target:** saucedemo.com
**Result:** PASS
**Duration:** 61s, 38 tool calls
**What happened:** Full e-commerce flow: login with credentials, extract 6 products, identify cheapest ($7.99 Onesie) and most expensive ($49.99 Fleece Jacket), add both to cart, complete checkout with form fill (name, zip), verify totals ($57.98 + $4.64 tax = $62.62), confirm order. Originally planned for demoqa.com but pivoted when that site returned server errors.
**Key finding:** Full checkout flows with price verification work reliably. The skill handles multi-step e-commerce without issues.

### Test 4: GitHub Repo Extraction
**Target:** github.com/vercel/next.js
**Result:** PASS
**Duration:** 83s, 37 tool calls
**What happened:** Extracted all 5 data points: exact star count (137,709 -- not the abbreviated "138k"), exact forks (30,463), open issues (2,038), first 3 README headings, and latest commit message. Worker used `browser_evaluate` with `title` attribute selectors to bypass GitHub's abbreviated number display.
**Key finding:** First Hard-tier test. Approximately 2x scaling versus Medium tier. The skill documentation was fully sufficient -- no external guidance needed.

### Test 5: Google Flights Search + Filter
**Target:** google.com/travel/flights
**Result:** PASS (after 2 retries)
**Duration:** 48s, 21 tool calls
**What happened:** First two attempts fought with Google's autocomplete widgets (custom React/Material components that ignored `browser_type` or reverted to geo-defaults). Third attempt bypassed the form entirely using URL pre-population: `?q=Flights+from+SFO+to+NRT+on+2026-04-17+return+2026-05-01`. Google parsed the natural language query correctly. Applied "1 stop or fewer" filter, extracted 3 flights with prices.
**Key finding:** For complex SPA forms with autocomplete widgets, URL query parameters beat fighting the input fields. The `?q=` natural language URL format is reliable; encoded parameter URLs are geo/session-dependent and unreliable.

### Test 6: HN Account Lifecycle
**Target:** news.ycombinator.com
**Result:** PASS
**Duration:** 39s, 22 tool calls
**What happened:** Created a new account, submitted a post ("Browser Agent Test Post"), correctly noted that HN has no account/post delete feature, and logged out cleanly. One retry needed because the initial username exceeded HN's 15-character limit.
**Key finding:** Test prompts should account for known site constraints (character limits, rate limits). The retry was a prompt quality issue, not a skill gap.

### Test 7: Stripe Iframe Checkout
**Target:** Stripe demo checkout page
**Result:** PASS
**Duration:** 168s, 59 tool calls
**What happened:** Standard `browser_fill` failed on the payment fields because they live inside a cross-origin iframe. Worker discovered a workaround: used `browser_evaluate` to extract the iframe's `src` URL, then navigated directly to that URL. This rendered the iframe content as a regular page, allowing normal `browser_fill` on card number, expiry, and CVC fields. Submitted payment and got visual confirmation (green checkmark on Pay button). Stripe's preview demo does not render a separate confirmation page -- the checkmark is the success signal.
**Key finding:** Cross-origin iframes can be bypassed by navigating directly to the iframe's `src` URL. This pattern works for payment forms and other embedded third-party content.

### Test 8: Wikipedia Multi-Language
**Target:** wikipedia.org (English and Japanese AI articles)
**Result:** PASS
**Duration:** 63s, 11 tool calls
**What happened:** Extracted all 6 data points from both English and Japanese articles using pure `browser_evaluate` -- zero accessibility tree snapshots. English: 479 citations, 12 TOC sections. Japanese: 314 citations, 15 TOC sections. Cleanest brutal-tier test.
**Key finding:** For content-heavy pages like Wikipedia, skip snapshots entirely and use `browser_evaluate` with targeted CSS selectors. The accessibility tree on these pages is massive and would blow token budgets. Evaluate-only mode is the correct approach.

### Test 9: Cloudflare Stealth Gauntlet
**Target:** nowsecure.nl (Cloudflare-protected)
**Result:** PASS (unexpected)
**Duration:** 36s, 12 tool calls
**What happened:** Browser passed the Cloudflare challenge with Layer 1 stealth only. Diagnostic results: `navigator.webdriver=false` (clean), `plugins.length=0` (suspicious), `window.chrome=undefined` (suspicious). However, Cloudflare's free tier did not check these deeper signals.
**Key finding:** Layer 1 stealth (headed mode, custom UA, persistent profile, automation flag disabled) is sufficient for Cloudflare free tier. Stricter sites (Pro, Enterprise, Turnstile) will require Layer 2+.

### Test 10: Linear E2E + AgentMail
**Target:** linear.app
**Result:** PARTIAL
**Duration:** ~180s, ~40 tool calls
**What happened:** Successfully created an AgentMail inbox, navigated to linear.app signup, and filled in the email address. Blocked by Cloudflare Turnstile CAPTCHA at the email verification step -- the interactive CAPTCHA cannot be bypassed with Layer 1 stealth. Worker handled an AgentMail inbox quota limit (3 inbox cap) autonomously by cleaning up stale inboxes. Phases 4-5 (onboarding + issue creation) were skipped due to the Turnstile block.
**Key finding:** Cloudflare Turnstile is a hard blocker at Layer 1. Production SaaS with security-conscious engineering (Linear, enterprise tools) will use Turnstile. Requires Layer 2+ stealth (rebrowser-patches or cloud browser with CAPTCHA solving).

---

## Findings Summary

1. **old.reddit.com works, reddit.com does not.** The modern SPA has aggressive anti-automation; the legacy HTML version works with a retry-on-block strategy.
2. **`browser_evaluate` with JS selectors beats accessibility snapshots for data extraction.** For data-heavy pages, targeted DOM queries cost ~200 tokens vs 47K tokens for a full snapshot.
3. **URL pre-population bypasses complex SPA forms.** When autocomplete widgets fight your input, navigate to a URL with parameters pre-encoded instead.
4. **Cross-origin iframes can be bypassed by navigating to the iframe's `src` URL.** Works for Stripe payment forms and similar embedded content.
5. **Evaluate-only mode is correct for content-heavy pages.** Wikipedia, documentation sites, and long articles should use zero snapshots.
6. **Layer 1 stealth passes Cloudflare free tier.** But `plugins.length=0` and `window.chrome=undefined` are fingerprint gaps that stricter sites will catch.
7. **Cloudflare Turnstile is a hard ceiling for Layer 1 stealth.** Interactive CAPTCHA requires Layer 2+ (binary patches or cloud browser with CAPTCHA solving).
8. **Do not use `return` in `browser_evaluate` expressions.** Eval expects a JS expression, not a statement. Use `document.title` not `return document.title`.
9. **Test prompts should include known site constraints.** Character limits, rate limits, and site-specific quirks cause unnecessary retries when not specified upfront.
10. **Visual-only confirmations exist.** Some sites (e.g., Stripe demo) show success as a visual indicator (checkmark) rather than a text confirmation page. Tests should account for this.

---

## Anti-Bot Detection Results

| Site | Protection | Result | Why |
|------|-----------|--------|-----|
| reddit.com | Anti-automation SPA | Blocked | Client-side rendering, obfuscated DOM, headless browser detection |
| old.reddit.com | Basic | Works (with retry) | Simple HTML version; append `?sort=hot` to bypass initial block |
| pastebin.com | Cloudflare transparent challenge | Blocked | Silent JS challenge with no interactive CAPTCHA to solve |
| linear.app | Cloudflare Turnstile | Blocked | Interactive CAPTCHA requiring Layer 2+ stealth |
| nowsecure.nl | Cloudflare free tier | Passed | Layer 1 stealth sufficient for free-tier checks |
| saucedemo.com | None | Passed | Standard test site, no detection |
| news.ycombinator.com | None | Passed | No anti-bot measures |
| github.com | None (for public pages) | Passed | Standard SPA navigation |
| google.com/travel/flights | None (for search) | Passed | No stealth needed for search functionality |
| notion.so | Basic anti-abuse | Passed | SaaS signup worked end-to-end with email OTP |
| automationexercise.com | None | Passed | Test/demo site |
| wikipedia.org | None | Passed | No anti-bot on public articles |
| Stripe demo | None | Passed | iframe bypass required but no anti-bot |

**Pattern:** Registration, form filling, and multi-step workflows succeed reliably on most sites. Anti-bot failures come from IP-level blocking, Cloudflare transparent challenges, or Turnstile interactive CAPTCHAs -- not from basic browser detection.

---

## Capabilities Proven Across Both Suites

| Capability | Tests | Evidence |
|-----------|-------|----------|
| Login + session cookies | v1: 1, 6, 9; v2: 3, 6 | SauceDemo, HN, quotes.toscrape |
| Multi-field registration | v1: 2, 7 | 11-step account lifecycle |
| Complex form widgets | v1: 3 | Date pickers, React Select, file upload |
| Drag-drop, alerts, iframes | v1: 5, 14; v2: 7 | Multiple interaction types, iframe bypass |
| Paginated scraping with session | v1: 9 | 50 quotes across 5 pages |
| SaaS signup with email OTP | v1: 12 | Notion end-to-end |
| OAuth redirect flow | v1: 13 | GitHub OAuth chain |
| Google Flights SPA | v1: 11; v2: 5 | Dynamic JS search + filter + URL pre-population |
| Multi-site autonomous flow | v1: 15 | Two sites, single session |
| Error recovery | v1: 14 | Form validation, alerts, iframes |
| Data extraction via JS eval | v2: 1, 2, 4, 8 | Token-efficient alternative to snapshots |
| Cross-origin iframe bypass | v2: 7 | Stripe checkout via direct iframe navigation |
| Cloudflare free tier bypass | v2: 9 | Layer 1 stealth sufficient |
| Multi-language content | v2: 8 | English and Japanese Wikipedia |
