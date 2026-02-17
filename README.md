# fieldwork

**Teach your AI agent to operate, not just code.**

Battle-tested operational skills for AI coding agents. Each skill is a self-contained runbook -- drop it into your project, and your agent gains a new capability.

Works with [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) and [Codex CLI](https://github.com/openai/codex). Adaptable to similar tools.

---

## What's a skill?

A skill is a folder containing instructions, references, and scripts that teach an AI agent *how* to do something. Not a single prompt -- a complete operational playbook with decision trees, fallback chains, and failure patterns learned the hard way.

The difference: a prompt says "search the web." A skill says "use WebSearch first, fall back to Jina if it fails, use Crawl4AI for JS-heavy pages, here's the decision tree, here are the 12 failure modes and their recovery steps."

Skills encode judgment, not just instructions.

## Skills

| Skill | What it does | Setup complexity |
|-------|-------------|-----------------|
| [browser-ops](skills/browser-ops/) | Browser automation -- forms, auth flows, scraping, email verification | Medium (npm install) |
| [web-search](skills/web-search/) | Web search + content extraction, zero API keys | Low (pip install) |
| [google-workspace-ops](skills/google-workspace-ops/) | Gmail, Calendar, Drive, Docs, Slides, Sheets automation | Medium (brew + OAuth) |
| [summarize](skills/summarize/) | YouTube, podcasts, PDFs, images, audio/video -> clean text | Low (brew install) |

## Quick start

### Option 1: Copy the skill folder

```bash
# Clone the repo
git clone https://github.com/nikitadubovikov/fieldwork.git

# Copy the skill you want into your project
cp -r fieldwork/skills/web-search .claude/skills/web-search
```

Your agent now has the skill. It will read the SKILL.md and follow its playbook.

### Option 2: Point your agent to it

Tell your AI agent:

> Learn the browser-ops skill from https://github.com/nikitadubovikov/fieldwork/tree/main/skills/browser-ops

The agent reads the SKILL.md and its references, then operates accordingly.

## Design principles

- **Self-contained** -- one folder, one skill, no shared dependencies between skills
- **Battle-tested** -- forged in daily production use, not written as exercises
- **Decision trees over instructions** -- teaches agents *when* to use each approach, not just *how*
- **Failure-aware** -- includes what doesn't work and why, so your agent doesn't repeat mistakes
- **Zero-friction** -- sensible defaults, minimal setup, API keys only when unavoidable

## How these are different

**vs prompt libraries:** Prompts are one-shot instructions. Skills are operational playbooks with decision trees, fallback chains, error recovery, and accumulated failure knowledge. A prompt tells the agent what to do. A skill teaches it how to think about a class of problems.

**vs MCP servers:** MCP gives agents tools (functions they can call). Skills give agents judgment (when to use which tool, what to do when it fails, which approach to try first). Skills and MCP are complementary -- browser-ops uses MCP tools under the hood.

**vs awesome-lists:** Those are link directories. These are the actual runbooks your agent reads and follows.

## Skill structure

Every skill follows the same layout:

```
skill-name/
  SKILL.md              # Main runbook -- the agent reads this
  references/           # Supporting docs (tool inventories, error patterns, etc.)
  scripts/              # Helper scripts (health checks, setup, utilities)
```

The SKILL.md is the entry point. It contains the decision tree, core workflows, anti-patterns, and pointers to references for deeper detail.

## License

Apache 2.0

## Author

Built by [Nikita Dubovikov](https://github.com/nikitadubovikov). These skills are extracted from daily AI agent operations -- browser automation, research workflows, content processing. They represent hundreds of hours of real-world testing against production websites, APIs, and edge cases.

More skills added as they mature in production.
