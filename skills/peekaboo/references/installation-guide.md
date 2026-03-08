# Peekaboo Installation Guide

Detailed setup instructions for AI coding agents. Follow these steps to go from zero to a working peekaboo automation setup.

## Prerequisites

- **macOS 13 (Ventura) or later**
- **Homebrew**
- **Terminal or AI coding agent runtime** (Claude Code, Codex CLI, etc.)
- **jq** (for JSON parsing)

Install `jq` if needed:

```bash
brew install jq
```

## Step 1: Install peekaboo CLI

Install peekaboo from the Homebrew tap:

```bash
brew install AugustDev/formulae/peekaboo
```

Verify installation:

```bash
peekaboo --version
```

Expected: version string in the `3.0.x` range.

## Step 2: Grant macOS permissions

Peekaboo needs both Accessibility and Screen Recording access for the app that runs commands (Terminal, iTerm, VS Code terminal, Claude Code host app, etc.).

1. Open `System Settings > Privacy & Security > Accessibility`
2. Add and enable your terminal/IDE app
3. Open `System Settings > Privacy & Security > Screen Recording`
4. Add and enable the same app

Important:

- Grant both permissions to the exact process host you are using.
- Restart that app after granting permissions, or AX checks can continue to fail.

## Step 3: Start the peekaboo daemon

For current shell session:

```bash
peekaboo daemon run --mode manual &
```

Confirm daemon process:

```bash
pgrep -fl "peekaboo daemon"
```

### Optional: Persistent daemon with launchd

Resolve the installed peekaboo path first:

```bash
PEEKABOO_BIN="$(command -v peekaboo)"
echo "$PEEKABOO_BIN"
```

Create a LaunchAgent file:

```bash
mkdir -p ~/Library/LaunchAgents
PEEKABOO_BIN="$(command -v peekaboo)"
cat > ~/Library/LaunchAgents/com.peekaboo.daemon.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.peekaboo.daemon</string>
    <key>ProgramArguments</key>
    <array>
      <string>__PEEKABOO_BIN__</string>
      <string>daemon</string>
      <string>run</string>
      <string>--mode</string>
      <string>manual</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/peekaboo-daemon.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/peekaboo-daemon.err.log</string>
  </dict>
</plist>
PLIST
sed -i '' "s|__PEEKABOO_BIN__|$PEEKABOO_BIN|g" ~/Library/LaunchAgents/com.peekaboo.daemon.plist
```

Load and start:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.peekaboo.daemon.plist
launchctl enable gui/$(id -u)/com.peekaboo.daemon
launchctl kickstart -k gui/$(id -u)/com.peekaboo.daemon
```

Check status:

```bash
launchctl print gui/$(id -u)/com.peekaboo.daemon | head -n 40
```

To stop/remove later:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.peekaboo.daemon.plist
rm -f ~/Library/LaunchAgents/com.peekaboo.daemon.plist
```

## Step 4: Install the skill

Use one of these installation paths.

### Claude Code style (`.claude/skills`)

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /path/to/fieldwork-skills/skills/peekaboo /path/to/your-project/.claude/skills/peekaboo
```

### Codex CLI style (`AGENTS.md`)

Codex reads the project root `AGENTS.md`. If your peekaboo skill bundle includes `SKILL.md`, append it:

```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:peekaboo -->"
  cat /path/to/fieldwork-skills/skills/peekaboo/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

If your local bundle does not include `SKILL.md`, install from a source that does, or copy the equivalent runbook content into `AGENTS.md`.

## Step 5: Configure the wrapper

The `peekaboo-safe.sh` wrapper adds timeout protection and retry-safe process cleanup around peekaboo calls. Make scripts executable:

```bash
cd /path/to/your-project/.claude/skills/peekaboo
chmod +x scripts/*.sh
```

Recommended usage pattern:

```bash
./scripts/peekaboo-safe.sh see --app "Safari" --json
```

