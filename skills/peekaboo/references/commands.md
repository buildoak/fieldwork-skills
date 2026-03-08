# Peekaboo Command Reference

Complete reference for all `peekaboo` subcommands (3.0.0-beta3). Organized by category.

**Self-documenting:** Run `peekaboo learn` for the canonical built-in reference prompt.

---

## Common Flags (all commands)

| Flag | Description |
|------|------------|
| `--log-level <level>` | trace, verbose, debug, info, warning, error, critical |

### Window/App Targeting (interaction commands)

Most interaction commands (click, type, paste, press, hotkey, drag, move, scroll, swipe) accept:

| Flag | Description |
|------|------------|
| `--app <name>` | Target app by name, bundle ID, or PID:N |
| `--pid <pid>` | Target app by process ID |
| `--window-id <id>` | Target window by CoreGraphics window ID (most stable) |
| `--window-title <title>` | Target window by title (partial match) |
| `--window-index <n>` | Target window by index (0-based, frontmost=0) |
| `--focus-timeout-seconds <n>` | Timeout for focus operations |
| `--focus-retry-count <n>` | Retries for focus operations |

---

## Vision Commands

### `see` — AX Tree Discovery

Primary discovery command. Returns element IDs in B1/T2/S3 format plus `snapshot_id`.

```bash
peekaboo see --app Safari --json --annotate --path /tmp/peekaboo/
peekaboo see --window-title "Login" --app Chrome --json
peekaboo see --mode screen --analyze "What applications are visible?"
peekaboo see --capture-engine auto --screen-index 0 --timeout-seconds 20
peekaboo see --analyze "Describe the current UI state" --app Finder
```

| Flag | Description |
|------|------------|
| `--app <name>` | Target application |
| `--json` | JSON output |
| `--annotate` | Visual annotation overlay |
| `--path <dir>` | Output directory for annotated screenshot |
| `--mode <mode>` | `screen` or `window` |
| `--window-title <title>` | Target specific window |
| `--analyze <prompt>` | AI analysis of the visible state |
| `--capture-engine <engine>` | Capture engine selection (auto) |
| `--screen-index <n>` | Display index |
| `--timeout-seconds <n>` | Timeout |

**Element ID format:** B1 (button), T2 (text field), S3 (static text), M4 (menu), I5 (image), L6 (link), C7 (checkbox), R8 (radio button).

**Snapshot tracking:** Every `see` returns `snapshot_id` for element resolution. Snapshots go stale -- re-run `see` for fresh IDs.

**AXWebArea:** Safari web content is wrapped in AXWebArea role elements.

### `image` — Static Screenshots

```bash
peekaboo image --mode screen --path /tmp/peekaboo/screenshot.png
peekaboo image --app Finder --mode screen --path /tmp/finder.png
peekaboo image --app menubar --path /tmp/menubar.png
peekaboo image --question "What is the main heading?" --app Safari
peekaboo image --format png --capture-focus --output-dir /tmp/
```

| Flag | Description |
|------|------------|
| `--mode <mode>` | `screen` (always use this) or `window` (broken: 698B stubs) |
| `--path <path>` | Output file path |
| `--app <name>` | Target application |
| `--question <prompt>` | AI analysis question |
| `--format <fmt>` | Output format (png) |
| `--capture-focus` | Capture focus state |
| `--output-dir <dir>` | Output directory |

**Bug:** Window-mode capture returns 698B stubs in beta3. Always use `--mode screen`.

### `analyze` — AI Image Analysis

```bash
peekaboo analyze --image-path /tmp/screenshot.png --question "Extract all text"
```

| Flag | Description |
|------|------------|
| `--image-path <path>` | Path to image file |
| `--question <prompt>` | Analysis question |

### `capture` — Live and Video Capture

Alias: `peekaboo watch`

```bash
peekaboo capture live --mode screen --duration-seconds 30 --output-dir /tmp/
peekaboo capture video --input video.mp4 --output-dir /tmp/frames/
peekaboo capture live --mode window --app Safari --max-frames 100
peekaboo capture live --mode region --region "100,100,800,600" --highlight-changes
```

| Flag | Description |
|------|------------|
| `live` / `video` | Submode: live capture or video ingestion |
| `--mode <mode>` | `screen`, `window`, `region` |
| `--duration-seconds <n>` | Capture duration |
| `--output-dir <dir>` | Frame output directory |
| `--input <path>` | Video file for ingestion |
| `--max-frames <n>` | Frame limit |
| `--region <coords>` | Region bounds "x,y,w,h" |
| `--highlight-changes` | Motion highlighting |
| `--app <name>` | Target app (window mode) |

