# Anti-Detection Hardening Guide

## The Problem

Modern websites deploy multiple layers of detection to identify automated browsers and block them. When you launch a Playwright-based browser, it carries dozens of signals that distinguish it from a human-operated Chrome session: a special flag in the JavaScript environment, missing browser plugins, synthetic rendering fingerprints, and protocol-level artifacts from the remote control mechanism itself.

Some sites barely check -- a news site or demo app will let any browser through. Others run sophisticated fingerprinting that inspects your GPU renderer string, counts installed plugins, analyzes mouse movement patterns, and checks whether the Chrome DevTools Protocol (the remote control channel) left traces in memory.

The goal of anti-detection hardening is to make your automated browser look indistinguishable from a regular human-operated browser, one layer at a time. You should apply the minimum stealth needed for your target site -- over-engineering stealth wastes time and money.

---

## Detection Layers (What Sites Check)

| Signal | What It Is | Vanilla Playwright | With Layer 1 | With Layer 2 | With Layer 3 |
|--------|-----------|-------------------|--------------|--------------|--------------|
| `navigator.webdriver` | A JavaScript boolean flag that browsers set to `true` when controlled by automation tools. Most basic bot check. | Exposed (`true`) | Hidden (`false`) | Hidden | Hidden |
| HeadlessChrome in User-Agent | The browser's self-identification string. Headless mode includes "HeadlessChrome" which is an obvious tell. | Present | Replaced with real Chrome UA | Replaced | Replaced |
| CDP detection (`Runtime.Enable`) | Chrome DevTools Protocol commands leave artifacts in the browser's runtime. Anti-bot scripts probe for these traces. This is the #1 detection vector in 2025-2026. | Detectable | Still detectable | Patched at binary level | Not present (cloud browser) |
| Plugin/MIME count | A real Chrome browser reports installed plugins (PDF viewer, etc). Automation browsers report zero plugins. | 0 plugins (suspicious) | 0 plugins (still suspicious) | 0 plugins | Matches real browser |
| Canvas fingerprint | Websites draw invisible shapes and read back the pixel data. Each GPU/driver combination produces a unique "fingerprint." Automation browsers produce consistent/synthetic fingerprints. | Consistent/synthetic | Consistent/synthetic | Consistent/synthetic | Randomized to look human |
| WebGL renderer | The GPU identification string reported by the browser. Headless mode reports a generic software renderer instead of a real GPU name. | Generic headless renderer | Partial improvement (headed mode uses real GPU) | Same as Layer 1 | Matches real hardware |
| IP reputation | Bot detection services maintain databases of known datacenter and VPN IP addresses. If your IP is flagged, no amount of browser stealth helps. | Your IP (datacenter/VPN = flagged) | Same IP | Same IP | Cloud service provides clean IPs |
| Cookie freshness | A browser with zero cookies, empty localStorage, and no browsing history looks freshly created -- which is suspicious. Real browsers accumulate data over time. | Empty (fresh) | Persistent profile retains cookies | Same as Layer 1 | Pre-warmed profiles available |
| Cloudflare Turnstile | An interactive CAPTCHA widget that requires the user to click a checkbox or solve a visual puzzle. Distinct from Cloudflare's silent "transparent challenge." | Blocked | Blocked | Blocked (patches incompatible as of Feb 2026) | Partially solvable (with CAPTCHA solver) |

---

## Stealth Escalation Tiers

### Tier 0: Vanilla Playwright (No Hardening)

What you get out of the box. Zero configuration.

**Works for:**
- Demo and test sites (saucedemo.com, demoqa.com, the-internet.herokuapp.com)
- Sites with no bot detection at all
- Internal tools and admin panels

**Fails against:**
- Any site checking `navigator.webdriver`
- Any site with Cloudflare (even free tier)
- Most production websites with login flows

**When to use:** Quick testing, development environments, sites you control.

### Tier 1: Environment Variable Hardening

```bash
# Run in headed mode (visible browser window) -- eliminates headless fingerprint
export AGENT_BROWSER_HEADED=1

# Replace the default User-Agent string to remove HeadlessChrome marker
export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"

# Use a persistent browser profile (retains cookies, localStorage, history between sessions)
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/stealth"

# Disable the Blink automation flag that sets navigator.webdriver=true
export AGENT_BROWSER_ARGS="--disable-blink-features=AutomationControlled"

# Create the profile directory
mkdir -p ~/.agent-browser/profiles/stealth
```

**What each setting does:**

