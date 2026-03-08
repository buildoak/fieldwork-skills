---
status: validated
validated: 2026-02-22
domain: browser-automation
---
# Reddit Login (New Frontend)

## When to Use
Authenticate into Reddit via Safari. Required before reddit-data-extraction or any authenticated Reddit operation.

## Prerequisites
- Safari browser, peekaboo health check passing
- Reddit credentials in macOS Keychain or vault.sh
- Home network (avoids CAPTCHA triggers)

## Flow

1. Navigate to login page:
   ```bash
   peekaboo-safe.sh open "https://www.reddit.com/login" --app Safari --wait-until-ready
   sleep 3
   ```

2. Probe DOM structure — Reddit new frontend wraps inputs in shadow DOM:
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var hosts = document.querySelectorAll(\"faceplate-text-input\");
     hosts.length + \" shadow hosts found\";
   " in document 1'
   ```

3. Fill username via shadow root traversal + React event dispatch:
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var host = document.querySelectorAll(\"faceplate-text-input\")[0];
     var input = host.shadowRoot.querySelector(\"input\");
     var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, \"value\").set;
     nativeSetter.call(input, \"USERNAME\");
     input.dispatchEvent(new Event(\"input\", {bubbles: true}));
     input.dispatchEvent(new Event(\"change\", {bubbles: true}));
   " in document 1'
   ```

4. Fill password (same pattern, second shadow host):
   ```bash
   osascript -e 'tell application "Safari" to do JavaScript "
     var host = document.querySelectorAll(\"faceplate-text-input\")[1];
     var input = host.shadowRoot.querySelector(\"input\");
     var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, \"value\").set;
     nativeSetter.call(input, \"PASSWORD\");
     input.dispatchEvent(new Event(\"input\", {bubbles: true}));
     input.dispatchEvent(new Event(\"change\", {bubbles: true}));
   " in document 1'
   ```

5. Submit — use coordinate click on the Login button (JS `.click()` may not work on React buttons):
   ```bash
   peekaboo-safe.sh see --analyze "Where is the Login button?" --app Safari
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 3
   ```

6. Verify login success:
   ```bash
   peekaboo-safe.sh see --analyze "Am I logged into Reddit? Can I see a user avatar or karma?" --app Safari
   ```

## Key Patterns

- **Shadow DOM is mandatory.** `document.querySelector('input')` returns nothing on Reddit's new frontend. Must traverse `faceplate-text-input` shadow roots.
- **nativeInputValueSetter is mandatory.** React controlled components ignore direct `.value =` assignment. Must use `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set` then dispatch `input` + `change` events.
- **Submit via coordinate click.** JS-triggered `.click()` on React buttons is unreliable. Use peekaboo coordinate click with `--no-auto-focus`.
- **No CAPTCHA on real Safari + home IP.** Tested Feb 22, 2026 — login succeeded without any challenge.

## Known Issues

- If Reddit serves a different login layout (A/B test), shadow host count may differ. Re-probe DOM structure.
- 2FA accounts require human handoff for code entry.
- Old Reddit (`old.reddit.com`) uses standard forms, not shadow DOM — different selectors needed.

## Evidence
- Validated Feb 22, 2026, Mac Mini, Safari, home network Dubai
- 6 consecutive test passes during validation session
