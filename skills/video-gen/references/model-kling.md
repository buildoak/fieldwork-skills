# Kling 3.0 Deep Dive

## Overview

Kling 3.0 by Kuaishou. The director's model. Best-in-class for multi-shot narratives, character consistency across shots, and cinematic storytelling. Native audio with multilingual lip sync.

## Endpoints

| Variant | Endpoint | Use Case |
|---------|----------|----------|
| V3 Pro T2V | `fal-ai/kling-video/v3/pro/text-to-video` | Multi-shot cinematic |
| V3 Pro I2V | `fal-ai/kling-video/v3/pro/image-to-video` | Animate from reference |
| V2.6 Pro I2V | `fal-ai/kling-video/v2.6/pro/image-to-video` | Single-shot quality |
| O3 Standard I2V | `fal-ai/kling-video/o3/standard/image-to-video` | Reference-heavy workflows |
| Motion Control | `fal-ai/kling-video/v3/standard/motion-control` | Camera path control |

## Prompt Structure

**Order matters.** Kling parses prompts in this hierarchy:

```
Scene -> Characters -> Action -> Camera -> Audio & Style
```

Write like a director giving scene instructions, not listing objects.

### Multi-Shot Syntax

Up to 6 shots per generation. Label each shot explicitly:

```
Shot 1: Wide establishing shot of a rain-soaked Tokyo intersection at night.
Neon signs reflect in puddles on the crosswalk.

Shot 2: Medium close-up of a young woman in a black trench coat standing
under a transparent umbrella. She looks up at the tallest building.

Shot 3: Her POV -- tilt up from street level to the rooftop, city lights
blurring as the camera moves. Thunder rumbles.

Shot 4: Close-up of her face, rain droplets on her cheek. She smiles
slightly and steps forward off the curb.
```

Do NOT compress everything into one paragraph. Each shot needs its own block with framing, subject position, and motion.

## Prompting Tips

### Emphasis Markers
Use `++` to weight important elements:
```
"++sleek red convertible++ driving along coastal highway at sunset"
```

### Character Consistency
Use Element Referencing for multi-shot consistency:
- Upload reference images or 3-8 second video clips
- Model extracts character traits, appearance, voice
- Multi-character coreference for 3+ distinct characters
- O3 variant supports multi-image element building with voice input

### Motion Control
Specify motion intensity values (0.1 to 1.0) for predictable results. Always include both subject movement AND camera behavior. `cfg_scale` at 0.5 gives more creative freedom.

### Camera Keywords That Work
Dolly push, whip-pan, shoulder-cam drift, crash zoom, snap focus, tracking, following, freezing, panning, synchronized movement, profile shots, macro close-ups, POV, shot-reverse-shot.

### Audio / Dialogue Format
```
[Character Name, tone/emotion]: "dialogue"
Immediately, [Character B, emotion]: "response"
```
Supported languages: Chinese, English, Japanese, Korean, Spanish (including dialects). Voice control improves clarity but costs more ($0.392/s vs $0.336/s).

### Negative Prompts
Supported. Use for quality control:
```
"blur, distort, low quality, camera shake, color distortion"
```

### Image-to-Video Tips
- Treat input images as anchors
- Focus prompts on how scenes evolve FROM the image
- Model preserves text, signage, and visual details from input
- Best model for text preservation in video

## Common Failure Modes

| Problem | Fix |
|---------|-----|
| Motion distortion | Reduce complexity; specify "stable camera movement"; break into simpler sequences |
| Object morphing mid-video | Use Elements with multiple reference angles; add "maintains exact appearance throughout" |
| Visual incoherence | Maintain consistent style terminology; don't mix "golden hour" with "studio lighting" |
| Audio muffled | Use voice control for clearer dialogue; keep ambient sounds minimal |
| Multi-shot continuity breaks | Reuse exact physical descriptors across shots (scars, watches, clothing) |

## Example Prompts

### Cinematic Multi-Shot
```
Shot 1: Wide establishing -- a weathered fishing village at dawn. Mist rolls
off the harbor. A single boat engine putters in the distance.

Shot 2: Medium shot -- an old fisherman with a white beard and blue cap mends
a net on the dock. His hands move with practiced rhythm.

Shot 3: Close-up -- his weathered hands pulling thread through the net, salt
crystals visible on the rope. Camera slowly pushes in.

Shot 4: Wide profile -- he stands, stretches, and walks down the dock toward
his boat. Morning light catches the mist behind him.
```

### Single Shot with Audio
```
Close-up of a street musician playing violin on a cobblestone corner in
Prague at twilight. String lights glow warmly behind him. Camera holds
steady on a medium close-up. [Musician, passionate]: plays a melancholic
Eastern European melody. Ambient: distant church bells, cobblestone
footsteps of passing pedestrians. Shot on 35mm, warm color grading.
```

## Pricing

| Variant | Video Only | With Audio | Voice Control |
|---------|-----------|-----------|---------------|
| V3 Standard | $0.168/s | $0.336/s | $0.392/s |
| V2.6 Pro | $0.07/s | $0.14/s | -- |
