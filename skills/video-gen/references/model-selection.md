# Model Selection

Select the lowest-cost model that satisfies the strictest shot requirement.

## Decision Tree

```text
Need character consistency across shots?
-> Kling O3 (element references, premium tier)

Need dialogue or lip sync?
-> Veo 3.1 (native audio, ultra tier)

Need cheap prototype loop?
-> LTX-2.3 (fast, $0.04/s, budget tier)

Need stylized/anime-adjacent look?
-> Kling V3 or Hailuo

Need pure budget run?
-> Wan ($0.05/s)

Need cinematic ultra quality?
-> Sora 2 ($0.30/s)
```

## Per-Model Table

| Model | i2v Support | Max Duration | Prompt Limit | Cost/sec | Consistency Method | Best For |
|-------|-------------|--------------|--------------|----------|--------------------|----------|
| LTX-2.3 | Yes | 10s (min 6s) | ~200 tokens | $0.04 | Prompt only | Budget prototypes, fast iteration |
| Wan | Yes | 5s | ~300 tokens | $0.05 | Prompt only | Budget with better quality |
| Hailuo | Yes | 6s | ~300 tokens | $0.046 | Prompt only | Stylized, anime-adjacent |
| Kling V3 | Yes | 10s | ~500 tokens | $0.168 | Multi-shot syntax | Standard production |
| Kling O3 | Yes | 10s | ~500 tokens | TBD | Element refs | Premium consistency |
| Veo 3.1 | Yes | 8s | ~300 tokens | $0.20 | Prompt + native audio | Dialogue scenes |
| Sora 2 | Yes (remix) | 10s | ~300 tokens | $0.30 | i2v remix | Cinematic ultra |

## Tier Mapping

- `budget` -> `LTX-2.3`
- `standard` -> `Kling V3`
- `premium` -> `Kling O3` (fallback: `Kling V3`)
- `ultra` -> `Veo 3.1` or `Sora 2`

## API Notes by Model

### LTX-2.3

- Keep prompts compact and verb-heavy.
- Target about 150-200 tokens.
- No element API; consistency is text anchoring only.
- **Duration constraint (production finding):** LTX-2.3 only accepts 6, 8, or 10 second durations. No sub-6s clips are possible.
  - Fast-cut sequences (1-2s per shot) require generating 6s and trimming with FFmpeg — wastes ~80% of generated video and credits.
  - For short shots, consider: (1) generate 6s and trim, (2) use fewer/longer shots (3-4s each), or (3) route to Kling (2s minimum, higher cost but no waste).
  - Also update the per-model table Max Duration: actual minimum is 6s, not arbitrary.

### Wan

- Similar flow to LTX with slightly better quality.
- Good budget fallback when LTX is too rough.
- Keep shots short and chain in edit.

### Hailuo

- Works well for stylized and anime-adjacent output.
- Put style words early in prompt.
- Keep identity details explicit to avoid style-over-identity drift.

### Kling V3

- Strong general-purpose production model.
- Supports richer spatial detail and longer prompt context.
- Good default for standard tier.

### Kling O3

- Use multi-reference prompt syntax for character assets.
- Reference support is in prompt syntax, not separate API parameter.
- Best choice when cast continuity is critical.

### Veo 3.1

- Native audio support for dialogue scenes.
- Include spoken line text in prompt when needed.
- Balance dialogue clarity with concise visual description.

### Sora 2

- Highest visual ceiling and highest cost.
- Use for hero shots and cinematic centerpiece sequences.
- i2v remix helps continuity when seeded from keyframes.

## Routing Heuristics by Shot Type

- Dialogue close-up -> Veo 3.1
- Continuity-critical character scene -> Kling O3
- Standard cinematic coverage -> Kling V3
- Fast prototype/blocking -> LTX-2.3
- Stylized montage -> Hailuo or Kling V3
- Hero cinematic reveal -> Sora 2

## Fallback Order

- `Kling O3 -> Kling V3`
- `Veo 3.1 -> Sora 2 -> Kling V3`
- `LTX-2.3 -> Wan`
- `Hailuo -> Kling V3`

## Production Learnings

### LTX-2.3 minimum duration
LTX-2.3 only generates 6s, 8s, or 10s clips — no sub-6s output is possible. Plan shot durations accordingly from the start. Do not design a storyboard with 1-3s clips and expect LTX to deliver them.

### Oil painting problem
Image-gen presets (e.g. city-playbook, painterly styles) carry their aesthetic into i2v keyframes. If a keyframe is painterly, the video will be painterly. The video model does not neutralize the keyframe's style — it amplifies it. Use explicit style keywords in every keyframe prompt rather than relying on presets.

### Fast-cut sequences (<3s per shot)
For fast-cut montages where target shot length is under 3s:
- Use Kling (2s minimum, no waste, higher cost per second)
- Or generate 6s with LTX and trim with FFmpeg — accepts ~70-80% waste
- Do not use LTX for fast-cut if budget efficiency matters
