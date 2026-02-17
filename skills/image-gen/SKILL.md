---
name: image-gen
description: |
  Image generation and editing via OpenRouter API. Five models from budget to premium,
  prompt engineering templates, vision-based quality review loop. Zero dependencies
  beyond Python stdlib. Use when: generate, create, draw, design, illustrate, edit,
  or modify images.
---

# image-gen

Generate and edit images via OpenRouter with a practical model-selection workflow, prompt-enhancement templates, and an optional vision-based quality review loop. This skill is built for reliable CLI use with Python stdlib-only scripts and JSON outputs that are easy to automate.

Terminology used in this file:
- **OpenRouter:** API gateway that provides access to multiple image models through one key.
- **Inpainting (mask-based editing):** Editing only selected regions of an image using a mask file.
- **JSON output contract:** Machine-readable output format your automation should parse directly.

## Setup

```bash
export OPENROUTER_API_KEY_IMAGES='your-key-here'
```

- **Claude Code:** copy this skill folder into `.claude/skills/image-gen/`
- **Codex CLI:** append this SKILL.md content to your project's root `AGENTS.md`

For the full installation walkthrough (prerequisites, API keys, verification, troubleshooting), see [references/installation-guide.md](references/installation-guide.md).

## Model selection

```text
What do you need?
  |
  +-- Fast + cheap + good enough?
  |     --> nanobanana (~$0.0004/image)
  |
  +-- High quality, no text?
  |     --> flux.2-pro (best visual quality)
  |
  +-- Text in the image?
  |     --> gpt-5-image (best text rendering)
  |
  +-- Image editing?
  |     +-- Describe changes in words --> gpt-5-image or nanobanana-pro
  |     +-- Paint mask area to change --> edit.py --mode openai
  |
  +-- Budget generation at scale?
  |     --> flux.2-klein (fastest, cheapest Flux)
  |
  +-- Quality + editing + reasoning?
        --> nanobanana-pro (best balance)
```

| Alias | Type | Cost | Best For |
|---|---|---|---|
| `flux.2-pro` | Image-only | ~$0.03/MP | Default high-quality generation |
| `flux.2-klein` | Image-only | ~$0.014/MP | Fast, budget generation |
| `gpt-5-image` | Text+Image | ~$0.04/image | Text rendering, complex edits |
| `nanobanana-pro` | Text+Image | ~$0.012/image | Balanced quality + editing |
| `nanobanana` | Text+Image | ~$0.0004/image | Lowest-cost generation |

Full comparison: `./references/model-card.md`

## Quick Reference

Default output directory in this skill: `./data/`

```bash
# Generate with default model (flux.2-pro)
python ./scripts/generate.py \
  --prompt "A red fox in snow" \
  --output-dir ./data/

# Generate with options (model, aspect ratio, size)
python ./scripts/generate.py \
  --prompt "Tokyo skyline at sunset" \
  --model nanobanana-pro \
  --aspect-ratio 16:9 \
  --size 2K \
  --output-dir ./data/

# Generate with text (GPT-5 Image)
python ./scripts/generate.py \
  --prompt 'Poster with text "HELLO WORLD" in bold sans-serif typography' \
  --model gpt-5-image \
  --output-dir ./data/

# Edit image (chat-based)
python ./scripts/edit.py \
  --mode openrouter \
  --input-image ./data/input.png \
  --prompt "Change the background to a sunset beach" \
  --model gpt-5-image \
  --output-dir ./data/

# Edit image (mask-based)
python ./scripts/edit.py \
  --mode openai \
  --input-image ./data/input.png \
  --mask ./data/mask.png \
  --prompt "Replace masked area with a small bonsai tree" \
  --openai-size 1024x1024 \
  --output-dir ./data/

# Review quality (auto mode)
python ./scripts/review.py \
  --image ./data/output.png \
  --original-prompt "A red fox in snow" \
  --auto
```

## Prompt engineering

### Enhance-before-generate protocol

1. Identify intent: photo, illustration, logo, diagram, etc.
2. Fill missing details: subject, style, lighting, composition, camera/look.
3. Tune prompt shape to model: concise for Flux, more explicit for GPT-5/NanoBanana family.
4. Add quality boosters that match requested style.

### Example: raw prompt -> enhanced prompt

- Raw prompt: `a cat in space`
- Enhanced prompt: `Orange tabby cat in a custom spacesuit floating in zero gravity, Earth visible in helmet reflection, dramatic rim lighting, cinematic framing, ultra-detailed, high contrast, clean background`

Templates and techniques: `./references/prompt-templates.md`

## Review loop

`review.py` scores generated output on four dimensions: `prompt_adherence`, `technical_quality`, `composition`, and overall `score`. It then returns a `verdict` plus critique and (when needed) a concrete prompt refinement.

Verdict actions:
- `accept` (score >= 7): deliver image
- `refine` (score 4-6): regenerate using `suggested_refinement`
- `reject` (score < 4): change model and/or significantly rework prompt

Use this loop for quality-critical outputs (client work, production assets, brand visuals), not for casual one-off image requests.

## Generation workflow

1. Choose model from the decision tree.
2. Enhance prompt using the protocol and templates.
3. Generate with `generate.py` or `edit.py`.
4. Review with `review.py` if quality requirements are high.
5. Iterate (refine prompt/model) or deliver final image.

## Script output contract

All scripts output JSON to stdout. Parse JSON, never plain text.

### generate.py success

