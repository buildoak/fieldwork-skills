# Browser Stealth Configuration

Anti-detection configuration for agent-browser. Layered approach -- apply from top down, escalate only when needed.

---

## Quick Setup (5 Minutes, $0)

Set these environment variables before launching the browser daemon:

```bash
# In ~/.zshrc or shell profile:
export AGENT_BROWSER_HEADED=1
export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/stealth"
export AGENT_BROWSER_ARGS="--disable-blink-features=AutomationControlled"

# Create persistent profile directory:
mkdir -p ~/.agent-browser/profiles/stealth
```

| Setting | What It Fixes | Effectiveness |
|---------|--------------|---------------|
| `HEADED=1` | Headless fingerprint (WebGL, canvas, plugins, UA) | High |
| Custom UA | HeadlessChrome marker in user agent | Medium |
| Persistent profile | Cookie freshness, empty localStorage, missing CF cookies | Medium-High |
| `--disable-blink-features` | `navigator.webdriver = true` | Medium |

**Beats:** Cloudflare free tier, basic bot detection on most sites.
**Fails against:** Cloudflare Enterprise, DataDome, Akamai.

---

## Layer 2: CDP Leak Fix (30 Minutes, $0) — CURRENTLY BLOCKED

> **Feb 2026:** rebrowser-patches 1.0.19 (latest) targets playwright-core 1.52. agent-browser 0.10.0 requires pw ^1.57 (ships 1.58.2). Patch fails on all target files. Project inactive 9+ months. See `failure-log.md` for options. Skip to Layer 3 if you need Turnstile bypass now.

The #1 detection vector in 2025-2026 is Playwright's `Runtime.Enable` CDP command. When a compatible version of rebrowser-patches exists, apply:

```bash
cd /opt/homebrew/lib/node_modules/agent-browser
npx rebrowser-patches@latest patch

# Verify patches applied:
REBROWSER_PATCHES_DEBUG=1 agent-browser open https://bot.sannysoft.com
```

Optional env vars for fine-tuning:
```bash
export REBROWSER_PATCHES_RUNTIME_FIX_MODE=addBinding
export REBROWSER_PATCHES_SOURCE_URL=app.js
export REBROWSER_PATCHES_UTILITY_WORLD_NAME=util
```

**Note:** Must re-patch after every `npm update -g agent-browser`.

**Combined with Layer 1:** Covers ~65% of detection signals. Passes Cloudflare Pro on most sites.

---

## Layer 3: Cloud Browser Provider (5 Minutes, $0-25/mo)

When local stealth isn't enough, route through a cloud browser with built-in stealth:

### Kernel (Recommended)
```bash
export AGENT_BROWSER_PROVIDER=kernel
export KERNEL_API_KEY=your_key_here
export KERNEL_PROFILE_NAME=gsd-default
# KERNEL_STEALTH defaults to true -- stealth mode enabled automatically
```

Includes: stealth mode, residential proxies, CAPTCHA solving, persistent profiles. 300ms browser spin-up.

### Browserbase
```bash
export AGENT_BROWSER_PROVIDER=browserbase
export BROWSERBASE_API_KEY=your_key
export BROWSERBASE_PROJECT_ID=your_project
```

### Browser Use
```bash
export AGENT_BROWSER_PROVIDER=browseruse
```

**Beats:** Cloudflare all tiers, DataDome basic, most anti-bot systems.

---

## Layer 4: Residential Proxy ($30-120/mo)

For IP-based blocking (OZON, some Cloudflare Enterprise):

```bash
# Bright Data example with country targeting:
export AGENT_BROWSER_PROXY="http://user-country-ru:pass@brd.superproxy.io:33335"

# Generic proxy:
export AGENT_BROWSER_PROXY="http://username:password@proxy.provider.com:7777"
```

**Only needed if:** Using local browser (not Kernel) and IP-based blocking is an issue.

---

## Decision Tree: Which Layer Do I Need?

```
Target site has no bot protection?
  YES --> Layer 1 env vars only (or skip stealth entirely)

Target uses basic Cloudflare (free tier)?
  YES --> Layer 1 (env vars)

Target uses Cloudflare Pro?
  YES --> Layer 1 + Layer 2 (rebrowser-patches)

Target uses Cloudflare Enterprise or DataDome?
  YES --> Layer 3 (Kernel cloud provider)

Target blocks by IP (datacenter/VPN IPs)?
  YES --> Layer 4 (residential proxy) OR Layer 3 (Kernel includes proxies)

Target is OZON or similar Russian e-commerce?
  YES --> Layer 4 with Russian residential proxy. No other workaround.
```

---

## Detection Signals and Coverage

| Signal | Layer 1 | +Layer 2 | +Layer 3 (Kernel) |
|--------|---------|----------|-------------------|
| navigator.webdriver | YES | YES | YES |
| HeadlessChrome UA | YES | YES | YES |
| CDP Runtime.Enable | NO | YES | YES |
| Plugin/mime count | NO | NO | YES |
| WebGL fingerprint | Partial | Partial | YES |
| Canvas fingerprint | NO | NO | YES |
| IP reputation | NO | NO | YES |
| Cookie freshness | YES | YES | YES |
| Cloudflare Turnstile | NO | NO | Partial |

---

## Known Blocked Sites

See `failure-log.md` for full details.

| Site | Protection | Status | Required Layer |
|------|-----------|--------|----------------|
| OZON | IP-level geo-block | BLOCKED | Layer 4 (Russian residential proxy) |
| Pastebin | Cloudflare transparent challenge | BLOCKED | Layer 3 + CAPTCHA solver |
| Linear | Cloudflare Turnstile | BLOCKED | Layer 3 (Layer 2 incompatible as of Feb 2026) |
| Most SaaS signups | Basic or none | WORKS | Layer 1 sufficient |
| Google Flights | None for search | WORKS | No stealth needed |
| Hacker News | None | WORKS | No stealth needed |

---

## All Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `AGENT_BROWSER_HEADED` | Run headed (visible browser) | off (headless) |
| `AGENT_BROWSER_USER_AGENT` | Custom user agent string | Chromium default |
| `AGENT_BROWSER_ARGS` | Chromium launch args (comma-separated) | none |
| `AGENT_BROWSER_PROFILE` | Persistent browser profile path | none (ephemeral) |
| `AGENT_BROWSER_STATE` | Storage state JSON file | none |
| `AGENT_BROWSER_SESSION` | Session name for isolation | `mcp` |
| `AGENT_BROWSER_PROXY` | Proxy server URL | none |
| `AGENT_BROWSER_PROXY_BYPASS` | Proxy bypass list | none |
| `AGENT_BROWSER_PROVIDER` | Cloud provider (kernel, browserbase, browseruse) | none (local) |
| `KERNEL_API_KEY` | Kernel API key | none |
| `KERNEL_PROFILE_NAME` | Kernel persistent profile name | none |
| `KERNEL_STEALTH` | Kernel stealth mode | true |
| `BROWSERBASE_API_KEY` | Browserbase API key | none |
| `BROWSERBASE_PROJECT_ID` | Browserbase project ID | none |
| `REBROWSER_PATCHES_RUNTIME_FIX_MODE` | CDP fix mode | addBinding |
| `REBROWSER_PATCHES_SOURCE_URL` | Source URL rename | (default) |
| `REBROWSER_PATCHES_UTILITY_WORLD_NAME` | Utility world rename | (default) |
