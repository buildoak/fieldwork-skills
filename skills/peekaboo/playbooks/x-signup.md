---
status: validated
validated: 2026-02-22
domain: browser-automation
---
# X/Twitter Account Registration

## When to Use
Create a new X (Twitter) account from scratch via Safari. Covers signup, email verification, and profile setup.

## Prerequisites
- Safari browser, peekaboo health check passing
- Fresh email address (not previously used on X)
- `gogcli` (gog) CLI for reading email verification codes from Gmail
- Home network (no CAPTCHA encountered, no phone number required)

## Flow

1. Navigate to signup:
   ```bash
   peekaboo-safe.sh open "https://x.com/i/flow/signup" --app Safari --wait-until-ready
   sleep 3
   ```

2. Check which form variant X served (email vs phone — random A/B test):
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     document.querySelector(\"input[type=email]\") ? \"email\" : \"phone\";
   " in document 1'
   ```
   If "phone" — reload until email form appears. Do not try to switch the field.

3. Fill name and email fields (React controlled components, nativeInputValueSetter):
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var inputs = document.querySelectorAll(\"input\");
     var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, \"value\").set;
     nativeSetter.call(inputs[0], \"Display Name\");
     inputs[0].dispatchEvent(new Event(\"input\", {bubbles: true}));
     nativeSetter.call(inputs[1], \"email@example.com\");
     inputs[1].dispatchEvent(new Event(\"input\", {bubbles: true}));
   " in document 1'
   ```

4. Fill date of birth (dropdown selects for month/day/year):
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var selects = document.querySelectorAll(\"select\");
     selects[0].value = \"1\"; selects[0].dispatchEvent(new Event(\"change\", {bubbles:true}));
     selects[1].value = \"15\"; selects[1].dispatchEvent(new Event(\"change\", {bubbles:true}));
     selects[2].value = \"1995\"; selects[2].dispatchEvent(new Event(\"change\", {bubbles:true}));
   " in document 1'
   ```

5. Click Next/Submit via coordinate click:
   ```bash
   peekaboo-safe.sh see --analyze "Where is the Next button?" --app Safari
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 3
   ```

6. Retrieve email verification code via gogcli:
   ```bash
   gog gmail messages list --query "from:x.com" --max-results 1 --format json | jq -r '.messages[0].snippet'
   # Extract 6-digit code from the snippet
   ```

7. Enter verification code:
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var input = document.querySelector(\"input[type=text]\") || document.querySelector(\"input[name=verfication_code]\");
     var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, \"value\").set;
     nativeSetter.call(input, \"123456\");
     input.dispatchEvent(new Event(\"input\", {bubbles: true}));
   " in document 1'
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari  # Next button
   ```

8. Set password, then profile setup:
   - Skip profile photo (or use `file-upload.md` playbook)
   - Accept suggested username or modify
   - Select 1+ interests from category grid
   - Follow 1+ suggested accounts
   - Each step: `see --analyze` to identify current screen, coordinate click to proceed

## Key Patterns

- **Email/phone form is random.** X serves either phone or email input on signup — bot-detection A/B test. Not switchable via JS or URL params. Reload until email form appears. Check with `document.querySelector('input[type=email]')`.
- **X uses regular DOM, not shadow DOM.** Unlike Reddit, X signup form inputs are in the regular DOM. But they use React controlled components, so nativeInputValueSetter + event dispatch is still required.
- **No CAPTCHA on real Safari + home IP.** No reCAPTCHA, no phone verification prompt encountered during validation.
- **If phone IS required** (rare on home IP): Manual bridge pattern. Agent pauses, coordinator asks user for phone number or code, agent injects it via JS. Do not try to automate phone verification.
- **gogcli for email verification.** `gog gmail messages list --query "from:x.com"` retrieves the verification email. Parse the 6-digit code from the message snippet or body.

## Known Issues

- X may add extra steps (tracking consent, notifications prompt) between signup screens. Use `see --analyze "What is the current screen asking?"` at each transition.
- Date of birth dropdowns may not fire `change` events correctly on Safari. If form won't advance, try coordinate-clicking each dropdown and visually selecting values.
- X rate-limits signup attempts per IP. If blocked, wait 24h or switch networks.
- Password requirements: 8+ characters. X validates in real-time and blocks Next if too weak.

## Evidence
- Validated Feb 22, 2026, Safari, home network
- Full end-to-end: signup, email verification via gogcli, profile setup completed
- No CAPTCHA, no phone verification required