```json
{
  "success": true,
  "path": "/abs/path/to/20260217-143052-flux-2-pro.png",
  "all_paths": ["/abs/path/to/20260217-143052-flux-2-pro.png"],
  "model": "black-forest-labs/flux.2-pro",
  "prompt": "the prompt used",
  "aspect_ratio": "16:9",
  "size": "2K",
  "cost_estimate": "~$0.120",
  "generation_time_ms": 8500,
  "image_count": 1
}
```

### generate.py / edit.py error

```json
{
  "success": false,
  "error": "HTTP 429: Too Many Requests",
  "details": "Rate limit exceeded...",
  "model": "black-forest-labs/flux.2-pro",
  "generation_time_ms": 150
}
```

### review.py output (auto mode)

```json
{
  "success": true,
  "mode": "auto",
  "score": 8,
  "prompt_adherence": 9,
  "technical_quality": 8,
  "composition": 7,
  "verdict": "accept",
  "critique": "Strong prompt adherence with vivid colors. Minor composition issue with empty right third.",
  "suggested_refinement": ""
}
```

## CLI flags reference

### generate.py

| Flag | Default | Description |
|---|---|---|
| `--prompt` | required | Generation prompt |
| `--model` | `flux.2-pro` | Model alias or full OpenRouter ID |
| `--aspect-ratio` | `1:1` | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| `--size` | `2K` | 1K, 2K, 4K |
| `--output-dir` | `./data/` | Output directory |
| `--output-file` | auto-named | Explicit output path |
| `--seed` | none | Random seed (model-dependent) |
| `--input-image` | none | Input image for editing |

### edit.py

| Flag | Default | Description |
|---|---|---|
| `--mode` | required | `openrouter` or `openai` |
| `--input-image` | required | Image to edit |
| `--prompt` | required | Edit instruction |
| `--mask` | none | Mask PNG (openai mode) |
| `--model` | `gpt-5-image` | Model for openrouter mode |
| `--openai-model` | `gpt-image-1` | Model for openai mode |
| `--openai-size` | none | Size for openai mode |
| `--openai-quality` | none | Quality for openai mode |
| `--output-dir` | `./data/` | Output directory |
| `--output-file` | auto-named | Explicit output path |

### review.py

| Flag | Default | Description |
|---|---|---|
| `--image` | required | Image to review |
| `--original-prompt` | required | Prompt used for generation |
| `--auto` | false | Auto-review via Anthropic API |

## Cost tracking

Report cost after every generation. Use the `cost_estimate` field from script output.

| Model | Typical Cost |
|---|---|
| NanoBanana | $0.0004 |
| Flux 2 Klein | $0.01-0.03 |
| NanoBanana Pro | $0.01-0.03 |
| Flux 2 Pro | $0.03-0.12 |
| GPT-5 Image | $0.03-0.10 |

Tip: for batch generation (5+ images), prefer NanoBanana or Flux 2 Klein to control spend.

## Error Handling

| Error | Action |
|---|---|
| No API key | Script exits with JSON error. Check env vars. |
| HTTP 429 (rate limit) | Wait 10s, retry. If persistent, switch model. |
| HTTP 402 (no credits) | Top up OpenRouter account. |
| No images in response | Check model supports image output. Try different model. |
| Timeout (>180s) | Model may be overloaded. Try Klein or NanoBanana for speed. |
| Image quality too low | Run review loop. Refine prompt or switch to higher-quality model. |

## Anti-Patterns

| Do NOT | Do Instead |
|---|---|
| Send raw user prompts to models | Always enhance prompts first |
| Use Flux for text in images | Use GPT-5 Image or NanoBanana Pro |
| Use GPT-5 for bulk generation | Use NanoBanana or Flux Klein (10-100x cheaper) |
| Skip cost reporting | Always report estimated cost |
| Retry same prompt on failure | Rework prompt or switch model |
| Use review loop for casual requests | Reserve for quality-critical work |
| Forget to set API key before running | Export required keys before running scripts |

## Bundled Resources Index

| Path | What | When to Load |
|---|---|---|
| `./scripts/generate.py` | Core image generation script | Every generation task |
| `./scripts/edit.py` | Chat-based and mask-based editing | Image modification requests |
| `./scripts/review.py` | Vision-based quality review | Quality-critical workflows |
| `./references/prompt-templates.md` | Prompt templates and enhancement techniques | Prompt engineering step |
| `./references/model-card.md` | Model capabilities, tradeoffs, pricing context | Model selection and optimization |
| `./references/installation-guide.md` | Detailed install walkthrough for Claude Code and Codex CLI | First-time setup or environment repair |
| `./references/api-reference.md` | API payload and integration details | Debugging and advanced usage |
| `./examples/` | Example outputs by model | Visual quality and style calibration |
| `./UPDATES.md` | Changelog for this skill | Checking new features/fixes |
| `./UPDATE-GUIDE.md` | Agent-oriented update instructions | Applying updates safely |

## Staying Updated

This skill ships with an `UPDATES.md` changelog and `UPDATE-GUIDE.md` for your AI agent.

After installing, tell your agent: "Check `UPDATES.md` in the image-gen skill for any new features."

When updating, tell your agent: "Read `UPDATE-GUIDE.md` and apply the latest changes from `UPDATES.md`."

Follow `UPDATE-GUIDE.md` so customized local files are diffed before any overwrite.

To check upstream updates directly from GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/buildoak/fieldwork-skills/main/skills/image-gen/UPDATES.md | head -40
```
