# Auth Setup Guide

Complete OAuth setup, token management, and multi-account configuration for gogcli.

Terminology:
- **OAuth:** Google's delegated authorization flow that grants API access without sharing passwords.
- **Google Cloud Project (GCP project):** The cloud project where you enable APIs and create OAuth credentials.
- **Keyring:** Secure local credential storage (for example, macOS Keychain).

---

## Prerequisites

1. **Google Cloud Project** with OAuth 2.0 credentials
2. **APIs enabled** in Google Cloud Console for each service you want to use

### Required APIs (enable in Google Cloud Console)

| Service | API Name |
|---------|----------|
| Gmail | Gmail API |
| Calendar | Google Calendar API |
| Drive | Google Drive API |
| Docs | Google Docs API |
| Slides | Google Slides API |
| Sheets | Google Sheets API |
| Contacts | People API |
| Tasks | Google Tasks API |
| Chat | Google Chat API |
| Forms | Google Forms API |
| Classroom | Google Classroom API |
| Apps Script | Apps Script API |
| Groups | Cloud Identity API / Admin SDK |

### OAuth Consent Screen

**CRITICAL:** This step is easy to miss but required before any OAuth flow will work.

1. Go to **APIs & Services** -> **OAuth consent screen** in Google Cloud Console
2. Choose **External** (unless you have a Google Workspace org)
3. Fill in:
   - App name (e.g., "gogcli")
   - User support email (your email)
   - Developer contact email (your email)
4. Click **Save and Continue**
5. **Add yourself as a test user:**
   - Click **Add Users**
   - Enter your Gmail address
   - Click **Save and Continue**

Without adding yourself as a test user, OAuth will fail with "app not verified".

---

## Standard Setup (Laptop / Desktop with Browser)

This is the simplest path. Use this if you have a browser available (the common case).

### 1. Install gogcli

```bash
brew tap steipete/tap
brew install gogcli
```

Verify: `gog version` should print the version number.

### 2. Store OAuth Credentials

Download your OAuth credentials JSON from Google Cloud Console (see Step 1 below), then:

```bash
gog auth credentials set /path/to/downloaded/credentials.json
```

### 3. Set a Keyring Password (optional but recommended)

`gog` stores OAuth tokens in a secure keyring. You can use the system keychain (default on macOS) or set an explicit password for a file-based keyring:

```bash
# Option A: Use macOS Keychain (default, no action needed)
# Tokens are stored in macOS Keychain automatically.

# Option B: Use file-based keyring with explicit password
gog auth keyring file
export GOG_KEYRING_PASSWORD=$(vault.sh get GOG_KEYRING_PASSWORD)  # recommended — see Credential Management below
```

