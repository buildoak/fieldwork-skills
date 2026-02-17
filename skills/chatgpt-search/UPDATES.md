# ChatGPT Search Updates

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
- New `references/` directory and `references/installation-guide.md` (safe to copy)
- `SKILL.md` install section is shorter but all information moved to the installation guide

## 2026-02-17

### new-files

| File | Description |
|------|-------------|
| `UPDATES.md` | Structured changelog for agent-driven updates |
| `UPDATE-GUIDE.md` | Agent update procedure and safety rules |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `pyproject.toml` | Switched build backend to `setuptools.build_meta`; bumped package version to `0.3.0` | No |
| `src/chatgpt_search/__init__.py` | Bumped runtime version to `0.3.0` | No |
| `src/chatgpt_search/db.py` | Added v1->v2 migration and v0 handling; migration chain now v1->v2->v3->v4 | No |
| `src/chatgpt_search/cli.py` | Added date parsing guardrails, db file validation, rebuild error handling, and `--limit > 0` validation | No |
| `src/chatgpt_search/searcher.py` | Convert all SQLite `OperationalError` query failures into user-facing `ValueError` | No |
| `src/chatgpt_search/enrichment.py` | Removed unused imports | No |
| `scripts/setup.sh` | Removed hardcoded export path, require export arg, use `python3 -m pip`, fixed usage path text | Yes (setup now requires path argument) |
| `SKILL.md` | Removed hardcoded local paths, removed unsupported column filter syntax, updated TF-IDF (keyword-weighting) `min_df` notes | No |

### removed-files

| File | Reason |
|------|--------|
| `PLAN.md` | Stale roadmap references removed to avoid confusion |

### breaking-changes

- `scripts/setup.sh` now requires a conversations export path argument instead of relying on a machine-specific default.

### migration-notes

- Update automation that calls setup to pass an explicit export path:
  `./scripts/setup.sh /path/to/conversations.json`.

## 2026-02-14

### Initial release
All files are new. Copy the entire `chatgpt-search/` directory.
