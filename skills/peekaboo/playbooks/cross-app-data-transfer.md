# Cross-App Data Transfer Playbook

Extract data from app A, transfer via clipboard, and enter into app B with verification.

## Status: **validated** | Last Updated: 2026-02-22

## Inputs
- `SOURCE_APP`: Application to extract data from (required)
- `TARGET_APP`: Application to insert data into (required)
- `SOURCE_SELECTOR`: Element ID or query for source data (required)
- `TARGET_SELECTOR`: Element ID or query for target field (required)
- `TRANSFER_TYPE`: text|image|file (default: text)

## Preconditions
- Both applications are installed and accessible
- Source data is visible/accessible in source app
- Target field is editable in target app
- Accessibility permissions granted

## FSM Flow
PREFLIGHT → EXTRACT → TRANSFER → INSERT → VERIFY → CLEANUP

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p /tmp/peekaboo

# Save current clipboard state
peekaboo-safe.sh clipboard save --slot backup

# Verify both apps are available
peekaboo-safe.sh app launch "$SOURCE_APP" --wait-until-ready
peekaboo-safe.sh app launch "$TARGET_APP" --wait-until-ready
```

### EXTRACT (State 7) - From Source App
```bash
# Switch to source application
peekaboo-safe.sh app switch --to "$SOURCE_APP"
sleep 1

# Discover source data structure
result=$(peekaboo-safe.sh see --app "$SOURCE_APP" --json --annotate --path /tmp/peekaboo/)
source_snapshot=$(echo "$result" | jq -r '.snapshot_id')

# Take screenshot for reference
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/source-state.png

case "$TRANSFER_TYPE" in
    "text")
        extract_text_data
        ;;
    "image")
        extract_image_data
        ;;
    "file")
        extract_file_data
        ;;
    *)
        echo "ERROR: Unknown transfer type: $TRANSFER_TYPE"
        exit 1
        ;;
esac
```

#### Text Extraction Function
```bash
extract_text_data() {
    # Method 1: Select and copy via AX
    peekaboo-safe.sh click --on "$SOURCE_SELECTOR" --snapshot "$source_snapshot" --app "$SOURCE_APP"

    # Select all text in field/area
    peekaboo-safe.sh hotkey --keys "cmd,a" --app "$SOURCE_APP"

    # Copy to clipboard
    peekaboo-safe.sh hotkey --keys "cmd,c" --app "$SOURCE_APP"

    # Verify clipboard has content
    clipboard_content=$(peekaboo-safe.sh clipboard get)
    if [ -z "$clipboard_content" ]; then
        echo "ERROR: No text copied to clipboard"
        exit 1
    fi

    echo "Extracted text: ${clipboard_content:0:50}..."
}
```

#### Image Extraction Function
```bash
extract_image_data() {
    # Method 1: Right-click and copy image
    peekaboo-safe.sh click --on "$SOURCE_SELECTOR" --right --snapshot "$source_snapshot" --app "$SOURCE_APP"
    sleep 0.5

    # Look for "Copy Image" in context menu
    peekaboo-safe.sh click --query "Copy Image" --app "$SOURCE_APP"

    # Alternative: Screenshot specific region
    # peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/extracted-image.png
    # peekaboo-safe.sh clipboard set --image-path /tmp/peekaboo/extracted-image.png
}
```

#### File Extraction Function
```bash
extract_file_data() {
    # Select file in Finder or app
    peekaboo-safe.sh click --on "$SOURCE_SELECTOR" --snapshot "$source_snapshot" --app "$SOURCE_APP"

    # Copy file reference
    peekaboo-safe.sh hotkey --keys "cmd,c" --app "$SOURCE_APP"

    echo "File copied to clipboard for transfer"
}
```

### TRANSFER (State - Intermediate)
```bash
# Clipboard is our transfer medium - data is already there
# Take snapshot for audit trail
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/transfer-point.png

echo "Data ready for transfer via clipboard"
```

### INSERT (State 5) - Into Target App
```bash
# Switch to target application
peekaboo-safe.sh app switch --to "$TARGET_APP"
sleep 1

# Discover target structure
target_result=$(peekaboo-safe.sh see --app "$TARGET_APP" --json --annotate --path /tmp/peekaboo/)
target_snapshot=$(echo "$target_result" | jq -r '.snapshot_id')

# Click target field to focus
peekaboo-safe.sh click --on "$TARGET_SELECTOR" --snapshot "$target_snapshot" --app "$TARGET_APP"
sleep 0.5

case "$TRANSFER_TYPE" in
    "text")
        insert_text_data
        ;;
    "image")
        insert_image_data
        ;;
    "file")
        insert_file_data
        ;;
