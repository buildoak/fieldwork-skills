# How to Update Browser Ops

Instructions for AI agents performing skill updates.

## Quick Update (for agents)

1. Fetch latest: `git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork-latest`
2. Read `UPDATES.md` in this skill's directory to see what changed
3. For each entry in `new-files`: copy to user's local skill directory (safe, no conflicts)
4. For each entry in `changed-files`:
   - If user has NO local edits: overwrite with new version
   - If user HAS local edits: show diff, let user decide
5. For each entry in `removed-files`: delete the old file after confirming the replacement exists
6. Check `breaking-changes` -- if any, require explicit user confirmation
7. Check `migration-notes` -- apply structural changes (new directories, moved files)

## What NOT to do
- Never delete the user's entire skill folder and re-copy
- Never overwrite files the user customized without asking
- Never auto-apply breaking changes
- Never modify files outside the skill directory

## Skill-specific notes

### scripts/venv/ should not be overwritten
The `scripts/venv/` directory (if it exists) contains a Python virtual environment created by `./scripts/agentmail.sh setup`. It is machine-specific and should never be copied from the repo. If the user has a venv, leave it in place. If they don't, they can recreate it with `./scripts/agentmail.sh setup`.

### Stealth env vars are separate from skill files
Layer 1 stealth configuration lives in the user's shell profile (`~/.zshrc` or `~/.bashrc`), not in the skill directory. Updating the skill does not affect stealth configuration. If new stealth settings are recommended, mention them to the user but do not modify their shell profile.

### AgentMail API key is user-specific
The AgentMail API key is stored in the user's environment (typically `~/.env.keys` or shell profile), not in the skill files. Updating the skill does not affect the API key. If the user hasn't set up AgentMail yet, point them to `./scripts/agentmail.sh setup`.

### references/playbooks/ is a new directory
As of the 2026-02-17 update, playbooks live in `references/playbooks/`. If the user's local copy predates this update, the directory won't exist. Create it before copying playbook files:
```bash
mkdir -p references/playbooks
```

### headed-browser-playbook.md moved
The file `references/headed-browser-playbook.md` was moved to `references/playbooks/headed-browser-setup.md`. After copying the new file, delete the old one to avoid confusion. Update any local references.
