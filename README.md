# fieldwork

**Teach your AI agent to operate, not just code.**

So here's how this started. A friend of mine -- Head of Growth, not an engineer -- asked me to help him use Claude Code and Codex to actually do his job faster. LinkedIn automation, company research, email workflows. The usual growth ops grind.

I gave him access to some of my skills. The ones I'd been building for weeks, forging against real websites that fight back, real APIs that timeout, real anti-bot systems that make you question your life choices. Browser automation that survived 15-task benchmarks. Web search that doesn't need a single API key. Google Workspace ops for email and calendar and docs.

And it worked. He went from "how do I make it click a button" to running autonomous research pipelines in a day.

That's when it clicked -- these skills shouldn't live in my private setup. They should be a proper public collection. Battle-tested operational playbooks that give AI agents real-world capabilities, not just coding tricks.

So here we are.

---

## What's a skill?

A skill is a folder. Inside: a `SKILL.md` runbook that tells your AI agent *how* to do something, plus reference docs and helper scripts. Your agent reads the runbook and follows it autonomously.

The difference matters. A prompt says "search the web." A skill says "use WebSearch first, fall back to Jina if it fails, use Crawl4AI for JS-heavy pages, here's the decision tree, here are the 12 failure modes and their recovery steps."

Prompts are one-shot. Skills encode judgment.

## Skills

| Skill | What it does | Setup |
|-------|-------------|-------|
| [browser-ops](skills/browser-ops/) | Browser automation -- forms, auth flows, scraping, email verification. 9 site-specific playbooks. | See SKILL.md |
| [web-search](skills/web-search/) | Web search + content extraction, zero API keys | See SKILL.md |
| [google-workspace-ops](skills/google-workspace-ops/) | Gmail, Calendar, Drive, Docs, Slides, Sheets | Multi-step -- see SKILL.md |
| [summarize](skills/summarize/) | YouTube, podcasts, PDFs, images, audio/video -> clean text | See SKILL.md |
| [chatgpt-search](skills/chatgpt-search/) | Search your ChatGPT exports -- FTS5, title boosting, 15 languages, TF-IDF keywords | See SKILL.md |
| [vault](skills/vault/) | Encrypted secrets vault -- API keys, passwords, tokens. Never plaintext. | See SKILL.md |
| [agent-mux](skills/agent-mux/) | Unified CLI for dispatching AI workers across Codex, Claude, and OpenCode. One command, one JSON contract. | External -- see [buildoak/agent-mux](https://github.com/buildoak/agent-mux) |
| [gsd-coordinator](skills/gsd-coordinator/) | Multi-step task orchestration -- dispatch, verify, synthesize across engines. Requires agent-mux. | Copy skill folder |
| [image-gen](skills/image-gen/) | Image generation and editing -- five models, prompt engineering, quality review loop. Zero deps beyond Python stdlib. | API key |

## The compound play

`agent-mux` is the execution layer -- one CLI command dispatches a worker to Claude, Codex, or OpenCode with the same JSON contract every time. `gsd-coordinator` is the orchestration brain -- it decides when to use which engine, which pattern fits the task (10x pipeline, triple-check, fan-out), and how to verify results before I trust them.

Together, they form the 10x pipeline I keep reaching for: Claude architects, Codex executes, the coordinator verifies and synthesizes. Alone, each one is weaker -- `agent-mux` without the coordinator is just a clean CLI, and the coordinator without `agent-mux` can't reach Codex or OpenCode. This compound setup is the same multi-model pipeline that built this repo.

When workers produce large outputs, `gsd-coordinator` writes artifacts to a configurable directory (defaults to `_workbench/` inside the skill). Deliverables go to their final destination.

Works with [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) and [Codex CLI](https://github.com/openai/codex). Adaptable to similar tools.

## Quick start

### Easiest: just tell your agent

Paste this into Claude Code or Codex CLI:

> Learn the browser-ops skill from https://github.com/buildoak/fieldwork-skills/tree/main/skills/browser-ops

The agent reads the SKILL.md and its references. Done.

### Or clone it

```bash
git clone https://github.com/buildoak/fieldwork-skills.git

# Copy the skill you want into your project
cp -r fieldwork-skills/skills/web-search .claude/skills/web-search
```

Your agent now has the skill.

### Full install (step by step)

If you're new to AI coding agents, here's the whole process:

1. **Get an AI coding agent.** Install [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) or [Codex CLI](https://github.com/openai/codex).
2. **Clone this repo.** `git clone https://github.com/buildoak/fieldwork-skills.git`
3. **Pick a skill.** Open the skill's folder (e.g., `skills/browser-ops/`) and read the SKILL.md. It has detailed setup instructions with prerequisites, install commands, and troubleshooting.
4. **Copy the skill folder** into your project's `.claude/skills/` directory (for Claude Code). For Codex CLI, add the skill's SKILL.md content to your project's AGENTS.md.
5. **Install runtime dependencies.** Each SKILL.md has a "Setup: Install dependencies" section. Follow it.
6. **Use it.** Tell your agent to use the skill. It reads the SKILL.md and follows the runbook.

Each skill's SKILL.md is self-contained -- it walks you through every step, including what to do when things go wrong.

## Staying updated

This repo gets regular updates -- new playbooks, new patterns, new failure findings. Each skill includes two files to make updates painless:

- **`UPDATES.md`** -- A structured changelog designed for AI agents. Lists new files, changed files, breaking changes, and migration notes. Your agent reads this to know exactly what changed.
- **`UPDATE-GUIDE.md`** -- Instructions your AI agent follows to apply updates safely. It knows not to overwrite your customizations, not to delete your config, and not to auto-apply breaking changes.

To check for updates, tell your agent:

> Check for updates to the browser-ops skill from https://github.com/buildoak/fieldwork-skills

The agent fetches the latest UPDATES.md from the remote, compares it against your local version, tells you what's new, and lets you choose which changes to apply. No surprises -- you see the diff before anything changes.

## What makes these different

**From prompt libraries:** A prompt tells the agent what to do. A skill teaches it how to think about a class of problems -- decision trees, fallback chains, error recovery, accumulated failure knowledge from hundreds of hours of real testing.

**From MCP servers:** MCP gives agents tools -- functions they can call. Skills give agents judgment -- when to use which tool, what to do when it fails, which approach to try first. They're complementary. browser-ops uses MCP tools under the hood.

**From awesome-lists:** Those are link directories. These are the actual runbooks your agent reads and follows. Written and maintained by someone who uses them daily.

## Design principles

- **Self-contained** -- one folder, one skill, no shared dependencies
- **Battle-tested** -- forged in production against sites that fight back
- **Decision trees over instructions** -- teaches agents *when*, not just *how*
- **Failure-aware** -- includes what doesn't work and why
- **Zero-friction** -- sensible defaults, minimal setup, API keys only when unavoidable
- **Update-safe** -- structured changelogs and agent-readable update guides

## Skill structure

```
skill-name/
  SKILL.md              # Main runbook -- the agent reads this
  UPDATES.md            # Structured changelog for AI agents
  UPDATE-GUIDE.md       # How to apply updates safely
  references/           # Supporting docs, failure logs, patterns, playbooks
  scripts/              # Health checks, setup, utilities
```

Each skill is self-contained. Copy one folder -- it works.

## License

Apache 2.0

## Author

Built by [Nick Oak](https://nickoak.com). Skills are updated as they mature in production. Check UPDATES.md in each skill for the latest changes.
