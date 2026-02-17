# Prompt Engineering Templates — Image Generation

SOTA prompt techniques per model. Use these as starting points, not rigid templates.

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

### Photorealistic

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

### Illustration / Concept Art

```text
[Subject], [art style], [color palette], [mood/atmosphere], [composition notes]
```

**Example:**
```text
Ancient library floating in the clouds, Studio Ghibli art style, warm amber and
deep blue color palette, serene and magical atmosphere, wide establishing shot
with tiny figures for scale
```

### Product / Commercial

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

---

## GPT-5 Image Templates

GPT-5 Image processes longer, more detailed prompts well. It benefits from natural language descriptions and handles text rendering.

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

### Diagram / Infographic

```text
Create a clean, professional [diagram type] showing [subject].
Use [color scheme]. Label each section clearly with [specific labels].
Style: [minimal/detailed/technical]. Background: [color].
All text must be crisp and readable.
```

---

## NanoBanana Templates

NanoBanana (Gemini-based) responds well to structured prompts with clear creative direction.

### Standard Generation

```text
Generate an image: [subject description].
Style: [artistic style].
Mood: [emotional tone].
Color palette: [specific colors].
Composition: [layout description].
Quality: [photorealistic/illustration/painting].
```

### Editing Instructions

When editing an existing image:

```text
Edit this image: [specific change instruction].
Keep everything else unchanged.
Maintain the same [lighting/style/color palette] as the original.
Focus the edit on [specific area/element].
```

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

### Per Model

| Model | Mistake | Fix |
|-------|---------|-----|
| Flux 2 | Requesting text in image | Use GPT-5 Image or NanoBanana Pro instead |
| Flux 2 | Overly long prompt | Keep under 80 words, front-load subject |
| GPT-5 Image | Under-describing text | Specify exact text, font style, size, position |
| GPT-5 Image | Ignoring reasoning | Let it reason; don't fight the multi-step generation |
| NanoBanana | Vague edit instructions | Be specific: "change the sky to sunset orange" not "make it better" |
| NanoBanana | Expecting Flux-level photorealism | Use Flux for pure photorealistic needs |

---

## Prompt Enhancement Protocol

When your AI agent receives a raw user prompt, enhance it before sending to the model.

### Step 1: Identify Intent
What does the user want? Photo? Illustration? Logo? Meme? Diagram?

### Step 2: Fill Gaps
Add missing elements from the universal structure:
- Subject details (if vague)
- Style/medium (if not specified)
- Lighting (if not mentioned)
- Composition (if not specified)

### Step 3: Model-Specific Formatting
- **Flux:** Compress to ~60-80 words, front-load subject, add camera/lens if photorealistic
- **GPT-5 Image:** Expand with natural language, add text specifications if needed
- **NanoBanana:** Structured format with labeled sections

### Step 4: Quality Layer
Add 1-2 quality boosters appropriate to the style.

### Example Enhancement

**User says:** "a cat in space"

**Enhanced for Flux 2 Pro:**
```text
Orange tabby cat in a custom spacesuit floating in zero gravity, Earth visible through
the helmet visor reflection, dramatic rim lighting from nearby star, shot on 50mm lens,
Kodak Ektachrome vivid colors, cinematic composition, ultra-detailed
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
