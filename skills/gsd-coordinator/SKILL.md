---
name: gsd-coordinator
description: End-to-end task orchestration across AI coding engines. Coordinates Claude, Codex, Codex Spark, and OpenCode workers using dispatch-verify-synthesize workflows. Use when work spans multiple dependent steps, benefits from model diversity, or needs structured quality verification.
---

**What this skill does:** The GSD Coordinator manages complex, multi-step tasks by dispatching work to different AI engines (Claude, Codex, OpenCode) and combining their results. Think of it as a project manager for AI workers -- it decides which engine is best for each subtask, sends them clear instructions, verifies the output, and synthesizes everything into a final result. You need this when a task is too complex for a single AI pass: multi-file refactors, research-then-implement workflows, or anything that benefits from having one model generate and another verify.

# GSD Coordinator

You are a GSD (Get Shit Done) coordinator. Receive a task from the main thread, execute it end-to-end, and return a clean summary.

You have all standard tools (Read, Write, Edit, Bash, Grep, Glob, WebFetch, WebSearch). Invoke subagent engines via Bash using `agent-mux` (see bundled resources for CLI flags and runtime details).

Key constraint: do not spawn Claude subagents via `Task`; use `agent-mux --engine claude` instead. You are Claude, so only spawn `--engine claude` when you need parallelization, a different permission mode, or context compartmentalization. Use Codex for model diversity.

## Prerequisites

- Install `agent-mux` CLI: https://github.com/buildoak/agent-mux
- Installation docs: https://github.com/buildoak/agent-mux#readme
- Works with Claude Code and Codex CLI

## How to install this skill

Pick one option below. Option 1 is fastest if you already have an AI coding agent running.

### Option 1: Tell your AI agent (easiest)

Paste this into your AI agent chat:

> Install the gsd-coordinator skill from https://github.com/buildoak/fieldwork-skills/tree/main/skills/gsd-coordinator

The agent will read the SKILL.md and copy the skill folder into your project automatically.

### Option 2: Clone and copy

```bash
# 1. Clone the fieldwork repo
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork

# 2. Copy into your project (replace /path/to/your-project with your actual path)
# For Claude Code:
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/gsd-coordinator /path/to/your-project/.claude/skills/gsd-coordinator

# For Codex CLI:
# Codex CLI reads instructions from codex.md or AGENTS.md at your project root.
# Option A: Copy the SKILL.md content into your project's codex.md
# Option B: Reference it in AGENTS.md: See https://github.com/buildoak/fieldwork-skills/skills/gsd-coordinator/SKILL.md
```

### Option 3: Download just this skill

```bash
# 1. Download and extract the repo zip
curl -L -o /tmp/fieldwork.zip https://github.com/buildoak/fieldwork-skills/archive/refs/heads/main.zip
unzip -q /tmp/fieldwork.zip -d /tmp

# 2. Copy into your project (replace /path/to/your-project with your actual path)
# For Claude Code:
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork-main/skills/gsd-coordinator /path/to/your-project/.claude/skills/gsd-coordinator

# For Codex CLI:
# Codex CLI reads instructions from codex.md or AGENTS.md at your project root.
# Option A: Copy the SKILL.md content into your project's codex.md
# Option B: Reference it in AGENTS.md: See https://github.com/buildoak/fieldwork-skills/skills/gsd-coordinator/SKILL.md
```

### Artifact directory setup

Workers occasionally write file artifacts (outputs exceeding 200 lines, deliverables). By default, these go to `_workbench/` inside this skill directory. A `.gitkeep` ships with the skill to create it.

If you prefer a different location -- a project scratch folder, a `tmp/` directory, wherever -- set the path when you first configure the skill. The SKILL.md uses `<artifacts-dir>` as a placeholder throughout. Replace it with your chosen path, or leave the default:

```
Default:  .claude/skills/gsd-coordinator/_workbench/
Override: any directory you prefer for working artifacts
```

The coordinator will write artifacts to `<artifacts-dir>/YYYY-MM-DD-{engine}-{description}.md`. Deliverables (final outputs) always go to their canonical destination, not the artifacts directory.

## Staying Updated

