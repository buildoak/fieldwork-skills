# Prompt Engineering Templates -- Image Generation

SOTA prompt techniques per model. Use these as starting points, not rigid templates.

**Note:** When using a `--preset`, the script handles style injection automatically.
These templates are for when you enhance prompts manually (no preset)
or need to understand what the preset system does internally.

---

## Universal Structure

Every effective image prompt has four layers. Order matters for attention weighting.

```text
[SUBJECT] + [ACTION/STATE] + [STYLE/MEDIUM] + [CONTEXT/ENVIRONMENT]
```

**Example:**
```text
A weathered lighthouse keeper (subject) standing at the railing, looking out to sea (action)
in the style of Edward Hopper (style), dramatic cliff edge at golden hour with crashing waves below (context)
```

---

## Flux 2 Templates

Flux responds best to concise, front-loaded prompts. Put the most important element first.
Flux 2 natively supports JSON structured prompts -- use them for multi-element scenes.

### JSON Structured Prompt (Recommended for Complex Scenes)

JSON prevents concept bleeding where adjectives from one element contaminate another.
Pass the JSON directly as the prompt text -- Flux interprets it natively.

```json
{
  "scene": "A weathered lighthouse on a rocky cliff at golden hour",
  "subjects": [
    {
      "description": "elderly keeper in dark blue wool sweater, salt-and-pepper beard",
      "position": "left third, leaning against railing",
      "action": "looking out to sea with one hand shading his eyes"
    }
  ],
  "style": "painterly illustration, visible brushstroke texture, naturalistic rendering",
  "color_palette": ["#C8A87C", "#2C3E50", "#E74C3C", "#8B9DC3", "#F0E68C"],
  "lighting": "golden hour, warm directional light from the left, long shadows",
  "mood": "contemplative, quiet, vast",
  "background": "churning grey-green sea, distant storm clouds, seabirds",
  "composition": "rule of thirds, subject at left intersection, vast sky occupying upper half",
  "camera": {
    "angle": "slightly below eye level",
    "lens": "35mm",
    "depth_of_field": "deep focus, everything sharp"
  }
}
```

### When to Use JSON vs Natural Language

| Scenario | Format | Why |
|----------|--------|-----|
| Multi-element scene (3+ subjects) | JSON | Prevents concept bleeding |
| Specific HEX color requirements | JSON | Direct palette control |
| Style consistency in a series | JSON (via preset) | Structural separation of style and content |
| Simple single-subject | Natural language | Faster, fewer tokens |
| Quick iteration | Natural language | Less overhead |

### Natural Language: Photorealistic

```text
[Subject with key details], [camera angle/shot type], [lighting condition],
[lens specification], [film stock/processing], [environment details]
```

**Example:**
```text
Portrait of an elderly Japanese potter with weathered hands shaping clay on a kick wheel,
medium close-up shot, soft natural window light from the left, shot on 85mm f/1.4 lens,
Kodak Portra 400 film stock, traditional workshop with wooden shelves of finished ceramics
```

### Natural Language: Illustration / Concept Art

```text
[Subject], [art style], [color palette], [mood/atmosphere], [composition notes]
```

**Example:**
```text
Ancient library floating in the clouds, Studio Ghibli art style, warm amber and
deep blue color palette, serene and magical atmosphere, wide establishing shot
with tiny figures for scale
```

### Natural Language: Product / Commercial

```text
[Product description], [presentation style], [background], [lighting setup],
[post-processing look]
```

**Example:**
```text
Sleek matte black wireless headphones, product hero shot on white marble surface,
single overhead softbox with subtle rim light, clean commercial photography,
high-key lighting with soft shadows
```

### Flux-Specific Rules

- **Front-load:** Word order = attention weight. Most important element first.
- **Length:** 30-80 words optimal. Under 100 max. Over 100 causes confusion.
- **No negative prompts:** Describe what you want, never what you don't.
- **HEX colors:** Associate with specific objects: "the car is #FF0000" works better than "use red #FF0000 in the image"
- **Camera specs matter:** "85mm f/2.0" vs "24mm f/11" produce very different images
- **Film stocks work:** Kodak Portra 400, Ektachrome, Cinestill 800T are well-understood
- **Sensory > explicit:** "wind ruffling fur, warm amber glow" > "windy scene with warm lighting"
- **Literal interpretation:** Avoid metaphor. Flux takes descriptions at face value.
- **prompt_upsampling:** ON by default. Auto-enhances basic prompts. Disable for precise prompts.

---

## GPT-5 Image Templates

