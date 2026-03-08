# peekaboo-ops Failure Reference

Common failure modes and recoveries. Updated from 20-test field validation (2026-02-22).

## Symptom Table

| Symptom | Likely Cause | Immediate Fix |
|---|---|---|
| Empty AX tree | App not frontmost | `peekaboo app switch --to AppName` |
| Empty AX tree | Accessibility missing | `./scripts/health-check.sh` |
| Empty AX tree | No display connected (headless) | Connect HDMI dummy plug, verify with `system_profiler SPDisplaysDataType` |
| Element not found | Stale snapshot — IDs expired | Re-run `peekaboo see --app AppName --json` and get fresh `snapshot_id` |
| Element not found | Wrong window focused | `peekaboo window focus --window-title ... --app AppName` |
| Element not found | ID used without `--snapshot` | Always pass `--snapshot $SID` from preceding `see` |
| Click no effect | Overlay/dialog blocker | Dismiss blocker, retry |
| Click no effect | Coordinate mismatch | Use ID-based click with `--snapshot` |
| Click timeout on dialog | Auto-focus conflict | Add `--no-auto-focus` flag |
| Hotkey fails / Bridge error | Wrong syntax (`cmd+w`) | Use `--keys "cmd,w"` comma-separated format |
| Hotkey fails / Bridge error | System-reserved shortcut | Use `menu click --path` instead |
| `see` timeout (10s) | Complex app without vision provider | Start UI-TARS server, or use AX-only apps |
| Screenshot 698B stub | Window-mode capture bug (beta3) | Always use `--mode screen` |
| Screenshot to wrong path | No `--path` given | Always pass `--path /tmp/peekaboo/` |
| `app launch` fails | App already running | Use `app switch --to` instead |
| Type goes to wrong app | Focus not set before type | `app switch --to` before every `type` |
| Save As = Duplicate | TextEdit maps Cmd+Shift+S to Duplicate | Use `menu click --path "File > Save As..."` |
| "Don't Save" button not found | AX label is "Delete" | Search for label "Delete" or identifier `DontSaveButton` |
| Dialog buttons missing from AX | Compact file dialog mode | Expand dialog or use coordinate click after visual confirmation |
| TCC permission prompt | Native OS dialog — outside AX tree | Cannot automate. Requires human pre-grant |
| Token exhaustion (50+ turns) | Long workflow without checkpoints | Implement budget gates, consider workflow splitting |
| Token exhaustion (100+ turns) | Complex analysis or error loops | Hard checkpoint required before continuing |
| FSM state loop | Retry logic without escape condition | Check max retry counts, implement circuit breaker |
| Daemon file-not-found | Beta3 daemon startup bug | Use `peekaboo daemon run --mode manual &` |
| Chrome window capture (1px strip) | Chrome issue #67 in beta3 | Switch to Safari for automation |

## Bug-Specific FSM Transitions (Beta3)

### Safari AX Click Misfires
- **Symptom**: AX click opens Start Page instead of clicking target
- **Transition**: INTERACT → force coordinate_click path → retry INTERACT
- **Command**: Use `peekaboo-safe.sh click --coords X,Y --no-auto-focus`

### Type Commands Target URL Bar
- **Symptom**: Text appears in Safari URL bar instead of form field
- **Transition**: INTERACT → force js_injection path → retry INTERACT
- **Command**: Use osascript JavaScript injection for web forms

### See Timeouts on Complex Apps
- **Symptom**: `peekaboo see` times out after 10+ seconds
- **Transition**: DISCOVER → start_ui_tars → retry DISCOVER
- **Recovery**: Start UI-TARS server, then retry see command

### Daemon Startup File-Not-Found
- **Symptom**: `peekaboo daemon start` fails with file not found
- **Transition**: PREFLIGHT → manual_daemon_start → retry PREFLIGHT
- **Command**: `peekaboo daemon run --mode manual &`

### Window-Mode Capture 698B Stubs
- **Symptom**: Screenshot files are 698 bytes and corrupted
- **Transition**: Any state using image capture → force screen mode
- **Command**: Always use `--mode screen`, never `--mode window`

### Token Budget Exhaustion
- **Symptom**: High token usage without progress
- **Transition**: Any state → CHECKPOINT_REQUIRED → human approval
- **Gates**: 50 turns (warn), 100 turns (pause), 150+ turns (explicit resume)

## Recovery Procedures

### Empty AX tree

1. `peekaboo app launch AppName` if needed
2. `peekaboo app switch --to AppName`
3. `peekaboo window focus --window-title "Expected" --app AppName`
4. `peekaboo see --app AppName --json --path /tmp/peekaboo/`
5. If still empty: `./scripts/health-check.sh`
6. If headless: verify HDMI dummy plug with `system_profiler SPDisplaysDataType`

### Element not found / Stale snapshot

1. Fresh snapshot: `peekaboo see --app AppName --json --annotate --path /tmp/peekaboo/`
2. Capture `snapshot_id` from output
3. Re-target via `role + label` using fresh `elem_N` IDs
4. Scroll and retry if element may be off-screen
5. Coordinates only as final fallback: `--coords x,y`

### Click timeout on dialogs

1. Add `--no-auto-focus` to the click command
2. If still failing, try coordinate click after visual confirmation
3. For compact file dialogs: buttons may be hidden from AX tree entirely

### Hotkey / Bridge error

1. Verify format: `--keys "cmd,w"` not `cmd+w`
2. If system-reserved (Cmd+Space, Cmd+Tab): use `menu click --path` instead
3. If the shortcut maps to a different action (Cmd+Shift+S in TextEdit): use `menu click --path` for the intended action

### `see` timeout

1. Check if app is a complex webview (Safari, Chrome, Electron)
2. Start UI-TARS server: `python3 -m mlx_vlm server --host 127.0.0.1 --port 8080` (from your VLM virtual environment)
3. Retry `see` — should return results in <1s with vision provider
4. For pure AX apps (Finder, System Settings, TextEdit): `see` works without UI-TARS

### Permission denied

1. System Settings -> Privacy & Security -> Accessibility
2. Enable Terminal/Claude Code
3. Restart terminal session
4. Re-run health-check

### Error recovery (graceful failures)

Peekaboo handles these gracefully — they return error JSON, not crashes:
- Bad element ID: returns "element not found" error
- Missing app: returns "application not found" error
- Expired snapshot: returns "snapshot expired" error

Re-discover and retry. These are not fatal.

## Critical Safety: NEVER run `tccutil reset`

`tccutil reset` resets TCC permissions for ALL apps, not just one. This will brick accessibility permissions for Terminal, Claude Code, and every other app. Use System Settings UI to manage permissions individually. This was a hard-won lesson.

## Escalation Contract

Escalate after 3 retries on the same step.

```json
{"severity":"error|fatal","step":"discover|target|act|verify|fallback","command":"peekaboo ...","evidence":"/tmp/peekaboo/failure.png","next_action":"retry focus recovery or escalate to human after 3 retries"}
```
