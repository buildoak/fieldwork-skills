# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Python 3.10+** (runtime for generation, editing, and review scripts)
- **OpenRouter API key** (required -- provides access to all image models)
- Optional: `OPENAI_API_KEY` (for mask-based inpainting via edit.py --mode openai)
- Optional: `ANTHROPIC_API_KEY` (for auto-review via review.py --auto)

No pip dependencies required -- all scripts use Python stdlib only.

## Claude Code Installation

Path: `.claude/skills/image-gen/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/image-gen /path/to/your-project/.claude/skills/image-gen
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
  echo "<!-- fieldwork-skill:image-gen -->"
  cat /tmp/fieldwork/skills/image-gen/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Get your OpenRouter API key

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Create an account
3. Add credits
4. Generate an API key

### Step 2: Set environment variables

```bash
export OPENROUTER_API_KEY_IMAGES='your-key-here'
# Fallback also supported:
# export OPENROUTER_API_KEY='your-key-here'
```

### Optional API keys

```bash
# For mask-based inpainting (edit.py --mode openai)
export OPENAI_API_KEY='your-openai-key-here'

# For auto-review (review.py --auto)
export ANTHROPIC_API_KEY='your-anthropic-key-here'
```

### Step 3: Create output directory

The default output directory is `./data/` inside the skill folder.

```bash
mkdir -p /path/to/skills/image-gen/data
```

## Verification

```bash
# Quick test: generate a simple image
python /path/to/skills/image-gen/scripts/generate.py \
  --prompt "A simple blue circle icon on white background" \
  --model nanobanana \
  --aspect-ratio 1:1 \
  --size 1K \
  --output-dir /path/to/skills/image-gen/data/

# Expect JSON output with "success": true and a file path
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No API key error | Set `OPENROUTER_API_KEY_IMAGES` or `OPENROUTER_API_KEY` env var |
| HTTP 429 (rate limit) | Wait 10s and retry. If persistent, switch to a different model. |
| HTTP 402 (no credits) | Top up your OpenRouter account at [https://openrouter.ai](https://openrouter.ai) |
| No images in response | Check model supports image output. Try a different model alias. |
| Timeout (>180s) | Model may be overloaded. Try `nanobanana` or `flux.2-klein` for speed. |
| `python: command not found` | Use `python3` instead, or install Python 3.10+ |

## Platform Notes

- **macOS:** Primary instructions above work as written. Python 3 is pre-installed on modern macOS.
- **Linux:** Same steps. Install Python if needed: `sudo apt install -y python3`.
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