**Diff strategies:** `fast` (default) or `quality`.
**Output formats:** PNG frames, contact sheets, MP4 video, metadata JSON.

---

## Interaction Commands

### `click` — Click Operations

```bash
peekaboo click --on B1 --wait-for 2000 --app Safari
peekaboo click --query "Submit" --app TextEdit
peekaboo click --coords 300,200 --app Finder
peekaboo click --on B5 --right --app Finder
peekaboo click --coords 400,300 --double --app Safari
peekaboo click --on B3 --snapshot "$snapshot_id" --app TextEdit
peekaboo click --on elem_62 --no-auto-focus --app AppName
```

| Flag | Description |
|------|------------|
| `--on <id>` | Element ID (B1, T2, etc.) |
| `--query <text>` | Fuzzy text matching |
| `--coords <x,y>` | Coordinate fallback |
| `--snapshot <id>` | Snapshot ID for element resolution |
| `--wait-for <ms>` | Wait after click |
| `--right` | Right-click |
| `--double` | Double-click |
| `--no-auto-focus` | Required for dialogs |
| `--app <name>` | Target application |

### `type` — Text Input

```bash
peekaboo type "Hello World" --wpm 150 --app TextEdit
peekaboo type "password123" --profile linear --delay 50
peekaboo type "text" --clear --return --app Notes
peekaboo type --tab 3 --escape --app Terminal
peekaboo type "query" --on T2 --app Safari
```

| Flag | Description |
|------|------------|
| `--wpm <n>` | Words per minute (human profile) |
| `--profile <name>` | `human` (default) or `linear` |
| `--delay <ms>` | Fixed delay between keys (linear profile) |
| `--clear` | Clear field first |
| `--return` | Press Return after typing |
| `--tab <n>` | Press Tab N times |
| `--escape` | Press Escape |
| `--on <id>` | Target element ID |
| `--app <name>` | Target application |

**Special sequences:** `\n` (newline), `\t` (tab), `\e` (escape), `\\` (literal backslash).

### `paste` — Atomic Paste Operations

Atomic: saves clipboard, sets content, pastes (Cmd+V), restores clipboard.

```bash
peekaboo paste --text "content" --app TextEdit
peekaboo paste --file-path /path/to/file.txt --app Notes
peekaboo paste --image-path /tmp/screenshot.png --app Messages
peekaboo paste --data-base64 "$BASE64" --uti public.rtf --app TextEdit
peekaboo paste --text "data" --restore-delay-ms 200 --app Safari
```

| Flag | Description |
|------|------------|
| `--text <text>` | Text content |
| `--file-path <path>` | File to paste |
| `--image-path <path>` | Image to paste |
| `--data-base64 <b64>` | Binary data (base64) |
| `--uti <type>` | UTI for binary data (e.g., public.rtf) |
| `--restore-delay-ms <ms>` | Clipboard restore delay |
| `--app <name>` | Target application |

### `press` — Individual Key Presses

```bash
peekaboo press return --app Terminal
peekaboo press tab --count 3 --app Safari
peekaboo press up down left right --app Finder
peekaboo press f1 f2 escape delete --app System\ Preferences
peekaboo press space --delay 100 --hold 50
```

| Flag | Description |
|------|------------|
| `--count <n>` | Repeat count |
| `--delay <ms>` | Delay between presses |
| `--hold <ms>` | Hold duration |
| `--app <name>` | Target application |

### `hotkey` — Keyboard Shortcuts

```bash
peekaboo hotkey --keys "cmd,c" --app TextEdit
peekaboo hotkey --keys "cmd,shift,t" --app Safari
peekaboo hotkey --keys "cmd,w" --hold-duration 100 --app Notes
```

| Flag | Description |
|------|------------|
| `--keys <combo>` | Comma-separated keys (NOT `cmd+w`) |
| `--hold-duration <ms>` | Hold duration |
| `--app <name>` | Target application |

**Important:** Always comma-separated format. System shortcuts may fail -- prefer `menu click --path`.

### `drag` — Drag and Drop

```bash
peekaboo drag --from B1 --to B5 --app Finder
peekaboo drag --from-coords 100,200 --to-coords 400,300
peekaboo drag --from S3 --to-app Trash --space-switch
peekaboo drag --from B2 --to B7 --profile human --modifiers shift
```