GPT-5 Image processes longer, more detailed prompts well. It benefits from natural language descriptions and handles text rendering. It reasons before generating.

### With Text Rendering

```text
Create [image type] with the text "[EXACT TEXT]" prominently displayed.
[Describe the visual context, layout, typography style].
The text should be [font style, size, position].
[Additional visual details, colors, mood].
```

**Example:**
```text
Create a vintage-style travel poster with the text "TOKYO" prominently displayed
at the top in bold Art Deco typography. Below the text, show the Tokyo skyline
at sunset with Mount Fuji in the background. Use a warm color palette of
coral, gold, and deep navy. The poster should have a slightly worn, textured
paper appearance. Include "JAPAN" in smaller text at the bottom.
```

**Text rendering tips:**
- Put literal text in quotes or ALL CAPS
- Specify font style, size, color, placement
- Spell out uncommon words letter-by-letter for accuracy
- Demand "verbatim rendering (no extra characters)"

### Complex Scene with Reasoning

GPT-5 Image reasons before generating. Leverage this with detailed scene descriptions.

```text
I need an image of [scene description with multiple elements].
Key requirements:
1. [Specific element/positioning]
2. [Specific element/positioning]
3. [Style/mood requirement]
4. [Technical requirement]
Please ensure [critical detail that must not be missed].
```

### With System Message (for series work)

When generating a series, use `--system-prompt` or a preset's `system_message` field.

**System message template:**
```text
You are an illustration generator for [project name].
All images must follow these visual rules:
- Palette: [specific colors or HEX values]
- Rendering: [style description]
- Composition: [layout rules]
- [Quality constraints]
- [Anti-patterns to avoid]
```

This sets persistent style context at zero prompt-token cost. The user prompt then only needs the scene description.

### Diagram / Infographic

```text
Create a clean, professional [diagram type] showing [subject].
Use [color scheme]. Label each section clearly with [specific labels].
Style: [minimal/detailed/technical]. Background: [color].
All text must be crisp and readable.
```

### GPT-5 Style Consistency Tips

- **Character anchor:** Generate base character first, reference in subsequent prompts
- **Preservation lists:** For each new image, state what must stay the same
- **Parameter locking:** Mark 3-5 critical visual parameters as unchangeable in every prompt
- **Multi-reference:** Reference inputs by index: "Image 1: product photo, Image 2: style reference"

---

## NanoBanana Templates

NanoBanana (Gemini-based) responds well to structured prompts with clear creative direction.
Supports system messages and JSON structure, but natural narrative descriptions work best.

### Standard Generation

```text
Generate an image: [subject description].
Style: [artistic style].
Mood: [emotional tone].
Color palette: [specific colors].
Composition: [layout description].
Quality: [photorealistic/illustration/painting].
```

### JSON Structure (for complex multi-subject scenes)

NanoBanana handles nested JSON for segregating visual components:

```json
{
  "task": "Generate an illustration",
  "scene": {
    "description": "A busy Tokyo street crossing at night",
    "subjects": [
      {"description": "Young woman with red umbrella", "position": "center foreground"},
      {"description": "Neon signs in Japanese and English", "position": "background"}
    ],
    "environment": "Rain-slicked streets reflecting neon lights"
  },
  "style": "cinematic photography, film grain, slightly desaturated",
  "mood": "urban solitude, beautiful loneliness"
}
```

### Editing Instructions

When editing an existing image:

```text
Edit this image: [specific change instruction].
Keep everything else unchanged.
Maintain the same [lighting/style/color palette] as the original.
Focus the edit on [specific area/element].
```

### NanoBanana-Specific Rules

- **Narrative over keywords:** "A quiet morning market where vendors arrange colorful fruit" > "market, fruit, morning, colorful"
- **No quality spam:** Skip "4k, trending on artstation, masterpiece" -- it understands natural language
- **Constrain palettes explicitly:** Without constraints, defaults to oversaturated for fantastical subjects
- **Anti-patterns:** Explicitly state "no neon, no oversaturation, naturalistic rendering" for muted styles
- **Multi-reference (Pro):** Up to 14 reference images, 5 human identity preservation
- **System messages:** Same format as GPT-5, works for series consistency

---

## Camera & Lens Presets

Copy-paste these for photorealistic prompts.

