# How to Update Image Gen

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

### data/ directory
The `data/` directory stores generated images. These are the user's outputs -- never delete or overwrite them during updates. The `.gitignore` excludes this directory from version control.

### Scripts
The Python scripts (`scripts/generate.py`, `scripts/edit.py`, `scripts/review.py`) use only Python stdlib -- no virtual environments or pip dependencies to manage. Users may have customized default output paths in the scripts. Diff before overwriting.

### API keys
API keys are stored in environment variables (`OPENROUTER_API_KEY_IMAGES`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`), not in the skill directory. Updates never affect credentials.