If using Option B, set `GOG_KEYRING_PASSWORD` in your shell profile so it persists across terminal sessions. See [Credential Management](#credential-management) below for all options (vault skill, custom secret manager, or plain export).

**macOS vs Linux:**
- **macOS:** System Keychain works out of the box with a GUI session. Use file-based keyring if you encounter Keychain access issues.
- **Linux:** No system keychain by default. Use `gog auth keyring file` with `GOG_KEYRING_PASSWORD`.

### 4. Authorize Your Account

```bash
gog login your-email@gmail.com --services all
```

A browser window opens automatically. Sign in with your Google account, review the requested permissions, and click **Allow**. The browser redirects back to localhost -- authorization is complete.

### 5. Verify

```bash
# Check auth status
gog auth status

# Quick test: list recent emails (read-only, safe)
gog gmail ls --max 3
```

You should see your email address with active auth status, and a list of recent emails.

---

## Credential Management

`GOG_KEYRING_PASSWORD` is the password that protects the local keyring file where `gog` stores your OAuth tokens. When using the file-based keyring (required for headless/SSH, optional on desktop), every `gog` command needs this password to read and write tokens.

You have three options for managing it, listed from most secure to least:

### Tier 1: Vault Skill (Recommended)

```bash
export GOG_KEYRING_PASSWORD=$(vault.sh get GOG_KEYRING_PASSWORD)
```

The [vault skill](../vault/) encrypts secrets at rest using `age` + `sops`. Secrets never touch disk in plaintext. One-time setup, then all skills in your environment can share the same vault.

To set it up:
1. Install the vault skill and run its setup: `cd path/to/skills/vault && ./scripts/setup.sh`
2. Store the password: `vault.sh set GOG_KEYRING_PASSWORD "your-password-here"`
3. Retrieve it anywhere: `vault.sh get GOG_KEYRING_PASSWORD`

See the [vault skill documentation](../vault/SKILL.md) for full details.

### Tier 2: Your Own Secret Manager

```bash
export GOG_KEYRING_PASSWORD=$(your-secret-manager get GOG_KEYRING_PASSWORD)
# Examples: 1Password CLI, Bitwarden CLI, pass, AWS Secrets Manager, etc.
```

If you already have a secret manager, use it. Same pattern, different backend.

### Tier 3: Plain Export (Least Secure)

```bash
export GOG_KEYRING_PASSWORD="your-password-here"
```

Works but secrets live in shell history and dotfiles. Not recommended for shared machines or CI environments.

---

All three tiers work identically from `gog`'s perspective -- it only cares that the environment variable is set. Choose the tier that fits your security needs.

---

## Headless / SSH Setup

**Problem:** On headless servers or SSH sessions, there is no browser for the OAuth consent flow. Additionally, macOS Keychain silently drops tokens without a GUI session.

**Solution:** Use `--manual` auth flow and file-based keyring.

### 1. Switch to file-based keyring

```bash
gog auth keyring file
export GOG_KEYRING_PASSWORD=$(vault.sh get GOG_KEYRING_PASSWORD)  # see Credential Management above for all options
```

Set `GOG_KEYRING_PASSWORD` in your shell profile so it persists. See [Credential Management](#credential-management) above for all options.

### 2. Pre-flight: Unlock Keychain (macOS only)

On macOS, always run this before any auth flow via SSH:

```bash
security unlock-keychain ~/Library/Keychains/login.keychain-db
```

Without this, token storage can silently fail and produce misleading errors.

### 3. Authenticate with Manual Flow

```bash
gog auth add your-email@gmail.com --services all --manual --force-consent
```

This prints an authorization URL. Copy it, open it in a browser on any device (phone, laptop, etc.), sign in, approve permissions. The browser redirects to `http://localhost/...` -- the page won't load (expected). Copy the entire redirect URL from the browser address bar and paste it back into the terminal.

> **WARNING (gog v0.11.0):** The `--remote --step 2` flow has a state mismatch bug.
> Use the `--manual` pipe method instead:
> ```bash
> echo "PASTE_REDIRECT_URL_HERE" | gog auth add your-email@gmail.com --services all --manual --force-consent
> ```

### 4. Verify

```bash
export GOG_KEYRING_PASSWORD=$(vault.sh get GOG_KEYRING_PASSWORD)  # or your preferred method
gog auth list
gog gmail ls --max 3
```

### Workers and Scripts

Always set `GOG_KEYRING_PASSWORD` when calling `gog` from scripts. See [Credential Management](#credential-management) for all options.

```bash
#!/bin/bash
export GOG_KEYRING_PASSWORD=$(vault.sh get GOG_KEYRING_PASSWORD)  # recommended
gog gmail search "is:unread" --json
gog cal events --today --json
```

---

## Step 1: Create OAuth Credentials

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **Create Credentials** -> **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `gogcli` (or any name)
5. Click **Create**
6. Download the JSON file

## Step 2: Store Credentials in gogcli

```bash
# Store the downloaded credentials JSON
gog auth credentials set /path/to/downloaded/credentials.json

# Verify
gog auth credentials list
```

Credentials are stored at: `~/Library/Application Support/gogcli/credentials.json`

## Step 3: Authorize an Account

```bash
# Authorize with all services
gog login your.email@gmail.com --services all

# This opens a browser for Google OAuth consent
# Grant all requested permissions
# The refresh token is stored in the system keyring
```

### Service-Specific Authorization

If you want minimal permissions:

```bash
# Read-only access
gog login email@gmail.com --services gmail,calendar,drive --readonly

# Specific services only
gog login email@gmail.com --services gmail,calendar

# Available services: user, gmail, calendar, chat, classroom, drive, docs, slides,
#   contacts, tasks, sheets, people, forms, appscript
# Use "all" for everything, "user" for just profile/identity
```

### Drive Scope Options

```bash
# Full Drive access (default)
gog login email@gmail.com --services drive --drive-scope full

# Read-only Drive
gog login email@gmail.com --services drive --drive-scope readonly

# File-only (can only access files created by the app)
gog login email@gmail.com --services drive --drive-scope file
```

### Browserless / Remote Auth

For headless environments or SSH sessions, see the [Headless / SSH Setup](#headless--ssh-setup) section above for the complete walkthrough. Quick reference:

```bash
# Manual flow (recommended for headless)
echo "PASTE_REDIRECT_URL_HERE" | gog auth add email@gmail.com --services all --manual --force-consent
```

> **WARNING (gog v0.11.0):** `--remote --step 2` has a state mismatch bug. Use the `--manual` pipe method shown above.

## Step 4: Verify

```bash
# Check auth status
gog status

# Check authenticated accounts
gog auth list

# Test with a simple command
gog whoami --json
gog cal events --today
```

---

## Token Management

### How Tokens Work

- **Refresh tokens** are stored in the system keyring (macOS Keychain by default)
- **Access tokens** are obtained automatically using the refresh token
- Access tokens expire after ~1 hour; gogcli refreshes them transparently
- Refresh tokens are long-lived but can be revoked by the user or Google

### Keyring Backends

```bash
# Check current backend
gog auth status

# Configure backend
gog auth keyring            # Show current
gog auth keyring auto       # Auto-detect (default)
gog auth keyring keychain   # macOS Keychain explicitly
gog auth keyring file       # File-based (less secure, for CI)
```

### Token Operations

```bash
# List all stored tokens
gog auth tokens list

# Remove a specific account
gog logout email@gmail.com

# Force re-consent (get a fresh refresh token)
gog login email@gmail.com --services all --force-consent
```

### Token Refresh Failures

If you get `auth_required` (exit code 4):

1. Token may be revoked -- re-login: `gog login EMAIL --services all`
2. OAuth app may need re-consent: add `--force-consent`
3. API may not be enabled in Google Cloud Console -- check API dashboard

---

## Multi-Account Setup

```bash
# Add multiple accounts
gog login personal@gmail.com --services all
gog login work@company.com --services all

# Set default account
gog config set default_account work@company.com

# Use specific account per command
gog gmail search "is:unread" -a personal@gmail.com --json
gog cal events --today -a work@company.com --json

# Account aliases
gog auth alias set work work@company.com
gog auth alias set personal personal@gmail.com
# Then use: gog gmail search "is:unread" -a work
```

---

## Named OAuth Clients

For different apps with different scopes:

```bash
# Store a second credentials JSON under a name
gog auth credentials set work-app.json --client work-app

# Login using named client
gog login work@company.com --client work-app --services gmail,calendar

# Use named client in commands
gog gmail search "is:unread" --client work-app --json
```

---

## Service Accounts (Workspace Only)

For Google Workspace domain-wide delegation:

```bash
# Configure service account
gog auth service-account set --key /path/to/service-account.json

# Impersonate a user
gog gmail search "is:unread" --service-account /path/to/sa.json --impersonate user@domain.com

# Google Keep requires special service account setup
gog auth keep --key /path/to/sa.json email@domain.com
```

---

## Configuration

```bash
# List all config
gog config list

# Key settings
gog config set default_account email@gmail.com
gog config get default_account

# Config file location
gog config path
# -> ~/Library/Application Support/gogcli/config.json

# Available config keys
gog config keys
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `OAuth client credentials missing` (exit 10) | Download credentials JSON from Google Cloud Console, run `gog auth credentials set FILE.json` |
| `auth_required` (exit 4) | Run `gog login EMAIL --services all` |
| `permission_denied` (exit 6) | Check API is enabled in Google Cloud Console. Re-login with correct `--services`. |
| Browser doesn't open for OAuth | Use `--manual` flow (see Headless / SSH Setup section) |
| Token stored but commands fail | Token may have wrong scopes. Re-login with `--services all --force-consent` |
| Rate limited (exit 7) | Wait 60s, retry. Reduce `--max` in queries. |
| Keychain access denied | macOS security dialog -- allow access. Or switch to file backend with `gog auth keyring file`. |
| Safari blocks OAuth consent screen | Safari rejects "Testing" mode OAuth apps. Use Chrome instead. |
| Auth codes expire before pasting | Google OAuth codes last ~5 minutes. Re-run the auth step if too slow. |
| "State mismatch" errors during remote auth | Clear stale state files: `rm -f ~/Library/Application\ Support/gogcli/oauth-manual-state-*.json` and use `--manual` instead of `--remote --step 2` |
| Keychain locked = silent auth failures | Run `security unlock-keychain ~/Library/Keychains/login.keychain-db` before auth flows on macOS |
| OAuth fails with "app not verified" | Add yourself as a test user in Google Cloud Console -> APIs & Services -> OAuth consent screen |
| `gog auth list` shows nothing after login | On headless/SSH: switch to file keyring (`gog auth keyring file`) + set `GOG_KEYRING_PASSWORD` (see [Credential Management](#credential-management)) |
