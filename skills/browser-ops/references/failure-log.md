# Browser Ops Failure Log

Known failures, anti-bot findings, and operational gotchas. Read this before planning any browser task against a site you haven't tested before.

Terminology used in this file:
- **Playwright:** A browser automation framework used by `agent-browser`.
- **SPA:** Single-page application, a site that renders most content in JavaScript after load.
- **DOM:** Document Object Model, the browser's structured page element tree.
- **a11y tree:** Accessibility tree used by `browser_snapshot`.
- **OAuth:** Redirect-based login protocol (for example, "Sign in with GitHub").

---

## The Feb 12 Disaster: Significant token budget burned in one task

### What happened

**Task:** Scrape product pricing across retailer websites. Three parallel browser workers were spawned.

**Results:**
- Worker 1 (retailer site 1 + Google Shopping): FAILED (exit 1)
- Worker 2 (retailer site 2 + retailer site 3): FAILED (exit 1)
- Worker 3 (additional online retailers): COMPLETED (exit 0)
- Task terminated before writing consolidated report -- zero usable output

**Cost:** significant token budget wasted.

### Root causes

**1. Session collision (primary cause)**

Three parallel workers shared a single agent-browser daemon. No per-worker session isolation. Worker A navigates to site 1, Worker B navigates to site 2, Worker A's page disappears. State collisions cascade into failures on every subsequent step.

**Fix:** Run browser workers SEQUENTIALLY. Per-worker session isolation (`AGENT_BROWSER_SESSION`) is architecturally possible but not yet implemented.

**2. 37-tool schema overhead**

`--browser` loads 25 browser tools + 15 base tools = 40 tool schemas. Each schema is ~500-1K tokens. That's 15-20K tokens of tool definitions resent on every Codex API turn. Three workers x multiple turns = massive token burn before any useful work happens.

**Fix:** Accept the overhead cost and factor it into task planning. Only enable `--browser` when browser interaction is genuinely required.

**3. Wrong tool for the job**

Product pricing from retailer pages is static content extraction. `WebSearch` or `WebFetch` handles this at ~1/100th the token cost. Browser agents are for interactive tasks (auth flows, form filling, session state). This was a misapplication of the browser stack.

**Fix:** Always check the decision tree in SKILL.md before reaching for `--browser`. If the data is publicly accessible without interaction, use WebSearch/WebFetch.

### Lessons codified

| Lesson | Rule |
|--------|------|
| Session collision kills parallel workers | Browser workers run SEQUENTIALLY only |
| Tool schema costs add up fast | Only use `--browser` for interactive tasks |
| Failed Codex workers bill fully | Budget-conscious tasks should run sequentially with early-exit |
| Static content doesn't need a browser | WebSearch/WebFetch first, browser as last resort |

---

## Anti-Bot Findings

### OZON (Russian e-commerce) -- BLOCKED

- 20+ bypass attempts failed
- Blocks at IP level -- non-Russian IPs are blacklisted regardless of browser fingerprint
- Playwright stealth, user-agent rotation, cookie manipulation all ineffective
- **Root cause:** IP-level geo-blocking, not browser fingerprinting
- **Required:** Residential Russian proxy. No other workaround exists.
- **Do not waste time retrying without a proxy.**

### Cloudflare Transparent Challenges -- NO BYPASS

- Pastebin (Task 8 in benchmark): Cloudflare issued a transparent challenge
- No interactive CAPTCHA exposed -- the challenge happens silently in JS
- Browser automation cannot solve transparent challenges
- **Mitigation:** Check if target site uses Cloudflare before starting. If it does, test manually first.

### Reddit -- SITE-SPECIFIC WORKAROUND

- **reddit.com** — BLOCKED. SPA with aggressive anti-bot. Client-side rendering, obfuscated DOM. Headless browser detection triggers silent block.
- **old.reddit.com** — WORKS. Simple HTML version. Initial navigation may hit "blocked by network security" page. Workaround: append `?sort=hot` to URL and retry. Simple HTML renders cleanly in a11y tree. Tested: 14 tool calls, 25.4 seconds, 5 posts + 3 comments extracted via `browser_evaluate`.
- **Strategy:** Try old.reddit.com with retry-on-block pattern before giving up on Reddit content extraction.