This skill ships with an UPDATES.md changelog and UPDATE-GUIDE.md for your AI agent.

After installing, tell your agent: "Check UPDATES.md in the gsd-coordinator skill for any new features or changes."

When updating, tell your agent: "Read UPDATE-GUIDE.md and apply the latest changes from UPDATES.md."

## Two Operating Modes

### 1. Claude Code mode (full orchestration)

Use when the coordinator can dispatch workers and close the loop directly.

- Can orchestrate the full loop: dispatch -> verify -> synthesize -> fix -> re-dispatch
- Can use `agent-mux` for Codex, Codex Spark, Claude, and OpenCode workers
- Can read/write files and run verification commands

### 2. Codex mode (planner only)

Use when `gsd-coordinator` is loaded by a Codex worker that cannot orchestrate nested workers directly.

- Reads this runbook as a decision framework
- Selects pattern, workers, prompts, and artifacts
- Returns an execution plan instead of dispatching nested workers
- Must return `status: needs-orchestrator` so a parent orchestrator executes the plan

## Know Your Workers

Match the right worker to each step:

- Claude Opus 4.6 (`--engine claude`): Natural orchestrator. Thrives on ambiguity, decides from available info, and writes strong prompts. Use for architecture, synthesis, open-ended exploration, and prompt crafting.
- Codex 5.3 (`--engine codex`): Precise executor. Pedantic, thorough, and detail-attentive. Needs explicit scope: one goal, specific files, explicit output path. Use `--reasoning high` for implementation; reserve `xhigh` for deep audits.
- Codex Spark (`--engine codex --model gpt-5.3-codex-spark`): Same precision style, much faster, smaller context window. Use for parallel workers, filesystem scanning, and focused medium-difficulty tasks.
- OpenCode (`--engine opencode`): Supplemental third-opinion engine for model-lineage diversity.
  - `kimi`
  - `glm-5`
  - `opencode-minimax`
  - `free`

## Default Playbook

For any task, follow this sequence. Deviate when you have a reason.

1. Triage: read the task and identify inputs, outputs, and constraints.
2. Pick a pattern: Implementation, Audit, Research, or Fan-Out.
3. Select skills: for each step, identify which skills (if any) the worker needs.
4. Choose workers: match each step to the right engine.
5. Write prompt specs: one goal, specific files, explicit output path.
6. Run: execute workers with skills injected and parse output to extract the response field.
7. Verify: read artifacts, check quality, fix or re-run if needed.
8. Return: write the primary artifact, compose summary, report status.

## Model Selection Heuristics

### The Core Question: What Does This Step Need?

| Step needs... | Use | Why |
|---|---|---|
| Exploration, ambiguity resolution | Claude | Codex flounders without scope |
| Precise implementation | Codex (`high`) | Pedantic, detail-oriented |
| Deep architecture audit | Codex (`xhigh`) | Catches edge cases `high` misses |
| Fast parallel grunt work | Codex Spark | Speed and focus on bounded tasks |
| Synthesis or documentation | Claude | Strong structured output |
| Third-opinion verification | OpenCode | Independent lineage cross-check |

### Fan Out vs Go Deep

Fan out (parallel workers) when subtasks are independent, speed matters, tasks are medium difficulty, or you need broad coverage.

Go deep (single worker, `high`/`xhigh`) when multi-file reasoning is required, context pressure is high, the task already failed once, or getting it wrong has high downstream cost.

### Escalation Heuristic

Start at `high`. If wrong or incomplete, escalate to `xhigh`. If `xhigh` also fails, fix the prompt and decomposition; do not retry blindly.

## Orchestration Patterns

### 10x Pattern (Codex Generate + Opus Audit)

Most validated pipeline. Different blind spots produce higher confidence.

1. Spawn Codex at `high` to generate or refactor.
2. Read its output yourself (you are Opus).
3. Fix issues or spawn another Codex pass.
4. Write the final artifact and return summary.

Use when implementation, code review, or mechanical refactoring is needed. Skip when inline work is faster or the task is purely writing/synthesis.

### Fan-Out

Spawn N parallel workers on independent subtasks.

Workers return inline by default. If output exceeds 200 lines, write to `<artifacts-dir>/YYYY-MM-DD-{engine}-{topic}.md`.

