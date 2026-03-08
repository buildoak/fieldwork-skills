# LTX-2.3 Deep Dive

## Overview

LTX-2.3 by Lightricks. The open-source workhorse. Apache 2.0 licensed, self-hostable, LoRA fine-tunable, only model with native 4K and 48 FPS. Cheapest per-second cost. The default model for iteration and budget workflows.

## Endpoints

| Variant | Endpoint | Cost (1080p) |
|---------|----------|-------------|
| T2V Standard | `fal-ai/ltx-2.3/text-to-video` | $0.06/s |
| T2V Fast | `fal-ai/ltx-2.3/text-to-video/fast` | $0.04/s |
| I2V | `fal-ai/ltx-2.3/image-to-video` | $0.06/s |
| Audio-to-Video | `fal-ai/ltx-2.3/audio-to-video` | $0.10/s |
| Extend Video | `fal-ai/ltx-2.3/extend-video` | $0.10/s |
| Retake Video | `fal-ai/ltx-2.3/retake-video` | $0.10/s |

I2V endpoint supports optional `end_image_url` parameter -- provide both start and end frame images and LTX generates a transition video between them. Powerful for controlled scene transitions.

## Key Advantages

1. **Cheapest:** $0.04/s at 1080p (fast tier)
2. **4K native:** Only model with 2160p output ($0.24/s)
3. **48 FPS:** Double frame rate option
4. **Open source:** Apache 2.0, fully self-hostable
5. **LoRA support:** Fine-tune on custom subjects/styles
6. **Five modes:** T2V, I2V, Audio-to-Video, Extend, Retake

## Prompting

### What Changed in 2.3
4x larger text connector means complex multi-subject prompts resolve much more accurately. You can be more specific without confusion.

### Critical I2V Rule
**For I2V: Do NOT describe the static scene** -- the model already sees the keyframe. DO describe temporal evolution, camera motion, and environmental dynamics. The prompt should answer "what happens next?" not "what do I see?"

Good I2V prompt: "Camera slowly dollies in, wind picks up scattering leaves across the path, clouds roll overhead casting moving shadows"
Bad I2V prompt: "A forest path with autumn leaves and overcast sky" (redundant with keyframe -- causes confusion)

### Negative Prompts
Supported. Good defaults:
```
blur, distort, low quality, overexposed, static, subtitles, poorly drawn, deformed, camera shake
```

## I2V Motion Quality

### FFmpeg Compression Trick
LTX was trained on compressed video, not pristine images. Clean PNG/JPEG keyframes get treated as flat photos -- produces paper warping. Fix: pre-process through H.264 CRF 24:
```bash
ffmpeg -i keyframe.png -c:v libx264 -crf 24 -frames:v 1 compressed.mp4
ffmpeg -i compressed.mp4 -frames:v 1 keyframe_compressed.png
```
CRF 20-30 range works. CRF 24 is the sweet spot.

### Stylized/Anime Inputs
Paper warping is worst with flat color fills, hard outlines, and no photographic depth cues. Solutions ranked:
1. **T2V instead of I2V** -- model generates its own 3D-coherent scene
2. **Photorealistic keyframe** -- use Flux photorealistic version as I2V input
3. **Compression trick + low denoise** -- preserve keyframe while allowing motion

### Prompt Structure for Motion
Action first, vibes later:
1. Subject + continuous action
2. Environment/context
3. Camera movement (single move only -- stacking causes jitter)
4. Lighting/style
5. Technical: "180-degree shutter, natural motion blur, 35mm lens"
6. Temporal change

### Camera Language
**Works:** dolly in, dolly out, slow pan left, truck right, crane up, tracking shot, slow orbit, tripod-locked, handheld.
**Breaks:** stacking multiple movements. One camera move per generation.
Lens specs help: 35mm (neutral cinematic), 50mm (intimate), 85mm (face stability).

### Anti-Warping Negative Prompt
```
morphing, distortion, warping, flicker, jitter, stutter, shaky camera, erratic motion, temporal artifacts, blur, low quality, overexposed, static, subtitles, poorly drawn, deformed
```
8-15 terms max -- too many dilute each other.

