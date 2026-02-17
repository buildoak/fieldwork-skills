# Cloudflare-Protected Sites Playbook

**Target:** Any site using Cloudflare protection
**Tested:** Feb 2026 (nowsecure.nl, Pastebin, Linear)
**Result:** Mixed -- depends on Cloudflare tier
**Stealth:** Layer 1 through Layer 3 depending on protection level

Terminology:
- **Turnstile:** Cloudflare's interactive CAPTCHA challenge.
- **Transparent challenge:** Cloudflare's silent JavaScript challenge with no visible checkbox.
- **Layer 3 (Kernel):** Cloud browser provider mode with built-in stealth and CAPTCHA handling.

## Decision Tree

```text
Is the site behind Cloudflare?
  |
  +-- How do you know?
  |     - Page briefly shows "Checking your browser..." on first visit
  |     - `cf-ray` header in response (Cloudflare request ID header)
  |     - Cloudflare error pages (1xxx codes)
  |     - Turnstile checkbox widget visible
  |
  +-- What tier of protection?
        |
        +-- Free tier (basic JS challenge, brief delay)
        |     --> Layer 1 stealth: PASS
        |     Tested: nowsecure.nl (12 calls, 36s)
        |
        +-- Transparent challenge (silent JS challenge, no interactive element)
        |     --> Layer 1: FAIL, Layer 2: FAIL, Layer 3: REQUIRED
        |     Tested: Pastebin (FAIL)
        |     No interactive CAPTCHA exposed -- challenge happens silently in JS
        |
        +-- Turnstile (interactive checkbox/puzzle CAPTCHA)
              --> Layer 1: FAIL, Layer 2: BLOCKED (Playwright version mismatch), Layer 3: REQUIRED
              Tested: linear.app (PARTIAL)
```

## What Works

### Layer 1 vs Cloudflare Free Tier

```bash
# Ensure Layer 1 stealth is configured:
export AGENT_BROWSER_HEADED=1
export AGENT_BROWSER_USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/stealth"
export AGENT_BROWSER_ARGS="--disable-blink-features=AutomationControlled"
```

```text
browser_navigate(url="https://target-site.com")
browser_wait(target="3000")                    # give Cloudflare challenge time to resolve
browser_snapshot()                             # should show the actual page content

# If still on challenge page, wait longer:
browser_wait(target="5000")
browser_snapshot()
```

Cloudflare free tier performs a brief JS challenge that resolves automatically with Layer 1 stealth. The key is waiting long enough for the challenge to complete.

### Diagnostic check (nowsecure.nl validated)

```text
browser_navigate(url="https://nowsecure.nl")
browser_wait(target="3000")
browser_snapshot()                             # should show "You are not detected" or similar

# Check browser fingerprint signals:
browser_evaluate(script="JSON.stringify({webdriver: navigator.webdriver, plugins: navigator.plugins.length, chrome: typeof window.chrome})")
# Expected with Layer 1: {webdriver: false, plugins: 0, chrome: "undefined"}
# plugins: 0 and chrome: undefined are suspicious but Cloudflare free tier ignores them
```

### Layer 3 (Kernel) for stricter protection

```bash
export AGENT_BROWSER_PROVIDER=kernel
export KERNEL_API_KEY=your_key_here
export KERNEL_PROFILE_NAME=cf-target
# KERNEL_STEALTH defaults to true -- stealth mode + CAPTCHA solving enabled
```

With Kernel, Cloudflare challenges (including Turnstile) are handled by the cloud provider's built-in CAPTCHA solving and clean fingerprint.

## What Doesn't Work

1. **Layer 1 against transparent challenges.** Pastebin (Cloudflare transparent challenge) blocked the browser completely. No interactive CAPTCHA was shown -- the challenge happened silently in JS and failed. There is no workaround at Layer 1.