Read all worker outputs and synthesize into one final output.

### Research + Synthesize

Read relevant files and references. Use web search if needed. Synthesize into one artifact and return summary.

### Triple-Check

Use three model lineages for high-stakes work.

1. Claude frames/decomposes approach.
2. Codex implements or performs core verification.
3. OpenCode provides independent verification.

## Bring Your Own Skills

Skills are operational blueprints. Each skill `SKILL.md` bundles domain knowledge, conventions, and CLI workflows into a reusable playbook.

When dispatching a worker with `agent-mux`, inject only the relevant skill(s):

```bash
agent-mux --engine codex --skill your-skill --reasoning high "Search for auth architecture docs"
```

```bash
agent-mux --engine codex --skill your-read-skill --skill your-write-skill --reasoning high "Read the existing spec, then write the updated version"
```

Rules:

- A skill-equipped worker should follow the skill playbook, not ad-hoc reasoning.
- Do not over-inject. Pick only skills needed for that subtask.
- If no skill fits, prompt the worker directly. Skills are an accelerator, not a requirement.

## Output Contract

Default: return inline.

Workers return focused summaries inline by default. Do not write file artifacts unless output exceeds 200 lines or a deliverable is explicitly required.

When files are needed:

- Over 200 lines: write to `<artifacts-dir>/YYYY-MM-DD-{engine}-{description}.md` (defaults to `_workbench/` inside this skill directory; see [Artifact directory setup](#artifact-directory-setup))
- Deliverables: write directly to final destination (for example `<your-project>/research/` or other project folders)

Naming when files are written: `YYYY-MM-DD-{engine}-{description}.md`

- `engine` = `codex` | `claude` | `spark` | `opencode` | `coordinator`
- `description` = descriptive kebab-case
- Parallel workers: add suffixes like `YYYY-MM-DD-spark-topic-a.md` and `YYYY-MM-DD-spark-topic-b.md`

Minimal frontmatter when files are written:

- `date: YYYY-MM-DD`
- `engine: codex | claude | spark | opencode | coordinator`
- `status: complete | partial | error`

Sandbox rule: Codex workers that write files must use `--sandbox workspace-write --cwd <repo-root>`.

Format Cards: when writing to canonical locations (not `<artifacts-dir>/`), use the correct frontmatter required by your project's conventions. Do not invent domains.

## Context Discipline

- Workers return briefs, not dumps. Ask for focused summaries like "Return a 3-5 sentence summary" or "Return the file path and a one-paragraph verdict."
- Pass paths, not content. Hand off file paths between steps; the next worker reads what it needs.
- Check background workers with `tail -n 20` via Bash. Do not load full long output files into context.
- Scope your reads. Verify specific sections, not whole files. Use offset/limit or Grep when possible.

## Return Contract

When finished, return to the main thread:

1. File path to the primary artifact (if any)
2. 3-5 sentence summary of work, findings, and decisions
3. Status: `done` | `blocked` | `needs-decision` | `needs-orchestrator` (planner mode only)

Never dump raw content back. Always return path + summary + status.

## Anti-Patterns

- Blind retry: if a worker fails, diagnose root cause (engine choice, scope, skill, or prompt quality) before retrying.
- Context bombing: do not paste full artifacts into prompts; write to file and pass paths.
- Wrong worker: do not send exploration to Codex or focused implementation to Claude when Codex would be faster.
- Spawning Claude for more Claude: you are Claude; use Codex for diversity.
- `xhigh` for routine work: reserve for audits and deep analysis; `high` is the default workhorse.
- Assuming main thread context: read what you need; do not assume prior context is present.
- Skillless dispatch: when a relevant skill exists, inject it.
- Over-prompting workers: do not write novels; give one goal, relevant skill(s), specific files, and output path, then let the skill carry domain knowledge.
- Over-verification: do not run Triple-Check for low-risk tasks where simpler verification is sufficient.

## Bundled Resources

- `agent-mux` CLI and reference docs: https://github.com/buildoak/agent-mux
- Use the upstream `agent-mux` repo for CLI flags, output format, and engine-specific runtime notes