| Flag | Description |
|------|------------|
| `--from <id>` | Source element ID |
| `--to <id>` | Target element ID |
| `--from-coords <x,y>` | Source coordinates |
| `--to-coords <x,y>` | Target coordinates |
| `--to-app <name>` | Cross-app target |
| `--space-switch` | Cross-space drag |
| `--profile <name>` | `human` for natural movement |
| `--modifiers <keys>` | Modifier keys during drag |
| `--app <name>` | Target application |

### `swipe` — Swipe Gestures

```bash
peekaboo swipe --from-coords 100,200 --to-coords 300,400 --duration 1000
peekaboo swipe --from B1 --to B5 --profile human --steps 20
```

| Flag | Description |
|------|------------|
| `--from-coords <x,y>` | Start coordinates |
| `--to-coords <x,y>` | End coordinates |
| `--from <id>` / `--to <id>` | Element IDs |
| `--duration <ms>` | Swipe duration |
| `--profile <name>` | Movement profile |
| `--steps <n>` | Interpolation steps |

### `move` — Mouse Movement

```bash
peekaboo move 500,300 --smooth --duration 800
peekaboo move --id B3 --profile human
peekaboo move --center
```

| Flag | Description |
|------|------------|
| `<x,y>` | Target coordinates |
| `--id <id>` | Target element ID |
| `--smooth` | Smooth movement |
| `--duration <ms>` | Movement duration |
| `--profile <name>` | Movement profile |
| `--center` | Move to screen center |

### `scroll` — Scrolling

```bash
peekaboo scroll --direction down --amount 5 --app Safari
peekaboo scroll --direction up --amount 10 --smooth --app Finder
peekaboo scroll --direction right --amount 3 --on S5 --app TextEdit
peekaboo scroll --direction down --amount 8 --delay 5 --app Finder
```

| Flag | Description |
|------|------------|
| `--direction <dir>` | up, down, left, right |
| `--amount <n>` | Scroll amount |
| `--smooth` | Smooth scrolling |
| `--on <id>` | Target element for scrolling |
| `--delay <ms>` | Delay between scroll steps |
| `--app <name>` | Target application |

---

## App/Window Commands

### `app` — Application Control

```bash
peekaboo app launch Safari --wait-until-ready
peekaboo app launch --bundle-id com.apple.TextEdit
peekaboo app switch --to "Visual Studio Code"
peekaboo app focus --name Terminal
peekaboo app hide --name Slack
peekaboo app unhide --name Finder
peekaboo app quit --name Safari --force
peekaboo app quit --all --except "Finder,Terminal"
peekaboo app relaunch TextEdit --wait 3 --wait-until-ready
peekaboo app switch --cycle
```

| Subcommand | Description |
|-----------|------------|
| `launch <name>` | Launch app (use `--bundle-id` for bundle ID) |
| `switch --to <name>` | Switch to app |
| `focus --name <name>` | Focus app |
| `hide --name <name>` | Hide app |
| `unhide --name <name>` | Unhide app |
| `quit --name <name>` | Quit app (`--force`, `--all`, `--except`) |
| `relaunch <name>` | Quit and relaunch (`--wait <s>`, `--wait-until-ready`) |
| `switch --cycle` | Cycle through apps (Cmd+Tab equivalent) |

### `window` — Window Management

```bash
peekaboo window focus --app Safari --title "GitHub"
peekaboo window focus --window-id 12345
peekaboo window move --app TextEdit --x 100 --y 100
peekaboo window resize --app Safari --width 1200 --height 800
peekaboo window set-bounds --app Terminal --x 0 --y 0 --width 1280 --height 720
peekaboo window close --app Chrome --title "Untitled"
peekaboo window minimize --app Finder
peekaboo window maximize --app Notes
peekaboo window list --app Safari --include-details ids,bounds
```

| Subcommand | Description |
|-----------|------------|
| `focus` | Focus window (`--app`, `--title`, `--window-id`) |
| `move` | Move window (`--x`, `--y`) |
| `resize` | Resize window (`--width`, `--height`) |
| `set-bounds` | Set position and size |
| `close` | Close window |
| `minimize` / `maximize` | Window state |
| `list` | List windows (`--include-details ids,bounds,off_screen`) |

### `list` — System Information

```bash
peekaboo list apps --json
peekaboo list windows --app Safari --include-details ids,bounds,off_screen
peekaboo list server-status --json
peekaboo list screens --json
peekaboo list permissions --json
```

