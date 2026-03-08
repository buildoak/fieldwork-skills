# Camera Movements & Shot Types Reference

Complete reference for camera language in video prompts. Use these terms directly in prompts -- all major video models recognize them.

## Camera Movements

### Dolly (Track-Based)

| Term | Description | Emotional Effect |
|------|-------------|-----------------|
| Dolly in | Camera moves toward subject on track | Intimacy, focus, building tension |
| Dolly out | Camera moves away from subject | Reveal, distance, isolation |
| Dolly left/right | Lateral track movement | Parallax, environmental scanning |
| Push in | Slow forward movement | Emphasis, building pressure |
| Pull back | Slow backward movement | Context reveal, release |
| Dolly zoom (Vertigo) | Dolly + opposite zoom simultaneously | Disorientation, psychological tension |

### Pan & Tilt (Rotation from Fixed Position)

| Term | Description | Emotional Effect |
|------|-------------|-----------------|
| Pan left/right | Horizontal rotation | Follow action, reveal scenery |
| Tilt up | Vertical rotation upward | Reveal height, power, aspiration |
| Tilt down | Vertical rotation downward | Reveal below, submission |
| Whip pan | Rapid horizontal snap | Surprise, energy, scene transition |
| Dutch tilt | Camera tilted on roll axis | Unease, tension, instability |

### Crane & Jib (Vertical Movement)

| Term | Description | Emotional Effect |
|------|-------------|-----------------|
| Crane up | Camera rises vertically | Grandeur, liberation, overview |
| Crane down | Camera descends vertically | Grounding, arrival, focus |
| Jib up | Smaller vertical rise (jib arm) | Gentle elevation, reveal |
| Jib down | Smaller vertical descent | Gentle descent, intimate |

### Tracking (Moving with Subject)

| Term | Description | Emotional Effect |
|------|-------------|-----------------|
| Tracking shot | Camera moves alongside subject | Engagement, journey |
| Following shot | Camera behind subject, same pace | POV-adjacent, pursuit |
| Leading shot | Camera ahead of subject | Anticipation, welcome |
| Steadicam | Stabilized fluid movement | Professional, smooth |
| Orbit / Arc | Camera circles around subject | Energy, showcase, drama |

### Handheld & Specialty

| Term | Description | Emotional Effect |
|------|-------------|-----------------|
| Handheld | Operator-held, organic motion | Realism, urgency, documentary |
| Shoulder-cam | Stable but with body sway | Intimate documentary |
| Crash zoom | Rapid zoom in | Impact, comedy, emphasis |
| Rack focus | Shift focus between planes | Redirect attention |
| Focus pull | Gradual focus transition | Reveal, connection |
| Lens flare | Light artifact from bright source | Warmth, realism |

## Shot Types / Framing

### Distance from Subject

| Term | Description | Best For |
|------|-------------|----------|
| Extreme wide / Establishing | Full environment, subject tiny | Scale, geography, scene setting |
| Wide shot | Full body + significant environment | Action, dance, establishing context |
| Medium wide / Cowboy | Knees to head | Walking, group interaction |
| Medium shot | Waist to head | Dialogue, standard conversation |
| Medium close-up | Chest to head | Emotional dialogue, interviews |
| Close-up | Face filling frame | Emotion, reaction, detail |
| Extreme close-up (ECU) | Single feature (eyes, hands, lips) | Intensity, micro-detail |
| Insert shot | Close-up of story-relevant object | Plot detail, prop reveal |

### Angle Relative to Subject

| Term | Description | Best For |
|------|-------------|----------|
| Eye level | Camera at subject's eye height | Neutral, conversational |
| Low angle | Camera below, looking up | Power, dominance, heroism |
| High angle | Camera above, looking down | Vulnerability, overview |
| Bird's eye / Aerial | Directly above | Geography, patterns, scale |
| Worm's eye | Ground level, looking up | Dramatic scale, architecture |
| Dutch angle | Tilted horizon line | Unease, tension, disorientation |

### Compositional Framing

| Term | Description | Best For |
|------|-------------|----------|
| Over-the-shoulder (OTS) | Behind one character, facing another | Dialogue, relationship |
| Two-shot | Two characters in frame | Relationship dynamics |
| POV | Character's exact perspective | Immersion, horror, VR |
| Profile shot | Side view of subject | Silhouette, contemplation |
| Through-frame | Shot through doorway/window/arch | Voyeurism, separation, framing |
| Reflection shot | Subject seen in mirror/water/glass | Duality, self-examination |

## Motion Description Templates

### Subject Motion
```
[Subject] [verb] [direction] [speed adverb]
```
Examples:
- "The dancer spins clockwise, arms extending slowly"
- "A bird descends in a gentle spiral toward the water"
- "The car accelerates forward down the rain-slicked highway"

### Camera Motion
```
Camera [movement type] [direction] [speed] [from/to position]
```
Examples:
- "Camera dollies in slowly from wide to medium close-up"
- "Camera cranes up from street level to rooftop height"
- "Camera tracks alongside the subject at walking pace"

### Combined Subject + Camera
```
As [subject action], the camera [camera motion], revealing [new element]
```
Examples:
- "As she walks through the doorway, the camera pulls back to reveal the vast empty hall beyond"
- "As the train arrives, the camera pans right to show the waiting crowd on the platform"
- "As the sun sets, the camera slowly cranes up to reveal the city skyline"

## Pro Tips

1. **Name the movement explicitly** -- "slow dolly in" beats "camera moves forward"
2. **Specify speed** -- "slowly", "steadily", "rapidly" change the result dramatically
3. **Combine subject + camera** -- both should move for dynamic shots
4. **Match movement to emotion** -- static for contemplation, handheld for urgency
5. **One camera move per clip** -- complex camera choreography rarely works in AI video
6. **Use "camera holds" for static** -- explicit is better than omitting
