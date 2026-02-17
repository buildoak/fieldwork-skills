# summarize CLI -- Full Command Reference

Version: 0.11.1
Binary: `/opt/homebrew/bin/summarize`
Source: `brew install steipete/tap/summarize`

---

## Usage

```bash
summarize [options] [input]
```

**Input types:**
- URL (web page, YouTube, podcast, PDF URL)
- Local file path (PDF, image, audio, video, text)
- `-` for stdin (pipe content, including binary)

---

## Core Modes

| Flag | Mode | LLM Required | Description |
|------|------|:---:|-------------|
| (none) | Summarize | Yes | Extract + summarize via LLM |
| `--extract` | Extract | No | Print raw extracted content, exit |
| `--json` | JSON | Depends | Structured output with diagnostics |
| `--slides` | Slides | Optional | Extract video slides inline |

---

## All Flags

### Input & Extraction

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--extract` | boolean | false | Print extracted content and exit (no LLM) |
| `--format` | `md`, `text` | `text` (URLs: `md` in extract mode) | Content output format |
| `--preprocess` | `off`, `auto`, `always` | `auto` | Use uvx/markitdown for PDFs and binary files |
| `--markdown-mode` | `off`, `auto`, `llm`, `readability` | `readability` | HTML-to-Markdown conversion mode |
| `--firecrawl` | `off`, `auto`, `always` | `auto` | Firecrawl usage for anti-bot sites |
| `--max-extract-characters` | integer | unlimited | Limit extract output length |

### YouTube & Video

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--youtube` | `auto`, `web`, `no-auto`, `yt-dlp`, `apify` | `auto` | YouTube transcript source |
| `--video-mode` | `auto`, `transcript`, `understand` | `auto` | Video handling strategy |
| `--slides` | boolean | false | Extract slides (scene detection via ffmpeg) |
| `--slides-ocr` | boolean | false | Run OCR on extracted slides (requires tesseract) |
| `--slides-dir` | path | `./slides` | Output directory for slide images |
| `--slides-scene-threshold` | 0.1-1.0 | 0.3 | Scene detection sensitivity |
| `--slides-max` | integer | 6 | Maximum slides to extract |
| `--slides-min-duration` | seconds | 2 | Minimum seconds between slides |
| `--slides-debug` | boolean | false | Show slide file paths instead of inline rendering |
| `--timestamps` | boolean | false | Include timestamps in transcripts |

### Audio Transcription

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--transcriber` | `auto`, `whisper`, `parakeet`, `canary` | `auto` | Transcription backend |

### LLM Summarization

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--model` | `auto`, `provider/model`, `cli/provider` | `auto` | LLM model selection |
| `--cli` | `claude`, `gemini`, `codex`, `agent` | - | Use CLI provider as backend |
| `--length` | `short\|medium\|long\|xl\|xxl` or char count | `xl` | Summary length guideline |
| `--max-output-tokens` | integer | - | Hard cap for LLM output tokens |
| `--force-summary` | boolean | false | Force LLM even if content is short |
| `--prompt` | text | - | Override summary prompt |
| `--prompt-file` | path | - | Read prompt from file |
| `--language, --lang` | language code or `auto` | `auto` | Output language |
| `--timeout` | duration (30s, 2m, 5000ms) | `2m` | Fetch + LLM timeout |
| `--retries` | integer | 1 | LLM retry attempts on timeout |