| Subcommand | Description |
|-----------|------------|
| `apps` | Running applications |
| `windows` | Application windows |
| `server-status` | Server status and capabilities |
| `screens` | Display information |
| `permissions` | Permission status |

### `menu` — Menu Interaction

```bash
peekaboo menu click --app TextEdit --path "File > Save As..."
peekaboo menu click --app Safari --path "View > Developer > Inspect Element"
peekaboo menu click --app Finder --item "New Folder"
peekaboo menu list --app Chrome --json
peekaboo menu list-all --json
peekaboo menu click-extra --title "WiFi"
```

| Subcommand | Description |
|-----------|------------|
| `click --path <path>` | Navigate menu path (preferred over hotkeys) |
| `click --item <name>` | Click menu item by name |
| `list` | List app menus |
| `list-all` | List all menus |
| `click-extra --title <name>` | Click system menu extra |

### `dialog` — Dialog Management

```bash
peekaboo dialog list --app TextEdit --window-title "Save"
peekaboo dialog click --button "OK" --app Safari
peekaboo dialog click --button "default" --app TextEdit
peekaboo dialog input --text "password123" --field "Password" --clear --app System\ Preferences
peekaboo dialog file --path /Users/<username>/Documents --name "report.pdf" --select Save --app TextEdit
peekaboo dialog file --path /tmp --ensure-expanded --select default --app Pages
peekaboo dialog dismiss --app Notes
peekaboo dialog dismiss --force --app Safari
```

| Subcommand | Description |
|-----------|------------|
| `list` | List dialog elements |
| `click --button <name>` | Click dialog button (`"default"` for default button) |
| `input` | Type into dialog field (`--text`, `--field`, `--clear`) |
| `file` | File dialog navigation (`--path`, `--name`, `--select`, `--ensure-expanded`) |
| `dismiss` | Dismiss dialog (`--force` sends Escape) |

### `dock` — Dock Interaction

```bash
peekaboo dock launch Safari
peekaboo dock right-click --app Finder --select "New Window"
peekaboo dock hide
peekaboo dock show
peekaboo dock list --include-all --json
```

| Subcommand | Description |
|-----------|------------|
| `launch <name>` | Launch from dock |
| `right-click` | Right-click dock item (`--select <menu item>`) |
| `hide` / `show` | Toggle dock visibility |
| `list` | List dock items (`--include-all`) |

### `menubar` — Menu Bar Items

```bash
peekaboo menubar list --json
peekaboo menubar click "Wi-Fi"
peekaboo menubar click --index 3 --verify
peekaboo menubar list --include-raw-debug --json
```

| Subcommand | Description |
|-----------|------------|
| `list` | List menu bar items (`--include-raw-debug`) |
| `click <name>` | Click menu bar item by name or `--index` |

### `space` — Spaces Management

```bash
peekaboo space list --detailed --json
peekaboo space switch --to 2
peekaboo space move-window --app Safari --to 3
peekaboo space move-window --app Terminal --to-current
peekaboo space move-window --app TextEdit --to 2 --follow
peekaboo space move-window --app Chrome --window-title "GitHub" --to 4
```

| Subcommand | Description |
|-----------|------------|
| `list` | List spaces (`--detailed`) |
| `switch --to <n>` | Switch to space |
| `move-window` | Move window between spaces (`--to`, `--to-current`, `--follow`, `--window-title`) |

---

## System Commands

### `open` — File and URL Operations

```bash
peekaboo open "https://example.com" --app Safari --wait-until-ready
peekaboo open ~/Documents/report.pdf --app Preview --no-focus
peekaboo open myfile.txt --bundle-id com.apple.TextEdit
```

| Flag | Description |
|------|------------|
| `--app <name>` | Open with specific app |
| `--bundle-id <id>` | Open with bundle ID |
| `--wait-until-ready` | Wait for app to be ready |
| `--no-focus` | Don't focus the app |

### `clipboard` — Clipboard Operations

```bash
peekaboo clipboard get
peekaboo clipboard set --text "Hello World"
peekaboo clipboard set --file-path /path/to/document.pdf
peekaboo clipboard set --image-path /tmp/screenshot.png
peekaboo clipboard load --file-path /path/file.txt
peekaboo clipboard --action set --data-base64 "$BASE64" --uti public.rtf --also-text "fallback"
peekaboo clipboard save --slot backup
peekaboo clipboard restore --slot backup
peekaboo clipboard set --text "content" --verify --allow-large --prefer text/plain
```

