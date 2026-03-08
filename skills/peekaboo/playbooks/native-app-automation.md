# Native App Automation Playbook

Template for automating any native macOS application using AX-first approach.

## Status: **validated** | Last Updated: 2026-02-22

## Inputs
- `APP_NAME`: Target application name (required)
- `WINDOW_TITLE`: Specific window to target (optional)
- `TASK_DESCRIPTION`: Natural language task description (optional, for agent mode)

## Preconditions
- Accessibility permissions granted for Terminal/Claude Code
- Target application installed and launchable
- Health check passes: `./scripts/health-check.sh`

## FSM Flow
PREFLIGHT → ACQUIRE_WINDOW → WAIT_FOR_UI_STABLE → DISCOVER → INTERACT → VERIFY → CLEANUP

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
# Expected: {"cli_exists":true,"accessibility_granted":true,"ax_test_success":true}
mkdir -p /tmp/peekaboo
```

### ACQUIRE_WINDOW (State 2)

**Navigate programmatically first.** Never click through UI to reach a target.

```bash
# Strategy 1 (preferred): URL scheme / direct open
# System Settings: open "x-apple.systempreferences:com.apple.Desktop-Settings.extension"
# Safari page:    open -a Safari "https://example.com"
# File in app:    open -a TextEdit /path/to/file

# Strategy 2: AppleScript for apps with scripting dictionary
# osascript -e 'tell app "Finder" to open folder "Desktop"'

# Strategy 3: CLI launch with target
peekaboo-safe.sh app launch "$APP_NAME" --wait-until-ready

# Always switch + focus after navigation
peekaboo-safe.sh app switch --to "$APP_NAME"
if [ -n "$WINDOW_TITLE" ]; then
    peekaboo-safe.sh window focus --window-title "$WINDOW_TITLE" --app "$APP_NAME"
fi
```

**Hostile AX apps** — do NOT use sidebar/tab navigation:
- **System Settings**: Use URL scheme `open "x-apple.systempreferences:com.apple.PANE_ID"`. SwiftUI sidebar clicks misfire (tested: clicked "Control Centre" instead of "Desktop & Dock" repeatedly). Toggles are invisible to AX role queries — use screenshot + coordinate click.

### WAIT_FOR_UI_STABLE (State 3)
```bash
sleep 1  # Allow UI to settle
# Optional: Check for loading indicators via see --analyze
```

### DISCOVER (State 4)
```bash
# Primary discovery - captures snapshot ID for element targeting
result=$(peekaboo-safe.sh see --app "$APP_NAME" --json --annotate --path /tmp/peekaboo/)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id')
echo "Snapshot: $snapshot_id"

# Save structure for debugging
echo "$result" > /tmp/peekaboo/ax-tree.json
```

### INTERACT (State 5)
Examples of common interactions:

```bash
# Click button by ID
peekaboo-safe.sh click --on B1 --snapshot "$snapshot_id" --app "$APP_NAME"

# Type in text field
peekaboo-safe.sh click --on T2 --snapshot "$snapshot_id" --app "$APP_NAME"
peekaboo-safe.sh type "Hello World" --return --profile human --app "$APP_NAME"

# Navigate menu (preferred over hotkeys)
peekaboo-safe.sh menu click --path "File > New Document" --app "$APP_NAME"

# Dialog handling
peekaboo-safe.sh click --on B3 --no-auto-focus --app "$APP_NAME"

# Drag and drop
peekaboo-safe.sh drag --from B1 --to B5 --app "$APP_NAME"

# Scroll if needed
peekaboo-safe.sh scroll --direction down --amount 3 --app "$APP_NAME"
```

### VERIFY (State 6)
```bash
sleep 1  # Allow action to complete

# Visual verification
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/after-action.png

# Or state analysis
peekaboo-safe.sh see --analyze "Did the action succeed?" --app "$APP_NAME"

# Or fresh AX tree for detailed verification
peekaboo-safe.sh see --app "$APP_NAME" --json --path /tmp/peekaboo/ > /tmp/peekaboo/after.json
```

### CLEANUP (State 8)
```bash
# Clean old snapshots
peekaboo-safe.sh clean --older-than 24

# Restore clipboard if modified
# peekaboo-safe.sh clipboard restore --slot backup
```

## Agent Mode Alternative
For complex multi-step workflows, use agent mode:

```bash
export OPENAI_API_KEY="your-key"
peekaboo-safe.sh agent "Open $APP_NAME, create new document, type 'Hello World', save as test.txt to Desktop" \
  --model gpt-5.1 --max-steps 15
```

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| Empty AX tree | App not frontmost | `app switch --to "$APP_NAME"` |
| Element not found | Stale snapshot | Fresh `see` command, new `snapshot_id` |
| Click timeout | Dialog auto-focus | Add `--no-auto-focus` flag |
| Menu path fails | Apple menu item | Use direct action or coordinate click |
| Type goes nowhere | Focus not set | Click target field first |
| Sidebar click hits wrong item | Tightly packed AX elements (System Settings) | Use URL scheme or AppleScript to navigate instead |
| Toggle invisible to AX | SwiftUI custom controls (System Settings) | Screenshot + coordinate click |
| AX click opens wrong pane | Element ID misidentification | Screenshot → visual verify → coordinate click |

## Security Notes
- No credential handling needed for native apps
- Screenshots may contain sensitive info - clean /tmp/peekaboo/ after use
- Use `umask 077` for private automation scripts

## Acceptance Tests

### Test 1: TextEdit Document Creation
```bash
APP_NAME="TextEdit"
# Run PREFLIGHT through CLEANUP states
# Expected: New document with typed content
```

### Test 2: Finder File Operations
```bash
APP_NAME="Finder"
WINDOW_TITLE="Desktop"
# Expected: Successfully navigate and select files
```

### Test 3: System Settings Toggle (hostile AX — validated Feb 22)
```bash
# DO NOT use AX sidebar navigation — clicks misfire (Control Centre instead of Desktop & Dock)
# Use URL scheme → screenshot → coordinate click
open "x-apple.systempreferences:com.apple.Desktop-Settings.extension"
sleep 3
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/settings.png
# Identify toggle coordinates from screenshot, then:
peekaboo-safe.sh click --coords X,Y --no-auto-focus --app "System Settings"
defaults read com.apple.dock autohide  # verify
```

## Token Budget
- Expected turns: 8-15 for simple tasks
- Cost estimate: ~$0.05-0.15 (Sonnet 4)
- Optimization: Use `see --analyze` for verification steps

## Common Element Types

| Role | ID Prefix | Usage |
|------|-----------|--------|
| Button | B1, B2, B3 | Click actions, form submission |
| TextField | T1, T2, T3 | Text input, search fields |
| StaticText | S1, S2, S3 | Labels, verification text |
| MenuButton | M1, M2, M3 | Dropdown menus, pop-ups |
| Image | I1, I2, I3 | Icons, graphics (clickable) |
| CheckBox | C1, C2, C3 | Toggle options |
| RadioButton | R1, R2, R3 | Single selection |