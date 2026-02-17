# Image Gen Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-02-18

### new-files

| File | Description |
|------|-------------|
| `references/installation-guide.md` | Detailed agent-readable installation guide for Claude Code and Codex CLI |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | Replaced verbose multi-section install block with concise Setup section delegating to installation guide | No -- same info, better organized |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
- New `references/installation-guide.md` is a new file (safe to copy)
- `SKILL.md` install section is shorter but all information moved to the installation guide

## 2026-02-17

### Initial release
All files are new. Copy the entire `image-gen/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| Scripts | `scripts/generate.py`, `scripts/edit.py`, `scripts/review.py` |
| References | `references/model-card.md`, `references/prompt-templates.md`, `references/api-reference.md` |
| Examples | `examples/` (showcase images) |
