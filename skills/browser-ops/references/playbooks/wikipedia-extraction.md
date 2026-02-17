# Wikipedia Extraction Playbook

**Target:** https://en.wikipedia.org, https://ja.wikipedia.org (and other language editions)
**Tested:** Feb 2026
**Result:** PASS (11 calls, 63 seconds)
**Stealth:** None needed (Wikipedia has no anti-bot)

## What Works

### Evaluate-only mode -- zero snapshots

Wikipedia articles are content-heavy pages with massive a11y trees. The correct approach is to skip snapshots entirely and use `browser_evaluate` with targeted CSS selectors for all data extraction.

```
# Navigate to the article
browser_navigate(url="https://en.wikipedia.org/wiki/Artificial_intelligence")
browser_wait(target="1000")

# Extract citation count
browser_evaluate(script="document.querySelectorAll('.reference').length")
# Returns: 479

# Extract table of contents sections
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.mw-heading h2')).map(e => e.textContent))")
# Returns: ["History", "Goals", "Approaches", ...]

# Extract first paragraph
browser_evaluate(script="document.querySelector('.mw-parser-output > p:not(.mw-empty-elt)').textContent")

# Extract all section headings (h2 + h3)
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.mw-heading h2, .mw-heading h3')).map(e => ({level: e.tagName, text: e.textContent})))")

# Extract infobox data (if present)
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.infobox tr')).map(tr => ({label: tr.querySelector('th')?.textContent?.trim(), value: tr.querySelector('td')?.textContent?.trim()})).filter(r => r.label))")
```

### Multi-language extraction

```
# English article
browser_navigate(url="https://en.wikipedia.org/wiki/Artificial_intelligence")
browser_wait(target="1000")
browser_evaluate(script="JSON.stringify({citations: document.querySelectorAll('.reference').length, sections: Array.from(document.querySelectorAll('.mw-heading h2')).map(e => e.textContent)})")

# Japanese article (same CSS selectors work across all Wikipedia editions)
browser_navigate(url="https://ja.wikipedia.org/wiki/%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD")
browser_wait(target="1000")
browser_evaluate(script="JSON.stringify({citations: document.querySelectorAll('.reference').length, sections: Array.from(document.querySelectorAll('.mw-heading h2')).map(e => e.textContent)})")

browser_close()
```

### Performance

- 11 tool calls total (both languages)
- 63 seconds total
- Zero accessibility tree snapshots
- Cleanest brutal-tier test in the benchmark

## What Doesn't Work

1. **Accessibility tree snapshots.** Wikipedia articles produce enormous a11y trees (easily 50K+ tokens for a long article). This blows token budgets and provides no advantage over targeted CSS selectors. Do not use `browser_snapshot` on Wikipedia.

2. **Full-page `browser_get_text`.** Similar problem -- returns the entire page text content, which for a Wikipedia article can be tens of thousands of characters. Use targeted selectors instead.

## Key Patterns

- **Evaluate-only mode is the correct approach.** For content-heavy pages like Wikipedia, skip all observation tools (snapshot, get_text, get_html) and go straight to `browser_evaluate` with targeted CSS selectors.
- **CSS selectors are consistent across Wikipedia editions.** `.reference` for citations, `.mw-heading h2` for section headings, `.mw-parser-output > p` for paragraphs, `.infobox` for infoboxes. These work on EN, JA, and other language editions.
- **No `return` keyword in evaluate expressions.** `browser_evaluate` expects a JS expression, not a statement. Use `document.title` not `return document.title`.
- **JSON.stringify for structured data.** When extracting arrays or objects, wrap in `JSON.stringify()` to get parseable output from `browser_evaluate`.
- **Navigate directly to article URLs.** Wikipedia URLs are predictable: `https://[lang].wikipedia.org/wiki/[Article_Title]`. No search or form interaction needed.

## Anti-Bot Notes

- **No anti-bot on Wikipedia.** Wikipedia is a public, open-access encyclopedia. No detection, no CAPTCHA, no Cloudflare.
- **No stealth needed.** Layer 0 (no stealth configuration) works perfectly.
- **Rate limiting may apply at extreme scale.** Wikipedia's API has rate limits, and aggressive scraping may trigger IP blocks. For one-off or low-volume extraction, not a concern.
- **Consider the Wikipedia API.** For structured data extraction at scale, the MediaWiki API (`api.php`) is more efficient than browser automation. Browser is useful for visual content or when you need the rendered page.

## Useful CSS Selectors for Wikipedia

| Data | Selector | Returns |
|------|----------|---------|
| Citation count | `.reference` | NodeList of citation elements |
| Section headings (h2) | `.mw-heading h2` | Top-level sections |
| Section headings (h3) | `.mw-heading h3` | Sub-sections |
| First paragraph | `.mw-parser-output > p:not(.mw-empty-elt)` | Article lead paragraph |
| All paragraphs | `.mw-parser-output > p` | All text paragraphs |
| Infobox rows | `.infobox tr` | Key-value data from sidebar |
| Categories | `#mw-normal-catlinks li a` | Article categories |
| External links | `.external.text` | External reference links |
| Interlanguage links | `.interlanguage-link a` | Links to other language editions |
| Last modified date | `#footer-info-lastmod` | Page modification timestamp |

## Sample Worker Prompt

```
Extract structured data from the English and Japanese Wikipedia articles on Artificial Intelligence.

APPROACH: Use evaluate-only mode. Do NOT use browser_snapshot -- Wikipedia pages have massive a11y trees that waste tokens. Use browser_evaluate with CSS selectors for all extraction.

Steps:
1. Navigate to https://en.wikipedia.org/wiki/Artificial_intelligence
2. Extract via browser_evaluate:
   - Citation count: document.querySelectorAll('.reference').length
   - Section headings: Array.from(document.querySelectorAll('.mw-heading h2')).map(e => e.textContent)
   - First paragraph: document.querySelector('.mw-parser-output > p:not(.mw-empty-elt)').textContent

3. Navigate to https://ja.wikipedia.org/wiki/%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD
4. Extract the same data points (same CSS selectors work across all Wikipedia editions)
5. Close browser

IMPORTANT: Do NOT use the "return" keyword in browser_evaluate expressions. Use expressions directly (e.g., document.title, not return document.title).

Report: citation counts, section headings, and first paragraph for both languages.
```