2. **Layer 1 against Turnstile.** Linear (Cloudflare Turnstile) showed an interactive checkbox CAPTCHA that Layer 1 cannot solve. The automation cannot click the checkbox with the right browser signals.

3. **Layer 2 (rebrowser-patches) as of Feb 2026.** rebrowser-patches 1.0.19 targets playwright-core 1.52, but agent-browser 0.10.0 ships Playwright 1.58.2. All three patch hunks fail. The project has been inactive for 9+ months. **Do not attempt `npx rebrowser-patches@latest patch`.**

4. **Retrying against blocked sites without escalating stealth.** If Cloudflare blocks you, retrying with the same stealth level will produce the same result. Escalate first, then retry.

## Key Patterns

- **Wait after navigation.** Cloudflare challenges take 2-5 seconds to resolve. Always `browser_wait(target="3000")` after navigating to a Cloudflare-protected site before taking a snapshot.
- **Detect challenge type from snapshot.** After waiting, snapshot the page. If you see:
  - Normal page content: challenge passed, proceed normally
  - "Checking your browser..." or spinner: wait longer (up to 10 seconds)
  - Turnstile checkbox: STOP, Layer 3 required
  - Blank page or error: transparent challenge failed, Layer 3 required
- **Test manually first.** Open the target site in a regular browser. If it loads with a brief delay, it is free tier (Layer 1 sufficient). If you see a checkbox CAPTCHA, it is Turnstile (Layer 3 required).
- **Persistent profile helps.** Cloudflare checks cookie freshness. A persistent profile with accumulated Cloudflare cookies (`cf_clearance`) from previous visits is more likely to pass.

## Fingerprint Gaps at Layer 1

Diagnostic results from nowsecure.nl test:

| Signal | Layer 1 Value | Expected (real browser) | Detection Risk |
|--------|--------------|------------------------|----------------|
| `navigator.webdriver` | `false` | `false` | Clean |
| `navigator.plugins.length` | `0` | `3-5` | Suspicious |
| `window.chrome` | `undefined` | `object` | Suspicious |
| WebGL renderer | Software | Hardware GPU | Suspicious (headed mode fixes this) |
| Canvas fingerprint | Inconsistent | Consistent | Detected by Enterprise |

Cloudflare free tier does not check the deeper signals (plugins, chrome object). Pro and Enterprise tiers do.

## Anti-Bot Notes

- **Cloudflare free tier:** Basic JS challenge. Layer 1 passes. Brief delay (2-5 seconds) then page loads.
- **Cloudflare Pro:** JS challenge + deeper fingerprint checks. Needs Layer 2 (when compatible) or Layer 3.
- **Cloudflare Enterprise:** Full fingerprint analysis + behavioral analysis. Needs Layer 3 (Kernel).
- **Cloudflare Turnstile:** Interactive CAPTCHA. Separate from tier-based protection. Can appear on any tier. Needs Layer 3 with CAPTCHA solving.
- **Transparent challenges:** Silent JS challenge with no user interaction. If it fails, there is nothing to click or solve. Needs Layer 3.

## Sample Worker Prompt

```text
Navigate to [TARGET_URL] which is protected by Cloudflare.

STEALTH CHECK: Before starting, verify your stealth configuration:
- If Layer 1 only (env vars): the site must be Cloudflare free tier. If you see a Turnstile CAPTCHA checkbox, STOP and report "Requires Layer 3 stealth."
- If Layer 3 (Kernel): proceed with confidence.

Steps:
1. Navigate to the target URL
2. Wait 3-5 seconds for Cloudflare challenge to resolve
3. Snapshot to check page state:
   - If normal content: proceed with your task
   - If "Checking your browser...": wait 5 more seconds, snapshot again
   - If Turnstile checkbox: STOP, screenshot, report "Blocked by Turnstile"
   - If blank/error page: STOP, screenshot, report "Blocked by transparent challenge"
4. [Continue with site-specific task]

Report: Cloudflare challenge result, then task result.
```
