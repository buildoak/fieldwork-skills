# Safari Login Playbook

Generic login flow for any website via Safari using hybrid AX + JavaScript approach.

## Status: **validated** | Last Updated: 2026-02-22

## Inputs
- `LOGIN_URL`: Target website login page (required)
- `USERNAME_SELECTOR`: CSS selector for username field (required)
- `PASSWORD_SELECTOR`: CSS selector for password field (required)
- `SUBMIT_SELECTOR`: CSS selector for submit button (optional)
- `USERNAME`: Username credential (use keychain, not plaintext)
- `PASSWORD`: Password credential (use keychain, not plaintext)

## Preconditions
- Safari browser available
- Credentials stored in macOS Keychain or vault.sh
- Health check passes
- No existing login session (or logout first)

## FSM Flow
PREFLIGHT → ACQUIRE_WINDOW → NAVIGATE → DISCOVER → INTERACT → VERIFY → CLEANUP

## Credential Security
**NEVER use plaintext credentials in scripts.** Use secure retrieval:

```bash
# Option 1: macOS Keychain
USERNAME=$(security find-generic-password -a "$USER" -s "website-login" -w)
PASSWORD=$(security find-generic-password -a "$USER" -s "website-password" -w)

# Option 2: vault.sh (if available)
USERNAME=$(vault.sh get username.website)
PASSWORD=$(vault.sh get password.website)

# Option 3: Environment variables (set and unset immediately)
export USERNAME="user"  # Set from secure source
export PASSWORD="pass"  # Set from secure source
```

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p /tmp/peekaboo
umask 077  # Private file permissions

# Secure credential retrieval
USERNAME=$(security find-generic-password -a "$USER" -s "website-login" -w 2>/dev/null || echo "")
PASSWORD=$(security find-generic-password -a "$USER" -s "website-password" -w 2>/dev/null || echo "")

if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    echo "ERROR: Credentials not found in keychain"
    exit 1
fi
```

### ACQUIRE_WINDOW (State 2)
```bash
# Launch Safari if needed
peekaboo-safe.sh app launch Safari --wait-until-ready

# Switch to Safari
peekaboo-safe.sh app switch --to Safari

# Close any existing login tabs to avoid confusion
# Optional: Check for existing login via see --analyze
```

### NAVIGATE (State 3)
```bash
# Navigate to login page - NEVER type URLs manually
peekaboo-safe.sh open "$LOGIN_URL" --app Safari --wait-until-ready
sleep 3  # Allow page load

# Verify navigation success
peekaboo-safe.sh see --analyze "Is this a login page with username and password fields?" --app Safari
```

### DISCOVER (State 4)
```bash
# Discover page structure - this may timeout on complex pages
result=$(peekaboo-safe.sh see --app Safari --json --annotate --path /tmp/peekaboo/ 2>/dev/null)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id // "none"')

# If see times out, check for UI-TARS server
if [ "$snapshot_id" = "none" ]; then
    echo "WARNING: AX discovery timed out. Starting UI-TARS for complex pages..."
    # Start UI-TARS server if not running
    if ! curl -sf http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then
        echo "Start UI-TARS server: python3 -m mlx_vlm server --host 127.0.0.1 --port 8080 (from VLM venv)"
    fi
fi
```

### INTERACT (State 5)
**Form filling MUST use JavaScript injection** - AX typing fails on web forms:

```bash
# Fill username field via JavaScript
osascript -e "tell application \"Safari\" to do JavaScript \"
    var userField = document.querySelector('$USERNAME_SELECTOR');
    if (userField) {
        userField.value = '$USERNAME';
        userField.dispatchEvent(new Event('input', {bubbles: true}));
        userField.dispatchEvent(new Event('change', {bubbles: true}));
        console.log('Username filled');
    } else {
        console.log('Username field not found');
    }
\" in document 1"

# Fill password field via JavaScript
osascript -e "tell application \"Safari\" to do JavaScript \"
    var passField = document.querySelector('$PASSWORD_SELECTOR');
    if (passField) {
        passField.value = '$PASSWORD';
        passField.dispatchEvent(new Event('input', {bubbles: true}));
        passField.dispatchEvent(new Event('change', {bubbles: true}));
        console.log('Password filled');
    } else {
        console.log('Password field not found');
    }
