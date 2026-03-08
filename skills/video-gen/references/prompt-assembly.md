# Prompt Assembly

This doc explains how `story-gen` compiles character, scene, and shot JSON into model-ready prompts.

## Assembly Pipeline

1. Character JSON -> natural language identity (`character_json_to_prompt`)
2. Scene JSON -> environment description (`scene_json_to_prompt`)
3. Shot JSON -> camera + action + mood fragment
4. Combine fragments:
   `{shot_size} {angle} shot. {character_desc}. {scene_desc}. {action}. {mood}. Camera: {movement}.`
5. Adapt for target model prompt limits (compress or expand)

## Why this works

- JSON is source of truth.
- Prompt wording can vary by model without losing intent.
- Identity remains stable when character anchors are always present.

## Sample Inputs

### Character JSON (Maya)

```json
{
  "name": "Maya",
  "age": 28,
  "ethnicity": "East Asian",
  "hair": {"color": "jet black", "style": "bob"},
  "clothing": {"jacket": "red leather jacket"},
  "accessories": {"glasses": "round wire-frame glasses", "ring": "silver index ring"}
}
```

### Scene JSON (cafe)

```json
{
  "location": "cozy cafe interior",
  "lighting": "warm golden light through rain-streaked window",
  "props": ["wooden table", "ceramic coffee cup"],
  "mood": "intimate"
}
```

### Shot JSON

```json
{
  "camera": {"shot_size": "medium close-up", "angle": "eye level", "movement": "slow zoom in"},
  "action": "Maya lifts her coffee cup and looks toward her friend",
  "mood": "thoughtful"
}
```

## Fragment Outputs

### `character_json_to_prompt`

```text
A 28-year-old East Asian woman with shoulder-length jet black bob, warm ivory skin, wearing a red leather jacket, round wire-frame glasses, silver ring on her right index finger.
```

### `scene_json_to_prompt`

```text
Inside a cozy cafe with a wooden table, warm golden light entering through a rain-streaked window.
```

### Shot fragment

```text
Medium close-up shot at eye level. She lifts her coffee cup and looks toward her friend. Thoughtful mood. Camera slowly zooms in.
```

## Base Combined Prompt

```text
Medium close-up eye level shot. A 28-year-old East Asian woman with shoulder-length jet black bob, warm ivory skin, wearing a red leather jacket, round wire-frame glasses, silver ring on her right index finger. Inside a cozy cafe with a wooden table, warm golden light entering through a rain-streaked window. She lifts her coffee cup and looks toward her friend. Thoughtful, intimate mood. Camera: slow zoom in.
```

## Model-Specific Examples

### LTX-2.3 (about 200 tokens, verb-heavy)

```text
Medium shot, 28-year-old woman with black bob and red leather jacket sits at cafe table, slowly lifting coffee cup, warm golden light streaming through window, camera gently zooming in.
```

Guidance:

- keep action verbs strong
- keep identity compact but intact
- remove secondary adjectives first

### Kling V3/O3 (about 500 tokens, detailed spatial)

```text
Medium close-up shot at eye level. A 28-year-old East Asian woman with warm ivory skin, shoulder-length jet black bob, oval face, wearing a red leather jacket over white t-shirt. She sits at a wooden cafe table near a rain-streaked window. Warm afternoon light illuminates her face. She lifts a ceramic coffee cup with her right hand, a silver ring visible on her index finger. Round wire-frame glasses reflect the light. Calm, observant expression. Camera slowly zooms in. Cozy, intimate mood.
```

Guidance:

- include spatial relationships
- include accessories and props
- for O3, prepend reference syntax lines when available

### Veo 3.1 (about 300 tokens, dialogue-aware)

```text
Medium close-up of a 28-year-old East Asian woman with black bob and red leather jacket at a cafe table. Warm golden light. She lifts her coffee cup and says: "I've been thinking about what you said." Camera slowly zooms in. Thoughtful, intimate mood.
```

Guidance:

- include dialogue text inline when spoken output is needed
- keep visual context concise to preserve speech clarity

## Prompt Limits and Compression Strategy

Approximate prompt budgets:

- LTX-2.3: about 200 tokens
- Veo 3.1: about 300 tokens
- Kling V3/O3: about 500 tokens

Compression priority order:

1. character identity
2. action
3. environment
4. camera
5. mood

Never compress character identity. Identity loss causes consistency failure.

Safe compression examples:

- camera phrase -> `slow zoom in`
- environment -> `cafe interior, warm window light`
- mood -> `thoughtful`

## Multi-Character Rule

For multi-character shots, list each character explicitly.

Example:

```text
Maya in red leather jacket sits left of frame. Leo in charcoal coat sits right of frame. They face each other across a wooden table.
```

## Interactive Workflow

In interactive (human-in-the-loop) mode, prompts live on disk rather than being assembled in memory. This allows human review and edit at each stage.

### Prompt file location
Each scene gets a dedicated folder. Shot prompts are stored as files:
```text
scenes/NN/prompt.md
```
Where `NN` is zero-padded shot number (e.g. `01`, `02`). The orchestration script reads `prompt.md` at generation time, not from memory.

### Style keyword injection
Style keywords are declared in the project manifest (`manifest.md`) under a `Style Keywords` section. The `gen_keyframe.py` script reads the manifest and injects style keywords into every keyframe prompt automatically. Do not hardcode style keywords inside individual `prompt.md` files — they belong in the manifest so they can be changed globally.

### No preset hardcoding
Never hardcode image-gen presets (e.g. city-playbook, painterly-style) directly in prompts. All style must be explicit keyword-based and declared in the manifest where the user can approve and adjust it. Presets carry hidden style baggage that corrupts video output (see consistency-guide.md Style Consistency section).

### Review gate
In interactive mode, the workflow pauses after keyframe generation for human style approval. Do not proceed to video generation until the user explicitly approves the keyframe style. This is the cheapest point to catch and fix style mismatches.

## Validation Checklist

Before sending prompt:

- character anchor included
- location + lighting included
- action in present tense
- camera movement specified
- prompt length fits model budget
- model-specific syntax applied

If validation fails, rebuild from JSON rather than patching the prompt manually.