| Subcommand/Flag | Description |
|----------------|------------|
| `get` | Read clipboard |
| `set --text <text>` | Set text content |
| `set --file-path <path>` | Set file content |
| `set --image-path <path>` | Set image content |
| `load --file-path <path>` | Shortcut for set --file-path |
| `--action set` | Action flag format (alternative syntax) |
| `--data-base64 <b64>` | Binary data |
| `--uti <type>` | UTI for binary data |
| `--also-text <text>` | Fallback text alongside binary |
| `save --slot <name>` | Save to named slot |
| `restore --slot <name>` | Restore from slot |
| `--verify` | Verify after set |
| `--allow-large` | Allow large payloads |
| `--prefer <type>` | Preferred content type |

### `clean` — System Maintenance

```bash
peekaboo clean --older-than 24
peekaboo clean --all-snapshots
peekaboo clean --snapshot abc-123
peekaboo clean --dry-run --older-than 48
```

| Flag | Description |
|------|------------|
| `--older-than <hours>` | Remove snapshots older than N hours |
| `--all-snapshots` | Remove all snapshot data |
| `--snapshot <id>` | Remove specific snapshot |
| `--dry-run` | Preview without deleting |

### `permissions` — Permission Management

```bash
peekaboo permissions status --json
peekaboo permissions grant
```

### `bridge` — Bridge Connectivity

```bash
peekaboo bridge status --json
peekaboo bridge status --no-remote
peekaboo bridge status --bridge-socket ~/custom/bridge.sock
```

### `config` — Configuration Management

```bash
peekaboo config show --json
peekaboo config edit
peekaboo config init
peekaboo config validate
peekaboo config add-provider ui-tars --type openai --base-url http://127.0.0.1:8080
peekaboo config list-providers --json
peekaboo config test-provider ui-tars
peekaboo config models-provider
peekaboo config remove-provider
peekaboo config set-credential openai --api-key "$OPENAI_API_KEY"
peekaboo config login anthropic
```

### `daemon` — Daemon Management

```bash
peekaboo daemon start
peekaboo daemon status --json
peekaboo daemon stop
```

### `run` — Script Execution

```bash
peekaboo run script.peekaboo.json --output results.json
peekaboo run workflow.peekaboo.json --no-fail-fast --verbose
```

### `sleep` — Timing Control

```bash
peekaboo sleep 1000    # 1 second
peekaboo sleep 500     # 500 milliseconds
```

### `visualizer` — Visual Feedback

```bash
peekaboo visualizer --json
```

Exercise visual feedback animations for debugging.

---

## AI Commands

### `agent` — Natural Language Automation

```bash
peekaboo agent "Open Safari and navigate to apple.com"
peekaboo agent "Take screenshot and save to Desktop" --model gpt-5.1 --max-steps 10
peekaboo agent "Task description" --queue-mode one-at-a-time
peekaboo agent "Set up TextEdit document" --dry-run
peekaboo agent --resume
peekaboo agent --resume-session SESSION_ID
peekaboo agent --chat
peekaboo agent --list-sessions
```

| Flag | Description |
|------|------------|
| `--model <name>` | AI model (gpt-5.1, claude-opus-4-5, gemini-3-flash) |
| `--max-steps <n>` | Maximum automation steps |
| `--dry-run` | Plan without executing |
| `--resume` | Resume last session |
| `--resume-session <id>` | Resume specific session |
| `--chat` | Interactive chat mode |
| `--queue-mode <mode>` | Queue mode (one-at-a-time) |
| `--list-sessions` | List saved sessions |
| `--no-cache` | Skip session cache |
| `--audio` | Microphone input |
| `--audio-file <path>` | Audio file input |

**API keys:** `OPENAI_API_KEY` env var, or `~/.peekaboo/credentials`, or `peekaboo config login`.

### `learn` — Self-Documenting Reference

```bash
peekaboo learn
```

Outputs the canonical built-in reference prompt. Workers can run this themselves for the most up-to-date command documentation.

---

## MCP Server Mode

21 tools via `peekaboo mcp serve`:

| Category | Tools |
|----------|-------|
| Vision | see, image, analyze, capture |
| Interaction | click, type, hotkey, drag, swipe, move, scroll |
| System | app, window, space, menu, dialog, dock, clipboard |
| Utilities | sleep, permissions, list |