Optional wrapper tuning:

```bash
export PEEKABOO_TIMEOUT=30
export PEEKABOO_MAX_AGE=60
```

## Step 6: Verify installation

Run health check from the skill root:

```bash
./scripts/health-check.sh
```

Minimum pass criteria:

- `cli_exists=true`
- `accessibility_granted=true`
- `ax_test_success=true`

Suggested machine check:

```bash
./scripts/health-check.sh | jq -e '.cli_exists == true and (.accessibility_granted == true or .accessibility_granted == "true") and .ax_test_success == true'
```

Exit code `0` means healthy.

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `Permission denied` / AX interaction failures | Accessibility not granted to the active app | Re-grant Accessibility in System Settings and restart terminal/IDE |
| `daemon_running=false` or commands hang | Daemon not running | Start it: `peekaboo daemon run --mode manual &` |
| Window mode returns empty/partial data | Beta3 window-mode bug | Use `--mode screen` workflows |
| `ax_test_success=false` right after granting permissions | Host app still using old TCC state | Fully quit and reopen the terminal/IDE |
| `jq_not_found` | jq missing | `brew install jq` |
| `display_connected=false` on headless Mac | No active display | Attach display or HDMI dummy plug |

## Environment Variables (Optional)

| Variable | Default | When to set |
|---|---|---|
| `PEEKABOO_RETINA_SCALE` | `2.0` | Set `1.0` for non-Retina displays |
| `OPENAI_API_KEY` | not set | Required only for `agent` mode (VLM-guided automation) |

Example:

```bash
export PEEKABOO_RETINA_SCALE=2.0
# Only needed for agent mode:
export OPENAI_API_KEY="your_key_here"
```

## Optional: Local VLM Server for Vision Fallback

Peekaboo's `see` command uses a hybrid approach: AX tree first (fast, structured, zero cost), then screenshot-based VLM analysis as fallback when AX data is insufficient. The VLM fallback requires a running vision-language model server.

**What you lose without it:** AX-only mode still works for most automation — you get element trees, clickable targets, and text extraction. Without VLM, you lose the ability to interpret visual layout, read non-AX content (images, canvas elements, custom-rendered UI), and recover from AX tree gaps.

**Recommended: MLX-based local VLM (Apple Silicon Macs)**

Install the MLX VLM server:

```bash
pip install mlx-vlm
```

Start the server:

```bash
python3 -m mlx_vlm.server --model mlx-community/Qwen2.5-VL-7B-Instruct-8bit --port 8080
```

Peekaboo discovers the VLM server via its config. Set the endpoint:

```bash
peekaboo config set vlm_endpoint http://localhost:8080/v1
```

**Memory considerations:** The 7B model requires ~8GB RAM. On machines with limited memory, use a smaller model or cap allocation:

```bash
export MLX_METAL_MEMORY_LIMIT=8589934592  # 8GB cap
```

**Alternative: Remote VLM via OpenAI-compatible API**

Any OpenAI-compatible vision API works. Set the endpoint and API key:

```bash
peekaboo config set vlm_endpoint https://api.openai.com/v1
export OPENAI_API_KEY="your_key_here"
```

**Verification:**

```bash
# Test VLM integration
peekaboo see --app "Finder" --vlm --json | jq '.vlm_used'
```

If `vlm_used` is `true`, the VLM path is working. If `false`, peekaboo fell back to AX-only (which may still be sufficient for the task).

## Quick Start Checklist

1. `brew install AugustDev/formulae/peekaboo jq`
2. Grant Accessibility + Screen Recording, then restart terminal/IDE
3. `peekaboo daemon run --mode manual &`
4. Install skill folder into `.claude/skills/peekaboo` (or append runbook to `AGENTS.md`)
5. `chmod +x scripts/*.sh`
6. `./scripts/health-check.sh`

When health check is healthy, proceed with `./scripts/peekaboo-safe.sh` for all automation calls.
