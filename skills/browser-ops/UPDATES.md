# Browser Ops Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-02-17

### new-files
Files that didn't exist before. Safe to copy without conflict risk.

| File | Description |
|------|-------------|
| `references/playbooks/booking-com.md` | Booking.com hotel search with date-locked pricing |
| `references/playbooks/google-flights.md` | Google Flights URL pre-population and filter patterns |
| `references/playbooks/linear-signup.md` | Linear signup (partial -- blocked by Cloudflare Turnstile) |
| `references/playbooks/notion-signup.md` | Notion full E2E signup with AgentMail OTP verification |
| `references/playbooks/reddit-scraping.md` | Reddit scraping via old.reddit.com with evaluate extraction |
| `references/playbooks/stripe-iframe.md` | Stripe cross-origin iframe bypass for payment forms |
| `references/playbooks/cloudflare-sites.md` | Cloudflare protection decision tree (free vs Pro vs Turnstile) |
| `references/playbooks/wikipedia-extraction.md` | Wikipedia evaluate-only extraction, zero snapshots |
| `references/playbooks/headed-browser-setup.md` | Headed browser setup, profile trust building, stealth tiers |
| `UPDATES.md` | This file -- structured changelog for AI agents |
| `UPDATE-GUIDE.md` | Instructions for AI agents performing skill updates |

### changed-files
Files that were modified. Review diff before applying if you have local edits.

| File | What changed | Breaking? |
|------|-------------|-----------|
| `references/battle-tested-patterns.md` | +Pattern 11 (post-search verification), +Pattern 12 (calendar widget protocol) | No -- additive |
| `references/failure-log.md` | +Booking.com anti-bot findings, +Layer 2 rebrowser-patches incompatibility in Open Issues | No -- additive |
| `SKILL.md` | +Playbooks section (routing table), +Staying Updated section, updated Bundled Resources Index, pattern count 10->12 | No -- additive |

### removed-files

| File | Reason |
|------|--------|
| `references/headed-browser-playbook.md` | Moved to `references/playbooks/headed-browser-setup.md` |

### breaking-changes
(none)

### migration-notes
- New `references/playbooks/` subdirectory -- create it before copying playbook files
- `headed-browser-playbook.md` moved from `references/` to `references/playbooks/headed-browser-setup.md` -- delete the old file after copying the new one
- If you have local references to `references/headed-browser-playbook.md`, update them to `references/playbooks/headed-browser-setup.md`

## 2026-02-14

### Initial release
All files are new. Copy the entire `browser-ops/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| References | `references/tool-inventory.md`, `references/battle-tested-patterns.md`, `references/failure-log.md`, `references/stealth-config.md`, `references/test-results.md`, `references/anti-detection-guide.md`, `references/headed-browser-playbook.md` |
| Scripts | `scripts/agentmail.sh`, `scripts/mailbox.py`, `scripts/requirements.txt`, `scripts/browser-check.sh` |
