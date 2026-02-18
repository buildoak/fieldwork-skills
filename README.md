[![License](https://img.shields.io/github/license/buildoak/fieldwork-skills)](LICENSE) [![Last Commit](https://img.shields.io/github/last-commit/buildoak/fieldwork-skills)](https://github.com/buildoak/fieldwork-skills/commits/main) [![GitHub Stars](https://img.shields.io/github/stars/buildoak/fieldwork-skills?style=social)](https://github.com/buildoak/fieldwork-skills)

# Fieldwork Tools

![fieldwork-skills](assets/banner.png)

**Teach your AI agent to operate 10x better.**

A collection of self-contained skills — each one a battle-tested playbook with code, decision trees, and failure recovery baked in. Not prompts. Not links. Operational runbooks your agent reads and follows autonomously. Works with [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) and [Codex CLI](https://github.com/openai/codex).

> AI agents: read root `AGENTS.md` first. It has the canonical installation/update flow for both Codex CLI and Claude Code.

---

## Backstory

So here is the story. I have been building my ideal Claude Code setup, [well, for a while](https://www.nickoak.com/posts/robots-v4/). Burning it down and starting again something like 10 times. Until I made the full circle and returned to simple `CLAUDE.md` + skills + some spice (nested agents).

Some time after, a friend of mine — Head of Growth, not an engineer — asked me to help him use Claude Code and Codex to actually do his job faster. LinkedIn automation, companies research, email workflows. The usual growth ops grind.

I gave him access to some of my skills. The ones I'd been forging for weeks against real-world friction — APIs that timeout, anti-bot systems that make you question your life choices, OAuth flows that break between Tuesday and Wednesday for no reason. Operational playbooks that survived hundreds of hours of production use and came out sharper every time.

And it worked. He went from "how do I make it click a button" to running autonomous research pipelines in a day.

That's when it clicked — these skills shouldn't live in my private setup. They should be a proper public collection. Not another awesome-list of links. Not a prompt library. Actual operational skills that encode judgment — when to use what, what breaks, how to recover, and what not to do.

But where this *really* started is further back. I wanted proper illustrations for Clifford Simak's *City* (1952) — talking dogs, dying cities, and a robot butler outliving humanity. That constraint rewired the whole build. You cannot throw "robot in snow" at a model and call it *City* — you need per-scene visual extraction and a style guide that tracks palette drift across 10,000 years of fictional history. That specificity bled into every other skill: the browser-ops playbooks that handle sites fighting back, the web-search fallback chains, the vault that encrypts secrets behind an intentionally misleading path. A specific book demanded precision, and precision became the standard.

---

## What's a skill?

A skill is a folder. Inside: a `SKILL.md` runbook that tells your AI agent *how* to do something, plus reference docs and helper scripts. Your agent reads the runbook and follows it autonomously.

The difference matters. A prompt says "search the web." A skill says "use WebSearch first, fall back to Jina if it fails, use Crawl4AI for JS-heavy pages, here's the decision tree, here are the 12 failure modes and their recovery steps."

Prompts are one-shot. Skills encode judgment.

## Skills

| Skill | What you can do with it |
|-------|------------------------|
| [browser-ops](skills/browser-ops/) | Let your agent fill forms, log into websites, scrape data, verify emails — anything that needs a real browser. 9 ready-made playbooks for common use cases. |
| [web-search](skills/web-search/) | Ask your agent to research anything on the web. Three fallback engines, zero API keys needed — probably better than Exa + Firecrawl, and it just works. |
| [google-workspace-ops](skills/google-workspace-ops/) | Have your agent send emails, manage your calendar, search Drive, edit Docs, Slides, and Sheets on your behalf. |
| [summarize](skills/summarize/) | Drop a YouTube link, podcast, PDF, or audio file — get clean extracted text back. Works with images too. |
| [chatgpt-search](skills/chatgpt-search/) | Search through your old ChatGPT conversations. Find that one discussion you had months ago in seconds. |
| [vault](skills/vault/) | Store API keys and secrets encrypted. Your agent can use them without ever seeing plaintext on disk. |
| [agent-mux](skills/agent-mux/) | Run Claude inside Codex or Codex inside Claude — second opinions, best of both worlds, one unified contract. See [buildoak/agent-mux](https://github.com/buildoak/agent-mux). |
| [gsd-coordinator](skills/gsd-coordinator/) | Give your agent complex multi-step tasks — it breaks them down, dispatches workers, verifies results, and synthesizes the output. |
| [image-gen](skills/image-gen/) | Generate and edit images from text prompts. Five models, smart prompt engineering, quality review built in. |

## The compound play

Each skill works on its own — but they get dramatically better together.

**Research pipeline.** `web-search` finds pages, `browser-ops` logs into the ones behind auth walls, `summarize` extracts the content, `vault` supplies the API keys — your agent chains them without you wiring anything up.

**Content production.** `web-search` gathers source material, `summarize` distills it, `image-gen` creates visuals, `google-workspace-ops` drafts the final doc and emails it to your team.

**The 10x engine.** `agent-mux` + `gsd-coordinator` are the enablers that make everything else compound. `agent-mux` lets you run Claude inside Codex or Codex inside Claude — one command, one JSON contract, any engine. `gsd-coordinator` is the orchestration brain on top: it breaks complex tasks into steps, dispatches workers across engines in parallel, verifies results, and synthesizes the output. Together they form a multi-model pipeline where Claude architects, Codex executes, and the coordinator makes sure nothing slips through. This compound setup is the same pipeline that built and audited this repo.

The more skills you install, the more your agent can chain on its own. That's the whole point — operational judgment that compounds.

## Quick start

### Easiest: just tell your agent

Paste this into Claude Code or Codex CLI:

> Learn the browser-ops skill from https://github.com/buildoak/fieldwork-skills/tree/main/skills/browser-ops

The agent reads the SKILL.md and its references. Done.

### Or clone it

```bash
git clone https://github.com/buildoak/fieldwork-skills.git

# Claude Code: copy one skill folder
cp -r fieldwork-skills/skills/web-search .claude/skills/web-search

# Codex CLI: append the skill runbook to root AGENTS.md
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:web-search -->"
  cat fieldwork-skills/skills/web-search/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

Your agent now has the skill.

### Full install (step by step)

If you're new to AI coding agents, here's the whole process:

1. **Get an AI coding agent.** Install [Claude Code](https://docs.anthropic.com/en/docs/build-with-claude/claude-code) or [Codex CLI](https://github.com/openai/codex).
2. **Clone this repo.** `git clone https://github.com/buildoak/fieldwork-skills.git`
3. **Pick a skill.** Open the skill's folder (e.g., `skills/browser-ops/`) and read the SKILL.md. It has detailed setup instructions with prerequisites, install commands, and troubleshooting.
4. **Install the skill** into your agent runtime. Claude Code uses `.claude/skills/<skillname>/`. Codex CLI reads root `AGENTS.md` only, so append the skill's `SKILL.md` there.
5. **Install runtime dependencies.** Each SKILL.md has a "Setup" section. Follow it.
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

**From MCP servers:** MCP (Model Context Protocol) servers give agents tools -- functions they can call. Skills give agents judgment -- when to use which tool, what to do when it fails, which approach to try first. They're complementary. browser-ops uses MCP tools under the hood.

**From awesome-lists:** Those are link directories. These are the actual runbooks your agent reads and follows. Written and maintained by someone who uses them daily.

## Design principles

- **Self-contained** -- one folder, one skill, no shared dependencies
- **Battle-tested** -- forged in production against sites that fight back
- **Decision trees over instructions** -- teaches agents *when*, not just *how*
- **Failure-aware** -- includes what doesn't work and why
- **Zero-friction** -- sensible defaults, minimal setup, API keys only when unavoidable
- **Update-safe** -- structured changelogs and agent-readable update guides

## Skill structure

```text
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
