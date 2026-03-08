---
status: validated
validated: 2026-02-22
domain: browser-automation
---
# macOS File Upload from Web Apps

## When to Use
Upload a file from a web application's file picker dialog. Covers the macOS file dialog that appears when clicking upload/attach buttons in Safari.

## Prerequisites
- Safari browser with web app open
- File exists at a known absolute path on disk
- peekaboo health check passing

## Flow

1. Trigger the file picker (click upload button in the web app):
   ```bash
   peekaboo-safe.sh see --analyze "Where is the upload/attach/choose file button?" --app Safari
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 2
   ```

2. Verify file dialog appeared:
   ```bash
   peekaboo-safe.sh see --analyze "Is there a macOS file picker dialog open?" --mode screen
   ```

3. Open Go To Folder with Cmd+Shift+G:
   ```bash
   peekaboo-safe.sh hotkey --keys "cmd+shift+g"
   sleep 1
   ```

4. Type the full absolute file path via System Events keystroke:
   ```bash
   osascript -e 'tell application "System Events" to keystroke "/tmp/peekaboo/path/to/file.png"'
   sleep 0.5
   osascript -e 'tell application "System Events" to key code 36'  # Return
   sleep 1
   ```

5. File gets selected in the dialog. Click Open/Upload:
   ```bash
   osascript -e 'tell application "System Events" to key code 36'  # Return to confirm
   sleep 2
   ```

6. Handle crop dialog if shown (some sites show image cropping after upload):
   ```bash
   peekaboo-safe.sh see --analyze "Is there a crop or resize dialog? Is there an Apply or Save button?" --app Safari
   # If crop dialog: click Apply (for pre-cropped images) or adjust and Apply
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   ```

7. Verify upload completed:
   ```bash
   peekaboo-safe.sh see --analyze "Did the file upload successfully? Is there a preview or confirmation?" --app Safari
   ```

## Key Patterns

- **Cmd+Shift+G is the canonical path.** Opens Go To Folder in any macOS file picker. This is deterministic — no Finder sidebar navigation, no visual tree traversal, no guessing.
- **System Events keystroke for path entry.** The Go To Folder text field is a system dialog, not in Safari's DOM. Use `osascript -e 'tell application "System Events" to keystroke "/full/path"'` followed by Return.
- **Never navigate Finder sidebar visually.** Sidebar items are tightly packed, AX clicks misfire. Path entry via Go To Folder is 100% reliable.
- **Return key confirms twice.** First Return confirms the Go To path (navigates to folder and selects file). Second Return clicks the Open/Upload button.

## Known Issues

- If the file dialog is in "compact" mode (no sidebar visible), Cmd+Shift+G still works.
- Some web apps use custom upload components (drag-and-drop only) that don't trigger the native file picker. For those, use JS-based file injection instead.
- Crop dialogs vary by site. Some auto-crop to required dimensions, others need manual adjustment.
- Large files may take time to upload after selection. Wait and verify with `see --analyze`.

## Evidence
- Validated on X profile picture upload, Feb 22, 2026, Mac Mini, Safari
- Cmd+Shift+G -> path entry -> Return -> file selected -> Apply crop -> upload confirmed
