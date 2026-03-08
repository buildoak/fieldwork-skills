# Veo 3.1 Deep Dive

## Overview

Veo 3.1 by Google DeepMind. The lip-sync champion. Best-in-class audio generation with natural dialogue, synchronized lip movements, and ambient sound design. Premium quality for talking heads and audio-critical production.

## Endpoints

| Variant | Endpoint | Latency |
|---------|----------|---------|
| Standard T2V | `fal-ai/veo3` | 90-120s |
| Fast T2V | `fal-ai/veo3/fast` | 45-70s |
| Standard I2V | `fal-ai/veo3/image-to-video` | 90-120s |
| Fast I2V | `fal-ai/veo3/fast/image-to-video` | 45-70s |
| Reference | `fal-ai/veo3/reference-to-video` | -- |

## Prompt Structure

5-element hierarchy (in this order):
1. **Shot specification** -- camera work, framing
2. **Setting and atmosphere** -- lighting, environment
3. **Subject specification** -- consistent visual markers
4. **Action sequence** -- temporal progression
5. **Dialogue integration** -- optional, with specific syntax

### Optimal Prompt Length
**150-300 characters is the sweet spot.** Below 100 = generic. Above 400 = unpredictable prioritization.

## Dialogue Syntax

Critical for good lip sync. The exact format matters:
```
[CHARACTER] [Visual Description] looks at camera and says: "Spoken line here."
```
The **colon (:)** and **quotes ("")** are crucial triggers for the lip-sync model.

### Audio-First Mental Model
Describe sounds to create more physically accurate videos:
- Explicit dialogue in quotes
- Sound effects: "footsteps on stone floor"
- Ambient: "distant traffic, market chatter"
- **Always add "no background music" when prioritizing lip sync**

## Character Consistency
Use distinctive visual markers. Not "a woman" but:
```
A woman in her thirties with auburn hair pulled back in a loose bun,
wearing a charcoal peacoat and silver-rimmed glasses.
```

## Duration Strategy

| Duration | Best For |
|----------|---------|
| 4s | Single action, establishing shots |
| 6s | Brief narrative, short dialogue exchange |
| 8s | Complex sequences, extended dialogue |

## Production Workflow
1. Start with **Fast variant** ($0.10-0.15/s vs $0.20-0.40/s)
2. Begin testing at **4s, 720p** -- cheapest iteration
3. **Disable audio** for 33-50% cost savings when not needed
4. `enhance_prompt: true` for exploration; disable for precise control
5. Use **seed parameter** for reproducible variations
6. Scale duration/resolution only after validating results

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Prompt too long (>400 chars) | Random prioritization. Trim to 150-300 |
| 1:1 aspect ratio weird edges | Uses outpainting -- can extend scenes unexpectedly |
| Max 2 concurrent requests | Across ALL fal.ai endpoints per user |
| `enhance_prompt: true` rewrites | May auto-modify policy-edge prompts silently |
| Generic dialogue | Use close-up/medium shot with mouth clearly visible |
| Background music drowns dialogue | Add "no background music" explicitly |

## Negative Prompts
Supported. Use nouns, not commands:
- Good: "wall, frame, text overlay, camera shake"
- Bad: "no walls, don't add frames"

## Example Prompts

### Dialogue Scene
```
Medium close-up of a man in his forties with salt-and-pepper beard,
wearing a worn leather jacket, sitting at a diner counter under warm
tungsten light. He stirs his coffee and says: "The thing about this
town is, nobody ever really leaves." Coffee shop murmur, spoon clinking,
distant jukebox. No background music.
```

### Cinematic Establishing
```
Slow crane shot descending over a misty coastal village at dawn.
Fishing boats bob in the harbor. Seagulls circle overhead. Golden
hour backlighting catches the mist rising off the water. Volumetric
fog rays between the dock pilings. 35mm film grain, desaturated
palette with warm amber highlights.
```

## Pricing

| Variant | No Audio | With Audio |
|---------|----------|-----------|
| Standard | $0.20/s | $0.40/s |
| Fast | $0.10/s | $0.15/s |

Cost tip: A 4s fast clip without audio costs $0.40. Perfect for iteration.
