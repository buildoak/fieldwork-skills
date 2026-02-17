# GSD Coordinator Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-02-18

### new-files

| File | Description |
|------|-------------|
| `references/installation-guide.md` | Detailed agent-readable installation guide for Claude Code and Codex CLI |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | Replaced verbose 3-option install block with concise Setup section delegating to installation guide | No -- same info, better organized |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
- New `references/installation-guide.md` is a new file (safe to copy)
- `SKILL.md` install section is shorter but all information moved to the installation guide

## 2026-02-17

### Initial release
All files are new. Copy the entire `gsd-coordinator/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| References | `references/orchestration-examples.md` |
| Update support | `UPDATES.md`, `UPDATE-GUIDE.md` |
| Artifacts | `_workbench/.gitkeep` |
