# Installation Guide

Detailed installation instructions for AI agents. This guide covers both Claude Code and Codex CLI environments.

## Prerequisites

- **Homebrew** (macOS package manager)
- Optional dependencies installed per feature (see dependency matrix below)

## Claude Code Installation

Path: `.claude/skills/summarize/`

1. Clone the fieldwork repo:
```bash
git clone https://github.com/buildoak/fieldwork-skills.git /tmp/fieldwork
```
2. Copy this skill folder into your project:
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R /tmp/fieldwork/skills/summarize /path/to/your-project/.claude/skills/summarize
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
  echo "<!-- fieldwork-skill:summarize -->"
  cat /tmp/fieldwork/skills/summarize/SKILL.md
} >> /path/to/your-project/AGENTS.md
```

## Running Setup / Dependencies

### Step 1: Add the Homebrew tap and install summarize CLI

```bash
brew tap steipete/tap
brew install summarize
```

### Step 2: Verify the CLI is installed

```bash
summarize --version
```

Should print something like "summarize 0.x.x".

If `command not found`: run `eval "$(/opt/homebrew/bin/brew shellenv)"` (Apple Silicon) or `eval "$(/usr/local/bin/brew shellenv)"` (Intel Mac), then retry.

### Step 3: Install optional dependencies (as needed)

Each tool below unlocks a specific capability. Install only what you need.

| Tool | What it unlocks | Install command |
|------|----------------|-----------------|
| `yt-dlp` | YouTube video downloads and podcast audio extraction | `brew install yt-dlp` |
| `ffmpeg` | Video slide extraction and audio processing | `brew install ffmpeg` |
| `whisper-cli` | Local speech-to-text (~1.5GB download) | `brew install whisper-cli` |
| `markitdown` | PDF and document text extraction | `python3 -m pip install markitdown` |
| `uv` | Fast Python tool runner (alternative for markitdown) | `brew install uv` |
| `tesseract` | OCR for scanned images | `brew install tesseract` |

### No API keys needed for extraction mode

`--extract` mode works without any API keys. LLM summarization mode requires the relevant model provider key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.).

## Verification

```bash
# Check CLI version
summarize --version

# Quick test: extract text from a URL
summarize --extract "https://example.com" --plain | head -5
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `brew: command not found` | Install Homebrew from [https://brew.sh](https://brew.sh), restart terminal |
| `No available formula with the name "summarize"` | Run `brew tap steipete/tap` first, then `brew install summarize` |
| `summarize: command not found` | Add Homebrew to PATH: `eval "$(/opt/homebrew/bin/brew shellenv)"` then restart terminal |
| `Missing uvx/markitdown` (PDF mode) | `brew install uv` |
| YouTube returns empty transcript | No captions available, no yt-dlp/whisper. Install `brew install yt-dlp` |
| Audio transcription fails | Install `brew install whisper-cli` or set `OPENAI_API_KEY` |
| Podcast extraction fails | Check yt-dlp is installed: `brew install yt-dlp` |

## Platform Notes

- **macOS:** Primary instructions above work as written (`brew tap` + `brew install`).
- **Linux:** Either install [Linuxbrew](https://brew.sh) and follow the same steps, or check the [summarize repo](https://github.com/steipete/summarize) for alternative install methods.
- **Windows:** Use [WSL2](https://learn.microsoft.com/windows/wsl/install) and follow the Linux instructions inside your WSL terminal.
