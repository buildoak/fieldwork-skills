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

> **Note:** This guide covers the standard setup with a browser available. For headless or SSH environments, see the [Headless / SSH Setup](auth-setup.md#headless--ssh-setup) section in auth-setup.md.

1. Create a Google Cloud project (free, no billing required)
2. Enable the Google APIs you need (Gmail, Calendar, Drive, etc.)
3. **Configure the OAuth consent screen** (required before OAuth will work):
   - Go to **APIs & Services -> OAuth consent screen** in Google Cloud Console
   - Choose **External** (unless you have a Google Workspace org)
   - Fill in app name (e.g., "gogcli"), support email, and developer contact email
   - **Add yourself as a test user** -- without this, OAuth fails with "app not verified"
   - See [auth-setup.md](auth-setup.md#oauth-consent-screen) for full details
4. Create OAuth credentials (Desktop app) and download the credentials JSON file
5. Store the credentials in gogcli:
```bash
gog auth credentials set /path/to/downloaded/credentials.json
```
6. Authorize your account:
```bash
gog login your-email@gmail.com --services all
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

## Credential Management

`GOG_KEYRING_PASSWORD` is required when using the file-based keyring (headless/SSH environments, or when opting out of system keychain). We recommend the [vault skill](../vault/) for managing it securely. For all options -- vault, custom secret managers, or plain export -- see the [Credential Management](auth-setup.md#credential-management) section in auth-setup.md.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `brew: command not found` | Install Homebrew from [https://brew.sh](https://brew.sh), restart terminal |
| `No available formula with the name "gogcli"` | Run `brew tap steipete/tap` first, then `brew install gogcli` |
| `gog: command not found` | Add Homebrew to PATH: `eval "$(/opt/homebrew/bin/brew shellenv)"` then restart terminal |
| `auth_required` | Run `gog login YOUR_EMAIL --services all` and complete browser consent |
| `invalid_grant` | Remove and re-add: `gog logout YOUR_EMAIL` then `gog login YOUR_EMAIL --services all` |
| `config` (exit 10) | No OAuth credentials JSON. Download from Google Cloud Console, run `gog auth credentials set FILE.json` |

## Platform Notes

- **macOS:** Primary instructions above work as written (`brew tap` + `brew install`).
- **Linux:** Either install [Linuxbrew](https://brew.sh) and follow the same steps, or build from source -- see the [gogcli repo](https://github.com/steipete/gogcli).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.

## Next Steps

- [SKILL.md](../SKILL.md) -- usage patterns, decision tree, and approval rules
- [gog-commands.md](gog-commands.md) -- full command reference for all 15 services
- [pipeline-patterns.md](pipeline-patterns.md) -- composable multi-service workflows
