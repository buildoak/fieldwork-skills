# peekaboo-ops Patterns

Practical patterns for native macOS UI automation with `peekaboo`.

## FSM Pattern (Finite State Machine)

All peekaboo workflows should follow the FSM pattern for reliability:

```
PREFLIGHT → CLASSIFY_TARGET → ACQUIRE_WINDOW → WAIT_FOR_UI_STABLE →
DISCOVER → INTERACT → VERIFY → EXTRACT → CLEANUP → DONE

Error paths: any_state → RECOVER → HUMAN_HANDOFF or ABORT
```

### FSM Implementation Template
```bash
current_state="PREFLIGHT"
retry_count=0
max_retries=3

fsm_transition() {
    local new_state="$1"
    echo "FSM: $current_state → $new_state"
    current_state="$new_state"
    retry_count=0
}

fsm_retry() {
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        fsm_transition "HUMAN_HANDOFF"
        return 1
    fi
    echo "FSM: Retry $retry_count/$max_retries in state $current_state"
    return 0
}
```

## Tier Routing Pattern

Route interactions based on target type:

```bash
route_interaction() {
    local target="$1"

    if is_native_macos_ui "$target"; then
        use_ax_interaction  # click --on B1, type
    elif is_web_form_field "$target"; then
        use_safari_js_injection  # osascript JavaScript
    elif is_web_button "$target"; then
        use_coordinate_click  # click --coords X,Y --no-auto-focus
    elif is_system_dialog "$target"; then
        use_ax_with_no_auto_focus  # click --on B1 --no-auto-focus
    else
        escalate_to_human
    fi
}
```

## Token-Efficient Reconnaissance Pattern

Optimize for cost by using analysis before expensive operations:

```bash
token_efficient_discovery() {
    local app="$1"

    # CHEAP: Quick state analysis (100 tokens)
    state=$(peekaboo-safe.sh see --analyze "What type of window is currently visible?" --app "$app")

    case "$state" in
        *"login"*|*"authentication"*)
            # MEDIUM: Get form structure (600 tokens)
            peekaboo-safe.sh see --app "$app" --json --path /tmp/peekaboo/
            ;;
        *"error"*|*"warning"*)
            # EXPENSIVE: Visual confirmation needed (1400 tokens)
            peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/error.png
            ;;
        *)
            # Continue with cheap analysis
            ;;
    esac
}
```

## Evidence Collection Pattern

Maintain audit trail for debugging and verification:

```bash
collect_evidence() {
    local step="$1"
    local evidence_dir="/tmp/peekaboo/evidence"

    mkdir -p "$evidence_dir"

    # Before state
    peekaboo-safe.sh see --app "$APP_NAME" --json > "$evidence_dir/${step}-before.json"
    peekaboo-safe.sh image --mode screen --path "$evidence_dir/${step}-before.png"

    # Perform action
    "$@"  # Execute the actual command

    # After state
    peekaboo-safe.sh see --app "$APP_NAME" --json > "$evidence_dir/${step}-after.json"
    peekaboo-safe.sh image --mode screen --path "$evidence_dir/${step}-after.png"

    # Decision log
    echo "Step: $step" > "$evidence_dir/${step}-decision.md"
    echo "Command: $*" >> "$evidence_dir/${step}-decision.md"
    echo "Timestamp: $(date)" >> "$evidence_dir/${step}-decision.md"
}
```

## AX Discovery

Start every flow with:

```bash
peekaboo see --app AppName --json --annotate --path /tmp/peekaboo/
```

This returns a `snapshot_id` plus element IDs in B1/T2/S3 format. Always capture the snapshot ID for subsequent clicks.

```bash
# Capture snapshot for ID-based interaction
result=$(peekaboo see --app AppName --json --path /tmp/peekaboo/)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id')
```

**Element ID format:** B1 (button), T2 (text field), S3 (static text), M4 (menu), I5 (image), L6 (link), C7 (checkbox), R8 (radio button).

Selection priority:
1. `role + label` via element ID + `--snapshot`
2. `role + value`
3. position/bounds
4. coordinates fallback (`--coords x,y`)

## AX Role Map

| Role | UI Type | Action |
|---|---|---|
| `AXButton` | button/toggle | `click --on B1 --snapshot $SID` |
| `AXTextField` | editable field | click + `type/paste` |
| `AXStaticText` | label/read-only | verify |
| `AXMenuButton` | menu trigger | `click --on M1 --snapshot $SID` |
| `AXScrollArea` | scroll region | `scroll --direction --amount` |
| `AXDialog` / `AXSheet` | modal UI | `click --on B1 --no-auto-focus` |
| `AXWebArea` | embedded browser | see safari-workarounds.md or handoff to browser-ops |

## Focus Pattern

```bash
peekaboo app switch --to AppName
peekaboo list windows --app AppName --json
peekaboo window focus --window-title "Target" --app AppName
peekaboo see --app AppName --json --path /tmp/peekaboo/
```

Always `app switch --to` before any interaction. Never assume focus persists.

## Interaction Patterns

### Click (ID-based, preferred)

