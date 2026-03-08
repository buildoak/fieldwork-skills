# Validated Test Results

Test results from peekaboo 3.0.0-beta3 field validation. Updated 2026-02-22.

---

## Round 1: Basic Operations (8/10 pass)

| Test | Result | Notes |
|------|--------|-------|
| Full screen capture | **PASS** | Always use `--mode screen` |
| App launch/switch | **PASS** | Use `app switch --to`, not bare launch |
| Click by text | **PASS** | Prefers AX elements |
| Menu bar/dock listing | **PASS** | Subcommands required |
| Clipboard operations | **PASS** | Use `-a` flag format |
| Type text | **PASS** | Ensure focus first |
| Window-mode capture | **FAIL** | 698B stubs -- beta3 bug |
| System hotkeys | **FAIL** | System-reserved shortcuts blocked |

**Window-mode capture bug:** `peekaboo image --mode window` returns 698B stub files. Root cause: beta3 regression in window capture. Workaround: always `--mode screen`.

**System hotkeys:** Shortcuts like Cmd+Space, Cmd+Tab are system-reserved and cannot be sent via peekaboo. Use `menu click --path` or `app switch --cycle` for equivalent actions.

## Round 2: Advanced Operations (6/10 pass, 3 partial, 1 caveat)

| Test | Result | Notes |
|------|--------|-------|
| AX tree discovery | **PASS** | B1/T2/S3 format, snapshot tracking works |
| ID-based click | **PASS** | Snapshot mandatory for element resolution |
| Menu navigation | **PARTIAL** | App menus work, Apple menu not addressable |
| Dialog interaction | **PASS** | `--no-auto-focus` required for dialog buttons |
| File dialogs | **PARTIAL** | Compact mode hides buttons from AX tree |
| Scroll operations | **PASS** | Directional, smooth, element targeting all work |
| Safari workflow | **PARTIAL** | `see` timeouts without vision, use workarounds (see safari-workarounds.md) |
| System Settings nav | **PASS** | Full AX tree support |
| Error recovery | **PASS** | Graceful failure handling with error JSON |
| Drag and drop | **PASS** | Coordinate and element support both work |

### Detailed Findings

**Menu navigation (PARTIAL):**
- App menus (`File > Save As...`) work reliably via `menu click --path`
- Apple menu items ("About This Mac") are not addressable via `menu click --path "AppName > ..."`
- System menu extras accessible via `menu click-extra --title`

**File dialogs (PARTIAL):**
- Standard expanded file dialogs work with `dialog file`
- Compact file dialogs hide Save/Cancel buttons from AX tree
- Workaround: `--ensure-expanded` flag or coordinate clicks after visual confirmation

**Safari workflow (PARTIAL):**
- AX discovery works (`see --app Safari --json`)
- Form filling unreliable via AX (use JS injection -- see safari-workarounds.md)
- Button clicks unreliable via AX (use coordinate clicks)
- `see` can timeout on complex pages without UI-TARS vision provider

## New Capabilities Validated (3.0.0-beta3)

### Agent Mode
- Natural language task automation: **WORKS**
- Multi-step planning and execution: **WORKS**
- Session management and resumption: **WORKS**
- Audio input support: **AVAILABLE** (not field-tested)

### Live Capture
- Real-time screen recording: **WORKS**
- Change-aware sampling with diff: **WORKS**
- Video ingestion and frame extraction: **WORKS**
- Motion highlighting: **WORKS**

### Spaces Management
- Virtual desktop listing: **WORKS**
- Space switching: **WORKS**
- Window movement between spaces: **WORKS**
- Follow behavior for transitions: **WORKS**

### Enhanced Dialog Support
- File dialog path navigation: **WORKS**
- Compact dialog detection: **PARTIAL** (buttons hidden)
- Button identification by role: **WORKS**

## AX Label Gotchas (Discovered During Testing)

| Visible Text | AX Label | Identifier | Notes |
|---|---|---|---|
| "Don't Save" | "Delete" | `DontSaveButton` | Use ID, not label |
| Save As (Cmd+Shift+S) | Duplicate | - | TextEdit maps differently. Use `menu click --path` |
| "About This Mac" | - | - | Apple menu, not addressable via `menu click --path` |
| Compact dialog buttons | Hidden | - | Save/Cancel not in AX tree when sheet is compact |
