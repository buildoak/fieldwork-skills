# Google Workspace Ops Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-02-19

### new-files
(none)

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | Added frontmatter fields (version, tools_required, triggers). Added "Sandboxed / CI Environments" section. Updated Bundled Resources Index (removed onboarding-headless.md entry, updated auth-setup.md description). | No |
| `references/auth-setup.md` | Added "Standard Setup (Laptop / Desktop with Browser)" section for headed mode. Added "Headless / SSH Setup" section with keychain unlock pre-flight and `--manual` pipe method. Added OAuth Consent Screen setup instructions. Added 6 new troubleshooting entries (Safari, auth expiry, state mismatch, keychain lock, app not verified, headless keyring). Moved Prerequisites to top. | No |

### removed-files

| File | Replacement |
|------|-------------|
| `references/onboarding-headless.md` | Content merged into `references/auth-setup.md` (Standard Setup + Headless / SSH Setup sections) |

### breaking-changes
(none)

### migration-notes
- `references/onboarding-headless.md` is deleted. All its useful content (GCP setup, credentials JSON, headless keyring, remote auth, API enablement, gotchas) has been absorbed into `references/auth-setup.md`.
- `references/auth-setup.md` now has two setup paths: "Standard Setup" (headed, browser available) and "Headless / SSH Setup" (no browser). The old "Headless Mac Setup" section at the top has been replaced.
- If you have local edits to `onboarding-headless.md`, review `auth-setup.md` to confirm your changes are preserved before deleting.

## 2026-02-18

### new-files

| File | Description |
|------|-------------|
| `references/installation-guide.md` | Detailed agent-readable installation guide for Claude Code and Codex CLI |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | Replaced verbose 3-option install block with concise Setup section delegating to installation guide | No -- same info, better organized |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
- New `references/installation-guide.md` is a new file (safe to copy)
- `SKILL.md` install section is shorter but all information moved to the installation guide

## 2026-02-17

### new-files

| File | Description |
|------|-------------|
| `UPDATES.md` | This file -- structured changelog for AI agents |
| `UPDATE-GUIDE.md` | Instructions for AI agents performing skill updates |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | +Staying Updated section | No -- additive |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
(none)

## 2026-02-14

### Initial release
All files are new. Copy the entire `google-workspace-ops/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| References | `references/gog-commands.md`, `references/pipeline-patterns.md`, `references/auth-setup.md`, `references/onboarding-headless.md` |
