# TrueSkill Rank Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-03-18

### Initial release
All files are new. Copy the entire `trueskill-rank/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| References | `references/algorithm.md`, `references/prior-runs.md`, `references/installation-guide.md` |
| Rubrics | `rubrics/practitioner-signal.md`, `rubrics/signal-serendipity-entropy.md`, `rubrics/example-template.md` |
| Scripts | `scripts/trueskill-rank.py` |
| Docs | `UPDATES.md`, `UPDATE-GUIDE.md` |

### Features
- Domain-agnostic TrueSkill batch ranking with swappable rubrics
- LLM-as-judge pairwise comparison engine
- Overlap coefficient 2-4 for match coverage control
- agent-mux dispatch for parallel judge execution
- Supports any text items: blog posts, research abstracts, product ideas, tweets, etc.
