# Orchestration Examples

Battle-tested patterns from real GSD coordinator sessions. Each example documents what was dispatched, why, and what made it work. All patterns validated in production across February 2026.

---

## Example 1: Writing Style Distillation (Fan-Out + Sequential Synthesis)

**Pattern:** Fan-Out (Phase 1) into Sequential Synthesis (Phases 2-3)
**Task:** Analyze a corpus of blog posts across multiple dimensions, synthesize findings into a canonical style reference, then update the consuming skill.
**Why this pattern:** Three independent analysis angles (quantitative, qualitative, delta) that feed into a single synthesis. Fan-out for speed on the independent work; sequential for the dependent synthesis that needs all three outputs.

### Setup

The coordinator had three input sources: a blog post corpus (8 posts), an existing voice card (extracted patterns), and a skill file with 10 correction-tested markers from real editing sessions. The goal: produce a single canonical reference document that reconciles all three sources.

### Dispatch

**Phase 1 -- 3 parallel workers:**

| Worker | Engine | Task | Output |
|--------|--------|------|--------|
| 1 | Codex 5.3 `high` | Quantitative corpus analysis: sentence length, punctuation habits, vocabulary fingerprint | Workbench file (218 lines) |
| 2 | Codex 5.3 `high` | Qualitative rhetorical analysis: structure patterns, metaphor inventory, self-referential moves | Workbench file (357 lines) |
| 3 | Codex Spark | Delta analysis: compare voice card against correction-tested markers, find gaps and conflicts | Workbench file (75 lines) |

**Phase 2 -- 1 sequential worker:**

| Worker | Engine | Task | Output |
|--------|--------|------|--------|
| 4 | Codex 5.3 `high` | Read all three Phase 1 outputs + originals, synthesize into 100-200 line reference with paste-ready injection block | Final deliverable (159 lines) |

**Phase 3 -- 1 sequential worker:**

| Worker | Engine | Task | Output |
|--------|--------|------|--------|
| 5 | Codex Spark | Update the consuming skill to reference the new document and broaden its scope | Updated skill file |

Workers were prompted to write intermediate artifacts to `_workbench/` with date-engine prefix naming.

### Result

5 workers, 41 tool calls, 18 minutes total. The synthesis worker reconciled quantitative data (19.5% fragment rate, heavy em-dash usage) with qualitative patterns (6-beat narrative arc) and the correction-tested markers (which took precedence on conflicts). The coordinator verified the deliverable by reading it directly before reporting back.

### What made it work

The key insight is **phase boundaries as quality gates**. Phase 2 could not start until all three Phase 1 outputs existed. This meant the synthesis worker had complete information, not partial views. The coordinator enforced this by prompting Phase 2 to read all three intermediate files.

Using Spark for the delta analysis (Worker 3) and the skill update (Worker 5) was the right call -- both were focused, bounded tasks. The corpus analyses needed `high` because they involved multi-file reasoning across 8+ documents.

---

## Example 2: Vault Build + Security Audit (10x Pipeline with Codex xHigh Audit)

**Pattern:** 10x Pipeline -- Codex `high` builds, Codex `xhigh` audits, Codex `high` fixes
**Task:** Build an encrypted secrets vault (age + SOPS), then security-audit it, then harden and package for public release.
**Why this pattern:** Security-sensitive code benefits from model diversity between builder and auditor. The builder optimizes for functionality; the auditor (at `xhigh` reasoning) catches the edge cases the builder's "get it working" mindset missed.

### Setup

The coordinator had already completed a research phase (separate GSD dispatch) that recommended age + SOPS as the encryption stack. The research returned inline -- no file artifact, just a structured recommendation. The build GSD received the recommendation as context in its prompt.

### Dispatch

**Build phase (single Codex `high` worker):**

The GSD coordinator received a 7-phase prompt covering: tool installation, directory creation, keypair generation, initial vault, shell integration, CLI wrapper script (6 commands), and verification checks. The coordinator executed this as a single Codex worker because the phases were tightly dependent.

Result: 7 phases complete, all verification checks pass. 5 minutes, 59 tool calls.

**Audit phase (Codex `xhigh` via separate GSD dispatch):**

A second GSD was spawned specifically for the audit + public release. The audit worker was prompted to check:
- Command injection vectors in shell scripts
- Temp file leaks (plaintext touching disk)
- Error paths that might leak secrets to stderr
- Race conditions in concurrent operations
- File permission enforcement

**Fix phase (applied by audit worker directly):**

### Result

The audit found 11 issues. The critical one: the `source` command used `eval` on raw decrypted values -- a value containing `$(rm -rf /)` would have executed as a shell command. Fixed with `printf %q` escaping.

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | Shell injection in `source` command via `eval` | Critical | Fixed |
| 2 | YAML parser fragile on multiline values | Medium | Fixed |
| 3 | SOPS path expression injection | Medium | Fixed |
| 4 | Value not JSON-encoded in `set` | Medium | Fixed |
| 5 | Secret visible in process args | Medium | Accepted (SOPS limitation) |
| 6 | Concurrent `set` not safe | Medium | Accepted (single-user) |
| 7 | `exec` command loses argument boundaries | Medium | Fixed |

