# gogcli Setup Guide (Headless Server)

Step-by-step guide for setting up gogcli on a headless Mac or Linux server.

---

## 1. Install

```bash
brew install steipete/tap/gogcli
```

---

## 2. GCP Setup

### Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)

### Configure OAuth Consent Screen

**CRITICAL:** This step is easy to miss but required.

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Workspace org)
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

### Create OAuth Client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `gogcli` (or anything)
5. Click **Create**
6. **Download JSON** (or copy client_id + client_secret)

---

## 3. Build Credentials JSON

If you downloaded the JSON, skip to step 4. If you only copied client_id + client_secret:

Create a file `credentials.json`:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"]
  }
}
```

Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with your actual values.

---

## 4. Set Credentials in gogcli

```bash
gog auth credentials set /path/to/credentials.json
```

Verify:

```bash
gog auth credentials list
# Should show your client_id
```

---

## 5. Headless Keyring Setup

**On headless servers, the default macOS Keychain can fail silently.** Switch to file-based keyring:

```bash
gog auth keyring file
```

Set keyring password (needed for every gog invocation):

```bash
export GOG_KEYRING_PASSWORD="your-password-here"
```

Add this to your shell profile (`~/.zshrc` or `~/.bashrc`) or set it in every script that calls gog.

---

## 6. Authenticate (Remote Flow)

Since headless servers may not have a browser session, use the two-step remote flow:

### Step 1: Get auth URL

```bash
gog auth add your.email@gmail.com --services gmail,calendar,drive,docs --remote --step 1
```

This prints a URL like: `https://accounts.google.com/o/oauth2/auth?client_id=...`

### Step 2: Authorize on any device

1. **Copy the auth URL**
2. **Open it on any device with a browser** (phone, laptop, etc.)
3. **Sign in and approve permissions**
4. Browser redirects to `http://localhost/?code=...&scope=...` — **this will fail** (expected)
5. **Copy the entire redirect URL from the browser address bar**

### Step 3: Complete auth

```bash
gog auth add your.email@gmail.com --services gmail,calendar,drive,docs --remote --step 2 --auth-url "PASTE_THE_REDIRECT_URL_HERE"
```

Replace `PASTE_THE_REDIRECT_URL_HERE` with the full `http://localhost/?code=...` URL you copied.

---

## 7. Enable APIs in Google Cloud Console

**People forget this step!** Each service needs its API enabled.

Visit these URLs (replace `YOUR_PROJECT_ID` with your GCP project ID):

- **Gmail API:** `https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=YOUR_PROJECT_ID`
- **Calendar API:** `https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview?project=YOUR_PROJECT_ID`
- **Drive API:** `https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=YOUR_PROJECT_ID`
- **Docs API:** `https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=YOUR_PROJECT_ID`

Click **Enable** for each one.

Or use the API Library:
1. Go to **APIs & Services** → **Library**
2. Search for "Gmail API", "Calendar API", etc.
3. Click **Enable**

---

## 8. Verify

```bash
GOG_KEYRING_PASSWORD="your-password" gog gmail labels list -a your.email@gmail.com --plain --no-input
```

Should print Gmail labels (INBOX, SENT, etc.).

Check auth:

```bash
GOG_KEYRING_PASSWORD="your-password" gog auth list
```

Should show your email with authenticated services.

---

## Gotchas Summary

| Gotcha | Solution |
|--------|----------|
| OAuth fails with "app not verified" | Add yourself as a test user in OAuth consent screen |
| `permission_denied` errors | Enable APIs in Google Cloud Console (step 7) |
| `gog auth list` shows nothing on headless servers | Switch to file keyring + set `GOG_KEYRING_PASSWORD` |
| Workers/scripts fail | Pass `GOG_KEYRING_PASSWORD` as env var in every invocation |
| Browser redirect fails during auth | Expected! Copy the localhost URL from address bar |

---

## For Workers / Scripts

Always set the keyring password:

```bash
GOG_KEYRING_PASSWORD="your-password" gog gmail search "is:unread" --json
```

Or export it at the start of your script:

```bash
#!/bin/bash
export GOG_KEYRING_PASSWORD="your-password"

gog gmail search "is:unread" --json
gog cal events --today --json
```

---

## Next Steps

- **Multi-account:** `gog auth add second.email@gmail.com ...`
- **Default account:** `gog config set default_account your.email@gmail.com`
- **Full reference:** See `auth-setup.md` for token management, service accounts, and multi-account details.
