# Dialog and File Picker Playbook

Handle macOS system dialogs: Save/Open, file pickers, permission sheets, alert dialogs.

## Status: **validated** | Last Updated: 2026-02-22

## Inputs
- `DIALOG_TYPE`: save|open|alert|permission (required)
- `FILE_PATH`: Target directory path for file operations (optional)
- `FILE_NAME`: Target filename for save operations (optional)
- `BUTTON_NAME`: Target button text: "OK"|"Cancel"|"Save"|"Don't Save" (required)

## Preconditions
- Dialog is currently visible on screen
- Accessibility permissions granted
- For file operations: target directory exists and is accessible

## FSM Flow
PREFLIGHT → DISCOVER → INTERACT → VERIFY → CLEANUP

This is a short-cycle automation - no app switching needed since dialogs are system-wide.

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p /tmp/peekaboo

# Verify dialog is present
dialog_present=$(peekaboo-safe.sh see --analyze "Is there a dialog or sheet visible on screen?" --mode screen)
if [[ "$dialog_present" != *"dialog"* ]] && [[ "$dialog_present" != *"sheet"* ]]; then
    echo "ERROR: No dialog detected"
    exit 1
fi
```

### DISCOVER (State 4)
```bash
# Capture system-wide AX tree to find dialog elements
result=$(peekaboo-safe.sh see --mode screen --json --annotate --path /tmp/peekaboo/)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id')

# Save dialog structure for debugging
echo "$result" > /tmp/peekaboo/dialog-structure.json

# Take screenshot for visual reference
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/dialog-screenshot.png
```

### INTERACT (State 5)

#### File Save Dialog
```bash
if [ "$DIALOG_TYPE" = "save" ]; then
    # Navigate to target directory if specified
    if [ -n "$FILE_PATH" ]; then
        peekaboo-safe.sh dialog file --path "$FILE_PATH" --ensure-expanded
        sleep 1
    fi

    # Set filename if specified
    if [ -n "$FILE_NAME" ]; then
        peekaboo-safe.sh dialog file --name "$FILE_NAME"
        sleep 0.5
    fi

    # Click Save button - use --no-auto-focus for dialogs
    peekaboo-safe.sh dialog click --button "Save" --no-auto-focus
fi
```

#### File Open Dialog
```bash
if [ "$DIALOG_TYPE" = "open" ]; then
    # Navigate to target directory
    if [ -n "$FILE_PATH" ]; then
        peekaboo-safe.sh dialog file --path "$FILE_PATH" --ensure-expanded
        sleep 1
    fi

    # Select file if specified
    if [ -n "$FILE_NAME" ]; then
        # Find and click the file in the file list
        peekaboo-safe.sh click --query "$FILE_NAME" --no-auto-focus
        sleep 0.5
    fi

    # Click Open/Select button
    peekaboo-safe.sh dialog click --button "Open" --no-auto-focus
fi
```

#### Alert Dialog
```bash
if [ "$DIALOG_TYPE" = "alert" ]; then
    # Simple button click - common buttons: OK, Cancel, Yes, No, Don't Save
    case "$BUTTON_NAME" in
        "Don't Save")
            # AX label is "Delete" for Don't Save button
            peekaboo-safe.sh click --query "Delete" --no-auto-focus
            ;;
        *)
            peekaboo-safe.sh dialog click --button "$BUTTON_NAME" --no-auto-focus
            ;;
    esac
fi
```

#### Permission Dialog
```bash
if [ "$DIALOG_TYPE" = "permission" ]; then
    echo "WARNING: TCC permission dialogs cannot be automated"
    echo "User must manually grant permissions in System Settings"
    echo "Dialog type: TCC (Transparency, Consent, and Control)"

    # Take screenshot for documentation
    peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/permission-dialog.png

    # Human handoff required
    exit 2
fi
```

### VERIFY (State 6)
```bash
sleep 1  # Allow dialog to dismiss

# Verify dialog is gone
dialog_gone=$(peekaboo-safe.sh see --analyze "Is the dialog closed? Is the main app window now visible?" --mode screen)

if [[ "$dialog_gone" == *"dialog"* ]] || [[ "$dialog_gone" == *"sheet"* ]]; then
    echo "WARNING: Dialog may still be visible"
    peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/dialog-still-open.png
else
    echo "SUCCESS: Dialog closed successfully"
fi
```

### CLEANUP (State 8)
```bash
# Clean dialog snapshots
peekaboo-safe.sh clean --older-than 1

echo "Dialog interaction completed"
```

## Compact Dialog Workaround

Some file dialogs appear in "compact" mode where Save/Cancel buttons are hidden from AX tree:

```bash
# Force expanded view to reveal buttons
peekaboo-safe.sh dialog file --ensure-expanded --path /path/to/user/Documents

# Alternative: Coordinate click if buttons remain hidden
# Get coordinates from visual inspection first
peekaboo-safe.sh click --coords 650,500 --no-auto-focus  # Save button position
```

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| Dialog not found | No active dialog | Wait or trigger dialog first |
| Button not clickable | Compact dialog mode | Use --ensure-expanded flag |
| File path navigation fails | Path doesn't exist | Verify path, use absolute paths |
| Permission dialog appears | TCC system dialog | Human handoff required |
| Click has no effect | Missing --no-auto-focus | Add flag to prevent focus conflicts |

## Security Notes
- File dialogs may expose sensitive directory structures in screenshots
- Permission dialogs cannot be automated by design
- Clean /tmp/peekaboo/ after file operations

## Acceptance Tests

### Test 1: TextEdit Save Dialog
```bash
# Trigger: TextEdit > File > Save As...
DIALOG_TYPE="save"
FILE_PATH="/path/to/user/Desktop"
FILE_NAME="test-document.txt"
BUTTON_NAME="Save"
# Expected: File saved to Desktop
```

### Test 2: Finder File Selection
```bash
# Trigger: Any app > File > Open...
DIALOG_TYPE="open"
FILE_PATH="/path/to/user/Documents"
FILE_NAME="existing-file.pdf"
BUTTON_NAME="Open"
# Expected: File opened in requesting app
```

### Test 3: Unsaved Changes Alert
```bash
# Trigger: Quit app with unsaved changes
DIALOG_TYPE="alert"
BUTTON_NAME="Don't Save"
# Expected: App quits without saving
```

## Token Budget
- Expected turns: 5-10
- Cost estimate: ~$0.03-0.08 (Sonnet 4)
- Low cost due to simple interaction pattern

## Common Button Mappings

| Visible Button | AX Label | Notes |
|----------------|----------|-------|
| "Don't Save" | "Delete" | Use query "Delete" |
| "Save As..." | "Duplicate" | TextEdit-specific mapping |
| "Open" | "Open" | Standard |
| "Cancel" | "Cancel" | Standard |
| "OK" | "OK" | Standard |

## Advanced File Dialog Operations

```bash
# Create new folder in dialog
peekaboo-safe.sh hotkey --keys "cmd,shift,n"

# Navigate up one level
peekaboo-safe.sh hotkey --keys "cmd,up"

# Navigate to home directory
peekaboo-safe.sh hotkey --keys "cmd,shift,h"

# Show hidden files
peekaboo-safe.sh hotkey --keys "cmd,shift,period"
```

## Integration with Native App Playbook

This playbook is often called from `native-app-automation.md` when file operations are triggered:

```bash
# In native app workflow
peekaboo-safe.sh menu click --path "File > Save As..." --app TextEdit
# Wait for dialog to appear
sleep 1
# Then run dialog playbook
source playbooks/dialog-and-file-picker.md
```