# Auth Setup Guide

Complete OAuth setup, token management, and multi-account configuration for gogcli.

---

## Headless Mac Setup (Headless / SSH)

**Problem:** macOS Keychain silently drops tokens on headless Mac or Linux server environments (no GUI session). `gog auth add` succeeds but `gog auth list` shows nothing — tokens are written but disappear.

**Solution:**

1. **Switch to file-based keyring:**
   ```bash
   gog auth keyring file
   ```

2. **Set keyring password as environment variable** (required for every gog invocation):
   ```bash
   export GOG_KEYRING_PASSWORD="your-password-here"
   ```

3. **Workers and scripts MUST include this env var** when calling gog:
   ```bash
   GOG_KEYRING_PASSWORD="your-password" gog gmail search "is:unread" --json
   ```

4. **Verify it works:**
   ```bash
   GOG_KEYRING_PASSWORD="your-password" gog auth list
   # Should show your authenticated accounts
   ```

This is **required** for headless environments without a GUI session. The default macOS Keychain backend can silently fail without one.

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

For headless environments or SSH sessions:

```bash
# Manual flow (paste redirect URL)
gog login email@gmail.com --services all --manual

# Remote flow (two-step)
gog login email@gmail.com --services all --remote --step 1
# Copy the printed URL, open in any browser, authorize
# Then:
gog login email@gmail.com --services all --remote --step 2 --auth-url "PASTE_REDIRECT_URL"
```

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
| Browser doesn't open for OAuth | Use `--manual` or `--remote` flow |
| Token stored but commands fail | Token may have wrong scopes. Re-login with `--services all --force-consent` |
| Rate limited (exit 7) | Wait 60s, retry. Reduce `--max` in queries. |
| Keychain access denied | macOS security dialog -- allow access. Or switch to file backend. |
