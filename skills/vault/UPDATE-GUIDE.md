# How to Update Vault

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

### Vault directory is NOT part of the skill
The vault itself (`~/.config/vault/` by default, or wherever the user configured it) lives outside the skill directory. Updating the skill never touches the vault, the encryption key, or any secrets. The skill is just the scripts that interact with the vault.

### Custom VAULT_DIR is user-specific
If the user has set `VAULT_DIR` in their shell profile, the skill scripts will respect it automatically. No migration needed when updating scripts.

### setup.sh should not be re-run
Running `setup.sh` on an existing vault will detect it and refuse to overwrite. This is intentional -- updating the skill does not require re-running setup.