The coordinator then verified the audit independently: "Codex 5.3 confirms the GSD's findings -- same 11 issues, same severity rankings." Both the GSD audit and independent Codex audit converged on the same vulnerabilities.

### What made it work

**The `xhigh` reasoning level justified itself on one finding.** The shell injection in `source` was the kind of subtle vulnerability that `high` reasoning would likely miss -- it requires thinking about what happens when user-controlled data flows through `eval`. The `xhigh` worker's pedantic, thorough analysis caught it.

The independent verification (coordinator re-running the audit separately) confirmed convergence -- two passes, same findings. This is the 10x pattern at its best: builder and auditor have different blind spots, and agreement between them produces high confidence.

---

## Example 3: Browser Automation Benchmark (Sequential Workers with Skill Injection)

**Pattern:** Sequential dispatch with skill injection, progressive difficulty escalation
**Task:** Run a 10-test browser automation benchmark, where each test executes real browser interactions against live websites.
**Why this pattern:** Browser workers share a single daemon -- parallel execution causes state collisions. Sequential is the only option. Skill injection (`--browser` + `browser-ops` skill) gives each worker the full playbook.

### Setup

The coordinator had a 10-test suite ranging from medium (Reddit scraping) to brutal (Stripe iframe checkout) to final-boss (SaaS signup with email verification). Each test was a self-contained browser task against a live site. The browser-ops skill contained: 25 tool references, 10 battle-tested patterns, stealth configuration, and failure history.

### Dispatch

Tests 1-3 were dispatched to a GSD coordinator as a batch:

```
Engine: Codex Spark via agent-mux
Skill: browser-ops (loaded via --browser flag)
Sandbox: danger-full-access (required for Unix socket to browser daemon)
Pattern: One Spark worker per test, run sequentially
```

Each worker was prompted to:
1. Read the browser-ops SKILL.md
2. Read relevant reference docs (tool inventory, battle-tested patterns)
3. Execute the test following the snapshot-act-snapshot loop
4. Return: status, steps taken, skill gaps found

Tests 4-10 followed the same pattern with progressively harder targets.

### Result

9/10 pass, 1 partial (Cloudflare Turnstile CAPTCHA -- requires Layer 2+ stealth, not an agent or skill gap).

Key discoveries during the benchmark:
- **URL pre-population pattern:** Google Flights' autocomplete widget resisted `browser_type`. Bypassed by navigating directly to `?q=` URL with parameters pre-encoded. 21 tool calls vs 67+ calls with timeout on the form-based approach.
- **iframe bypass pattern:** Stripe's cross-origin iframes blocked `browser_fill`. Solution: extract iframe `src` URL via `browser_evaluate`, navigate directly to it, interact normally.
- **Evaluate-only mode:** Wikipedia's massive a11y tree blew token budgets. Skipped snapshots entirely, used `browser_evaluate` with targeted CSS selectors for all extraction. 11 calls, 63 seconds, zero snapshots.

### What made it work

**Skill injection was the multiplier.** Workers with the browser-ops skill loaded made correct decisions about snapshot modes, tool selection (`fill` vs `type`), and escalation paths -- because the skill's playbook told them exactly when to use each approach. Workers without the skill would have defaulted to full snapshots (10x more expensive) and used `fill` everywhere (breaking autocomplete fields).

**Sequential execution was non-negotiable.** All workers share one browser daemon. The coordinator enforced this by dispatching one worker at a time and ensuring `browser_close()` was called between tests.

---

## Example 4: Skill Publishing Pipeline (Build + Audit + Fix with Style Injection)

**Pattern:** 10x Pipeline with parallel build phase, sequential audit and fix
**Task:** Port an internal skill to a public repository, including SKILL.md rewrite, image compression, README in the author's writing style, and repo-level README update.
**Why this pattern:** The build has two independent tracks (skill scaffold + README/images), but the audit and fix must see the complete output. Writing-style injection ensures the public-facing README matches the author's voice.

### Setup

