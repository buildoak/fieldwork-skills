# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Node.js 18+** (JavaScript runtime for agent-browser)
- **npm** (bundled with Node.js)
- Optional: **Python 3.10+** (only for AgentMail email verification flows)

## Claude Code Installation

Path: `.claude/skills/browser-ops/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/browser-ops /path/to/your-project/.claude/skills/browser-ops
```

## Codex CLI Installation

Codex reads `AGENTS.md` only (not `codex.md`, not `.codex/skills/`).

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Append `SKILL.md` to your project `AGENTS.md` with a marker:
```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:browser-ops -->"
  cat /tmp/fieldwork/skills/browser-ops/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Install agent-browser

The browser automation server that provides the 25 browser tools.

```bash
npm install -g @anthropic-ai/agent-browser
```

If you see `EACCES` / "Permission denied": run `sudo npm install -g @anthropic-ai/agent-browser` instead.

**Minimum version:** `agent-browser >= 0.10.0` required. v0.9.1 has a critical Playwright hang bug.

### Step 2: Start the daemon

The browser daemon must be running before your agent can use browser tools.

```bash
agent-browser start
```

### Step 3 (Optional): AgentMail for email verification flows

Only needed for signup flows that require email verification (OTP codes, confirmation links).

```bash
python3 -m pip install agentmail
```

Get your API key at [https://agentmail.to](https://agentmail.to) (free tier available).

Alternatively, run the bundled setup:
```bash
./scripts/agentmail.sh setup
```

## Verification

Run these commands to confirm everything works:

```bash
# Check agent-browser is installed (should print 0.10.0 or higher)
agent-browser --version

# Check the daemon is running (should show "running" and a port number)
agent-browser status

# Full health check (CLI + daemon + stealth + agentmail)
./scripts/browser-check.sh

# Quick check (just CLI + daemon)
./scripts/browser-check.sh quick
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npm ERR! code EACCES` | Run with `sudo`: `sudo npm install -g @anthropic-ai/agent-browser` |
| `agent-browser: command not found` | Add npm bin to PATH: `export PATH="$(npm config get prefix)/bin:$PATH"` then restart terminal |
| `agent-browser status` shows "not running" | Start the daemon: `agent-browser start` |
| `Error: listen EADDRINUSE` | Another process is using the port. Run `agent-browser stop` then `agent-browser start` |
| `node: command not found` | Install Node.js 18+ from [https://nodejs.org](https://nodejs.org) or `brew install node` |
| Codex sandbox blocks browser socket | Use `--sandbox danger-full-access` (`--full` in agent-mux). The Unix socket requires full access. |

## Platform Notes

- **macOS:** Primary instructions above work as written. Use `brew install node` if you prefer Homebrew.
- **Linux:** Same steps. Install Node.js via your package manager (`sudo apt install -y nodejs npm` on Ubuntu/Debian, `sudo dnf install -y nodejs npm` on Fedora).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
