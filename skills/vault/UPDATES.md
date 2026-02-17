# Vault Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

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

### Initial release
All files are new. Copy the entire `vault/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| Scripts | `scripts/vault.sh`, `scripts/setup.sh` |
| Docs | `UPDATES.md`, `UPDATE-GUIDE.md` |

### Features
- Encrypted secrets vault using `age` (public-key encryption) + `sops` (encrypted YAML secrets files)
- Commands: get, set, list, source, exec, verify, doctor, setup
- Colorized output (green/red/yellow) with graceful fallback for non-terminals
- Input validation preventing SOPS path-expression injection and shell injection
- Shell-safe export generation (printf %q) for eval safety
- Auto-fix file permissions on every operation
- Comprehensive `doctor` command with round-trip encryption test
- `--help` flag on every command
- All paths configurable via env vars (VAULT_DIR, VAULT_FILE, SOPS_AGE_KEY_FILE)
- One-command setup script with dependency installation