### Output & Display

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--json` | boolean | false | Structured JSON output with metrics |
| `--stream` | `auto`, `on`, `off` | `auto` | Stream LLM output (TTY only) |
| `--plain` | boolean | false | Raw text, no ANSI/OSC rendering |
| `--no-color` | boolean | false | Disable ANSI colors |
| `--theme` | `aurora`, `ember`, `moss`, `mono` | - | CLI color theme |
| `--verbose` | boolean | false | Debug info to stderr |
| `--debug` | boolean | false | Alias for --verbose + detailed metrics |
| `--metrics` | `off`, `on`, `detailed` | `on` | Metrics display |

### Cache

| Flag | Description |
|------|-------------|
| `--no-cache` | Bypass LLM summary cache |
| `--no-media-cache` | Disable media download cache (yt-dlp) |
| `--cache-stats` | Print cache stats and exit |
| `--clear-cache` | Delete cache database and exit |

### Meta

| Flag | Description |
|------|-------------|
| `-V, --version` | Print version |
| `-h, --help` | Display help |

---

## Environment Variables

### LLM Provider Keys (for summarization mode only)

| Variable | Required For |
|----------|-------------|
| `ANTHROPIC_API_KEY` | `anthropic/...` models |
| `OPENAI_API_KEY` | `openai/...` models + Whisper cloud transcription |
| `GEMINI_API_KEY` | `google/...` models |
| `XAI_API_KEY` | `xai/...` models |
| `OPENROUTER_API_KEY` | OpenRouter routing |
| `Z_AI_API_KEY` | `zai/...` models |

### Extraction & Transcription

| Variable | Purpose |
|----------|---------|
| `FIRECRAWL_API_KEY` | Anti-bot website extraction fallback |
| `APIFY_API_TOKEN` | YouTube transcript fallback (Apify actor) |
| `FAL_KEY` | FAL AI Whisper fallback for audio |
| `GROQ_API_KEY` | Groq Whisper for audio transcription |
| `YT_DLP_PATH` | Custom path to yt-dlp binary |
| `SUMMARIZE_YT_DLP_COOKIES_FROM_BROWSER` | yt-dlp cookies source (e.g., `chrome`) |

### Local Transcription

| Variable | Purpose |
|----------|---------|
| `SUMMARIZE_WHISPER_CPP_MODEL_PATH` | Custom whisper.cpp model path |
| `SUMMARIZE_WHISPER_CPP_BINARY` | Custom whisper binary (default: `whisper-cli`) |
| `SUMMARIZE_DISABLE_LOCAL_WHISPER_CPP` | Set to `1` to force remote transcription |
| `SUMMARIZE_ONNX_PARAKEET_CMD` | Parakeet ONNX command (use `{input}` placeholder) |
| `SUMMARIZE_ONNX_CANARY_CMD` | Canary ONNX command |
| `SUMMARIZE_TRANSCRIBER` | Default transcriber (auto/whisper/parakeet/canary) |

### CLI Provider Paths

| Variable | Purpose |
|----------|---------|
| `CLAUDE_PATH` | Path to Claude CLI binary |
| `CODEX_PATH` | Path to Codex CLI binary |
| `GEMINI_PATH` | Path to Gemini CLI binary |
| `AGENT_PATH` | Path to Cursor Agent CLI binary |

### Display

| Variable | Purpose |
|----------|---------|
| `SUMMARIZE_MODEL` | Override default model selection |
| `SUMMARIZE_THEME` | CLI theme (aurora/ember/moss/mono) |
| `SUMMARIZE_TRUECOLOR` | Force 24-bit color |
| `SUMMARIZE_NO_TRUECOLOR` | Disable 24-bit color |

### Base URL Overrides

| Variable | Purpose |
|----------|---------|
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint |
| `OPENAI_WHISPER_BASE_URL` | Whisper endpoint override |
| `ANTHROPIC_BASE_URL` | Anthropic endpoint override |
| `GOOGLE_BASE_URL` / `GEMINI_BASE_URL` | Google endpoint override |
| `XAI_BASE_URL` | xAI endpoint override |
| `Z_AI_BASE_URL` | Z.AI endpoint override |

---

## Length Presets

| Preset | Target Chars | Range |
|--------|-------------|-------|
| `short` / `s` | ~900 | 600-1,200 |
| `medium` / `m` | ~1,800 | 1,200-2,500 |
| `long` / `l` | ~4,200 | 2,500-6,000 |
| `xl` | ~9,000 | 6,000-14,000 |
| `xxl` | ~17,000 | 14,000-22,000 |

Custom: any integer >= 50 (e.g., `20000`, `20k`).

---

## Subcommands

| Command | Purpose |
|---------|---------|
| `summarize daemon install --token TOKEN` | Install daemon for Chrome extension |
| `summarize transcriber setup` | Configure local ONNX transcription |
| `summarize slides URL` | Slides-only mode |
| `summarize refresh-free` | Refresh OpenRouter free model config |

---

## Examples

```bash
# Basic extraction
summarize --extract "https://example.com" --plain
summarize --extract "https://example.com" --format md --plain

# YouTube
summarize --extract "https://www.youtube.com/watch?v=VIDEO_ID" --plain
summarize --extract "https://www.youtube.com/watch?v=VIDEO_ID" --timestamps --plain
summarize --extract "https://www.youtube.com/watch?v=VIDEO_ID" --slides --slides-ocr --plain

# Podcast
summarize --extract "https://feeds.example.com/podcast.xml" --plain
summarize --extract "https://podcasts.apple.com/us/podcast/SHOW/EPISODE" --plain

# PDF
summarize --extract "https://example.com/doc.pdf" --plain
summarize --extract "/local/path/file.pdf" --plain

# Image OCR
summarize --extract "/path/to/image.png" --plain

# Audio/Video
summarize --extract "/path/to/audio.mp3" --plain
summarize --extract "/path/to/video.mp4" --plain

# Stdin
pbpaste | summarize --extract - --plain
cat file.pdf | summarize --extract - --plain

# LLM summarization (requires API key)
summarize "https://example.com" --model anthropic/claude-sonnet-4-5 --length long
summarize "https://example.com" --json --model openai/gpt-5-mini

# With custom prompt
summarize "https://example.com" --prompt "List all technical decisions mentioned" --model auto

# Verbose / debug
summarize --extract "https://example.com" --verbose --plain
```
