# Web Search Tool Comparison

Side-by-side comparison of all 5 tools in the web-search skill. Use lighter tools first; escalate only when they fail.

Terminology:
- **JS:** JavaScript-driven page behavior.
- **Playwright:** Browser automation framework used by Crawl4AI.
- **SPA:** Single-page application with dynamic client-side rendering.

## Comparison Matrix

| Tool | Type | JS Support | API Key | Latency | Best For |
|------|------|:----------:|:-------:|---------|----------|
| **WebSearch** | Built-in search | No | None | ~1s | Quick factual answers, URL discovery, first-choice search |
| **Crawl4AI** | Browser-based scraper | Yes (full Playwright) | None | 3-10s | JS-heavy SPAs, dynamic content, batch URL scraping |
| **Jina** | HTTP API (read + search) | No | Optional (rate limits) | ~1s | Static page extraction, lightweight search fallback |
| **duckduckgo-search** | Python search library | No | None | ~1s | Emergency search fallback, zero-dependency option |
| **WebFetch** | Built-in URL fetcher | No | None | ~2s | Quick URL content with AI summary, last-resort extraction |

## Detailed Profiles

### WebSearch (Built-in)
- **What:** Claude Code built-in web search. Returns search result blocks with titles, URLs, snippets.
- **Strengths:** Zero setup, always available, supports domain filtering, integrated into agent workflow.
- **Weaknesses:** No SDK/CLI access (tool-only), results are search blocks not raw JSON, no page content extraction.
- **Typical failure:** Thin snippets, generic ranking for niche technical topics.

### Crawl4AI
- **What:** Open-source scraper with full Playwright browser rendering. Outputs LLM-friendly markdown.
- **Strengths:** Full JS rendering, handles SPAs, batch crawling, structured data extraction strategies.
- **Weaknesses:** Requires `pip install crawl4ai && crawl4ai-setup`, heavier than other options, slower.
- **Typical failure:** Dynamic script blockers, aggressive anti-bot sites.

### Jina
- **What:** URL-to-markdown converter (`r.jina.ai`) and search (`s.jina.ai`) via HTTP. Zero install -- just curl.
- **Strengths:** Zero install, fast (~1s), works everywhere curl works, both search and extract in one service.
- **Weaknesses:** No JS rendering, rate limited without API key, misses dynamically loaded content.
- **Typical failure:** Empty/truncated output on JS-rendered pages.

### duckduckgo-search
- **What:** Python library for DuckDuckGo search. Includes text and news search modes.
- **Strengths:** Completely free, no API key, no registration, news mode for recency-sensitive queries.
- **Weaknesses:** Less AI-optimized results, Python-only, unstable title metadata, no content extraction.
- **Typical failure:** Repetitive snippets, sparse coverage for niche technical topics.

### WebFetch (Built-in)
- **What:** Claude Code built-in URL fetcher. Fetches page, converts HTML to markdown, processes with AI model.
- **Strengths:** Zero setup, AI-processed output, handles redirects, 15-min cache.
- **Weaknesses:** Cannot handle authenticated/private URLs, may summarize (not return full) large content, no JS rendering.
- **Typical failure:** Auth failure on private URLs, content truncation on large pages.

## Recommended Sequencing

### For search:
1. **WebSearch** (default, always available)
2. **Jina** `s.jina.ai` (if WebSearch unavailable or insufficient)
3. **duckduckgo-search** (emergency fallback)

### For extraction:
1. **Crawl4AI** `crwl` (JS-heavy or dynamic content)
2. **Jina** `r.jina.ai` (static pages, fast and lightweight)
3. **WebFetch** (built-in fallback, AI-summarized output)

## Cost/Latency Notes

- Keep WebSearch and Jina as defaults -- they are low latency and free.
- Budget one crawl per source URL when using Crawl4AI; overusing it destroys throughput.
- duckduckgo-search news mode is useful when freshness or date constraints are explicit.
- WebFetch caches results for 15 minutes -- efficient for repeated access to the same URL.

## Quality Gates

Before reporting results, enforce:
1. At least two independent sources for factual claims.
2. Domain authority diversity unless the topic is intentionally vendor-specific.
3. Source freshness check when dates are available.
4. Explicit notes for any unsupported claim that cannot be confirmed from extracted snippets.
