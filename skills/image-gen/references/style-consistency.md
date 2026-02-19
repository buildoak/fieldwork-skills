# Style Consistency Techniques

For generating consistent series of images (multiple images that should look like they belong together).

---

## Technique Stack

Layer these for maximum consistency. Higher layers add more control.

| Layer | Technique | Models | Effort |
|-------|-----------|--------|--------|
| 1 | **Style preset** | All | Low -- just use `--preset` |
| 2 | **System message** | GPT-5, NanoBanana | Low -- included in preset |
| 3 | **JSON structured prompt** | Flux, NanoBanana | Auto with preset for Flux |
| 4 | **Reference image anchoring** | All (best: Flux, NanoBanana Pro) | Medium -- needs "golden" image |
| 5 | **HEX color palette** | Flux (native), others (interpreted) | Low -- included in preset |

---

## Reference Image Workflow

The strongest consistency technique. Use a "golden" image from the series as a visual anchor.

### Workflow

1. Generate the first image in the series with extra care (iterate until right)
2. Save it as the "golden" reference
3. All subsequent images: `--style-ref /path/to/golden.png`
4. Optionally add the path to the preset's `reference_images` array

### Model Capabilities

- **Flux 2 Pro:** Up to 8 reference images (9MP total budget)
- **NanoBanana Pro:** Up to 14 references, 5-person identity preservation
- **GPT-5 Image:** Reference with style transfer instruction

### CLI

```bash
# Single reference
python generate.py --prompt "New scene" --style-ref /path/to/golden.png

# Multiple references (combine style + content refs)
python generate.py --prompt "New scene" \
  --style-ref /path/to/style-ref.png \
  --style-ref /path/to/character-ref.png
```

The script automatically prepends a style transfer instruction ("Generate a new image in the exact visual style of the provided reference image(s)") before the user's prompt.

---

## Seed Workflow (GPT-5 / NanoBanana only)

For controlled variations of a successful generation:

1. Generate an image, note the seed from output
2. Regenerate with same seed + modified prompt for variations
3. Different seeds + identical prompts = same style, different composition

Flux does NOT support seeds via OpenRouter.

---

## Per-Model Consistency Notes

### Flux 2 Pro / Klein

- JSON structured prompts prevent concept bleeding between elements
- HEX color palettes (`"the car is #FF0000"`) give precise color control
- Prompt upsampling is ON by default -- disable with `--no-prompt-upsampling` for precise prompts
- Reference images are the primary consistency tool (up to 8 images)

### GPT-5 Image

- System messages set persistent style context at zero prompt-token cost
- Character anchoring: generate base character first, reference in subsequent prompts
- Preservation lists: "character appearance must remain unchanged"
- Parameter locking: identify 3-5 critical parameters, mark as unchangeable in every prompt

### NanoBanana Pro / NanoBanana

- Supports system messages (same as GPT-5)
- Multi-reference capability is strongest in class (up to 14 references)
- Up to 5 human images for identity preservation
- **Known weakness:** Defaults to oversaturated palettes for alien/fantastical subjects
- **Mitigation:** Explicitly constrain palette: "muted earth tones, desaturated palette, no neon, naturalistic rendering"
