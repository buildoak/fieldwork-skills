# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **age** (modern encryption tool, public-key cryptography)
- **sops** (encrypted YAML secrets manager)
- **jq** (JSON processor for shell scripts)
- All installable via Homebrew or system package manager

## Claude Code Installation

Path: `.claude/skills/vault/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/vault /path/to/your-project/.claude/skills/vault
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
  echo "<!-- fieldwork-skill:vault -->"
  cat /tmp/fieldwork/skills/vault/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Run the setup script

The setup script installs encryption tools (if needed), creates the vault directory, and generates your encryption key.

```bash
cd /path/to/skills/vault
./scripts/setup.sh
```

This handles everything: dependency installation, vault directory creation (`~/.shit/` by default), key generation, and initial encrypted YAML file.

### Manual install (alternative)

If you prefer manual steps:

```bash
# Install dependencies
brew install age sops jq

# Create vault directory
mkdir -p ~/.shit
chmod 700 ~/.shit

# Generate encryption key
age-keygen -o ~/.shit/.age-identity
chmod 600 ~/.shit/.age-identity
```

### Custom vault path

The default vault directory (`~/.shit`) is intentionally obscure. To customize:

```bash
export VAULT_DIR="$HOME/.config/vault"
VAULT_DIR="$HOME/.config/vault" ./scripts/setup.sh
```

Add the export to your shell profile for persistence.

## Verification

```bash
# Full health check (tools, permissions, encryption test)
./scripts/vault.sh doctor

# Quick verify (round-trip encryption test)
./scripts/vault.sh verify

# Store and retrieve a test secret
./scripts/vault.sh set TEST_KEY "hello_vault"
./scripts/vault.sh get TEST_KEY
# Should print: hello_vault
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `sops not found` | `brew install sops` |
| `age not found` | `brew install age` |
| `jq not found` | `brew install jq` |
| `Age identity not found` | Run `./scripts/setup.sh` to create it |
| `Vault decrypted but no secrets found` | Normal for a fresh vault. Add a secret with `vault.sh set` |
| `Failed to set key` | Key name must use only letters, digits, and underscores |
| `Key not found` | Run `vault.sh list` to see available keys |
| `Permission denied` | Run `vault.sh doctor` to check and fix permissions |

## Platform Notes

- **macOS:** Primary instructions above work as written. All deps available via Homebrew.
- **Linux:** Install via package manager: `sudo apt install -y age sops jq` (Ubuntu/Debian) or equivalent. Some distros may need manual sops install -- see [sops releases](https://github.com/getsops/sops/releases).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
