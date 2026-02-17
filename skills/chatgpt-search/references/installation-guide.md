# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Python 3.10+** (runtime for the search engine)
- **ChatGPT conversation export** (`conversations.json` from ChatGPT settings > Export data)
- No API keys required

## Claude Code Installation

Path: `.claude/skills/chatgpt-search/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/chatgpt-search /path/to/your-project/.claude/skills/chatgpt-search
```

## Codex CLI Installation

Codex reads `AGENTS.md` only (not `codex.md`, not `.codex/skills/`).

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Append `SKILL.md` to your project `AGENTS.md` with a marker:
```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:chatgpt-search -->"
  cat /tmp/fieldwork/skills/chatgpt-search/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Run the setup script

The setup script installs Python dependencies (scikit-learn, langdetect) and builds the FTS5 search index.

```bash
cd /path/to/skills/chatgpt-search
./scripts/setup.sh /path/to/your/conversations.json
```

The setup script requires the path to your exported `conversations.json` file as an argument.

### Step 2: Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/skills/chatgpt-search/src
```

Add this to your shell profile for persistence.

### Manual install (alternative)

If you prefer manual steps over the setup script:

```bash
python3 -m pip install scikit-learn langdetect
export PYTHONPATH=/path/to/skills/chatgpt-search/src
python -m chatgpt_search.cli --rebuild --export /path/to/conversations.json
```

## Verification

```bash
# Check the index exists and show corpus stats
export PYTHONPATH=/path/to/skills/chatgpt-search/src
python -m chatgpt_search.cli --stats

# Run a test search
python -m chatgpt_search.cli "test query" --limit 3
```

Expected: `--stats` shows conversation count, message count, keyword count, and model breakdown. Search returns ranked results with BM25 scores.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Database not found` | Index not built. Run `./scripts/setup.sh /path/to/conversations.json` |
| `ModuleNotFoundError: No module named 'chatgpt_search'` | Set `PYTHONPATH` to point to the `src/` directory |
| `scikit-learn` warning during build | Run `python3 -m pip install scikit-learn` |
| `Invalid search query` | FTS5 syntax error -- check for unmatched quotes in your query |
| No keyword results | Normal for small exports. Rebuild with more conversation data. |
| Setup script fails | Ensure Python 3.10+ is installed and the conversations.json path is correct |

## Platform Notes

- **macOS:** Primary instructions above work as written. Use `brew install python3` if needed.
- **Linux:** Same steps. Install Python via your package manager (`sudo apt install -y python3 python3-pip`).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
