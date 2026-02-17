---
name: agent-mux
description: Unified multi-engine worker dispatch CLI for AI coding agents. Run Codex, Claude, and OpenCode workers with one command and one JSON output contract. Use when tasks need subagent orchestration, model diversity, or parallel worker execution. Canonical implementation and runtime docs are maintained in the upstream buildoak/agent-mux repository.
---

# agent-mux

Dispatch AI coding workers across engines with a single CLI and stable JSON output. This skill is a fieldwork integration guide for the upstream `agent-mux` project.

## How to install this skill

Pick one option below. Option 1 is fastest if you already have an AI coding agent running.

### Option 1: Tell your AI agent (easiest)

Paste this into your AI agent chat:

> Install the agent-mux skill from https://github.com/buildoak/fieldwork-skills/tree/main/skills/agent-mux

The agent will read this `SKILL.md` and install it for your environment.

### Option 2: Clone and copy

```bash
# 1. Clone the fieldwork repo
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork

# 2A. Claude Code: copy this skill folder into your project
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/agent-mux /path/to/your-project/.claude/skills/agent-mux

# 2B. Codex CLI: Codex reads AGENTS.md only
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:agent-mux -->"
  cat /tmp/fieldwork/skills/agent-mux/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

### Option 3: Download just this skill

```bash
# 1. Download and extract the repo zip
curl -L -o /tmp/fieldwork.zip https://github.com/buildoak/fieldwork-skills/archive/refs/heads/main.zip
unzip -q /tmp/fieldwork.zip -d /tmp

# 2A. Claude Code: copy this skill folder into your project
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork-main/skills/agent-mux /path/to/your-project/.claude/skills/agent-mux

# 2B. Codex CLI: Codex reads AGENTS.md only
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:agent-mux -->"
  cat /tmp/fieldwork-main/skills/agent-mux/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

For Codex CLI, do not use `codex.md` or `.codex/skills/`. Root `AGENTS.md` is the only instruction source.

## Staying Updated

This skill ships with `UPDATES.md` changelog data and `UPDATE-GUIDE.md` instructions for AI agents.

After installing, tell your agent: "Check `UPDATES.md` in the `agent-mux` skill for changes."

When updating, tell your agent: "Read `UPDATE-GUIDE.md` and apply the latest changes from `UPDATES.md`."

Follow `UPDATE-GUIDE.md` so customized local files are diffed before any overwrite.

For runtime behavior, CLI flags, and release notes, always use the upstream repository:

- https://github.com/buildoak/agent-mux

## Quick Start

Install the upstream CLI, then run a minimal dispatch:

```bash
agent-mux --engine codex --reasoning high "Summarize src/auth changes and list risks"
```

Expected output shape:

```json
{
  "engine": "codex",
  "status": "ok",
  "response": "..."
}
```

## Core Workflow

1. Choose engine (`codex`, `claude`, or `opencode`) for the step.
2. Pass one clear goal and bounded scope.
3. Parse the JSON response and use `response` as the worker output.
4. Retry only after fixing prompt scope or engine choice.

## Dependency Boundaries

- Required external dependency: upstream `agent-mux` CLI from `https://github.com/buildoak/agent-mux`.
- Optional local dependency: other fieldwork skills may call `agent-mux`, but this skill does not require any other skill folder from this repository.

## Anti-Patterns

| Do NOT | Do instead |
|--------|------------|
| Assume this repo contains the full `agent-mux` implementation | Install and reference the upstream `buildoak/agent-mux` project |
| Send vague multi-goal prompts | Send one bounded goal per worker call |
| Ignore JSON contract | Parse `status` and `response` deterministically |
| Blindly retry failed dispatches | Adjust scope, engine, or prompt before retrying |

## Error Handling

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `agent-mux: command not found` | CLI not installed | Install from upstream repo and verify `$PATH` |
| Worker returns empty/partial output | Prompt too broad or context too large | Narrow scope, split task, rerun |
| Non-zero exit code | Engine runtime/auth issue | Re-run with debug flags from upstream docs and resolve engine auth |

## Bundled Resources Index

| Path | What | When to load |
|------|------|--------------|
| `./README.md` | Pointer doc describing upstream ownership | First read in this folder |
| `https://github.com/buildoak/agent-mux` | Canonical implementation, install docs, CLI flags | Always for real usage |