\" in document 1"

# Clear credentials from memory immediately
unset USERNAME PASSWORD

# Submit via coordinate click (AX click on web buttons fails)
if [ -n "$SUBMIT_SELECTOR" ]; then
    # Option 1: JavaScript form submission
    osascript -e "tell application \"Safari\" to do JavaScript \"
        var submitBtn = document.querySelector('$SUBMIT_SELECTOR');
        if (submitBtn) {
            submitBtn.click();
        } else {
            document.querySelector('form').submit();
        }
    \" in document 1"
else
    # Option 2: Manual coordinate click - get coordinates from see output or visual inspection
    peekaboo-safe.sh click --coords 400,500 --no-auto-focus --app Safari
fi

sleep 2  # Allow form submission
```

### VERIFY (State 6)
```bash
# Check for successful login
login_check=$(peekaboo-safe.sh see --analyze "Did the login succeed? Are we now on a dashboard or logged-in page?" --app Safari)
echo "Login verification: $login_check"

# Take screenshot for evidence
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/login-result.png

# Check for common failure indicators
error_check=$(peekaboo-safe.sh see --analyze "Is there a login error message or CAPTCHA on screen?" --app Safari)
if [[ "$error_check" == *"error"* ]] || [[ "$error_check" == *"CAPTCHA"* ]]; then
    echo "ERROR: Login failed - $error_check"
    # Escalate to HUMAN_HANDOFF state
    exit 1
fi
```

### CLEANUP (State 8)
```bash
# Clean sensitive screenshots
rm -f /tmp/peekaboo/login-*.png 2>/dev/null || true

# Clean snapshots
peekaboo-safe.sh clean --older-than 1

echo "Login completed successfully"
```

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| Page won't load | Network/URL issue | Verify URL, check connection |
| Form fields not found | Wrong selectors | Inspect page, update selectors |
| JavaScript fails | CSP/security restrictions | Try coordinate input as fallback |
| Login error message | Wrong credentials | Verify keychain, check for CAPTCHA |
| CAPTCHA appears | Bot detection | Escalate to human handoff |
| 2FA prompt | Account security | Escalate to human for code entry |

## Common CSS Selectors

| Field Type | Common Selectors |
|------------|------------------|
| Username | `input[name="username"]`, `input[name="email"]`, `#username`, `#email` |
| Password | `input[name="password"]`, `input[type="password"]`, `#password` |
| Submit | `input[type="submit"]`, `button[type="submit"]`, `.login-button`, `#login-btn` |

## Security Notes
- **Store credentials in macOS Keychain, never in scripts**
- **Unset credential variables immediately after use**
- **Clean sensitive screenshots after verification**
- **Use `umask 077` for private file permissions**
- **CAPTCHA and 2FA require human handoff**

## Acceptance Tests

### Test 1: GitHub Login
```bash
LOGIN_URL="https://github.com/login"
USERNAME_SELECTOR="#login_field"
PASSWORD_SELECTOR="#password"
SUBMIT_SELECTOR="input[type='submit']"
# Expected: Successful authentication to dashboard
```

### Test 2: Gmail Login
```bash
LOGIN_URL="https://accounts.google.com/signin"
USERNAME_SELECTOR="input[type='email']"
PASSWORD_SELECTOR="input[type='password']"
# Expected: May trigger 2FA handoff
```

## Token Budget
- Expected turns: 10-20
- Cost estimate: ~$0.10-0.25 (Sonnet 4)
- High cost due to screenshot verification steps

## Safari-Specific Workarounds

1. **AX click on web buttons opens Start Page** → Use coordinate clicks
2. **Type commands target URL bar** → Use JavaScript injection
3. **See timeouts on complex pages** → Start UI-TARS server
4. **Form validation requires events** → Always dispatch input/change events

## References
- Complete Safari workflow: `references/safari-workarounds.md`
- CSS selector tools: Safari Developer Tools (Develop menu)