---
name: web-search
description: Web search and content extraction skill for AI coding agents. Zero API keys required. Decision tree with fallback chains across 5 tools.
---

# Web Search

Web search, scraping, and content extraction for AI coding agents. Zero API keys required. Five tools organized in fallback chains: WebSearch and Crawl4AI as primary, Jina as secondary, duckduckgo-search and WebFetch as fallbacks. Use when your agent needs web information -- finding pages, extracting content, or conducting research.

## How to install this skill

### Option 1: Point your agent at it (easiest)

Tell your AI coding agent to install this skill by pasting this into your chat:

> Install the web-search skill from [github.com/nikitadubovikov/fieldwork/skills/web-search](https://github.com/nikitadubovikov/fieldwork/tree/main/skills/web-search)

Your agent will read the SKILL.md and follow the instructions. This is the recommended approach for most users.

### Option 2: Clone into your project

```bash
# Clone the fieldwork repo (if you haven't already)
git clone https://github.com/nikitadubovikov/fieldwork.git

# Go to your project directory
cd /path/to/your-project

# Create the skills directory if it doesn't exist
# For Claude Code:
mkdir -p .claude/skills
cp -r /path/to/fieldwork/skills/web-search .claude/skills/web-search

# For Codex CLI:
mkdir -p .codex/skills
cp -r /path/to/fieldwork/skills/web-search .codex/skills/web-search
```

### Option 3: Download just this skill

```bash
# Download and extract the fieldwork repo
curl -L -o /tmp/fieldwork.zip https://github.com/nikitadubovikov/fieldwork/archive/refs/heads/main.zip
unzip -q /tmp/fieldwork.zip -d /tmp

# Copy the skill into your project (Claude Code)
mkdir -p /path/to/your-project/.claude/skills
cp -r /tmp/fieldwork-main/skills/web-search /path/to/your-project/.claude/skills/

# Or for Codex CLI:
mkdir -p /path/to/your-project/.codex/skills
cp -r /tmp/fieldwork-main/skills/web-search /path/to/your-project/.codex/skills/
```

> **Platform notes:**
> These instructions are for macOS and Linux. On Linux, replace `brew install` with your package manager (`apt`, `dnf`, etc.). On Windows, use WSL2 (Windows Subsystem for Linux) and follow the Linux instructions.

---

## Setup: Install dependencies

Installing the skill (above) just copies the instruction files. You also need the tools installed on your machine so the skill can use them.

### What you'll need

- **Python 3.10+** -- programming language runtime, needed for the web scraping libraries. Download from https://python.org if needed.

### Check prerequisites

```bash
# Check Python version (3.10 or newer required)
# If this command fails, install Python from https://python.org
python3 --version
```

### Install scraping tools

```bash
# Install web scraping and search libraries
# Always use python3 -m pip to avoid Python 2/3 confusion
python3 -m pip install crawl4ai duckduckgo-search

# Set up browser engine for crawl4ai
# This installs Playwright browser binaries so crawl4ai can render JS-heavy websites
# It may take a minute to download ~150MB of browser files
crawl4ai-setup
```

### Verify it's working

```bash
# Test that crawl4ai is importable
python3 -c "import crawl4ai; print('crawl4ai ready')"

# Test that the CLI is available
crwl --help

# Expected: "crawl4ai ready" and crwl help output
# If you see ModuleNotFoundError: run `python3 -m pip install crawl4ai` again
# If you see "crwl: command not found": run `crawl4ai-setup` again
```

### No API keys needed

Everything works out of the box. The built-in tools (WebSearch, WebFetch) require zero installation. Crawl4AI and duckduckgo-search are free and keyless.

Optional: Set `JINA_API_KEY` to increase Jina rate limits (get from https://jina.ai), but it is not required.

```bash
# Optional: add to your shell profile (~/.zshrc or ~/.bashrc) for persistence
export JINA_API_KEY='jina_...'
```

### Verify full setup

```bash
# Run from the skill directory
bash ./scripts/search-check.sh
```

---

## Decision Tree

```text
Need info from the web?
  |
  +-- Need to SEARCH for pages/answers?
  |     +-- Default first choice --> WebSearch (built-in, zero setup)
  |     +-- WebSearch unavailable? --> Jina s.jina.ai (no key needed)
  |     +-- Both fail? --> duckduckgo-search Python lib (emergency fallback)
  |
  +-- Need to EXTRACT content from a known URL?
  |     +-- JS-heavy SPA, dynamic content? --> Crawl4AI crwl (full browser rendering)
  |     +-- Simple text page (article, docs, blog)? --> Jina r.jina.ai (fast, no install)
  |     +-- Jina/Crawl4AI unavailable? --> WebFetch (built-in, AI-summarized)
  |     +-- Need structured data extraction? --> Crawl4AI with extraction strategy
  |     +-- Multiple URLs in batch? --> Crawl4AI batch mode
  |
  +-- Need DEEP RESEARCH (search + extract + combine)?
        --> WebSearch to find URLs --> Crawl4AI/Jina extract each --> synthesize

Rule of thumb: WebSearch for finding, Jina for reading, Crawl4AI for rendering.
```

---

## Tool Reference

### WebSearch (Built-in) -- Primary Search

**What:** Claude Code built-in web search tool. Returns search results with links and snippets.
**Install required:** None (built-in to Claude Code)
**Strengths:** Zero setup, zero API keys, integrated into agent workflow, always available
**Weaknesses:** No direct SDK/CLI access (tool-only), results are search-result blocks not raw JSON

```
# Invoked as a Claude Code tool:
WebSearch(query="your search query")

# Supports domain filtering:
WebSearch(query="your query", allowed_domains=["docs.python.org"])
WebSearch(query="your query", blocked_domains=["pinterest.com"])
```

**Returns:** Search result blocks with titles, URLs, and content snippets.

### WebFetch (Built-in) -- Fallback URL Extraction

**What:** Claude Code built-in URL fetcher. Fetches page content, converts HTML to markdown, processes with AI.
**Install required:** None (built-in to Claude Code)
**Strengths:** Zero setup, AI-processed output, handles redirects, 15-min cache
**Weaknesses:** Cannot handle authenticated/private URLs, may summarize large content

```
# Invoked as a Claude Code tool:
WebFetch(url="https://example.com/page", prompt="Extract the main content")
```

**Limitations:**
- Will fail for authenticated URLs (Google Docs, Confluence, Jira, private GitHub)
- HTTP auto-upgraded to HTTPS
- Large content may be summarized rather than returned in full
- When redirected to a different host, returns redirect URL instead of content

### Crawl4AI -- JS-Rendering Web Scraper

**What:** Open-source scraper with full Playwright browser rendering. Outputs LLM-friendly markdown.
**Install required:** `pip install crawl4ai && crawl4ai-setup`
**Strengths:** Full JS rendering, handles SPAs, batch crawling, structured extraction
**Weaknesses:** Requires Playwright install, heavier than Jina

```bash
# CLI (simplest)
crwl https://example.com
crwl https://example.com -o markdown

# Python API
from crawl4ai import AsyncWebCrawler
async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url='https://example.com')
    print(result.markdown)
```

### Jina Reader/Search -- Zero-Install Extraction & Search

**What:** URL-to-markdown converter and search via HTTP API. No install needed -- just curl.
**API key:** Not required. `JINA_API_KEY` is optional and only increases rate limits.
**Strengths:** Zero install, fast (~1s), works everywhere curl works, search + extract in one service
**Weaknesses:** No JS rendering, rate limited without API key

```bash
# Read a URL (returns markdown)
curl -s 'https://r.jina.ai/https://example.com'

# Search (returns search results)
curl -s 'https://s.jina.ai/your+search+query'

# With API key (higher rate limits, optional)
curl -s -H "Authorization: Bearer $JINA_API_KEY" 'https://r.jina.ai/https://example.com'
```

### duckduckgo-search -- Emergency Search Fallback

**What:** Python library for DuckDuckGo search. Zero API keys, zero registration.
**Install required:** `pip install duckduckgo-search`
**Strengths:** Completely free, no API key, no rate limit concerns, reliable fallback
**Weaknesses:** Less AI-optimized results than WebSearch, Python-only

```python
from duckduckgo_search import DDGS
results = DDGS().text("your query", max_results=5)
for r in results:
    print(r['title'], r['href'], r['body'])
```

```bash
# One-liner from CLI
python3 -c "from duckduckgo_search import DDGS; import json; print(json.dumps(DDGS().text('your query', max_results=5), indent=2))"
```

---

## Core Workflows

### Pattern 1: Quick Web Search

When: Need factual answers or find relevant pages

1. Use WebSearch: `WebSearch(query="your query here")`
2. Parse results: each result has title, URL, and content snippet
3. Fallback: `curl -s 'https://s.jina.ai/your+query+here'`
4. Emergency: `python3 -c "from duckduckgo_search import DDGS; ..."`

### Pattern 2: URL Content Extraction

When: Have a URL, need its content as clean text/markdown

a) JS-heavy site: `crwl URL` (Crawl4AI, full rendering)
b) Lightweight static page: `curl -s 'https://r.jina.ai/URL'` (Jina)
c) Both fail: `WebFetch(url="URL", prompt="Extract the main content")`