esac
```

#### Text Insertion Function
```bash
insert_text_data() {
    # Clear existing content if needed
    peekaboo-safe.sh hotkey --keys "cmd,a" --app "$TARGET_APP"

    # Paste text content
    peekaboo-safe.sh hotkey --keys "cmd,v" --app "$TARGET_APP"

    # Alternative atomic paste (preserves original clipboard)
    # peekaboo-safe.sh paste --text "$clipboard_content" --app "$TARGET_APP"
}
```

#### Image Insertion Function
```bash
insert_image_data() {
    # Paste image - works in most apps that accept images
    peekaboo-safe.sh hotkey --keys "cmd,v" --app "$TARGET_APP"

    echo "Image pasted into target application"
}
```

#### File Insertion Function
```bash
insert_file_data() {
    # Paste file reference
    peekaboo-safe.sh hotkey --keys "cmd,v" --app "$TARGET_APP"

    echo "File reference pasted - may open or attach depending on target app"
}
```

### VERIFY (State 6)
```bash
sleep 1  # Allow paste operation to complete

# Take screenshot of result
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/target-result.png

# Verify insertion via text analysis
case "$TRANSFER_TYPE" in
    "text")
        verify_result=$(peekaboo-safe.sh see --analyze "Is there text content visible in the target field?" --app "$TARGET_APP")
        ;;
    "image")
        verify_result=$(peekaboo-safe.sh see --analyze "Is there an image visible in the target area?" --app "$TARGET_APP")
        ;;
    "file")
        verify_result=$(peekaboo-safe.sh see --analyze "Is there a file or file reference visible?" --app "$TARGET_APP")
        ;;
esac

echo "Transfer verification: $verify_result"

if [[ "$verify_result" == *"yes"* ]] || [[ "$verify_result" == *"visible"* ]]; then
    echo "SUCCESS: Data transfer completed"
else
    echo "WARNING: Transfer may have failed - check target app"
    exit 1
fi
```

### CLEANUP (State 8)
```bash
# Restore original clipboard
peekaboo-safe.sh clipboard restore --slot backup

# Clean temporary files
rm -f /tmp/peekaboo/source-state.png /tmp/peekaboo/transfer-point.png /tmp/peekaboo/target-result.png 2>/dev/null || true

# Clean snapshots
peekaboo-safe.sh clean --older-than 1

echo "Cross-app data transfer completed successfully"
```

## Common Transfer Patterns

### Pattern 1: Text Notes → Email
```bash
SOURCE_APP="Notes"
TARGET_APP="Mail"
SOURCE_SELECTOR="T1"  # Note content area
TARGET_SELECTOR="T3"  # Email body field
TRANSFER_TYPE="text"
```

### Pattern 2: Safari → TextEdit
```bash
SOURCE_APP="Safari"
TARGET_APP="TextEdit"
SOURCE_SELECTOR="S5"  # Selected text on webpage
TARGET_SELECTOR="T1"  # Document area
TRANSFER_TYPE="text"
```

### Pattern 3: Finder → Messages
```bash
SOURCE_APP="Finder"
TARGET_APP="Messages"
SOURCE_SELECTOR="I1"  # File icon
TARGET_SELECTOR="T2"  # Message input field
TRANSFER_TYPE="file"
```

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| Nothing copied | Source selection failed | Retry selection, use hotkey instead |
| Paste fails | Target not focused | Re-click target field |
| Wrong content pasted | Clipboard contaminated | Save/restore clipboard properly |
| File path instead of file | App-specific handling | Check target app's paste behavior |
| Permission denied | Sandboxing restrictions | Use drag-and-drop alternative |

## Security Notes
- Clipboard contents are temporarily visible to all apps
- Sensitive data should use secure paste operations
- Clean clipboard after sensitive transfers
- Screenshots may capture private data

## Advanced Techniques

### Drag and Drop Alternative
```bash
# For apps that support drag-and-drop
peekaboo-safe.sh drag --from "$SOURCE_SELECTOR" --to-app "$TARGET_APP" --space-switch
```

### Multiple Item Transfer
```bash
# Transfer multiple items in sequence
for item in item1 item2 item3; do
    # Extract item
    # Transfer item
    # Verify item
done
```

### Format-Specific Transfer
```bash
# Rich text preservation
peekaboo-safe.sh clipboard set --data-base64 "$RTF_DATA" --uti public.rtf --also-text "fallback"
```

## Acceptance Tests

### Test 1: Safari URL → TextEdit
```bash
SOURCE_APP="Safari"
TARGET_APP="TextEdit"
# Copy URL from address bar to document
# Expected: URL appears as text in TextEdit
```

### Test 2: Notes Content → Mail Body
```bash
SOURCE_APP="Notes"
TARGET_APP="Mail"
# Copy note content to email draft
# Expected: Formatted text preserved in email
```

### Test 3: Finder Image → Messages
```bash
SOURCE_APP="Finder"
TARGET_APP="Messages"
TRANSFER_TYPE="image"
# Send image file via Messages
# Expected: Image appears in message thread
```

## Token Budget
- Expected turns: 12-25
- Cost estimate: ~$0.15-0.30 (Sonnet 4)
- Medium cost due to dual-app verification

## Integration Notes

This playbook is often used as a component in larger workflows:
- Data migration between apps
- Content creation pipelines
- Report generation workflows
- Cross-platform data sharing