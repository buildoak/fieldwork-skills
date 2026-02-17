# How to Update chatgpt-search

Instructions for AI agents performing skill/module updates.

## Quick Update (for agents)

1. Fetch latest source into a temporary directory.
2. Read `UPDATES.md` to identify target version and file-level changes.
3. Copy each file in `new-files` (safe additive copy).
4. For each file in `changed-files`:
   - If there are no local edits, overwrite.
   - If local edits exist, review diff and merge intentionally.
5. For each file in `removed-files`, delete only after confirming replacement intent.
6. Check `breaking-changes`; require explicit user confirmation before applying.
7. Apply any `migration-notes` steps.
8. Validate with:
   - `pip install -e .`
   - `python -m pytest tests/ -v`

## What NOT to do

- Never delete and re-copy the entire project directory.
- Never overwrite user-customized files without checking for local edits.
- Never auto-apply breaking changes without confirmation.
- Never edit files outside the project root.

## Project-specific notes

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