Decision: Is it a SPA/JS-heavy? Use Crawl4AI. Static content? Use Jina first. If output is empty/broken, escalate.

### Pattern 3: Deep Research

When: Need comprehensive research on a topic with multiple sources

1. WebSearch to find relevant pages
2. Pick top 3-5 URLs from results
3. Extract each with Crawl4AI or Jina
4. If any extraction fails (JS site), use the other tool
5. Synthesize extracted content into research summary

Token budget: ~5K per extracted page, budget 25K total for 5 pages

### Pattern 4: Batch URL Scraping

When: Need content from multiple URLs (5+)

```python
import asyncio
from crawl4ai import AsyncWebCrawler
urls = ['url1', 'url2', 'url3']

async def batch():
    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(url=url)
            print(f'--- {url} ---')
            print(result.markdown[:2000])

asyncio.run(batch())
```

### Pattern 5: Fallback Chain

When: Primary tool fails

Search chain: WebSearch (built-in) --> Jina s.jina.ai --> duckduckgo-search

Extract chain: Crawl4AI crwl --> Jina r.jina.ai --> WebFetch (built-in)

Always try the primary tool first, escalate on failure.

---

## MCP Configuration

Jina MCP (optional enhancement, not required):

```json
{
  "jina-reader": {
    "command": "npx",
    "args": ["-y", "jina-ai-reader-mcp"]
  }
}
```

