# Web Search Tool Comparison

This matrix is intentionally opinionated: use heavier tools only when lighter tools fail to provide usable signal.

## Tool Matrix

| Tool | What it is | Speed | Quality for long-form extraction | Best fit | Typical failure mode |
|---|---|---:|---|---|---|
| `web_search` | Built-in index-first query tool | High | Low | Fast facts, short answer prompts | Thin snippets, generic ranking |
| `duckduckgo-search` text | Python package search across public index | High | Low-Medium | Broad discovery and URL harvesting | Repetitive snippets, unstable title metadata |
| `duckduckgo-search` news | Time-aware news search mode | Medium | Medium | Recency-sensitive asks, release events | Sparse coverage for niche technical topics |
| `crawl4ai` | Full-page browser-like crawler + markdown extraction | Medium-Low | High | Docs, RFCs, change logs, long policy pages | Dynamic script blockers, JS-heavy pages |
| `browser_ops` | Browser automation skill (external) | Low | High | JS hydration, anti-bot pages, interactive UIs | Session management overhead, stricter site anti-automation |

## Recommended Sequencing

- Use `web_search` and `duckduckgo-search` first. They are fast and cheap.
- Escalate to news mode only when freshness or date constraints are explicit.
- For any answer requiring evidence quality > one paragraph, run `crawl4ai` against only 2-4 shortlisted URLs.
- Use `browser_ops` as the last resort for pages that require interactive or rendered execution.

## Capability Trade-Offs

- If you only need to rank where to look next, `web_search` is the default.
- If you need clean text from structured pages, `crawl4ai` beats raw snippets almost always.
- If the site is dynamic and refuses static extraction, `browser_ops` is the least fragile fallback.
- If the query is time-sensitive, `duckduckgo-search` news mode usually gives better signal than generic search.

## Cost/Latency Notes

- Keep `web_search` and text search as the default; they are low latency.
- Budget one crawl chain per final source URL when using `crawl4ai`; overusing it destroys throughput.
- Reserve `browser_ops` for the small minority of pages where JS rendering or anti-automation checks are blocking static extraction.

## Quality Gates

Before reporting, enforce:
1. At least two independent sources for factual claims.
2. Domain authority diversity unless the topic is intentionally vendor-specific.
3. Source freshness check when dates are available.
4. Explicit notes for any unsupported claim that can’t be confirmed from extracted snippets.

## Fallback Priorities

- `web_search` failure: try `duckduckgo-search` text with wider region and relaxed result limit.
- `duckduckgo-search` quality issue: switch to news mode if recency matters.
- `crawl4ai` blocked: route directly to `browser_ops`.
- `browser_ops` blocked: narrow to official source URLs and static pages.

## Operator Guidance

- Never begin with heavy extraction.
- Never trust one source for high-stakes claims.
- Never return an answer with less than one verifiable URL per claim.
- Keep query logs concise; avoid dumping noisy results into final responses.
