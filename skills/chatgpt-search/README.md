# chatgpt-search

**Turn your ChatGPT export into a searchable database.**

ChatGPT gives you a data export. It's a 150MB JSON file with every conversation you've ever had. Useful in theory. In practice, it's a blob. You can't search it. You can't filter by date, language, or model. You can't find that one conversation where you worked out that pricing strategy six months ago.

This tool fixes that. It parses the export, builds a SQLite FTS5 index (SQLite's built-in full-text search engine) with BM25 ranking (a relevance-scoring formula), extracts TF-IDF keywords (a term-weighting method that surfaces distinctive words) per conversation, and gives you a CLI that actually works. Search by topic, filter by date range, filter by which model answered, filter by language. Browse full conversations. Explore keywords.

A prompt says "search your chats." A skill says "here's a persistent FTS5 index with title boosting, date filtering, language detection, and TF-IDF keywords -- and here's when to use it vs. grep (plain text matching)."

---

## Why this exists

ChatGPT's built-in search is real-time and forgetful. It searches the server, requires a connection, doesn't support offline access, and gives you no control over ranking or filtering. If you use ChatGPT heavily -- especially across multiple languages or models -- you accumulate thousands of conversations containing genuine reasoning, decisions, and context that you'll want to reference later.

The export is the raw material. This tool makes it useful.

What it does well:
- BM25-ranked full-text search with Porter stemming (basic word-root matching for English)
- Title boosted 10x (conversation titles are strong signals)
- Code blocks extracted to a separate field (0.5x weight, so code doesn't drown out prose)
- Per-message language detection across 15 languages
- TF-IDF keyword extraction per conversation (unigrams + bigrams)
- Filters: date range, role (user/assistant), model (gpt-4, o3, etc.), language

What it does not do:
- Semantic search. This is lexical BM25. "tools for building websites" won't match "React." Search for the specific terms.
- Stemming beyond English. Porter stemmer handles English well. Other languages get Unicode tokenization but not morphological analysis.
- Incremental updates. ChatGPT exports are full dumps. You rebuild from scratch each time. Takes ~27 seconds on 1,500 conversations.
- Real-time sync. This works offline against your local export.

---

## Install

```bash
git clone https://github.com/buildoak/fieldwork-skills.git
cd fieldwork-skills/skills/chatgpt-search
pip install -e .
```

That's it. The package has two dependencies: `scikit-learn` (for TF-IDF) and `langdetect` (for language detection). Both install automatically.

### Get your data

1. Go to [ChatGPT Settings](https://chatgpt.com/#settings)
2. **Data Controls** > **Export data**
3. Wait for the email (usually minutes, sometimes hours)
4. Download the ZIP, extract `conversations.json`

Note: ChatGPT limits exports to once every ~30 days. Plan accordingly.

### Build the index

```bash
chatgpt-search --rebuild --export ~/Downloads/conversations.json
```

This parses the export, builds the FTS5 index, runs TF-IDF keyword extraction, and stores everything in `~/.chatgpt-search/index.db`. On 1,514 conversations (149MB export), it takes about 27 seconds.

To update after a new export, run the same command. It drops and rebuilds cleanly.

### Or use the setup script

```bash
./scripts/setup.sh ~/Downloads/conversations.json
```

Same thing, but also installs dependencies if missing.

---

## Usage

```bash
# Full-text search
chatgpt-search "transformer attention"

# Date filtering
chatgpt-search "kubernetes" --since 2025-01
chatgpt-search "pytorch" --since 2025-06 --until 2025-12

# Role filtering -- search only your messages or only AI responses
chatgpt-search "pricing strategy" --role user
chatgpt-search "code review" --role assistant

# Model filtering (partial match)
chatgpt-search "reasoning" --model o3
chatgpt-search "analysis" --model gpt-5

# Language filtering
chatgpt-search "machine learning" --lang en
chatgpt-search "обучение" --lang ru

# Phrase queries (exact match)
chatgpt-search '"attention is all you need"'

# Prefix queries
chatgpt-search "transfor*"

# Browse a full conversation by ID (or partial ID)
chatgpt-search --conversation abc123
chatgpt-search -c abc123

# Keyword exploration
chatgpt-search --keywords                                    # top TF-IDF keywords
chatgpt-search --keywords --keywords-conversation abc123     # keywords for one conversation

# Corpus statistics
chatgpt-search --stats

# Limit results (default: 20)
chatgpt-search "topic" -n 50

# Custom database location
chatgpt-search --db /path/to/index.db "query"
```

### Search syntax

FTS5 query syntax (SQLite full-text query operators) is supported:

| Syntax | Example | Meaning |
|--------|---------|---------|
| Simple terms | `transformer attention` | Implicit AND |
| Phrase | `"attention is all"` | Exact phrase match |
| Prefix | `transfor*` | Words starting with "transfor" |
| OR | `pytorch OR tensorflow` | Either term |
| NOT | `python NOT java` | Exclude term |

---

## How it works

**Parser.** ChatGPT stores conversations as trees -- regenerated responses create branches. The parser walks backward from `current_node` via parent pointers to extract the canonical (non-branching) thread. Each message gets its text cleaned: Unicode PUA citation markers stripped, citeturn markup removed, code blocks separated from prose.

**Indexer.** Messages go into SQLite with an FTS5 virtual table. Three indexed columns with different BM25 weights: conversation title (10x), message content (1x), code (0.5x). Title boosting matters -- conversation titles are surprisingly good relevance signals. Language detection runs per-message via langdetect.

**Enrichment.** After indexing, scikit-learn's TfidfVectorizer runs over conversation-level content (all messages concatenated, code stripped). Conversations are grouped by dominant language, each group gets language-appropriate stopword lists. Top-10 keywords per conversation, stored in a `keywords` table.

**Search.** BM25 queries against FTS5, with optional SQL filters for date, role, model, and language. Results grouped by conversation for cleaner output.

---

## Performance

Tested on a 149MB export (1,514 conversations, 16,689 messages):

| Metric | Value |
|--------|-------|
| Full index build (with TF-IDF) | ~27 seconds |
| Database size | ~89 MB |
| Keywords extracted | ~15,000 |
| Search latency | <50ms |

---

## For AI agents

This repo includes a `SKILL.md` -- a runbook for AI coding agents (Claude Code, Codex CLI). Copy the repo into your project's `.claude/skills/chatgpt-search/` directory and the agent can search your ChatGPT history autonomously.

The skill includes a decision tree, CLI reference, anti-patterns, and error handling. The agent reads it and knows when to use this tool vs. grep vs. other search skills.

### Staying updated

- `UPDATES.md` -- structured changelog designed for agents
- `UPDATE-GUIDE.md` -- safe update procedure (don't overwrite local edits, confirm breaking changes)

---

## Limitations

Be honest about what this is and isn't:

- **Lexical, not semantic.** BM25 matches words, not meaning. Expand your queries manually. Search "ML" AND "machine learning" AND "deep learning" separately.
- **English stemming only.** Porter stemmer helps English recall (searching "running" matches "run"). Other languages get Unicode tokenization but no morphological analysis.
- **Full rebuild only.** No incremental updates. Each new export means a full rebuild (~27s). ChatGPT's export format doesn't support diffs.
- **Export cooldown.** ChatGPT limits data exports to roughly once per 30 days. Your index is only as fresh as your last export.
- **Language detection is probabilistic.** Short messages (<20 chars) default to English. Mixed-language conversations use the dominant language for TF-IDF grouping.

---

## Requirements

- Python 3.10+
- scikit-learn >= 1.3
- langdetect >= 1.0.9

## License

MIT

## Author

Built by [Nick Oak](https://nickoak.com).
