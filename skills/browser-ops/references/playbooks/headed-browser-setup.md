# Headed Browser Playbook

## Why Use a Headed Browser?

Running browser automation with a visible browser window and a real user profile gives you significant advantages over headless mode.

**Stealth.** A headed browser uses the real GPU for rendering, reports accurate system capabilities, and behaves identically to a human-operated browser. Headless mode, by contrast, uses a software renderer and carries multiple fingerprint differences that anti-bot systems detect.

**Trust signals.** A persistent browser profile accumulates cookies, localStorage data, and browsing history over time. Anti-bot systems consider these signals when deciding whether to trust a session. A fresh, empty browser profile looks suspicious -- a profile with weeks of accumulated data looks human.

**Debugging.** You can watch automation happen in real time. When something goes wrong -- a form not filling, a button not clicking, an unexpected popup -- you see it immediately instead of debugging from screenshots and logs.

**Lower detection rate.** In our testing, headed mode with a persistent profile (Tier 1 stealth) passes Cloudflare free tier and most basic bot detection. Headless mode fails these same checks.

---

## When to Use Headed vs Headless

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Sites with anti-bot detection | Headed + profile | Trust signals matter, real GPU fingerprint helps |
| Simple web scraping (no login) | Headless | Speed, no UI needed, lower overhead |
| Auth flows with potential CAPTCHA | Headed | Can manually solve if automation gets stuck |
| Background server tasks | Headless | No display available (unless using virtual display) |
| Sites with Cloudflare | Headed + Tier 1 | Combination passes free-tier checks |
| SaaS signup flows | Headed + profile | Accumulated trust helps with anti-abuse systems |
| Development and debugging | Headed | Visual feedback speeds up iteration |
| High-volume parallel scraping | Headless | Headed mode locks to one instance per display |

---

## Setting Up a Browser Profile

### Step 1: Create a Fresh Chrome Profile

The simplest approach is to let agent-browser create and manage the profile automatically:

```bash
# Set the profile directory
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/main"

# Create the directory
mkdir -p ~/.agent-browser/profiles/main
```

The first time agent-browser launches with this profile path, it creates a clean Chrome profile in that directory. Every subsequent launch reuses the same profile -- cookies, history, localStorage, and all other browser state persist between sessions.

**Alternative: Use an existing Chrome profile.** If you already have a Chrome installation with profiles you use for browsing, you can point agent-browser at one:

```bash
# macOS Chrome profile location
export AGENT_BROWSER_PROFILE="$HOME/Library/Application Support/Google/Chrome/Profile 1"
```

Be careful with this approach -- automation activity in your personal browsing profile could affect your accounts.

### Step 2: Build Trust Signals

Before using the profile for automation against anti-bot protected sites, warm it up with normal browsing activity:

1. **Browse manually for 2-3 days before automating.** Launch the browser with your profile, visit sites you normally use. This creates a realistic browsing history.

2. **Visit common sites:** Google, YouTube, news sites, social media. These are the sites anti-bot systems expect to see in a real user's cookie jar.

3. **Accept cookies and allow notifications on a few sites.** Real users do this. An empty permissions/cookie consent state is a signal of a fresh profile.

4. **Log into a few services.** Having active sessions (Gmail, social media) in the profile makes it look like a real daily-driver browser. Use accounts you are comfortable associating with automation.

5. **Let time pass.** Profile age matters. A profile created today and immediately used for automation is suspicious. A profile that has been active for a week is far less so.

### Step 3: Configure agent-browser for Headed Mode

Set these environment variables in your shell profile (`~/.zshrc`, `~/.bashrc`, or equivalent):

```bash
# Run in headed mode (visible browser window)
export AGENT_BROWSER_HEADED=1

# Point to your persistent profile
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/main"

# Set a realistic User-Agent string
export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"

# Disable the automation detection flag
export AGENT_BROWSER_ARGS="--disable-blink-features=AutomationControlled"
```

Then start agent-browser:

```bash
agent-browser start
```

A visible Chrome window will appear. All browser automation commands will execute in this window.

### Step 4: Keep the Profile Alive

The profile is your trust capital. Maintain it:

- **Periodically browse manually** (once a week is enough) to keep cookies fresh and add new history entries.
- **Do not clear cookies or history.** That is your accumulated trust. If you need a clean environment for testing, create a separate profile instead.
- **If you need to automate a new site,** visit it manually first. A single manual visit creates cookies and referrer data that make the automated visit look like a return visit.
- **Back up the profile directory** occasionally. If something corrupts the profile, you do not want to rebuild trust from scratch.

---

## Combining Headed Mode with Stealth Tiers

Headed mode is not an alternative to the stealth tiers -- it is the foundation that all other tiers build on.

### Headed + Tier 1 (Environment Variables)

This is the recommended baseline for all production automation:

```bash
export AGENT_BROWSER_HEADED=1
export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/main"
export AGENT_BROWSER_ARGS="--disable-blink-features=AutomationControlled"
```

**What you get:** Real GPU fingerprint, persistent cookies, clean User-Agent, `navigator.webdriver=false`. Passes Cloudflare free tier and most basic bot detection.

