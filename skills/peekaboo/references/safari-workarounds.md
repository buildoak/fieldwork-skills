# Safari Workarounds

Safari-specific bugs and canonical workarounds for peekaboo automation. Updated 2026-02-22.

---

## Core Problem

Safari's web content lives inside `AXWebArea` role elements in the AX tree. Peekaboo can discover these elements but interaction is unreliable:

1. **AX click on web forms opens Start Page tab** instead of clicking the element
2. **`peekaboo type` targets the URL bar**, not form fields inside web content
3. **`see` can timeout** on complex web pages without a vision provider (UI-TARS)

## Canonical Safari Flow

For any Safari web page interaction, follow this exact sequence:

### 1. Navigate via `open`

```bash
peekaboo open "https://example.com/form" --app Safari
sleep 2  # wait for page load
```

Never type URLs into the address bar. Always use `peekaboo open`.

### 2. Discover via `see`

```bash
peekaboo see --app Safari --json --path /tmp/peekaboo/
```

This works for AX tree discovery. Note that web elements appear under AXWebArea nodes.

### 3. Fill Forms via JavaScript Injection

The canonical method for Safari form filling is AppleScript JS injection:

```bash
# Single field
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"input[name=username]\").value = \"user\"" in document 1'

# Password field
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"input[name=password]\").value = \"pass\"" in document 1'

# Select dropdown
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"select[name=country]\").value = \"US\"" in document 1'

# Checkbox
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"input[name=agree]\").checked = true" in document 1'

# Trigger change events (needed for React/Vue forms)
osascript -e 'tell application "Safari" to do JavaScript "var el = document.querySelector(\"input[name=field]\"); el.value = \"value\"; el.dispatchEvent(new Event(\"input\", {bubbles: true})); el.dispatchEvent(new Event(\"change\", {bubbles: true}))" in document 1'
```

**Why not `peekaboo type`?** It targets the URL bar, not the focused form field. The AX tree sees web form fields but `type` doesn't route to them correctly.

**Why not `peekaboo paste`?** Same focus routing issue as `type`.

### 4. Click Buttons via Coordinates

AX click on Safari web elements opens a Start Page tab instead of clicking. Use coordinate clicks:

```bash
# Get button position from see output or visual inspection
peekaboo click --coords 400,500 --no-auto-focus --app Safari
```

The `--no-auto-focus` flag is critical -- without it, click commands can trigger focus changes that interfere with the action.

### 5. Verify via Screenshot

```bash
peekaboo image --mode screen --path /tmp/peekaboo/after-submit.png
```

---

## Element ID Format in Safari

Safari web elements use the same B1/T2/S3 format but are nested under AXWebArea:

- Web buttons appear as B-prefixed IDs
- Web text fields appear as T-prefixed IDs
- Web static text appears as S-prefixed IDs

However, **do not trust AX-based click/type for these elements**. Use JS injection for input and coordinates for clicks.

## `see` Timeouts

Safari pages with complex DOMs can cause `see` to timeout (default 10s). Solutions:

1. **Start UI-TARS server** for vision-based discovery:
   ```bash
   python3 -m mlx_vlm server --host 127.0.0.1 --port 8080  # run from your VLM venv
   ```
2. **Increase timeout:** `--timeout-seconds 20`
3. **Use screen mode:** `--mode screen` for less complex parsing

## Complete Safari Workflow Recipe

```bash
# 1. Navigate
peekaboo open "https://example.com/login" --app Safari
sleep 2

# 2. Discover
peekaboo see --app Safari --json --path /tmp/peekaboo/

# 3. Fill form via JS
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"input[name=username]\").value = \"myuser\"" in document 1'
osascript -e 'tell application "Safari" to do JavaScript "document.querySelector(\"input[name=password]\").value = \"mypass\"" in document 1'

# 4. Submit via coordinates
peekaboo click --coords 400,500 --no-auto-focus --app Safari
sleep 2

# 5. Verify
peekaboo image --mode screen --path /tmp/peekaboo/result.png
```

## When to Use browser-ops Instead

If the Safari automation is complex (multi-page flows, dynamic content, iframes), consider using the `browser-ops` skill instead. Peekaboo's Safari workarounds are best for simple form fills and single-page interactions.