### Cloudflare Turnstile (Interactive CAPTCHA) -- BLOCKED at Layer 1

- **Tested on:** linear.app (Test 10, Final Boss)
- Worker navigated to signup, filled email, but Cloudflare Turnstile interactive CAPTCHA blocked verification
- Layer 1 stealth (headed, custom UA, persistent profile, automation flag disabled) is insufficient
- **Required:** Layer 3 (Kernel cloud provider with CAPTCHA solving) — see Layer 2 note below
- **Distinction from Cloudflare transparent challenge:** Turnstile is an interactive checkbox/puzzle CAPTCHA, not a silent JS challenge. Different mechanism, same outcome — blocked.
- **Pattern:** Production SaaS with security-conscious engineering (Linear, likely Notion in future, enterprise tools) will use Turnstile. Layer 1 has a ceiling here.

#### Layer 2 (rebrowser-patches) — Currently Incompatible (Feb 2026)

rebrowser-patches 1.0.19 (latest, May 2025) targets playwright-core 1.52. agent-browser 0.10.0 ships playwright-core 1.58.2 — 6 minor versions ahead. Patch hunks fail on all 3 target files (crPage.js, crServiceWorker.js, page.js). The rebrowser project has been inactive for 9 months (issue #113 open, no maintainer response).

**Options when revisiting:**
1. Manual surgical port of the 3 core patches to pw 1.58+ (concepts are simple, ~4 hunks)
2. Wait for rebrowser-patches update (stale project — low confidence)
3. Skip to Layer 3 (Kernel) — guaranteed solve, paid service

**Do not attempt `npx rebrowser-patches@latest patch` — it will fail.**

### Booking.com -- DATE PARAMETER STRIPPING

- **URL pre-population completely blocked:** All `searchresults.html` URLs with query parameters are redirected to static city pages. Date, destination, and guest params are stripped server-side.
- **First search from homepage → city page redirect:** Even manual form filling with correct calendar clicks gets redirected to a city landing page (`/city/my/sandakan.html`) that resets the date picker to blank.
- **Recovery:** Re-enter dates on the city page's search bar and search again. Second search should preserve date context and yield date-locked pricing.
- **Root cause:** Booking.com serves a "city template" for certain destination queries. This template is a static marketing page, not a search results page. It has its own search bar but ignores incoming date params.
- **Layer 1 stealth:** Sufficient -- no CAPTCHA or block. The issue is UX/anti-bot redirect behavior, not detection.
- **Working strategy:**
  1. **Search by landmark** ("Sepilok Orangutan Rehabilitation Centre"), not city name ("Sandakan"). Landmark searches return lat/long-based results (204 properties) instead of triggering the city redirect.
  2. **Get per-night pricing from individual hotel page calendars.** Search results page never shows date-locked prices -- but each hotel's availability calendar does (e.g., "14 $133").
  3. **ArrowDown + Enter for autocomplete.** Booking.com's React autocomplete ignores click events on options -- use keyboard navigation.
  4. **Watch for the "I'm flexible" tab trap.** After selecting dates, the calendar may open on the wrong tab. Explicitly click "Calendar" tab.

### Yandex Market -- WORKAROUND EXISTS

- JSON-LD structured data available in page source
- `browser_evaluate('document.querySelector("script[type=\\"application/ld+json\\"]")?.textContent')`
- No browser interaction needed -- this is a Tier 3 extraction
- Can often use WebFetch instead of a browser entirely

### Sites That Work Fine

Based on benchmark (12/15 pass, 100% excluding external blockers):

| Site | Complexity | Notes |
|------|-----------|-------|
| saucedemo.com | Login + cart | Standard auth + e-commerce |
| automationtesting.in | Registration | Multi-field forms |
| demoqa.com | Complex widgets | Date pickers, React Select |
| the-internet.herokuapp.com | Multiple | Drag-drop, alerts, iframes |
| news.ycombinator.com | Real site auth | Account creation + upvote |
| automationexercise.com | 11-step flow | Full registration lifecycle |
| quotes.toscrape.com | Pagination | Session persisted across 5 pages |
| google.com/travel/flights | Search + filter | Real Google product, complex UI |
| booking.com | Hotel search + pricing | Landmark search + hotel calendar pricing |
| notion.so | SaaS signup + OTP | End-to-end with AgentMail |
| dashboard.render.com | OAuth redirect | GitHub OAuth flow |
| github.com | SPA extraction | Star count, forks, README headings |
| saucedemo.com | Login + cart + checkout | Full e-commerce flow |
| stripe demo (checkout) | iframe payment form | Cross-origin iframe bypass |
| wikipedia.org (EN + JA) | Multi-language extraction | Evaluate-only mode, zero snapshots |
| nowsecure.nl | Cloudflare gauntlet | Passed free-tier Cloudflare with Layer 1 |

**Pattern:** Registration, form filling, and multi-step workflows succeed reliably. Anti-bot failures come from IP-level blocking (OZON) or Cloudflare transparent challenges, not from browser detection.

---

## AgentMail: Email Verification Infrastructure

For tasks requiring email verification (account signup, OTP flows).

### Setup

- AgentMail wrapper: `./scripts/mailbox.py` (self-contained in skill dir)
- CLI tool: `./scripts/agentmail.sh` (setup/create/poll/extract)
- First-time: `./scripts/agentmail.sh setup` (creates local venv)
- Active mailbox: `your-mailbox@agentmail.to`
- API key: stored in your environment variables or shell profile

### Usage pattern

```text
1. Create or reuse a mailbox via CLI
2. Use mailbox email in browser signup form
3. Poll mailbox for incoming verification email
4. Extract verification link or OTP code
5. Navigate to link or enter code in browser
```

### Validated flows

- **Notion signup (Task 12):** Full end-to-end -- signup -> AgentMail OTP poll -> extract code -> submit -> complete onboarding -> create page. Highest complexity task in benchmark.
- **PKP forum (Task 10):** Email verification itself worked perfectly. Blocked by moderator approval gate (external, not email-related).

### Gotchas

- Poll timing: emails can take 5-30 seconds to arrive. Build in wait/retry.
- Some services detect `agentmail.to` domain -- have backup domains if needed.
- OTP codes expire. Extract and submit promptly after polling.

---

## Benchmark Summary

15-task browser autonomy benchmark (Feb 11-12, 2026).

| Result | Count | Tasks |
|--------|-------|-------|
| PASS | 12 | 1, 2, 3, 5, 6, 7, 9, 11, 12, 13, 14, 15 |
| FAIL (external) | 3 | 4 (SSL outage), 8 (Cloudflare), 10 (moderator gate) |

**Effective success rate excluding external blockers: 100%.**

All three failures were external -- site outage, Cloudflare bot detection, and human moderator approval gate. None were agent capability gaps.

### Standout: Notion end-to-end (Task 12)

Navigate to signup -> enter email -> poll AgentMail for OTP -> extract and submit code -> complete onboarding (name, workspace) -> reach dashboard -> create a page. Real SaaS product with real anti-abuse measures. Validates the full stack working together on a production service.

---

## Open Issues (as of Feb 2026)

| Issue | Status | Impact |
|-------|--------|--------|
| Per-worker browser session isolation | Not implemented | Blocks parallel browser workers |
| Token efficiency benchmarks | Not done | Can't quantify snapshot mode savings precisely |
| Residential proxy for OZON | Not set up | Can't access Russian e-commerce |
| AgentMail integration into all benchmark tasks | Partial | Only Task 10 and 12 use email |
| Session persistence (stay logged in) | Not implemented | Each task starts fresh |
| Rate limiting for production use | Not implemented | Risk of triggering anti-bot on sustained use |
| Layer 2 rebrowser-patches | Blocked (pw 1.52 vs 1.58) | Cannot bypass Turnstile; skip to Layer 3 when needed |