| Setting | What It Fixes | How It Works |
|---------|--------------|--------------|
| `HEADED=1` | Headless fingerprint (WebGL, canvas, plugins, UA) | Runs a visible browser window that uses the real GPU renderer and reports accurate system capabilities |
| Custom UA | HeadlessChrome in user agent string | Replaces the automation-revealing UA with a standard Chrome identifier |
| Persistent profile | Empty cookies, missing browsing history | Reuses the same browser profile between sessions, accumulating cookies and data like a real user |
| `--disable-blink-features` | `navigator.webdriver = true` | Tells Chromium not to set the automation detection flag |

**Works for:**
- Cloudflare free tier (confirmed: nowsecure.nl passes)
- Basic bot detection on most production sites
- Hacker News, GitHub (public pages), Google Flights, Wikipedia
- Most SaaS signup flows without Turnstile

**Still fails against:**
- Sites checking CDP (Chrome DevTools Protocol) artifacts
- Cloudflare Pro/Enterprise
- DataDome, Akamai, PerimeterX
- Cloudflare Turnstile (interactive CAPTCHA)

**Cost:** Free. Takes 5 minutes to set up.

### Tier 2: Binary-Level Patching (rebrowser-patches)

```bash
# Navigate to your agent-browser installation
cd /path/to/agent-browser

# Apply patches to Playwright's Chromium binary
npx rebrowser-patches@latest patch

# Verify patches applied (opens a browser and checks detection signals)
REBROWSER_PATCHES_DEBUG=1 agent-browser open https://bot.sannysoft.com
```

**What this does:** Modifies Playwright's bundled Chromium binary to remove automation artifacts at the source code level. Specifically targets the `Runtime.Enable` CDP command -- the #1 detection vector -- so anti-bot scripts cannot find traces of remote control in the browser's runtime.

**Optional fine-tuning:**
```bash
export REBROWSER_PATCHES_RUNTIME_FIX_MODE=addBinding
export REBROWSER_PATCHES_SOURCE_URL=app.js
export REBROWSER_PATCHES_UTILITY_WORLD_NAME=util
```

