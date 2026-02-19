# Image Gen Updates

Structured changelog for AI agents. Read this to determine what changed and whether updates are safe to apply.

## 2026-02-20

### new-files

| File | Description |
|------|-------------|
| `presets/default.json` | Default preset (no style constraints, quality-focused defaults) |
| `references/style-consistency.md` | Reference image workflow, seed workflow, per-model consistency techniques |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `scripts/generate.py` | Added preset system, style reference images, system messages, prompt upsampling, enhanced model registry with `supports_system_message`/`supports_prompt_upsampling`/`prompt_format` fields. New CLI flags: `--preset`, `--style-ref`, `--system-prompt`, `--prompt-upsampling`/`--no-prompt-upsampling`. Enhanced output JSON with `enhanced_prompt`, `preset`, `style_refs`, `system_message_used` fields. All existing robustness preserved (input validation, binascii error handling, per-image parent dir creation). | No -- all new flags are optional, existing behavior unchanged when no new flags are used |
| `SKILL.md` | Added version 2.1.0, tools_required, triggers frontmatter. New sections: Style Presets, Style References, System Messages, Prompt Upsampling, credential management. Updated CLI flags table, anti-patterns, bundled resources index. | No -- additive only |
| `references/prompt-templates.md` | Added JSON structured prompts for Flux, GPT-5 system message template, NanoBanana JSON structure, Flux-specific rules, NanoBanana-specific rules, GPT-5 style consistency tips. Enhanced prompt example with JSON variant. Updated enhancement protocol with preset step. Added more anti-pattern entries. | No -- additive only |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
- `--model`, `--aspect-ratio`, and `--size` argparse defaults changed from hardcoded values to `None` for preset priority resolution. Effective defaults remain the same (flux.2-pro, 1:1, 2K) when no preset is used.
- New `presets/` directory created with `default.json`. Safe to copy.
- New `references/style-consistency.md` is a new file. Safe to copy.
- `generate.py` output JSON may now include additional fields (`enhanced_prompt`, `preset`, `style_refs`, `system_message_used`) that were not present before. Consumers should handle unknown fields gracefully.

## 2026-02-18

### new-files

| File | Description |
|------|-------------|
| `references/installation-guide.md` | Detailed agent-readable installation guide for Claude Code and Codex CLI |

### changed-files

| File | What changed | Breaking? |
|------|-------------|-----------|
| `SKILL.md` | Replaced verbose multi-section install block with concise Setup section delegating to installation guide | No -- same info, better organized |

### removed-files
(none)

### breaking-changes
(none)

### migration-notes
- New `references/installation-guide.md` is a new file (safe to copy)
- `SKILL.md` install section is shorter but all information moved to the installation guide

## 2026-02-17

### Initial release
All files are new. Copy the entire `image-gen/` directory.

| Category | Files |
|----------|-------|
| Core | `SKILL.md` |
| Scripts | `scripts/generate.py`, `scripts/edit.py`, `scripts/review.py` |
| References | `references/model-card.md`, `references/prompt-templates.md`, `references/api-reference.md` |
| Examples | `examples/` (showcase images) |
