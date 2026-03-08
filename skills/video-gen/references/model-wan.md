# Wan 2.5/2.6 Deep Dive

## Overview

Wan 2.5/2.6 (Alibaba) is the budget baseline for this stack. It is currently the cheapest
video model available in this catalog and is the best default choice for social-first,
rapid-turnaround work where cost per second matters more than premium texture realism.

## Endpoints

| Variant | Endpoint |
|---------|----------|
| T2V | `fal-ai/wan-25-preview/text-to-video` |
| I2V (v2.5) | `fal-ai/wan-25-preview/image-to-video` |
| I2V (v2.6) | `fal-ai/wan/v2.6/image-to-video` |

## Modes, Resolution, and Duration

- Modes: text-to-video (T2V), image-to-video (I2V)
- Resolution: `720p`, `1080p`
- Duration: `5s` or `10s`
- No listed frame-rate override in reference notes (use default model cadence)

## Audio Capabilities

- Native audio support is available from Wan 2.5+
- Supports dialogue, ambience, and background music when sourced from URL inputs
- Use audio flag at generation time in prompt payload:
  - `generate_audio: true`
  - Add concise audio intent into `prompt` (e.g. "quiet office ambience", "news anchor dialogue")
- Cost impact: ~$0.05/s without audio, ~$0.10/s with audio

## Pricing

| Mode | Cost |
|------|------|
| Video only | ~$0.05/s |
| With audio | ~$0.10/s |

This remains the cheapest option in the current catalog.

## Prompting Tips

- Start with a concise scene sentence, then add 2-3 temporal beats.
- Keep each prompt in one language for best compliance (Chinese or English).
- Keep camera motion explicit and sparse for stronger consistency:
  - `slow push in`, `track left`, `hold`
- For I2V, let motion inherit from source composition; avoid conflicting movement directives.
- Add emotional anchors for faces in motion sequences:
  - `focus on soft eyes`, `small confident smile`, `eyes track the door`

### Negative Prompt Support

Supported and should be kept short.  
Cap is **500 characters max** for negative prompts.

Example:

```
blurry, warped hands, text artifacts, subtitle labels, logo overlays, camera shake, flicker
```

### Bilingual Prompting

Wan supports bilingual usage; choose one primary language block to reduce drift.
If code-switching, group by line and keep each sentence short.

## Best Practices

1. Use `720p` + 5s for ideation, then scale to `1080p`/10s only for winners.
2. Keep I2V inputs stable: avoid ultra-dynamic source motion and keep subject framing simple.
3. Use negative prompts for recurring failures (blur/motion artifacts) instead of inflating the positive prompt.
4. Lock style early with 1-3 adjectives only (`cinematic, photoreal, clean lighting`).
5. Prefer longer pauses over fast cuts; Wan handles steady scenes better than abrupt direction changes.

## Failure Modes and Fixes

| Symptom | Fix |
|---------|-----|
| Temporal jitter around edges | Simplify motion verbs and reduce simultaneous subject/camera changes |
| Character drift | Add stronger identity cues and reduce shot complexity |
| Dialogue sounds flat/noisy | Keep fewer sound layers, disable ambient crowd effects first, then re-enable |
| Abrupt ending | Add ending beat in final 1s and request a natural tail-off |
| Over-saturated colors | Explicitly include `muted palette` and `natural skin tones` in prompt |

## Example Prompt Pattern

```
A woman in a white jacket walks through a rainy Tokyo crossing.
Long-lens background compression, cinematic 1080p.
As she looks up, the camera slowly tracks left and holds.
Background ambience: distant train horns, soft rain, low city traffic hum.
Narration: calm, soft female voice, calm but urgent.
Negative prompt: blurry, warped face, jittery camera, subtitles, logo.
```

