# How to Update Peekaboo

Instructions for AI agents performing skill updates.

## Quick Update (for agents)

1. Fetch latest: git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork-latest
2. Read UPDATES.md in this skill's directory to see what changed
3. For each entry in new-files: copy to user's local skill directory (safe, no conflicts)
4. For each entry in changed-files:
   - If user has NO local edits: overwrite with new version
   - If user HAS local edits: show diff, let user decide
5. For each entry in removed-files: delete the old file after confirming the replacement exists
6. Check breaking-changes -- if any, require explicit user confirmation
7. Check migration-notes -- apply structural changes (new directories, moved files)

## What NOT to do
- Never delete the user's entire skill folder and re-copy
- Never overwrite files the user customized without asking
- Never auto-apply breaking changes
- Never modify files outside the skill directory

## Skill-specific notes

### scripts/ are executable
Both scripts/health-check.sh and scripts/peekaboo-safe.sh must retain their executable permission. If copying from a zip or archive, run chmod +x scripts/*.sh after extraction.

### macOS permissions are machine-specific
Accessibility and Screen Recording permissions are granted per-machine and per-terminal app. Updating the skill does not affect these permissions. If peekaboo stops working after a macOS update, re-grant permissions in System Settings > Privacy & Security.

### peekaboo CLI version compatibility
This skill is validated against peekaboo 3.0.0-beta3. If you update peekaboo to a newer version, re-run scripts/health-check.sh to verify compatibility. Check references/installation-guide.md for version-specific notes.