### Settings Sweet Spots
| Setting | Sweet Spot | Danger Zone |
|---------|-----------|-------------|
| CFG | 3.0-4.0 | >5.0 causes flicker |
| Steps | 30-40 | <20 low quality |
| Denoise | 0.55-0.70 | High CFG + high denoise = shimmer |
| Motion weight | 0.4-0.7 | >0.75 = rubbery limbs |
| Resolution | 720p gen, upscale to 4K | -- |

## LoRA Fine-Tuning

### Training Tips
1. **Quality over quantity:** 5 excellent clips beat 20 mediocre ones
2. **Consistency:** Same lighting, resolution, subject matter
3. **Unique trigger tokens:** Use "fl0wdnc" not "dance"
4. **Starting parameters:** 500 steps, 0.0002 learning rate, rank 32
5. **Success indicator:** Final loss between 0.01-0.05

### Compatibility Warning
LTX-2.0 LoRAs must be retrained for 2.3 -- the latent space changed.

## Resolution and Cost

| Resolution | Fast | Standard |
|-----------|------|----------|
| 1080p | $0.04/s | $0.06/s |
| 1440p | $0.08/s | $0.12/s |
| 4K (2160p) | $0.16/s | $0.24/s |

48 FPS doubles frame count and cost proportionally.

## Best Endpoints by Use Case

| Workflow | Endpoint | Why |
|----------|----------|-----|
| Quick storyboard | `text-to-video/fast` | Cheapest, fastest |
| Production quality | `text-to-video` | Better coherence |
| 4K final output | `text-to-video` with 2160p | Only 4K option |
| Extend clip | `extend-video` | Add time to start/end |
| Fix a section | `retake-video` | Re-generate portion |
| Music video sync | `audio-to-video` | Audio drives visuals |

## Example Prompts

### Budget Iteration
```
A coffee cup on a wooden table, steam rising. Morning sunlight through
a window creates warm patches. Camera slowly pushes in. Photorealistic.
```

### 4K Cinematic
```
Aerial drone shot over autumn forest canopy. Red, orange, and gold
leaves stretching to the horizon. Morning mist threads between the
treetops. Camera moves forward slowly at 100 meters altitude.
Golden hour lighting, deep shadows between trees. Ultra sharp,
4K quality, cinematic color grading.
```

## Duration Constraints

**LTX-2.3 only accepts 6, 8, or 10 second durations.** There is no 1s, 2s, 3s, or 4s option.

Implications:
- Fast-cut sequences (1-2s per shot) are not directly supported. You must generate 6s minimum and trim with FFmpeg.
- Trimming wastes ~80% of generated video on 1-2s target shots (billing is per second generated, not per second kept).
- For short clips: generate 6s, identify the best segment, trim with `ffmpeg -ss <start> -t <target_duration> -i input.mp4 output.mp4`.

Workarounds when you need short clips:
1. **Generate 6s + trim** -- wastes credits but works with LTX
2. **Use fewer, longer shots (3-4s each)** -- less waste, compatible with LTX 6s minimum
3. **Switch to Kling** -- supports 2s minimum, costs more per second but no waste on short clips

## Limitations
- Raw visual quality below premium models (Veo, Sora, Kling V3)
- Character faces can be inconsistent in longer clips
- Audio quality functional but not matching Veo's lip sync
- No multi-shot native support (single continuous shot only)
- Text rendering in video is weak
- Minimum duration 6s -- no sub-6s clips without post-trim
- 4:3 aspect ratio produces best motion quality. Non-4:3 ratios skew toward limited hand/arm/face movements.

## When to Use LTX vs. Premium

| Scenario | Use LTX | Use Premium |
|----------|---------|------------|
| Prototyping / iteration | Yes | No |
| Budget under $1/clip | Yes | No |
| 4K required | Yes (only option) | No |
| Dialogue / lip sync | No | Yes (Veo) |
| Multi-shot narrative | No | Yes (Kling) |
| LoRA custom training | Yes (only option) | No |