**Important notes:**
- Must re-patch after every agent-browser update
- As of February 2026, rebrowser-patches targets Playwright 1.52 while agent-browser ships Playwright 1.58. The patches do not apply cleanly. Check the [rebrowser-patches repo](https://github.com/nicokosi/rebrowser-patches) for compatibility updates before attempting.
- If patches fail, skip directly to Tier 3.

**Works for (when compatible):**
- Most Cloudflare Pro sites
- DataDome basic
- PerimeterX basic
- Combined with Tier 1: covers approximately 65% of detection signals

**Still fails against:**
- Canvas/WebGL fingerprint checks (not patched)
- Plugin count checks (still reports 0)
- IP reputation checks
- Cloudflare Turnstile (interactive CAPTCHA)

**Cost:** Free. Takes 30 minutes to set up.

### Tier 3: Cloud Browser Services

When local stealth is not enough, route your automation through a cloud browser service. These services run pre-configured browsers with built-in stealth, residential IP addresses, and sometimes CAPTCHA-solving capabilities.

**How they work:** Instead of launching a local Chromium, agent-browser connects to a remote browser instance hosted by the cloud service. The remote browser has human-like fingerprints, clean IP addresses, and accumulated browsing history -- making it much harder for anti-bot systems to flag.

**Options:**

**Kernel (recommended)**
```bash
export AGENT_BROWSER_PROVIDER=kernel
export KERNEL_API_KEY=your_key_here
```
Includes: stealth mode, residential proxies, CAPTCHA solving, persistent profiles. Fast browser spin-up (~300ms).

**Browserbase**
```bash
export AGENT_BROWSER_PROVIDER=browserbase
export BROWSERBASE_API_KEY=your_key
export BROWSERBASE_PROJECT_ID=your_project
```

**When to use:** Target site uses Cloudflare Enterprise, DataDome, or other commercial anti-bot. You need reliable access to a specific site for ongoing automation.

**Works for:**
- Cloudflare all tiers (including Enterprise)
- DataDome basic
- Most commercial anti-bot systems
- Cloudflare Turnstile (partially -- depends on provider's CAPTCHA solver)

**Still fails against:**
- The most aggressive protections (some Akamai Enterprise)
- Sites with custom behavioral analysis

**Cost:** $0-25/month depending on usage.

### Tier 4: Residential Proxy + Full Stealth Stack

The final escalation. For sites that block by IP address regardless of browser fingerprint.

```bash
# Example with country-targeted residential proxy
export AGENT_BROWSER_PROXY="http://username-country-us:password@proxy.provider.com:7777"
```

**When to use:** The target site blocks datacenter and VPN IP addresses at the network level. No amount of browser stealth helps because the block happens before your browser even renders the page. This is common with e-commerce sites that enforce geo-restrictions.

**How it works:** Routes your browser traffic through a residential IP address -- an IP that belongs to a real ISP customer, not a datacenter. Anti-bot services see traffic from what looks like a normal home internet connection.

**Works for:**
- IP-level geo-blocking
- Sites that blacklist datacenter IPs
- Combined with Tiers 1-3 for maximum coverage

**Cost:** $30-120/month depending on provider and traffic volume.

---

## Quick Decision Tree

```
Does the site have bot protection?
  |
  +-- No protection (demo sites, internal tools)
  |     --> Tier 0 (vanilla Playwright, no config needed)
  |
  +-- Basic Cloudflare (free tier)?
  |     --> Tier 1 (environment variables)
  |
  +-- Cloudflare Pro or basic commercial anti-bot?
  |     --> Tier 1 + Tier 2 (rebrowser-patches, if compatible)
  |
  +-- Cloudflare Enterprise, DataDome, or advanced anti-bot?
  |     --> Tier 3 (cloud browser service)
  |
  +-- Blocks by IP address (datacenter/VPN IPs rejected)?
  |     --> Tier 4 (residential proxy)
  |         OR Tier 3 (cloud services include residential IPs)
  |
  +-- Interactive CAPTCHA (Cloudflare Turnstile)?
        --> Tier 3 (cloud browser with CAPTCHA solving)
```

**General rule:** Start at the lowest tier that works. Over-engineering stealth wastes setup time and money. Test manually first if you are unsure what protection a site uses.

---

## Site-Specific Notes

Based on testing across 25 tasks in two benchmark suites.

| Site / Category | Protection Level | Minimum Tier | Notes |
|----------------|-----------------|--------------|-------|
| Demo/test sites (saucedemo, demoqa) | None | Tier 0 | No detection at all |
| Hacker News | None | Tier 0 | No anti-bot measures |
| Wikipedia | None | Tier 0 | No detection on public articles |
| Google Flights | None (for search) | Tier 0 | No stealth needed for search |
| GitHub (public pages) | None | Tier 0 | Standard SPA, no bot checks |
| Notion (signup) | Basic anti-abuse | Tier 1 | Email OTP is the real gate, not bot detection |
| Cloudflare free tier sites | Cloudflare free | Tier 1 | Confirmed passing on nowsecure.nl |
| old.reddit.com | Basic | Tier 1 + retry | Append `?sort=hot` on initial block |
| reddit.com (modern) | Aggressive anti-automation | Not feasible | SPA with obfuscated DOM; use old.reddit.com or API |
| Pastebin | Cloudflare transparent challenge | Tier 3 | Silent JS challenge, no interactive element to solve |
| Linear | Cloudflare Turnstile | Tier 3 | Interactive CAPTCHA at signup |
| Cloudflare Pro sites | CDP detection | Tier 2 (when compatible) | Binary patches needed for CDP artifacts |
| E-commerce with geo-blocking | IP-level blocking | Tier 4 | Need residential proxy matching target country |

---

## Combining Stealth Tiers

The tiers are cumulative, not alternatives. Each higher tier adds to the previous ones:

```
Tier 1 (env vars)
  + Tier 2 (binary patches)    = Covers ~65% of detection signals
    + Tier 3 (cloud browser)   = Covers ~90% of detection signals
      + Tier 4 (residential IP) = Maximum coverage
```

You can also mix: Tier 1 + Tier 4 (local browser with residential proxy) is cheaper than Tier 3 and works when the only problem is IP reputation.

---

## Detection Signal Coverage Matrix

| Signal | Tier 0 | Tier 1 | + Tier 2 | + Tier 3 |
|--------|--------|--------|----------|----------|
| `navigator.webdriver` | Exposed | Hidden | Hidden | Hidden |
| HeadlessChrome UA | Present | Replaced | Replaced | Replaced |
| CDP `Runtime.Enable` | Detectable | Detectable | Patched | Clean |
| Plugin/MIME count | 0 (suspicious) | 0 (suspicious) | 0 (suspicious) | Matches real browser |
| WebGL fingerprint | Generic headless | Real GPU (headed) | Real GPU (headed) | Matches real hardware |
| Canvas fingerprint | Synthetic | Synthetic | Synthetic | Randomized |
| IP reputation | Your IP | Your IP | Your IP | Clean residential IP |
| Cookie freshness | Empty | Persistent profile | Persistent profile | Pre-warmed profile |
| Cloudflare Turnstile | Blocked | Blocked | Blocked | Partially solvable |
