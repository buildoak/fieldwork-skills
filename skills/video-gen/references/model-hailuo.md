# MiniMax Hailuo-02 Deep Dive

## Overview

MiniMax Hailuo-02 is the stylization choice in this catalog, strongest for anime-leaning
imagery, expressive micro-movements, and controllable camera behavior. It trades higher
cost than Wan for more distinct stylistic output.

## Endpoints (Standard vs Pro)

| Profile | Mode | Endpoint |
|---------|------|----------|
| Standard | I2V | `fal-ai/minimax/hailuo-02/standard/image-to-video` |
| Pro | T2V | `fal-ai/minimax/hailuo-02/pro/text-to-video` |
| Pro | I2V | `fal-ai/minimax/hailuo-02/pro/image-to-video` |

## Modes, Resolution, Duration, FPS

- Modes: T2V, I2V
- Resolution:
  - Standard: `512p`, `768p`
  - Pro: `1080p`
- Duration: up to `10s`
- FPS: `24-30` range (typically set by model defaults/quality path)

## Camera Control Syntax

Hailuo responds to explicit camera-control blocks in the prompt. Keep them short and structured:

```text
CAMERA: [type: dolly_in, direction: left_to_right, speed: 0.6, lock: medium]
```

Recommended camera types: `dolly_in`, `dolly_out`, `pan_left`, `pan_right`, `tilt_up`,
`tilt_down`, `orbit`, `static`.

### Micro-Expression Emphasis

Hailuo-02 handles facial micro-adjustments better than most mid-tier options. Use
emotion micro-cues near the subject:
`eyes narrow`, `lip tremor`, `confident smile`, `quiet intake of breath`.

## Prompting Tips

- Keep one dominant style per run (`anime`, `soft painterly`, `semi-real`) to avoid style drift.
- For camera-heavy shots, put camera block before ambience lines:
  - `CAMERA: [type: orbit, speed: 0.4]`
  - `Environment: ...`
  - `Lighting: ...`
  - `Character performance: ...`
- For I2V, avoid conflicting motion directions between image composition and camera direction.
- Use concise negative prompts over verbose prohibitions for stronger control.

## Best Practices

1. Pick Standard for draft shots (`512p`/`768p`) and reserve Pro for final hero clips.
2. Use the shortest frame duration first, then expand to full 10s with locked camera intent.
3. Match FPS intent (`24` if cinematic, `30` if kinetic).
4. For stylization, pin both texture and motion: `clean linework, stable lighting, fluid physics`.
5. Separate subject, motion, and camera into clear prompt lines.

## Failure Modes and Fixes

| Problem | Fix |
|---------|-----|
| Flat face motion / expression freezing | Add explicit micro-expression cues and reduce prompt length |
| Warped anatomy during fast cuts | Lower movement intensity and shorten action arcs |
| Camera jump cuts | Replace compound camera actions with one primary move per segment |
| Soft or smeared edges | Increase prompt contrast with `sharp lighting contrast` |
| Over-stylized artifacts | Tone down anime keywords if structure drifts |

## Cost Snapshot

| Tier | Cost |
|------|------|
| Hailuo Standard | ~$0.045/s |
| Hailuo Pro | ~$0.08/s |

No explicit audio pricing in reference notes; use `N/A` when no included audio pricing is defined.

## Example Prompt

```text
Wide anime interior shot of a moonlit train platform, soft rain.
CAMERA: [type: dolly_in, direction: forward, speed: 0.5, duration: 7s]
Character: young woman in school uniform, anxious eyes, subtle lip quiver.
Animation look: clean edges, painterly lighting, controlled motion blur.
Ambient: distant wind chime, low train rumble.
No camera jitter, no subtitles.
```