| Preset | Prompt Fragment | Effect |
|--------|----------------|--------|
| Portrait | `shot on 85mm f/1.4 lens, shallow depth of field` | Soft background, subject isolation |
| Landscape | `shot on 24mm f/8 lens, deep focus` | Everything sharp, wide vista |
| Macro | `shot on 100mm macro lens, extreme close-up, f/2.8` | Tiny details, creamy bokeh |
| Street | `shot on 35mm f/2 lens, natural street lighting` | Documentary feel |
| Cinematic | `shot on anamorphic 40mm lens, 2.39:1 aspect ratio` | Lens flares, oval bokeh |
| Aerial | `drone shot from 100m altitude, wide-angle lens` | Bird's eye view |
| Tilt-shift | `tilt-shift lens effect, miniature appearance` | Toy-like, selective focus |

## Film Stock Presets

| Preset | Prompt Fragment | Look |
|--------|----------------|------|
| Portra 400 | `Kodak Portra 400 film stock, warm skin tones, fine grain` | Warm, natural, portrait-perfect |
| Ektachrome | `Kodak Ektachrome slide film, vivid saturated colors` | Punchy, high contrast |
| Tri-X 400 | `Kodak Tri-X 400, high contrast black and white, visible grain` | Classic B&W photojournalism |
| Cinestill 800T | `Cinestill 800T, tungsten-balanced, halation around highlights` | Neon glow, night photography |
| Fuji Velvia 50 | `Fuji Velvia 50, hyper-saturated colors, fine grain` | Landscape, vivid nature |
| Fuji Pro 400H | `Fuji Pro 400H, pastel tones, soft color rendition` | Soft, dreamy, wedding-style |
| Ilford HP5 | `Ilford HP5 Plus, medium contrast B&W, versatile grain` | Classic, all-purpose B&W |

---

## Style Modifier Library

### Art Movements

| Style | Prompt Fragment |
|-------|----------------|
| Impressionist | `in the style of French Impressionism, visible brushstrokes, soft light, plein air` |
| Art Nouveau | `Art Nouveau style, flowing organic lines, decorative botanical elements` |
| Art Deco | `Art Deco style, geometric patterns, gold and black, luxurious symmetry` |
| Bauhaus | `Bauhaus design, primary colors, geometric shapes, clean functional lines` |
| Ukiyo-e | `Japanese ukiyo-e woodblock print style, flat colors, bold outlines, wave patterns` |
| Constructivism | `Russian Constructivist poster, bold red and black, diagonal composition, propaganda style` |

### Digital Art Styles

| Style | Prompt Fragment |
|-------|----------------|
| Cyberpunk | `cyberpunk aesthetic, neon lights reflecting on wet streets, holographic UI elements, dystopian` |
| Vaporwave | `vaporwave aesthetic, pastel pink and cyan, Greek busts, retro technology, palm trees` |
| Low-poly | `low-poly 3D render style, geometric facets, soft gradient shading` |
| Pixel art | `detailed pixel art, 16-bit style, crisp pixels, retro game aesthetic` |
| Isometric | `isometric 3D illustration, 30-degree angle, flat shading, game asset style` |
| Flat design | `flat design illustration, bold colors, minimal shadows, clean vector style` |

### Traditional Media

| Style | Prompt Fragment |
|-------|----------------|
| Watercolor | `loose watercolor painting, wet-on-wet technique, color bleeding, white paper showing through` |
| Oil painting | `oil painting, thick impasto brushstrokes, rich color depth, canvas texture visible` |
| Charcoal | `charcoal drawing on textured paper, dramatic value range, smudged edges` |
| Ink wash | `Chinese ink wash painting, sumi-e style, minimal brushstrokes, negative space` |
| Gouache | `gouache illustration, opaque flat colors, matte finish, graphic quality` |
| Pencil sketch | `detailed pencil sketch, cross-hatching, graphite on paper, technical precision` |

### Photography Styles

| Style | Prompt Fragment |
|-------|----------------|
| Fashion editorial | `high fashion editorial photography, dramatic lighting, editorial pose, Vogue magazine style` |
| Food photography | `overhead food photography, natural window light, marble surface, fresh ingredients` |
| Architecture | `architectural photography, leading lines, dramatic perspective, golden ratio composition` |
| Nature macro | `nature macro photography, morning dew drops, shallow DOF, backlit, National Geographic quality` |
| Street documentary | `candid street photography, black and white, Magnum Photos style, decisive moment` |

---

## Quality Booster Phrases

Add these to the end of any prompt for higher quality output.

**For photorealism:**
```text
masterful composition, ultra-sharp focus, professional photography, award-winning,
8K resolution, National Geographic quality
```

**For illustration:**
```text
highly detailed, trending on ArtStation, concept art, professional illustration,
award-winning digital art
```

