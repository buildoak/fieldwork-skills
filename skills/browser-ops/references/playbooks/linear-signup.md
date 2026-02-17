# Linear Signup Playbook

**Target:** https://linear.app
**Tested:** Feb 2026
**Result:** PARTIAL (Phases 1-2 pass, Phase 3 blocked by Cloudflare Turnstile)
**Stealth:** Layer 3 required (Kernel cloud provider with CAPTCHA solving)

## What Works

### Phase 1: AgentMail inbox creation

```bash
# Create or reuse an AgentMail inbox
./scripts/agentmail.sh create linear-signup-01

# If inbox limit reached (3 inbox cap), clean up stale inboxes first
./scripts/agentmail.sh list
./scripts/agentmail.sh delete <stale_inbox_id>
./scripts/agentmail.sh create linear-signup-01
```

Worker handled the 3-inbox quota limit autonomously during testing by detecting the error and cleaning up stale inboxes.

### Phase 2: Signup form fill

```
browser_navigate(url="https://linear.app/signup")
browser_snapshot()

# Fill email field with AgentMail address
browser_fill(ref="@email_field", text="linear-signup-01@agentmail.to")
browser_click(ref="@continue_button")           # "Continue with email" or similar
browser_wait(target="2000")
browser_snapshot()                               # check for CAPTCHA or verification step
```

This phase completes successfully with Layer 1 stealth.

### Phase 3: Email verification (BLOCKED)

```
# This is where the flow breaks:
# Cloudflare Turnstile interactive CAPTCHA appears at the email verification step.
# The CAPTCHA cannot be bypassed with Layer 1 stealth.
# browser_snapshot() shows the Turnstile challenge widget.
```

### Phase 4: Onboarding (not reached)

Would follow standard multi-step form pattern (name, workspace name, team size, etc.) similar to Notion onboarding.

### Phase 5: Issue creation (not reached)

Would use standard browser interaction to create an issue in the workspace.

## What Doesn't Work

1. **Layer 1 stealth against Cloudflare Turnstile.** Headed mode, custom UA, persistent profile, and automation flag disabled are all insufficient. The Turnstile interactive CAPTCHA (checkbox/puzzle) is a hard blocker.

2. **Layer 2 (rebrowser-patches).** As of Feb 2026, rebrowser-patches 1.0.19 targets playwright-core 1.52. agent-browser 0.10.0 ships playwright-core 1.58.2. The patch fails on all 3 target files (crPage.js, crServiceWorker.js, page.js). The rebrowser project has been inactive for 9+ months. **Do not attempt `npx rebrowser-patches@latest patch` -- it will fail.**

3. **Any browser-side bypass of Turnstile.** Turnstile is fundamentally different from Cloudflare's transparent challenge. It is an interactive CAPTCHA that requires either a real human click with matching browser signals or a CAPTCHA-solving service.

## Key Patterns

- **AgentMail inbox quota management.** Linear test discovered the 3-inbox cap. Worker should check inbox count before creating and clean up stale inboxes if needed.
- **Turnstile detection.** When you snapshot a page and see a Cloudflare Turnstile widget (checkbox with "Verify you are human" text), stop and report the block. Do not waste calls retrying.
- **Phase-gated execution.** Structure the task so each phase can report independently. Phases 1-2 succeed even when Phase 3 blocks. This gives partial credit and useful data.

## Anti-Bot Notes

- **Cloudflare Turnstile interactive CAPTCHA.** This is the #1 blocker for security-conscious SaaS signups. It is distinct from Cloudflare's transparent challenge (which is a silent JS challenge with no interactive element).
- **Layer 3 (Kernel cloud) is the minimum.** Kernel includes built-in CAPTCHA solving and clean browser fingerprints. This is the recommended path.
- **Pattern for production SaaS:** Expect Turnstile on any production SaaS with security-conscious engineering (Linear, enterprise tools). Plan for Layer 3 from the start.

### Stealth escalation for Linear

```
Layer 1 (env vars)          --> FAILS at email verification (Turnstile)
Layer 2 (rebrowser-patches) --> INCOMPATIBLE (pw version mismatch, Feb 2026)
Layer 3 (Kernel cloud)      --> REQUIRED (CAPTCHA solving + clean fingerprint)
```

```bash
# Layer 3 setup for Linear:
export AGENT_BROWSER_PROVIDER=kernel
export KERNEL_API_KEY=your_key_here
export KERNEL_PROFILE_NAME=linear-signup
# KERNEL_STEALTH defaults to true
```

## Sample Worker Prompt

```
Sign up for a Linear account using AgentMail for email verification.

IMPORTANT: This site uses Cloudflare Turnstile CAPTCHA. You MUST have Layer 3 stealth enabled (Kernel cloud provider). If running with Layer 1 only, the flow will block at email verification. Report the block and stop -- do not waste calls retrying.

Steps:
1. Create an AgentMail inbox: ./scripts/agentmail.sh create linear-signup-01
   - If you hit the 3-inbox limit, list and delete stale inboxes first
2. Navigate to https://linear.app/signup
3. Fill email: linear-signup-01@agentmail.to
4. Click Continue
5. If Turnstile CAPTCHA appears: STOP, screenshot, report "Blocked by Cloudflare Turnstile -- requires Layer 3"
6. If no CAPTCHA: poll AgentMail for verification email (timeout 120s)
7. Extract OTP/verification link
8. Complete verification
9. Complete onboarding steps (name, workspace, team size)
10. Create a test issue
11. Screenshot at each milestone

Report: phase reached, screenshots, any error details.
```
