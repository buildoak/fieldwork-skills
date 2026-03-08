# Cost Reference

Use this reference to estimate per-story generation cost before execution.

## Video Generation Cost per Second

| Model | Cost/sec | 5s clip | 10s clip |
|-------|----------|---------|----------|
| LTX-2.3 | $0.04 | $0.20 | $0.40 |
| Wan | $0.05 | $0.25 | $0.50 |
| Hailuo | $0.046 | $0.23 | $0.46 |
| Kling V3 | $0.168 | $0.84 | $1.68 |
| Veo 3.1 | $0.20 | $1.00 | $2.00 |
| Sora 2 | $0.30 | $1.50 | $3.00 |

## Supporting Costs

- Character reference images: `$0.03/image` (FLUX.2-Pro via `image-gen`)
- Budget tier: `2 images/character`
- Standard+ tier: `6 images/character`
- Keyframe generation: `$0.03/shot` (FLUX.2-Pro)
- QA review: `$0.10/review` (Claude Vision)
- ElevenLabs voiceover: `$0.20/minute`
- Veo native audio: included in video cost
- Claude decomposition: about `$0.05 per story`

## Tier Estimates

Assumptions used in table:

- regen buffer = 30%
- 3 primary characters
- one QA pass per shot
- ElevenLabs used except where native audio replaces it

| Tier | Shots | Duration | Video | Char Sheets (3 chars) | Keyframes | QA | Audio | Regen Buffer (30%) | **Total** |
|------|-------|----------|-------|-----------------------|-----------|----|-------|--------------------|-----------|
| Budget | 5 | 30s | $1.20 | $0.18 | $0.15 | $0.50 | $0.10 | $0.36 | **~$2.50** |
| Standard | 8 | 60s | $8.06 | $0.54 | $0.24 | $0.80 | $0.20 | $2.42 | **~$12.30** |
| Premium | 12 | 90s | $15.12 | $1.08 | $0.36 | $1.20 | $0.30 | $4.54 | **~$22.60** |
| Ultra | 15 | 120s | $24.00 | $1.35 | $0.45 | $1.50 | $0.40 | $7.20 | **~$34.90** |

## Cost Formula

```text
total = (video_cost * 1.3) + char_sheets + keyframes + qa + audio + decomposition
```

Where:

- `video_cost = sum(shot_duration * model_cost_per_sec)` for all shots
- `char_sheets = num_chars * images_per_char * 0.03`
- `keyframes = num_shots * 0.03`
- `qa = num_shots * 0.10`
- `audio = total_minutes * 0.20` (ElevenLabs) or `0` (Veo native/skipped)
- `1.3 multiplier = 30% re-generation buffer`

## Quick Sanity Math

### Budget example

- video: `30s * 0.04 = 1.20`
- video with buffer: `1.20 * 1.3 = 1.56`
- extras: `0.18 + 0.15 + 0.50 + 0.10 + 0.05 = 0.98`
- total: `1.56 + 0.98 = 2.54` -> about `$2.50`

### Standard example

- video base: `$8.06`
- buffered video: `$10.48`
- extras with decomposition: `0.54 + 0.24 + 0.80 + 0.20 + 0.05 = 1.83`
- expected total: about `$12.31`

## Practical Budget Controls

If cost rises above plan:

1. reduce average shot duration first
2. reduce regeneration loop count
3. swap model on non-hero shots
4. reduce character sheet views only on budget tier
5. skip external audio when Veo native audio is acceptable

## Waste Factor (LTX Minimum Duration)

LTX-2.3 enforces a 6s minimum. For short target shots, generated seconds are partially wasted.

### Waste rate by target shot duration

| Target Duration | Generated (LTX) | Useful % | Waste % |
|----------------|-----------------|----------|---------|
| 1s | 6s | ~17% | ~83% |
| 2s | 6s | ~33% | ~67% |
| 3s | 6s | ~50% | ~50% |
| 4s | 6s | ~67% | ~33% |
| 6s+ | 6s+ | 100% | 0% |

For 1-2s target shots, effective waste is 70-80% of generated video and credits.

### Cost-per-useful-second
Cost-per-generated-second is misleading when minimum duration creates waste. The real metric is cost-per-useful-second:
```text
cost_per_useful_second = (generated_duration * model_cost_per_sec) / target_duration
```
For a 1s LTX shot: `(6 * $0.04) / 1 = $0.24/useful-second` — 6x the listed rate.

### Budget recommendation for interactive workflow
In interactive workflows (human-in-the-loop, iterative approvals), add a 30% buffer on top of baseline estimates to absorb re-generations triggered by style rejection, prompt iteration, and approval cycles.

## Reporting Convention

For each run, log:

- planned tier
- actual model mix by shot
- planned total vs actual total
- regeneration count
- cost delta reason

This keeps future estimates accurate and prevents hidden spend drift.