**For commercial/product:**
```text
studio photography, professional retouching, magazine quality, commercial campaign,
product photography masterclass
```

---

## Common Mistakes to Avoid

### All Models

| Mistake | Problem | Fix |
|---------|---------|-----|
| Prompt too long (Flux) | Flux ignores late tokens | Front-load key elements, keep under 100 words |
| Prompt too short (GPT-5) | Underspecified, generic output | Add details: lighting, mood, composition, style |
| "Beautiful" / "Amazing" | Meaningless filler | Replace with specific visual descriptors |
| Contradictory instructions | "Dark moody scene, bright vivid colors" | Pick one direction |
| Ambiguous subject | "A person in a place" | Specify: age, posture, clothing, location details |
| No style anchor | Model picks random style | Always specify medium/style |
| Negative prompts via text | "No blurry, no artifacts" | Describe what you WANT, not what you don't want |
| Verbal colors with Flux | "Use warm reds" is imprecise | Use HEX: "the wall is #B22222, the sky is #E8D4B0" |

### Per Model

| Model | Mistake | Fix |
|-------|---------|-----|
| Flux 2 | Requesting text in image | Use GPT-5 Image or NanoBanana Pro instead |
| Flux 2 | Overly long prompt | Keep under 80 words, front-load subject |
| Flux 2 | Using JSON for simple prompts | Natural language is fine for single-subject scenes |
| GPT-5 Image | Using JSON structured prompts | GPT-5 prefers natural language with labeled sections |
| GPT-5 Image | Under-describing text | Specify exact text, font style, size, position |
| GPT-5 Image | Ignoring reasoning | Let it reason; don't fight the multi-step generation |
| NanoBanana | Vague edit instructions | Be specific: "change the sky to sunset orange" not "make it better" |
| NanoBanana | Expecting Flux-level photorealism | Use Flux for pure photorealistic needs |
| NanoBanana | Not constraining palette | Explicitly state "muted," "desaturated," "no neon" for non-vivid styles |

---

## Prompt Enhancement Protocol

When your AI agent receives a raw user prompt, enhance it before sending to the model.

### Step 1: Identify Intent
What does the user want? Photo? Illustration? Logo? Meme? Diagram?

### Step 2: Select Preset (if series work)
Is this part of a visual series or project? If yes, use `--preset`.

### Step 3: Fill Gaps
Add missing elements from the universal structure:
- Subject details (if vague)
- Style/medium (if not specified)
- Lighting (if not mentioned)
- Composition (if not specified)

### Step 4: Model-Specific Formatting
- **Flux:** Compress to ~60-80 words, front-load subject, add camera/lens if photorealistic. For complex scenes, use JSON.
- **GPT-5 Image:** Expand with natural language, add text specifications if needed. Use system message for series.
- **NanoBanana:** Structured format with labeled sections. Constrain palette explicitly for muted styles.

### Step 5: Quality Layer
Add 1-2 quality boosters appropriate to the style.

### Example Enhancement

**User says:** "a cat in space"

**Enhanced for Flux 2 Pro (natural language):**
```text
Orange tabby cat in a custom spacesuit floating in zero gravity, Earth visible through
the helmet visor reflection, dramatic rim lighting from nearby star, shot on 50mm lens,
Kodak Ektachrome vivid colors, cinematic composition, ultra-detailed
```

**Enhanced for Flux 2 Pro (JSON, when part of a series):**
```json
{
  "scene": "Orange tabby cat in custom spacesuit floating in zero gravity",
  "subjects": [{"description": "Orange tabby cat, curious expression, custom-fitted spacesuit", "position": "center", "action": "floating weightlessly, one paw reaching toward a star"}],
  "style": "cinematic illustration, photorealistic textures",
  "color_palette": ["#1a1a2e", "#16213e", "#FF6B35", "#F5F5DC"],
  "lighting": "dramatic rim lighting from nearby star, Earth glow fill",
  "mood": "wonder, adventure, playful",
  "composition": "center subject, Earth in background, star field",
  "camera": {"angle": "slightly below", "lens": "50mm"}
}
```

**Enhanced for GPT-5 Image:**
```text
Create a playful and heartwarming illustration of an orange tabby cat wearing a
miniature astronaut suit, floating gracefully in the vacuum of space. The cat should
have a curious expression visible through the clear helmet visor. Earth is visible
in the background, blue and luminous. Stars scatter across the deep black of space.
The lighting is dramatic with a warm rim light from a nearby star. Style: Pixar-quality
3D rendering with photorealistic textures. The image should feel whimsical yet
scientifically detailed.
```
