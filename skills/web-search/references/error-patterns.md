# Web Search Error Patterns

The patterns below are grouped by signal, root cause, and recovery order. Use them in this exact sequence so your AI agent recovers consistently instead of flailing.

## Pattern 1: Zero Results with No Exception
### Symptom
- Search tool returns empty list and no network error.

### Likely causes
- Over-restrictive query terms
- Locale mismatch
- Overly low result limit

### Recovery
1. Retry with 1.5x broader query terms.
2. Remove strict filtering and run `duckduckgo-search` text with `max_results` 12.
3. If still empty, switch to a topic-framed query (add synonyms, package names, or official brand terms).

### Stop condition
- If at least 3 relevant links return, continue with extraction.

## Pattern 2: High Noise / Low Signal
### Symptom
- 10+ results but mostly duplicate sites or low-quality mirrors.

### Likely causes
- Bad query intent
- Ranking bias toward mirrors/spam
- Generic phrasing without domain anchoring

### Recovery
1. Keep one explicit domain filter (vendor/docs/community/forum).
2. Prefer `web_search` first result clusters over raw list order.
3. Extract only top 3 high-authority URLs and discard repeated mirror entries.

### Stop condition
- Signal quality improves when at least 2 diverse domains are represented.

## Pattern 3: Crawl Returns Empty or Truncated Content
### Symptom
- `crawl4ai` reports success but extracted text is empty or missing core sections.

### Likely causes
- JS-hydrated page
- Dynamic block with script-based rendering
- Selector mismatch or anti-bot challenge

### Recovery
1. Retry crawl with longer timeout and reduced concurrency.
2. If still weak, pass URL to `browser_ops`.
3. If browser automation cannot render content, capture only visible static sections and report limited confidence.

### Stop condition
- Source is accepted only when the same key claim appears at least twice (or from official changelog/primary docs).

## Pattern 4: Timeout and Retry Storms
### Symptom
- Repeated request timeouts from every tool.

### Likely causes
- Corporate network filtering
- SSL interception
- Transient DNS outage

### Recovery
1. Pause for 20 seconds and rerun with fewer parallel calls.
2. Test one known URL directly (example.com, docs.python.org).
3. If baseline fetch fails, escalate as environment/network issue and stop broad crawling.

### Stop condition
- Environment-level network fault is confirmed or resolved.

## Pattern 5: Contradictory Claims Across Sources
### Symptom
- Same topic has mutually incompatible details across extracted pages.

### Likely causes
- Old vs current source mix
- One source summarizing unofficial commentary
- Cached fragments or stale mirrors

### Recovery
1. Tag source dates and prioritize official primary sources.
2. Re-run with `ddgs_news` when freshness is required.
3. Keep both claim variants only if confidence is explicitly split; otherwise discard unverified statements.

### Stop condition
- Final answer can cite at least one primary source per resolved claim.

## Pattern 6: Permission / Bot Gate
### Symptom
- 403 / access denied / CAPTCHA-like interstitial.

### Likely causes
- Anti-bot policy
- Missing browser headers
- Untrusted IP behavior

### Recovery
1. Try direct URL extraction with `browser_ops`.
2. Reduce depth and call count to that domain.
3. If blocked again, switch to alternative authoritative sources and document the block.

### Stop condition
- Confirmed restriction exists and alternative sources are now used.

## Pattern 7: Tool Mismatch for User Intent
### Symptom
- User asks for "latest", but retrieved content is historical.

### Likely causes
- Started with stale-first query path
- Recency mode never activated

### Recovery
1. Re-run with news/recency-aware search.
2. Extract publication dates and reject unscored legacy references.
3. Add an explicit freshness note if only stale sources were accessible.

### Stop condition
- At least one source is explicitly within acceptable freshness window.

## Pattern 8: No Viable Signal (Hard failure)
### Symptom
- Every channel fails and no verifiable evidence remains.

### Likely causes
- Transient global index outage
- Network/firewall outage
- Topic has no public source coverage

### Recovery
1. Provide a concise "I could not verify this with public sources" status.
2. Suggest one narrower follow-up query.
3. Offer to retry in a later window.

### Stop condition
- User receives a transparent limitation plus next steps.

## Integration Note

When extraction is blocked repeatedly by rendering and policy, use the `browser-ops` skill as the final fallback. That tool is in the same repository and should already be available if you installed the skill pack.