### Headed + Tier 2 (Binary Patches)

When Tier 1 is not enough and rebrowser-patches is compatible with your Playwright version:

```bash
# Apply patches (one-time, re-apply after updates)
cd /path/to/agent-browser
npx rebrowser-patches@latest patch
```

**What you add:** CDP artifacts removed at the binary level. Combined with headed mode, covers approximately 65% of detection signals. Passes most Cloudflare Pro sites.

### Headed + Tier 3 (Cloud Browser)

For the hardest targets, you can use a cloud browser in headed mode for debugging while routing actual automation through the cloud service:

```bash
export AGENT_BROWSER_PROVIDER=kernel
export KERNEL_API_KEY=your_key
```

Note: With cloud browsers, headed/headless is managed by the service. The local browser window becomes a debugging view, not the automation target.

### Headed + Tier 4 (Residential Proxy)

Combine headed mode with a residential proxy when IP reputation is the blocker:

```bash
export AGENT_BROWSER_HEADED=1
export AGENT_BROWSER_PROXY="http://username:password@proxy.provider.com:7777"
# ... plus all other Tier 1 env vars
```

This gives you a real browser fingerprint (headed) with a clean IP address (proxy) -- effective against sites that check both browser signals and IP reputation.

---

## Limitations of Headed Mode

- **Requires a display.** On a Mac or desktop Linux, you have a physical monitor. On a headless server, you need a virtual display (Xvfb on Linux, or a virtual display framework). macOS servers typically need an HDMI dummy plug for GPU rendering.

- **Slower than headless.** Rendering visible UI (compositing, painting, layout) adds overhead. For simple tasks the difference is negligible. For high-throughput scraping, headless is faster.

- **Profile is locked to one browser instance at a time.** Chrome profiles cannot be shared between concurrent browser instances. If you need parallel automation, each instance needs its own profile directory.

- **Not suitable for parallel execution.** Browser-ops enforces sequential worker execution (one worker at a time) regardless of mode. With headed mode, you also have the visual constraint of one browser window being manipulated at a time.

- **Browser window may be distracting.** If you are working on the same machine, a browser window opening, navigating, and clicking can be disruptive. Consider running automation on a dedicated machine or virtual desktop.

---

## Tips for Social Media and Professional Networks

Social media platforms and professional networks have the most sophisticated anti-bot detection because automated activity directly impacts their business model (spam, fake accounts, data scraping). If you need to automate interactions with these sites:

**Profile warmth is critical.** Use the browser profile for genuine manual browsing on the platform for at least a week before any automation. The platform tracks session behavior patterns over time.

**Respect rate limits.** Do not automate faster than a human could operate. Space actions 3-5 seconds apart minimum. Vary the timing randomly. Anti-bot systems detect unnaturally consistent timing between actions.

**Warm up each session.** Before performing the target action, spend 1-2 minutes browsing normally: scroll the feed, view a few profiles, read some content. This establishes a normal session pattern before the automated action.

**Do not automate connection requests or messages at scale.** Bulk outreach is the #1 trigger for account restrictions. If you must send messages, keep volume low (5-10 per day) and personalize each one.

**Use an established profile.** A profile with months of history, many connections, and regular activity is far less likely to be flagged than a new or dormant account.

**Accept that some platforms will detect you eventually.** If you automate at any meaningful scale, sophisticated platforms will eventually flag your account. Have a plan for what happens when detection occurs.

---

## Tips for Other High-Detection Sites

### Cloudflare-Protected Sites

- Layer 1 stealth (headed + env vars) passes Cloudflare free tier consistently.
- Cloudflare Pro requires Layer 2 (binary patches) or Layer 3 (cloud browser).
- Cloudflare Turnstile (interactive CAPTCHA) is a hard blocker at Layers 1-2. Requires Layer 3 with CAPTCHA-solving capability.
- Test the site manually first to identify what level of Cloudflare protection is active. A simple way: if you see a checkbox challenge, it is Turnstile. If the page just loads slowly and then works, it is a transparent challenge.

### E-Commerce Sites

- Many e-commerce platforms use geo-blocking at the IP level. If you are accessing a site meant for a specific country, you may need a residential proxy in that country (Tier 4).
- JSON-LD structured data (`<script type="application/ld+json">`) is available on many e-commerce sites and can be extracted via `browser_evaluate` without triggering interaction-based detection.
- Product pages are generally safer to automate than checkout flows, which often have additional anti-fraud checks.

### General Advice

- **Start with the lowest tier that works.** Over-engineering stealth wastes time and money. Many sites have weaker detection than you expect.
- **Test manually first.** Open the target site in a regular browser. If it loads without any challenge, Tier 0 or 1 is probably sufficient.
- **Monitor for degradation.** Sites update their anti-bot regularly. A configuration that worked last month may not work today. If automation starts failing, check whether the site upgraded its protection.
- **Check the test results and failure log.** The `test-results.md` and `failure-log.md` references contain findings from 25+ tested sites. If your target site (or a similar one) has been tested, start with the documented working configuration.
