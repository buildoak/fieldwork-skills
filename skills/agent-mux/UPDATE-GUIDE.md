# How to Update Agent Mux

Instructions for AI agents performing skill updates.

## Quick Update (for agents)

1. Fetch latest: `git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork-latest`
2. Read `UPDATES.md` in this skill directory before modifying anything
3. For each entry in `new-files`: copy to the user's local skill directory (safe, no conflicts)
4. For each entry in `changed-files`:
   - If user has NO local edits: overwrite with new version
   - If user HAS local edits: show diff and ask for confirmation
5. Check `breaking-changes` -- if present, require explicit user confirmation
6. Check `migration-notes` -- apply any documented structural changes

## What NOT to do

- Never delete the user's entire skill directory and re-copy
- Never overwrite customized files without showing a diff and asking first
- Never auto-apply breaking changes
- Never modify files outside this skill directory

## Skill-specific notes

### Upstream project is canonical
`agent-mux` is maintained at https://github.com/buildoak/agent-mux. If runtime flags or behavior change upstream, update this skill's documentation accordingly, but do not assume local runtime setup is identical across machines.

### Local toolchain settings are user-specific
Any user-specific environment variables, auth state, shell aliases, or wrapper scripts are outside this skill folder and must not be overwritten during updates.
