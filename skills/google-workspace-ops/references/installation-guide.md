# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Homebrew** (macOS package manager)
- **Google Cloud project** with APIs enabled (one-time setup, free, no billing required)
- **OAuth credentials JSON** downloaded from Google Cloud Console

## Claude Code Installation

Path: `.claude/skills/google-workspace-ops/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/google-workspace-ops /path/to/your-project/.claude/skills/google-workspace-ops
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
  echo "<!-- fieldwork-skill:google-workspace-ops -->"
  cat /tmp/fieldwork/skills/google-workspace-ops/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Add the Homebrew tap and install gog CLI

```bash
brew tap steipete/tap
brew install gogcli
```

### Step 2: Verify the CLI is installed

```bash
gog version
```

Should print something like "gog version 0.x.x".

If `command not found`: run `eval "$(/opt/homebrew/bin/brew shellenv)"` (Apple Silicon) or `eval "$(/usr/local/bin/brew shellenv)"` (Intel Mac), then retry.

### Step 3: Connect your Google account (one-time, ~10-15 min)

This requires a Google Cloud project with OAuth credentials. The full process with screenshots is in [auth-setup.md](auth-setup.md).

1. Create a Google Cloud project (free, no billing required)
2. Enable the Google APIs you need (Gmail, Calendar, Drive, etc.)
3. Download a credentials JSON file from the Google Cloud Console
4. Run:
```bash
gog login YOUR_EMAIL --services all
```

### Step 4: Verify authentication

```bash
gog auth status
```

Should show your email address and active auth status.

## Verification

```bash
# Check CLI version
gog version

# Check auth status
gog auth status

# Quick test: list recent emails (read-only, safe)
gog gmail search "is:unread" --max 3 --json --no-input
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `brew: command not found` | Install Homebrew from [https://brew.sh](https://brew.sh), restart terminal |
| `No available formula with the name "gogcli"` | Run `brew tap steipete/tap` first, then `brew install gogcli` |
| `gog: command not found` | Add Homebrew to PATH: `eval "$(/opt/homebrew/bin/brew shellenv)"` then restart terminal |
| `auth_required` | Run `gog login YOUR_EMAIL --services all` and complete browser consent |
| `invalid_grant` | Remove and re-add: `gog auth remove YOUR_EMAIL` then `gog login YOUR_EMAIL --services all` |
| `config` (exit 10) | No OAuth credentials JSON. Download from Google Cloud Console, run `gog auth credentials set FILE.json` |

## Platform Notes

- **macOS:** Primary instructions above work as written (`brew tap` + `brew install`).
- **Linux:** Either install [Linuxbrew](https://brew.sh) and follow the same steps, or build from source -- see the [gogcli repo](https://github.com/steipete/gogcli).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
