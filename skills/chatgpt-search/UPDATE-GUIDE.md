# How to Update chatgpt-search

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

### Setup script now requires explicit export path

Run setup with:

```bash
./scripts/setup.sh /path/to/conversations.json
```

Do not assume machine-specific default data paths.

### Database migrations are sequential

Schema upgrades must be applied in order:

- v1 -> v2 (keywords table + `conversations.message_count`)
- v2 -> v3 (`messages.lang`)
- v3 -> v4 (drop legacy `entities`)