MCP is optional. Your agent can use CLI/Python/built-in tools directly.

---

## Environment Setup

**Zero API keys required.** All tools work out of the box.

Optional:
- `JINA_API_KEY` (get from https://jina.ai) -- increases rate limits, not required

```bash
export JINA_API_KEY='jina_...'  # optional
```

Install:
- `pip install crawl4ai duckduckgo-search`
- `crawl4ai-setup`  # installs Playwright browsers

Built-in tools (WebSearch, WebFetch) require no installation.

Verify: `./scripts/search-check.sh`

---

## Anti-Patterns

| Do NOT | Do instead |
|---|---|
| Use Crawl4AI for simple text pages | Use Jina `r.jina.ai` (zero overhead) |
| Use Jina for JS-heavy SPAs | Use Crawl4AI (Jina has no JS rendering) |
| Skip the fallback chain | Always have a backup: WebSearch->Jina->duckduckgo, Crawl4AI->Jina->WebFetch |
| Extract full pages when you need one fact | Use WebSearch (returns relevant snippets directly) |
| Batch with Jina for 10+ URLs | Use Crawl4AI batch mode (designed for it) |
| Forget rate limits | Jina without API key has stricter limits |
| Use WebFetch for authenticated URLs | It will fail; use browser-ops skill or direct API access |

---

## Error Handling

| Symptom | Tool | Cause | Fix |
|---|---|---|---|
| No results returned | WebSearch | Query too specific or topic too niche | Broaden query, try Jina s.jina.ai or duckduckgo-search |
| Redirect notification | WebFetch | URL redirects to different host | Make a new WebFetch request with the provided redirect URL |
| Auth failure | WebFetch | Authenticated/private URL | Use browser-ops skill or direct API access instead |
| Content summarized | WebFetch | Page content too large | Use Jina r.jina.ai or Crawl4AI for full content |
| 429 Too Many Requests | Jina | Rate limit hit | Add `JINA_API_KEY` header, or add delay between requests |
| Empty/truncated output | Jina | JS-rendered content not captured | Escalate to Crawl4AI: `crwl URL` |
| crwl: command not found | Crawl4AI | Not installed or not on PATH | `pip install crawl4ai && crawl4ai-setup` |
| Playwright browser not found | Crawl4AI | `crawl4ai-setup` not run | Run: `crawl4ai-setup` |
| TimeoutError | Crawl4AI | Page too slow or blocking | Add timeout parameter, check if site blocks bots |
| SSL certificate error | Any | Expired or self-signed cert | Retry; for Crawl4AI add `ignore_https_errors=True` |
| 403 Forbidden | Jina/Crawl4AI | Site blocking automated access | Try different tool from fallback chain |
| ImportError: duckduckgo_search | duckduckgo-search | Package not installed | `pip install duckduckgo-search` |
| RatelimitException | duckduckgo-search | Too many requests too fast | Add 1-2s delay between calls, or switch to WebSearch |

---

## Bundled Resources Index

| Path | What | When to load |
|---|---|---|
| `./references/tool-comparison.md` | Side-by-side comparison: latency, cost, JS support, accuracy | When choosing between tools for a specific use case |
| `./references/error-patterns.md` | Detailed failure modes and recovery per tool | When debugging a failed extraction or search |
| `./scripts/search-check.sh` | Health check: verifies all tools are available | Before first web search task in a session |
| `./scripts/setup.sh` | One-shot installer for all dependencies | First-time setup or after environment reset |
