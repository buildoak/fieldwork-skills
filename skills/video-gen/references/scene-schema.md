# Scene JSON Schema

Scene JSON defines reusable environment anchors. Shots reference `scene_id` so lighting, palette, weather, and props remain stable across the timeline.

## Schema

| Path | Type | Required | Allowed Values / Notes |
|------|------|----------|------------------------|
| `scene_id` | string | yes | Stable scene key (`scene-cafe-interior`). |
| `title` | string | yes | Human-readable scene name. |
| `description` | string | yes | Narrative purpose of scene. |
| `environment.location` | string | yes | Physical place description. |
| `environment.lighting` | string | yes | `natural`, `artificial`, `dramatic`, `soft`, `harsh`, `golden_hour`, `blue_hour` |
| `environment.color_palette` | string | yes | `warm`, `cool`, `monochrome`, `vibrant`, `muted`, `high_contrast` |
| `environment.time_of_day` | string | yes | `dawn`, `morning`, `noon`, `afternoon`, `dusk`, `night` |
| `environment.weather` | string | yes | `clear`, `cloudy`, `rainy`, `snowy`, `foggy`, `stormy` |
| `environment.props` | array<string> | yes | Persistent visible objects in the scene. |

## Notes

- Keep `location` concrete enough for repeatability.
- Keep `props` short and persistent; do not include one-off actions.
- Treat scenes as reusable modules: one scene can power multiple shots.

## Example Scenes

```json
[
  {
    "scene_id": "scene-cafe-interior",
    "title": "Corner Cafe Morning",
    "description": "Intimate reunion space with warm social energy.",
    "environment": {
      "location": "small neighborhood cafe with wood tables, large front window, hanging plants",
      "lighting": "soft",
      "color_palette": "warm",
      "time_of_day": "morning",
      "weather": "cloudy",
      "props": [
        "ceramic coffee mugs",
        "chalkboard menu",
        "window condensation",
        "open notebook"
      ]
    }
  },
  {
    "scene_id": "scene-city-rooftop-night",
    "title": "Rooftop Reflection",
    "description": "Quiet emotional beat above the city skyline.",
    "environment": {
      "location": "urban rooftop with skyline view and waist-high concrete ledge",
      "lighting": "blue_hour",
      "color_palette": "cool",
      "time_of_day": "night",
      "weather": "clear",
      "props": [
        "string lights",
        "metal folding chairs",
        "windblown paper cup"
      ]
    }
  },
  {
    "scene_id": "scene-forest-path",
    "title": "Forest Walk",
    "description": "Transition sequence focused on movement and mood.",
    "environment": {
      "location": "narrow forest path lined with tall pines and damp ground",
      "lighting": "natural",
      "color_palette": "muted",
      "time_of_day": "afternoon",
      "weather": "foggy",
      "props": [
        "fallen branches",
        "mossy stones",
        "wooden trail marker"
      ]
    }
  }
]
```
