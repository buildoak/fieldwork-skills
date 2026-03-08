# Shot JSON Schema

Shot JSON is the executable unit for generation. Each shot binds camera language, action, dialogue, characters, timing, and transition behavior.

## Schema

| Path | Type | Required | Allowed Values / Notes |
|------|------|----------|------------------------|
| `shot_id` | string | yes | Stable key (`shot-001`). |
| `scene_id` | string | yes | Foreign key to scene definition. |
| `order` | integer | yes | Timeline order (1..N). |
| `duration_sec` | integer | yes | Range: `2-10`. |
| `camera.angle` | string | yes | `eye_level`, `high`, `low`, `bird`, `worm` |
| `camera.shot_size` | string | yes | `extreme_wide`, `wide`, `medium`, `close_up`, `extreme_close_up` |
| `camera.movement` | string | yes | `static`, `pan_left`, `pan_right`, `tilt_up`, `tilt_down`, `zoom_in`, `zoom_out`, `dolly_forward`, `dolly_back`, `orbit_left`, `orbit_right` |
| `action` | string | yes | Visual action description, present tense. |
| `dialogue` | string | no | Spoken line or empty string. |
| `characters_present` | array<string> | yes | Character IDs visible in shot. |
| `mood` | string | yes | Emotional tone and pacing anchor. |
| `transition_to_next` | string | yes | `cut`, `crossfade`, `match_cut`, `fade_out`, etc. |
| `keyframe_source` | string | no | `generated`, `bridge_from_prev`, `manual`. |
| `model_hint` | string | no | Optional per-shot model hint. |

## Camera Vocabulary Guide

### Angle

| Angle | Meaning | Use It When |
|-------|---------|-------------|
| `eye_level` | Neutral human perspective. | Dialogue and baseline continuity shots. |
| `high` | Camera above subject. | Show vulnerability, context, or spatial relation. |
| `low` | Camera below subject. | Emphasize power, confidence, or scale. |
| `bird` | Top-down overhead. | Geography, choreography, scene layout. |
| `worm` | Extreme low-up angle. | Dramatic stylization and exaggerated scale. |

### Shot Size

| Shot Size | Meaning | Use It When |
|-----------|---------|-------------|
| `extreme_wide` | Full environment dominates frame. | Establishing context and location. |
| `wide` | Full body + environment. | Blocking and movement. |
| `medium` | Waist-up framing. | Conversational beats. |
| `close_up` | Face or object emphasis. | Emotion and detail cues. |
| `extreme_close_up` | Isolated detail. | Symbolic moments or transitions. |

### Movement

| Movement | Meaning | Use It When |
|----------|---------|-------------|
| `static` | Locked frame. | Calm, tension, or emphasis on performance. |
| `pan_left` / `pan_right` | Rotate horizontally. | Follow lateral action or reveal information. |
| `tilt_up` / `tilt_down` | Rotate vertically. | Reveal height or direct attention. |
| `zoom_in` / `zoom_out` | Lens zoom without moving camera. | Subjective emphasis or detachment. |
| `dolly_forward` / `dolly_back` | Camera physically moves in/out. | Add depth and cinematic momentum. |
| `orbit_left` / `orbit_right` | Circular move around subject. | Dynamic relationship or emotional shift. |

## Example Shots

```json
[
  {
    "shot_id": "shot-001",
    "scene_id": "scene-cafe-interior",
    "order": 1,
    "duration_sec": 8,
    "camera": {
      "angle": "eye_level",
      "shot_size": "wide",
      "movement": "dolly_forward"
    },
    "action": "Maya enters the cafe and spots Leo at the window table.",
    "dialogue": "",
    "characters_present": ["maya", "leo"],
    "mood": "tentative warmth",
    "transition_to_next": "cut",
    "keyframe_source": "generated",
    "model_hint": "kling-v3"
  },
  {
    "shot_id": "shot-002",
    "scene_id": "scene-cafe-interior",
    "order": 2,
    "duration_sec": 6,
    "camera": {
      "angle": "high",
      "shot_size": "close_up",
      "movement": "static"
    },
    "action": "Close-up of their hands around coffee mugs as both laugh.",
    "dialogue": "Maya: Let's not lose another five years.",
    "characters_present": ["maya", "leo"],
    "mood": "relief and trust",
    "transition_to_next": "fade_out",
    "keyframe_source": "bridge_from_prev",
    "model_hint": "veo-3.1"
  }
]
```
