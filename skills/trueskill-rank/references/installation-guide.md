# TrueSkill Rank Installation Guide

## Prerequisites

- **Python 3.11+** -- verify with `python3 --version`
- **pip** -- verify with `pip3 --version`

## Install TrueSkill Library

```bash
pip install trueskill
```

Verify: `python3 -c "import trueskill; print(trueskill.__version__)"`

Expected output: `0.4.5` (or later)

## agent-mux (Optional, Recommended)

agent-mux dispatches ranking prompts to Codex Spark workers in parallel. Without it, the script falls back to direct OpenAI API calls (requires `OPENAI_API_KEY`).

If agent-mux is installed as a fieldwork skill alongside trueskill-rank, the script auto-discovers it. Otherwise, ensure `agent-mux` is on your `PATH` or set `AGENT_MUX_PATH` to the binary location.

## API Fallback

If agent-mux is not available, the script uses the OpenAI API directly via `urllib.request` (stdlib, zero extra deps). This requires:

```bash
export OPENAI_API_KEY="sk-..."
```

The fallback uses `gpt-4o-mini` by default.

## Install for Claude Code

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /path/to/fieldwork/skills/trueskill-rank /path/to/your-project/.claude/skills/trueskill-rank
```

## Install for Codex CLI

Append the SKILL.md content to your project's root `AGENTS.md`:

```bash
touch /path/to/your-project/AGENTS.md
{
  echo
  echo "<!-- fieldwork-skill:trueskill-rank -->"
  cat skills/trueskill-rank/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Verify Installation

```bash
python3 -c "import trueskill; print('trueskill OK')"
python3 /path/to/skills/trueskill-rank/scripts/trueskill-rank.py --help
```

Both commands should complete without errors.