The coordinator had: the internal skill to port, a writing style reference document (produced by Example 1's pipeline), the target repo structure, and the user's explicit instruction: "Codex 5.3 high to build, Codex 5.3 xhigh to audit, Codex 5.3 high to fix."

### Dispatch

**Phase 1 -- Build (2 parallel Codex `high` workers):**

| Worker | Task |
|--------|------|
| 1 | Skill scaffold: read source, create public SKILL.md (strip internal references), copy scripts/references, create UPDATES.md |
| 2 | Images + README: compress showcase images, read writing style reference, write skill README in author's voice, update repo README |

Worker 2 was given explicit instruction to read the writing style reference and apply its "Quick Injection" block when writing. This is skill injection at the content level -- not a `--skill` flag, but style guidance embedded in the prompt.

**Phase 2 -- Audit (1 Codex `xhigh` worker):**

Prompted to read ALL Phase 1 outputs and check:
- Does SKILL.md work standalone without access to the internal coordinator?
- Are scripts copied correctly (no internal path references)?
- Does README follow the author's writing style? (Cross-reference against style document)
- Are internal references, paths, or coordinator-specific logic leaking?
- Are images compressed to reasonable size?

**Phase 3 -- Fix (1 Codex `high` worker):**

Read audit findings, fix every FAIL item.

### Result

29 tool calls total. The audit caught: one leaked internal path, one missing setup instruction, and style drift in the README (too formal, missing signature sentence fragments). All fixed in Phase 3.

### What made it work

**The explicit 3-phase contract from the user** ("high to build, xhigh to audit, high to fix") was the clearest possible dispatch instruction. No ambiguity about engine selection or reasoning levels. The coordinator could focus entirely on prompt quality rather than architectural decisions.

**Writing style injection via reference document** worked better than inline style instructions. Workers could read the 159-line reference and internalize the patterns, rather than following 2-3 vague adjectives in the prompt.

---

## Example 5: GSD Builds Without Workers (When the Coordinator Is Enough)

**Pattern:** Direct execution by coordinator, no worker dispatch
**Task:** Build a search tool with parser, indexer, CLI, and test suite.
**Why this pattern:** When the architecture is clear, scope is well-defined, and the work is pure implementation -- sometimes the fastest path is the coordinator doing it directly.

### Setup

A GSD coordinator was dispatched with a detailed 6-phase prompt: research prior art, plan, refine with structured reflection, build, test with real data, verify + audit. Budget authorized: "10-15 Codex workers."

### Dispatch

The coordinator read the prompt, assessed the task, and built the entire tool directly -- parser, indexer, searcher, CLI, setup script, SKILL.md, README. 37 tests passing, 1,514 records indexed. No Codex workers dispatched.

### Result

91 tool calls, 15 minutes. Working tool shipped.

But: the coordinator skipped two planned enrichment layers (NER + TF-IDF keyword extraction) that the user had explicitly approved. The main thread caught this:

> "The GSD was pragmatic -- it shipped a working tool fast. But it cut two enrichment layers you approved."

A second GSD was dispatched specifically for the skipped features + audit.

### What made it work (and what did not)

**The coordinator was correct that direct execution was faster** for a well-defined implementation task. Dispatching 10 workers for a single-file Python tool would have been overhead without benefit.

**The coordinator was wrong to silently drop approved scope.** This is the anti-pattern: a worker optimizing for speed at the cost of completeness. The fix: the main thread caught the gap and dispatched a second pass.

**The lesson:** GSD coordinators will sometimes take shortcuts. The main thread must verify not just quality but scope -- did the coordinator do everything that was asked, or did it decide some parts were unnecessary?

---

## Example 6: Source Accuracy Investigation (Failure Recovery Pipeline)

**Pattern:** Investigation + targeted fix, triggered by user catching a fabrication
**Task:** A Codex worker had created a public skill file that mixed content from two source documents, one canonical and one deprecated. The user spotted a reference that did not exist in the canonical source.
**Why this pattern:** When a worker produces plausible-looking output that contains fabricated content, you need a structured investigation before fixing -- otherwise the fix worker might perpetuate the same errors.

### Setup

A previous GSD had created a public SKILL.md from a canonical source file. The user noticed the output referenced `agent-comms` -- a convention from a deprecated v1 document that did not exist in the canonical v2 source. The user flagged it: "this is a smoking gun."

### Dispatch

The GSD coordinator was given three jobs, each with a different execution model:

**Job 1 -- Investigation (coordinator reads directly, no Codex):**

The coordinator was explicitly told: "do this yourself, no Codex." It read all three files (canonical source, deprecated source, generated output) and performed a line-by-line accuracy audit:
- What content is NOT traceable to the canonical source?
- What content from the canonical source is MISSING?
- Where did fabricated conventions come from?

**Job 2 -- Fix (Codex `high`):**

Based on investigation findings, a Codex worker rewrote the SKILL.md with explicit rules:
- Every pattern must be traceable to the canonical source
- The deprecated source can supplement only where canonical is silent
- Strip all fabricated content
- Keep valuable new additions (two operating modes, "bring your own skills") that were correct generalizations

**Job 3 -- Create missing files + commit (Codex `high`):**

A second worker created UPDATES.md, UPDATE-GUIDE.md, and amended the commit.

### Result

26 tool calls. The investigation found that the Codex worker had pulled conventions from the deprecated document and mixed them with the canonical source, producing output that looked correct but was based on the wrong source of truth. The fix worker produced a faithful rewrite.

### What made it work

**The coordinator investigated before fixing.** If it had gone straight to "fix the file," the fix worker would have had the same blind spot as the original worker. The investigation phase (Job 1) built the accuracy map that the fix worker (Job 2) could follow.

**"Do this yourself, no Codex" for the investigation** was critical. The investigation required reading three files and comparing them at the concept level -- understanding which document was canonical and which was deprecated. This is judgment work, not execution work. Sending it to Codex would risk the same fabrication pattern.

**User vigilance was the trigger.** The automated pipeline (build + audit) did not catch the source confusion. The user's domain knowledge ("there's no `agent-comms` in that file") was the signal that something was wrong. This is why the main thread must spot-check outputs, especially when workers create content from source documents.
