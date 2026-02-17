# Notion Signup Playbook

**Target:** https://www.notion.so/signup
**Tested:** Feb 2026
**Result:** PASS (full end-to-end)
**Stealth:** Layer 1 sufficient (basic anti-abuse, no CAPTCHA)

## What Works

The complete validated flow -- signup through OTP verification through onboarding through page creation. This is the standout benchmark task and the most complex validated pattern.

### Step-by-step

```bash
# Step 1: Create AgentMail inbox
./scripts/agentmail.sh create notion-signup-01
# Returns: inbox ID and email address (notion-signup-01@agentmail.to)
```

```
# Step 2: Navigate to signup
browser_navigate(url="https://www.notion.so/signup")
browser_snapshot()

# Step 3: Enter email
browser_fill(ref="@email_field", text="notion-signup-01@agentmail.to")
browser_click(ref="@continue_button")          # "Continue with email" or submit
browser_wait(target="2000")
browser_snapshot()                             # should show "check your email" message
```

```bash
# Step 4: Poll for verification email (may take 5-30 seconds)
./scripts/agentmail.sh poll notion-signup-01@agentmail.to --timeout 120
# Returns: inbox_id and message_id when email arrives

# Step 5: Extract OTP code
./scripts/agentmail.sh extract <inbox_id> <message_id>
# Returns: { "otp": "123456" } or { "link": "https://..." }
```

```
# Step 6: Enter OTP in browser
browser_fill(ref="@otp_field", text="123456")
browser_click(ref="@submit_button")            # submit OTP
browser_wait(target="2000")
browser_snapshot()                             # should show onboarding form

# Step 7: Complete onboarding (multiple steps)
# Step 7a: Name
browser_fill(ref="@name_field", text="Agent Workspace")
browser_click(ref="@next_button")
browser_snapshot()

# Step 7b: Workspace type / team size (varies)
browser_click(ref="@option")                   # select workspace type
browser_click(ref="@next_button")
browser_snapshot()
# Repeat for each onboarding step -- snapshot between each to navigate correctly

# Step 8: Verify dashboard reached
browser_snapshot()                             # should show Notion dashboard
browser_screenshot(path="/tmp/notion-dashboard.png")

# Step 9: Create content (prove full access)
browser_click(ref="@new_page_button")          # "New page" or "+" button
browser_type(ref="@page_title", text="Created by agent")
browser_screenshot(path="/tmp/notion-page.png")

# Step 10: Cleanup
browser_close()
```

## What Doesn't Work

1. **Rushing through OTP submission.** OTP emails can take 5-30 seconds to arrive. If you poll too aggressively or with too short a timeout, you will miss the email. Always use `--timeout 120`.

2. **Skipping onboarding steps.** Notion's onboarding has multiple required steps (name, workspace type, team size, use case). You cannot skip or bypass them. Snapshot between each step to understand what is being asked.

3. **Using `agentmail.to` on some other services.** Some services detect and block the `agentmail.to` domain. Notion does not block it (as of Feb 2026), but have a backup email strategy for services that do.

## Key Patterns

- **OTP poll with generous timeout.** `--timeout 120` (2 minutes). OTP emails can be delayed. Polling too quickly wastes calls; too short a timeout causes false failure.
- **Extract and submit promptly.** OTP codes expire. Once the email arrives, extract the code and submit it to the browser immediately. Do not leave it sitting.
- **Snapshot between every onboarding step.** Notion's onboarding flow changes periodically. The steps may vary from what was tested. Always snapshot to see what the current step requires before filling/clicking.
- **Screenshot at milestones.** Take screenshots at: email sent, OTP submitted, dashboard reached, page created. These serve as evidence and debugging artifacts.
- **AgentMail inbox reuse.** If a mailbox already exists for this purpose, reuse it rather than creating a new one (3-inbox cap).

## Anti-Bot Notes

- **Basic anti-abuse only.** Notion uses standard anti-abuse measures (rate limiting, email domain checks) but no CAPTCHA or Cloudflare protection on the signup flow as of Feb 2026.
- **Layer 1 stealth is sufficient.** Headed mode + custom UA + persistent profile passes without issues.
- **`agentmail.to` domain accepted.** Not all services accept disposable email domains, but Notion does.
- **Future risk.** Notion may add Turnstile or similar CAPTCHA in the future. If the signup flow starts blocking, check for Cloudflare integration and escalate to Layer 3.

## Sample Worker Prompt

```
Sign up for a new Notion account using AgentMail for email verification, complete onboarding, and create a test page.

Steps:
1. Create AgentMail inbox: ./scripts/agentmail.sh create notion-test-01
2. Navigate to https://www.notion.so/signup
3. Enter email: notion-test-01@agentmail.to
4. Click Continue
5. Poll for OTP email: ./scripts/agentmail.sh poll notion-test-01@agentmail.to --timeout 120
6. Extract OTP: ./scripts/agentmail.sh extract <inbox_id> <message_id>
7. Enter OTP code in browser and submit
8. Complete ALL onboarding steps (snapshot between each to see what is required)
9. Once on dashboard, click "New page"
10. Type page title: "Automated test page - [current date]"
11. Screenshot at these milestones: email confirmation page, OTP submitted, dashboard, page created
12. Close browser

OTP TIMING: Emails take 5-30 seconds. Poll with --timeout 120. Once extracted, submit immediately (codes expire).

Report: success/failure at each phase, screenshots taken.
```
