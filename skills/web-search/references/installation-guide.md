# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Python 3.10+** (runtime for Crawl4AI and duckduckgo-search)
- No API keys required (all tools work out of the box)
- Optional: `JINA_API_KEY` to increase Jina rate limits

## Claude Code Installation

Path: `.claude/skills/web-search/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/web-search /path/to/your-project/.claude/skills/web-search
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
  echo "<!-- fieldwork-skill:web-search -->"
  cat /tmp/fieldwork/skills/web-search/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Option A: One-shot setup script

```bash
cd /path/to/skills/web-search
bash ./scripts/setup.sh
```

This installs Crawl4AI, duckduckgo-search, and sets up Playwright browser binaries.

### Option B: Manual install

#### Step 1: Install Python packages

```bash
python3 -m pip install crawl4ai duckduckgo-search
```

If you see "Permission denied": run `python3 -m pip install --user crawl4ai duckduckgo-search` instead.

#### Step 2: Set up Crawl4AI browser engine

Downloads ~150MB of Playwright browser binaries for JS-rendered pages.

```bash
crawl4ai-setup
```

If `crawl4ai-setup: command not found`: run `python3 -m crawl4ai.setup` instead.

### Optional: Jina API key

Not required. Increases rate limits for Jina reader/search.

```bash
export JINA_API_KEY='jina_...'
```

## Verification

```bash
# Check Python packages are installed
python3 -c "import crawl4ai, duckduckgo_search; print('All imports OK')"

# Check Crawl4AI CLI
crwl --help

# Full health check
bash ./scripts/search-check.sh
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Install Python 3.10+ from [https://python.org](https://python.org) or `brew install python3` (macOS) |
| `Package 'crawl4ai' requires a different Python: 3.9` | Upgrade to Python 3.10+, then rerun install |
| `ModuleNotFoundError: No module named 'crawl4ai'` | Run `python3 -m pip install crawl4ai` |
| `crawl4ai-setup: command not found` | Run `python3 -m crawl4ai.setup` instead |
| `Executable doesn't exist` (Playwright) | Run `crawl4ai-setup` to install browser binaries |
| `crwl: command not found` | Rerun `crawl4ai-setup` |

## Platform Notes

- **macOS:** Primary instructions above work as written. Use `brew install python3` if you prefer Homebrew.
- **Linux:** Same steps. Install Python via your package manager (`sudo apt install -y python3 python3-pip` on Ubuntu/Debian).
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
