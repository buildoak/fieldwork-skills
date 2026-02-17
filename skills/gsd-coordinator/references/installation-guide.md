# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **agent-mux CLI** (upstream dependency -- dispatches work to Codex, Claude, and OpenCode engines)
- **Bun >= 1.0.0** (runtime for agent-mux)
- At least one engine API key:
  - `OPENAI_API_KEY` (for Codex engine)
  - `ANTHROPIC_API_KEY` (for Claude engine, optional)
  - `OPENROUTER_API_KEY` (for OpenCode engine, optional)

## Claude Code Installation

Path: `.claude/skills/gsd-coordinator/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/gsd-coordinator /path/to/your-project/.claude/skills/gsd-coordinator
```

## Codex CLI Installation

Codex reads `AGENTS.md` only (not `codex.md`, not `.codex/skills/`).

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Append `SKILL.md` to your project `AGENTS.md` with a marker:
```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:gsd-coordinator -->"
  cat /tmp/fieldwork/skills/gsd-coordinator/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Install agent-mux CLI

The GSD Coordinator dispatches workers via `agent-mux`. Install it first.

```bash
git clone https://github.com/buildoak/agent-mux.git /path/to/agent-mux
cd /path/to/agent-mux && ./setup.sh && bun link
```

If `bun: command not found`: install Bun first: `curl -fsSL https://bun.sh/install | bash`

### Step 2: Set API keys

At minimum, set `OPENAI_API_KEY` for Codex engine:

```bash
export OPENAI_API_KEY='sk-...'
```

Optional engines:
```bash
export ANTHROPIC_API_KEY='sk-ant-...'   # Claude engine
export OPENROUTER_API_KEY='sk-or-...'   # OpenCode engine
```

### Step 3: Artifact directory

Workers write artifacts to `_workbench/` inside this skill directory by default. A `.gitkeep` ships with the skill. Override if needed by setting a different path in your coordinator configuration.

## Verification

```bash
# Check agent-mux is installed
agent-mux --help

# Run one bounded worker task
agent-mux --engine codex --reasoning high "Say hello and confirm you are working"

# Verify JSON output
# Expect: { "success": true, "engine": "codex", "response": "...", ... }
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `agent-mux: command not found` | Install from https://github.com/buildoak/agent-mux and run `bun link` |
| `bun: command not found` | Install Bun: `curl -fsSL https://bun.sh/install \| bash` |
| `MISSING_API_KEY` | Set the required API key env var for the engine you are using |
| Worker returns non-JSON output | Re-run with `--effort high`, check stderr for errors |
| Worker output is empty or generic | Rewrite prompt with one goal, specific files, and expected output |

## Platform Notes

- **macOS:** Primary instructions above work as written.
- **Linux:** Same steps. Bun and agent-mux work on Linux natively.
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
