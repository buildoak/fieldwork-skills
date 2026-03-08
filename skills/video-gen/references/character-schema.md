# Character JSON Schema

## Anchor Pattern
Character JSON is the identity anchor. Every generator step (character sheets, keyframes, shot prompts, QA checks) reads the same object, so the model sees a stable identity definition instead of ad-hoc prose.

## Schema

| Path | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | yes | Display name used in story and prompt text. |
| `face.shape` | string | yes | Face geometry (`oval`, `round`, `square`, etc.). |
| `face.skin_tone` | string | yes | Precise skin descriptor used repeatedly. |
| `face.age` | integer | yes | Character age in years. |
| `face.features.eyes` | string | yes | Eye shape/color detail. |
| `face.features.nose` | string | yes | Nose profile detail. |
| `face.features.mouth` | string | yes | Mouth/lip detail. |
| `hair.color` | string | yes | Hair color anchor. |
| `hair.style` | string | yes | Style anchor (`bob`, `buzz`, `ponytail`). |
| `hair.length` | string | yes | Length anchor (`short`, `shoulder_length`, etc.). |
| `hair.texture` | string | yes | Texture anchor (`straight`, `wavy`, `curly`, `coily`). |
| `body.build` | string | yes | Build descriptor (`athletic slim`, `stocky`). |
| `body.height` | string | yes | Numeric or relative height. |
| `body.scale_reference` | string | yes | Relative scale to other cast. |
| `clothing.default.top` | string | yes | Default top garment. |
| `clothing.default.bottom` | string | yes | Default lower garment. |
| `clothing.default.shoes` | string | yes | Default footwear. |
| `clothing.default.accessories` | string | yes | Clothing accessory layer (jacket, scarf). |
| `clothing.scene_overrides[]` | array<object> | yes | Scene-specific clothing changes. |
| `accessories.glasses` | string | yes | Eyewear or `none`. |
| `accessories.jewelry` | string | yes | Jewelry details. |
| `accessories.watch` | string | yes | Watch details or `none`. |
| `scars_marks[]` | array<string> | yes | Scars, freckles, marks, birthmarks. |
| `tattoos[]` | array<string> | yes | Tattoo descriptors and placement. |
| `voice.pitch` | string | yes | Vocal pitch range. |
| `voice.accent` | string | yes | Accent descriptor. |
| `voice.age_sound` | string | yes | Perceived voice age. |
| `expression_default` | string | yes | Resting expression anchor. |
| `distinguishing_features[]` | array<string> | yes | Repeated behavior/visual identifiers. |

## Complete Example: Maya

```json
{
  "name": "Maya",
  "face": {
    "shape": "oval",
    "skin_tone": "warm ivory",
    "age": 28,
    "features": {
      "eyes": "almond-shaped dark brown eyes",
      "nose": "straight narrow nose",
      "mouth": "defined cupid's bow, medium lips"
    }
  },
  "hair": {
    "color": "jet black",
    "style": "blunt bob",
    "length": "shoulder_length",
    "texture": "straight"
  },
  "body": {
    "build": "athletic slim",
    "height": "168 cm",
    "scale_reference": "average female height in frame; slightly shorter than male co-lead"
  },
  "clothing": {
    "default": {
      "top": "white crew-neck tee",
      "bottom": "dark jeans",
      "shoes": "white low-top sneakers",
      "accessories": "red leather jacket"
    },
    "scene_overrides": [
      {
        "scene_id": "scene-cafe-interior",
        "top": "white crew-neck tee",
        "bottom": "dark jeans",
        "shoes": "white low-top sneakers",
        "accessories": "red leather jacket draped on chair"
      }
    ]
  },
  "accessories": {
    "glasses": "round wire-frame glasses",
    "jewelry": "silver ring on right index finger",
    "watch": "none"
  },
  "scars_marks": [
    "small scar on left eyebrow"
  ],
  "tattoos": [],
  "voice": {
    "pitch": "medium-soft",
    "accent": "neutral North American",
    "age_sound": "late 20s"
  },
  "expression_default": "calm and observant",
  "distinguishing_features": [
    "pauses briefly before replying",
    "keeps shoulders relaxed and posture upright"
  ]
}
```

## Why This Prevents Drift

- Same source object is reused in every prompt and QA pass.
- Identity fields are explicit, not implied by prose memory.
- Scene overrides only change allowed fields (typically clothing), preserving face/hair/body anchors.
- Prompt builders pull deterministic text from the same keys each time.

## Compilation: Character JSON -> Prompt String

Template:

```text
{name}, {age}-year-old, {face.shape} face, {face.skin_tone}, {face.features.eyes},
{face.features.nose}, {face.features.mouth}, {hair.color} {hair.length} {hair.style} ({hair.texture}),
{body.build}, height {body.height}, wearing {clothing.default.top}, {clothing.default.bottom},
{clothing.default.shoes}, {clothing.default.accessories}, accessories: {accessories.glasses},
{accessories.jewelry}, {accessories.watch}, marks: {scars_marks}, tattoos: {tattoos},
default expression: {expression_default}.
```

Compiled example for Maya:

```text
Maya, 28-year-old, oval face, warm ivory skin, almond-shaped dark brown eyes, straight narrow nose,
defined cupid's bow, medium lips, jet black shoulder-length blunt bob (straight), athletic slim,
height 168 cm, wearing white crew-neck tee, dark jeans, white low-top sneakers, red leather jacket,
accessories: round wire-frame glasses, silver ring on right index finger, none watch,
marks: small scar on left eyebrow, tattoos: none, default expression calm and observant.
```
