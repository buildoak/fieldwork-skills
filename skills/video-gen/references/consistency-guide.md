# Consistency Guide
This guide defines how `story-gen` preserves identity and visual continuity across multi-shot generation.

## Objective
Maintain stable character identity, wardrobe, scale, lighting, and action continuity from shot 1 to final cut.

## Three-Layer Strategy
1. Layer 1: Asset-First Character Sheets
2. Layer 2: Element Referencing
3. Layer 3: Temporal Bridging
Use all three layers together.

## Layer 1: Asset-First Character Sheets
Generate reference images before any video generation.
Do not render clips until sheet assets are complete.

### Required views by tier
| Tier | Required Views | Images/Character |
|------|----------------|------------------|
| Budget | front + 3/4 | 2 |
| Standard | front, profile, 3/4, back, side, action pose | 6 |
| Premium | front, profile, 3/4, back, side, action pose | 6 |
| Ultra | front, profile, 3/4, back, side, action pose | 6 |
Minimum baseline: front, profile, 3/4.

### Generation settings
- Model: `FLUX.2-Pro`
- Lighting: neutral studio lighting
- Background: neutral backdrop
- Pose: neutral readable pose
- Framing: consistent framing across views

### Identity source of truth
Character JSON drives prompt generation.
Rule: same JSON -> same description -> same character.
Do not hand-edit identity text per shot without updating JSON.

### Naming pattern
- `characters/<id>/sheet-front.png`
- `characters/<id>/sheet-profile.png`
- `characters/<id>/sheet-3q.png`
- `characters/<id>/sheet-back.png`
- `characters/<id>/sheet-side.png`
- `characters/<id>/sheet-action.png`

## Layer 2: Element Referencing
Bind character assets into keyframe and clip generation.

### Kling O3
Kling O3 supports multi-reference images via prompt syntax (not API parameter).
Use style refs directly in prompt text:
```text
[style-ref: characters/maya/sheet-front.png]
[style-ref: characters/maya/sheet-3q.png]
Medium close-up shot...
```
Use references for keyframes and identity-critical shots.

### LTX-2.3
LTX-2.3 has no element API.
Consistency depends on repeated detailed text anchors.
Repeat in every shot prompt:
- face description
- hair color/style
- signature wardrobe item
- distinguishing accessory

### Prompt anchoring rule
Repeat each character `anchor_prompt` in every shot prompt.
For multi-character shots, list each character explicitly.
Avoid vague references like "the other person" when continuity matters.

## Layer 3: Temporal Bridging
Bridge adjacent shots using the last frame of shot N as i2v seed for shot N+1.

### Extraction command
```bash
ffmpeg -sseof -0.1 -i video.mp4 -frames:v 1 -q:v 2 bridge.jpg
```
Use `bridge.jpg` as input for the next shot.

### When to bridge
Bridge when:
- shots are sequential in same scene
- character continues same action thread
- no intentional time or location jump
Typical cases:
- dialogue coverage swaps
- reaction inserts
- continuous movement across cuts

### When NOT to bridge
Do not bridge for:
- scene change
- time skip
- establishing shot after dialogue
- flashback or dream transition

### Fallback
If extraction fails, use the shot keyframe instead.
This degrades continuity but keeps pipeline execution unblocked.

## Vision2JSON Reverse Path
After generating reference sheets, audit outputs with Claude Vision and refine JSON.

### Feedback loop
1. Generate character sheet from JSON.
2. Analyze result with Claude Vision.
3. Compare generated image to JSON spec.
4. Refine JSON where drift appears.
5. Regenerate sheets and continue.
Loop summary: `JSON -> image -> JSON refinement -> better prompts`.

### Drift correction examples
- hair color wrong -> tighten `hair.color`
- signature ring missing -> strengthen accessory fields
- face shape off -> refine `face.shape` and facial feature fields

## Troubleshooting Consistency Failures
### Character face changed
Fix:
- strengthen face description
- add distinguishing traits (scar, eyebrow mark, glasses geometry)
- keep identity anchor text unchanged across shots

### Clothing drift
Fix:
- avoid generic clothing nouns
- use explicit descriptors
- example: `weathered brown leather bomber jacket with ribbed cuffs`

### Lighting mismatch
Fix:
- include scene lighting in every shot prompt
- state direction and quality of light
- avoid relying on model defaults

### Scale/proportion issues
Fix:
- define `scale_reference` in character body JSON
- restate relative scale in multi-character prompts

## Style Consistency

Image style and video style are not decoupled. The keyframe's visual style is inherited by the video model.

### Core rule
A painterly keyframe produces a painterly video. A photorealistic keyframe produces a cinematic video. The video model follows the keyframe's aesthetic register, not the video prompt alone.

### Keyframe style for cinematic output
If you want realistic, cinematic video output: use "photorealistic, cinematic" in keyframe prompts. Do not assume the video model will reinterpret a stylized image as live-action.

### Style checkpoint
Before generating the full keyframe batch, generate and approve the first keyframe's style. If style is wrong, fix the keyframe prompt before proceeding. Generating all keyframes then discovering a style mismatch wastes time and money.

### Anti-painting suffix
When generating cinematic content, append the following to keyframe prompts:
```text
photorealistic, cinematic photography, not painting, not illustration
```
This suppresses painterly drift from presets or style-heavy descriptions.

## Operator Checklist
Before render:
- character sheets complete for all cast
- tier view count met
- anchor prompts compiled from character JSON
- keyframes generated with references (or prompt-only for LTX)
- bridge policy selected per shot transition
During render:
- inspect first 1-2 shots for drift
- if drift appears, stop and fix JSON before full batch
After render:
- run continuity QA
- log drift type and corrective action for future runs
