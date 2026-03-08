# How to Update Video Gen

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

### output/ directory
Generated videos are saved to the output directory (default `./output/`). These are the user's outputs -- never delete or overwrite them during updates.

### Project directories
Project mode creates structured project folders with manifests, state files, and scene artifacts. These are user work products -- never modify or delete during updates.

### Scripts
The Python scripts use Python stdlib + requests -- no virtual environments needed beyond `pip install requests`. Users may have customized default output paths or model defaults in scripts. Diff before overwriting.

### API keys
API keys are stored in environment variables (`FAL_KEY`, `IMAGE_GEN_SCRIPT`), not in the skill directory. Updates never affect credentials.
