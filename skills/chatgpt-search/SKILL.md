---
name: chatgpt-search
description: |
  Search ChatGPT conversation exports using SQLite FTS5.
  BM25-ranked full-text search with TF-IDF keywords,
  date/role/model/language filtering, and conversation browsing.
  Use when agent needs to search past ChatGPT conversations by topic,
  find specific discussions, browse conversation history,
  or find conversations by extracted keywords.
  Do NOT use for non-ChatGPT knowledge bases — use a dedicated document search tool.
  Do NOT use for Apple Notes or Obsidian — use a dedicated document search tool.
---

# chatgpt-search

SQLite FTS5 search engine for ChatGPT conversation exports. BM25-ranked full-text search
with title boosting, code separation, TF-IDF keyword extraction,
and filtering by date, role, model, and language.

**Repo:** `<skill-root>`
**Data:** `<your-export-path>/conversations.json`
**Default DB:** `~/.chatgpt-search/index.db`

## DECISION TREE

```text
Need to search past ChatGPT conversations?
  |
  +-- Know a topic/keyword? --> Full-text search: "query"
  |     +-- Want only user messages? --> add --role user
  |     +-- Want a specific model's responses? --> add --model gpt-5
  |     +-- Want a date range? --> add --since 2025-01 --until 2025-06
  |     +-- Want a specific language? --> add --lang ru
  |
  +-- Know a conversation ID? --> --conversation <id> (or partial ID)
  |
  +-- Want to explore keywords?
  |     +-- Top corpus keywords --> --keywords
  |     +-- Keywords for a conversation --> --keywords --keywords-conversation <id>
  |
  +-- Want corpus overview? --> --stats
  |
  +-- Need to search non-ChatGPT docs? --> Use your project's document search skill
  +-- Need to search Apple Notes/Obsidian? --> Use a dedicated document search tool
  +-- Need web search? --> Use web-search skill
```

## Setup

```bash
cd <skill-root> && ./scripts/setup.sh <your-export-path>/conversations.json
```

This installs dependencies (scikit-learn, langdetect) and builds the index
from the provided conversations.json location. Rebuild takes ~26 seconds
on the full corpus (1,514 conversations, 16,689 messages).

## CLI Reference

```bash
# Set PYTHONPATH (or install the package)
export PYTHONPATH=<skill-root>/src

# --- Search ---

# Full-text search
python -m chatgpt_search.cli "transformer attention"

# Date filtering
python -m chatgpt_search.cli "kubernetes" --since 2025-01
python -m chatgpt_search.cli "pytorch" --since 2025-06 --until 2025-12

# Role filtering (search only user messages or assistant responses)
python -m chatgpt_search.cli "pricing strategy" --role user

# Model filtering (partial match)
python -m chatgpt_search.cli "code review" --model gpt-5
python -m chatgpt_search.cli "reasoning" --model o3

# Language filtering
python -m chatgpt_search.cli "machine learning" --lang en
python -m chatgpt_search.cli "обучение" --lang ru

# Phrase queries (exact match)
python -m chatgpt_search.cli '"attention is all you need"'

# Prefix queries
python -m chatgpt_search.cli "transfor*"

# Limit results
python -m chatgpt_search.cli "topic" --limit 5
python -m chatgpt_search.cli "topic" -n 50

# --- Browse ---

# Browse a full conversation
python -m chatgpt_search.cli --conversation <conversation-id>
python -m chatgpt_search.cli -c <partial-id>

# --- Keyword Exploration ---

# Top keywords across the corpus (by total TF-IDF score)
python -m chatgpt_search.cli --keywords

# Keywords for a specific conversation
python -m chatgpt_search.cli --keywords --keywords-conversation <conversation-id>

# --- Corpus Info ---

# Corpus statistics (conversations, messages, keywords, models, dates)
python -m chatgpt_search.cli --stats

# --- Index Management ---

# Rebuild index (includes TF-IDF enrichment)
python -m chatgpt_search.cli --rebuild --export /path/to/conversations.json

# Custom database location
python -m chatgpt_search.cli --db /path/to/index.db "query"
```

## Search Syntax

FTS5 query syntax is supported:

| Syntax | Example | Meaning |
|--------|---------|---------|
| Simple terms | `transformer attention` | Implicit AND |
| Phrase | `"attention is all"` | Exact phrase match |
| Prefix | `transfor*` | Words starting with "transfor" |
| OR | `pytorch OR tensorflow` | Either term |
| NOT | `python NOT java` | Exclude term |

## Architecture

- **Engine:** SQLite FTS5 with BM25 ranking
- **Indexing:** Message-level rows, conversation metadata joined at query time
- **Boosting:** Title at 10x weight, content at 1x, code at 0.5x
- **Tokenizer:** Porter stemmer + Unicode61 (handles diacritics)
- **TF-IDF:** scikit-learn TfidfVectorizer, unigrams + bigrams, code blocks stripped,
  top-10 keywords per conversation, min_df=2 for larger language groups and min_df=1
  for small groups, max_df=0.8
- **Language Detection:** langdetect per message, 15 languages supported
- **Parser:** Canonical thread extraction via `current_node` backward traversal
- **Code separation:** Fenced code blocks extracted to separate field
- **PUA cleanup:** Unicode Private Use Area citation markers stripped
- **Citeturn cleanup:** ChatGPT citation markup (citeturn0search1, etc.) stripped

## Performance

Tested on 149MB export (1,514 conversations, 16,689 messages):

| Metric | Value |
|--------|-------|
| Full index build (with TF-IDF) | ~26 seconds |
| TF-IDF extraction alone | ~3 seconds |
| Database size | ~89 MB |
| Keywords extracted | 15,085 |
| Search latency | <50ms |

## Anti-Patterns

| Do NOT | Do instead |
|--------|------------|
| Use for non-ChatGPT document search | Use your project's document search skill |
| Use for Apple Notes or Obsidian | Use a dedicated document search tool |
| Expect semantic search | This is lexical BM25 -- use exact terms, expand synonyms manually |
| Search single common words ("the", "is") | Use qualifying terms to narrow results |
| Forget to rebuild after new export | Run --rebuild after importing new conversations.json |
| Expect TF-IDF keywords on fresh/tiny corpora | Small groups use min_df=1, but tiny exports can still yield sparse keywords |

## Error Handling

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Database not found" | Index not built | Run `--rebuild --export /path/to/conversations.json` |
| No keyword results | Corpus too small or low textual signal | Normal for small exports; rebuild with more data |
| "Invalid search query" | FTS5 syntax error | Check query syntax; avoid unmatched quotes |
| scikit-learn warning during build | scikit-learn not installed | Run `python3 -m pip install scikit-learn` |
