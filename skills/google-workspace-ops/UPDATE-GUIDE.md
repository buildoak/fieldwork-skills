# How to Update Google Workspace Ops

Instructions for AI agents performing skill updates.

## Quick Update (for agents)

1. Fetch latest: `git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork-latest`
2. Read `UPDATES.md` in this skill's directory to see what changed
3. For each entry in `new-files`: copy to user's local skill directory (safe, no conflicts)
4. For each entry in `changed-files`:
   - If user has NO local edits: overwrite with new version
   - If user HAS local edits: show diff, let user decide
5. Check `breaking-changes` -- if any, require explicit user confirmation
6. Check `migration-notes` -- apply structural changes (new directories, moved files)

## What NOT to do
- Never delete the user's entire skill folder and re-copy
- Never overwrite files the user customized without asking
- Never auto-apply breaking changes
- Never modify files outside the skill directory

## Skill-specific notes

### OAuth credentials are user-specific
The `gog` CLI stores OAuth tokens locally (typically in `~/.config/gog/`). These are never part of the skill directory and are unaffected by updates. If the user needs to re-authenticate, run `gog login EMAIL --services all`.

### Google Cloud project setup is one-time
The Google Cloud Console project, enabled APIs, and downloaded credentials JSON are user-specific setup steps documented in `references/auth-setup.md`. Updating the skill does not require re-doing this setup.