```bash
# Standard click -- always with snapshot
sid=$(peekaboo see --app AppName --json | jq -r '.snapshot_id')
peekaboo click --on B5 --snapshot "$sid" --app AppName

# Dialog/sheet click -- add --no-auto-focus
peekaboo click --on B3 --no-auto-focus --app AppName

# Query-based click -- fuzzy text matching
peekaboo click --query "Submit" --app AppName

# Coordinate fallback -- last resort only
peekaboo click --coords 640,420 --app AppName
```

### Hotkeys

```bash
# Comma-separated with --keys flag
peekaboo hotkey --keys "cmd,w" --app AppName
peekaboo hotkey --keys "cmd,shift,s" --app AppName

# Prefer menu paths -- hotkeys can map to unexpected actions
peekaboo menu click --path "File > Save As..." --app AppName
```

### Scroll

```bash
peekaboo scroll --direction down --amount 5 --app AppName
peekaboo scroll --direction down --amount 10 --smooth --app AppName
peekaboo scroll --direction down --amount 5 --on S3 --app AppName  # targeted scroll
```

### Drag and drop

```bash
# Element-based drag
peekaboo drag --from B1 --to B5 --app AppName

# Coordinate-based drag
peekaboo drag --from-coords "300,300" --to-coords "500,300" --app AppName
```

### Clipboard

```bash
peekaboo clipboard -a set --text "content to copy"
peekaboo clipboard -a get

# Slot-based save/restore for preserving user clipboard
peekaboo clipboard save --slot backup
# ... work with clipboard ...
peekaboo clipboard restore --slot backup
```

### URL navigation

```bash
peekaboo open "https://example.com" --app Safari
```

### Text input matrix

| Input Type | Method |
|---|---|
| short field | `type` |
| long content | `paste` |
| sensitive input | `type` |
| input + submit | `type --return` |

Example:

```bash
peekaboo app switch --to AppName
peekaboo click --on T3 --snapshot "$sid" --app AppName
peekaboo type "query" --return --profile human --app AppName
```

## Agent Mode Pattern

For complex multi-step tasks, agent mode can plan and execute autonomously:

```bash
# Natural language workflow
export OPENAI_API_KEY="your-key"
peekaboo agent "Open TextEdit, create new document, type 'Hello World', and save as hello.txt to Desktop"

# Dry run to preview plan without executing
peekaboo agent "Set up TextEdit document" --dry-run

# Resume interrupted session
peekaboo agent --resume --max-steps 5

# Interactive chat for iterative tasks
peekaboo agent --chat
```

Use agent mode when: task is multi-step, natural language is easier than scripting, or error recovery matters. Use manual primitives when: precision matters, you need exact timing, or agent mode is overkill.

## Live Capture Pattern

```bash
# Start live capture with change detection
peekaboo capture live --mode screen --duration-seconds 30 --output-dir /tmp/capture/ --highlight-changes

# Process recorded video
peekaboo capture video --input recording.mp4 --output-dir /tmp/frames/ --max-frames 100
```

## Spaces Pattern

```bash
# List all spaces
peekaboo space list --detailed --json

# Move window to different space and follow
peekaboo space move-window --app Safari --to 3 --follow

# Switch between spaces
peekaboo space switch --to 2
```

## Menu Navigation Pattern (Preferred over Hotkeys)

```bash
peekaboo app switch --to TextEdit
peekaboo menu click --app TextEdit --path "File > Save As..."
peekaboo dialog file --path ~/Documents --name "document.txt" --select Save
```

## File Dialog Pattern

```bash
# Ensure expanded dialog for button visibility (compact mode hides buttons)
peekaboo dialog file --app TextEdit --path /Users/<username>/Documents --ensure-expanded --select default
```

## AX Label Gotchas

Labels in the AX tree do not always match visible text. Always discover first.

| Visible text | AX label | Identifier | Notes |
|---|---|---|---|
| "Don't Save" | "Delete" | `DontSaveButton` | Use ID, not label |
| Save As (Cmd+Shift+S) | Duplicate | - | TextEdit maps this differently. Use `menu click --path` |
| "About This Mac" | - | - | Apple menu, not app menu. Not addressable via `menu click --path "AppName > ..."` |
| Compact dialog buttons | Hidden | - | Save/Cancel not in AX tree when sheet is compact |

## Verification Patterns

```bash
peekaboo see --app AppName --json --path /tmp/peekaboo/ > /tmp/peekaboo/before.json
sid=$(jq -r '.snapshot_id' /tmp/peekaboo/before.json)
peekaboo click --on B5 --snapshot "$sid" --app AppName
sleep 1
peekaboo see --app AppName --json --path /tmp/peekaboo/ > /tmp/peekaboo/after.json
```

```bash
peekaboo see --app AppName --json \
  | jq '.elements[] | select(.role=="AXButton" and .label=="Save")'
```

## Screenshot Pattern

```bash
# Always --mode screen, always --path
mkdir -p /tmp/peekaboo
peekaboo image --mode screen --path /tmp/peekaboo/evidence.png
peekaboo image --mode screen --path /tmp/peekaboo/app-state.png --app AppName

# Annotated screenshots for debugging
peekaboo see --app AppName --annotate --path /tmp/peekaboo/debug.png
```

Never omit `--path` -- files land on Desktop or CWD. Never use `--mode window` -- returns 698B stubs in beta3.

## Recovery Snippet

```bash
peekaboo app switch --to AppName
peekaboo see --app AppName --json --path /tmp/peekaboo/
./scripts/health-check.sh
```
