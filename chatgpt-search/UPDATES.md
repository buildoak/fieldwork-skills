# ChatGPT Search Updates

Structured changelog for AI agents. Read this before applying updates so you can
merge safely with local edits.

## v0.3.0 (2026-02-17)

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
| `SKILL.md` | Removed hardcoded local paths, removed unsupported column filter syntax, updated TF-IDF `min_df` notes | No |

### removed-files

| File | Reason |
|------|--------|
| `PLAN.md` | Stale roadmap references removed to avoid confusion |

### breaking-changes

- `scripts/setup.sh` now requires a conversations export path argument instead of relying on a machine-specific default.

### migration-notes

- Update automation that calls setup to pass an explicit export path:
  `./scripts/setup.sh /path/to/conversations.json`.

## v0.2.0 (2026-02-17)

### baseline

Version `0.2.0` was the pre-update baseline before the reliability and migration
hardening in `v0.3.0`.
