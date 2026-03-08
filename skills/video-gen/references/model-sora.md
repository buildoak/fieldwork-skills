# Sora 2 Deep Dive

## Overview

Sora 2 by OpenAI. The precision model. Excels at complex multi-element scenes, long-form video (up to 25s in Pro), and has a unique remix mode for transforming existing videos. Most expensive model but delivers when scenes are complex.

## Endpoints

| Variant | Endpoint | Max Duration |
|---------|----------|-------------|
| Standard T2V | `fal-ai/sora-2/text-to-video` | 12s |
| Pro T2V | `fal-ai/sora-2/text-to-video/pro` | 25s |
| Standard I2V | `fal-ai/sora-2/image-to-video` | 12s |
| Pro I2V | `fal-ai/sora-2/image-to-video/pro` | 25s |
| Remix V2V | `fal-ai/sora-2/video-to-video/remix` | Transform existing |

## Prompt Structure

Sora processes prompts in this order:

1. **Visual prose description** -- style first, then scene
2. **Cinematography block** -- framing, DoF, lighting, mood
3. **Actions in beats** -- specific, timed, physical
4. **Dialogue** -- labeled speakers, concise
5. **Background sound** -- diegetic audio, rhythm cues

### Style Is Your Strongest Lever
"The same details will read very differently depending on whether you call for a polished Hollywood drama, a handheld smartphone clip, or a grainy vintage commercial." Establish style early.

### Use Concrete Nouns
- Good: "wet asphalt, zebra crosswalk, neon signs reflecting"
- Bad: "a beautiful street at night"

### Action in Beats
- Good: "Actor takes four steps to the window, pauses, and pulls the curtain"
- Bad: "walks across the room"

### Dialogue Rules
- Label speakers consistently
- Keep lines concise and natural
- Limit to 1-2 exchanges per 4-second clip
- Place dialogue in a separate block below visual description
- Long speeches will NOT sync properly

## Duration Strategy

**Two 4s clips stitched > one 8s clip.** Better quality and consistency at shorter durations.

| Duration | Approach |
|----------|---------|
| 4s | Standard quality. Best consistency |
| 8s | Good for single-action sequences |
| 12s | Max standard. Quality starts to degrade |
| 25s (Pro) | Extended sequences. Use sparingly |

## Remix Mode

Transform existing videos with controlled changes. One change at a time:
- "Same shot, switch to 85mm lens"
- "Same lighting, new palette: teal, sand, rust"
- "Same composition, change season to winter"

Multiple changes per remix reduce consistency. Layer changes across multiple remixes instead.

Important: `delete_video: true` is the default. Set to `false` to retain original for further remixes.

## What Doesn't Work
- Vague descriptions ("beautiful", "cinematic")
- Long complex speeches
- Mixing competing character traits
- Overly detailed specs (paradoxically reduces consistency)
- Background motion during dialogue

## Pro Tips
- Shorter prompts encourage creative freedom; longer prompts restrict but may not deliver
- Keep background motion minimal during dialogue
- Reuse phrasing for continuity across clips
- Strip shots back to basics if they misfire
- BYO OpenAI key option charges directly to OpenAI account

## Example Prompts

### Film Noir Style
```
A private detective in a wrinkled trench coat and fedora stands under a
flickering streetlight in a rain-soaked 1940s alley. Black and white.
Film noir. High contrast with deep shadows. He lights a cigarette, the
match briefly illuminating his scarred jawline.

Action: He takes a long drag, exhales slowly, then turns and walks down
the alley, footsteps echoing.

Sound: Rain on metal awnings, distant jazz trumpet, match strike.
```

### Shot Stack Pattern
```
Beat 1 (0-2s): ENTER -- The door swings open. A woman in a red coat
steps into the sunlit room. She pauses at the threshold.

Beat 2 (2-4s): REACT -- She sees the empty chair by the window. Her
expression shifts from expectation to quiet resignation.

Beat 3 (4-6s): EXIT -- She turns slowly, coat brushing the doorframe,
and walks back out. Door closes.
```

## Pricing

| Variant | 720p | 1080p |
|---------|------|-------|
| Standard/Pro | $0.30/s | $0.50/s |

Most expensive per second. Use for final production, not iteration.
Cost tip: Draft with Wan or LTX, finalize with Sora.
