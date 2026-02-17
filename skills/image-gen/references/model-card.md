# Model Card — Image Generation Stack

All models accessed via OpenRouter `/api/v1/chat/completions` unless noted.

---

## Model Comparison

| Model | ID | Speed | Quality | Text in Image | Image Editing | Cost | Best For |
|-------|-----|-------|---------|:---:|:---:|------|----------|
| **Flux 2 Pro** | `black-forest-labs/flux.2-pro` | Medium | Excellent | No | Yes (ref images) | ~$0.03/MP | Default high-quality generation |
| **Flux 2 Klein** | `black-forest-labs/flux.2-klein-4b` | Fast | Good | No | No | ~$0.014/MP | Budget/fast generation |
| **GPT-5 Image** | `openai/gpt-5-image` | Slow | Excellent | Excellent | Excellent | ~$0.04/image | Text rendering, complex edits, reasoning |
| **NanoBanana Pro** | `google/gemini-3-pro-image-preview` | Medium | Excellent | Good | Excellent | ~$0.012/image | Versatile gen + edit, 2K/4K output |
| **NanoBanana** | `google/gemini-2.5-flash-image` | Fast | Good | Fair | Good | ~$0.0004/image | Cheapest viable option |

---

## Decision Tree

```
What do you need?
  |
  +-- Fast, cheap, good enough?
  |     --> NanoBanana (gemini-2.5-flash-image) — $0.0004/image
  |
  +-- High quality, no text needed?
  |     --> Flux 2 Pro — best overall image quality
  |
  +-- Text in the image? (labels, signs, UI mockups)
  |     --> GPT-5 Image — best text rendering by far
  |
  +-- Image editing? (modify existing image)
  |     +-- Chat-based edit (describe changes)?
  |     |     --> GPT-5 Image or NanoBanana Pro
  |     +-- Mask-based inpainting (paint area to change)?
  |           --> OpenAI API directly (edit.py --mode openai)
  |
  +-- Budget generation at scale?
  |     --> Flux 2 Klein — fastest Flux, lowest cost
  |
  +-- High quality + editing + reasoning?
        --> NanoBanana Pro — best balance of capability and cost
```

---

## Detailed Model Profiles

### Flux 2 Pro (`black-forest-labs/flux.2-pro`)

**Strengths:**
- Frontier-level visual quality and reliability
- Strong prompt adherence
- Stable lighting, sharp textures
- Consistent character/style across references
- Up to 4 MP resolution

**Weaknesses:**
- No text rendering in images
- Image-only output (no conversational text)
- More expensive than Klein

**Modalities:** Input: text, image | Output: image only
**Pricing:** $0.03 first MP, $0.015 each subsequent MP
**Context:** 46,864 tokens

### Flux 2 Klein (`black-forest-labs/flux.2-klein-4b`)

**Strengths:**
- Fastest in Flux 2 family
- Most cost-effective Flux option
- Maintains good image quality for the speed

**Weaknesses:**
- Lower quality than Pro
- No text rendering
- No image input for editing

**Modalities:** Input: text | Output: image only
**Pricing:** $0.014 first MP, $0.001 subsequent MP

### GPT-5 Image (`openai/gpt-5-image`)

**Strengths:**
- Best text rendering in generated images (signs, labels, UI)
- Superior instruction adherence
- Detailed editing from natural language
- Can reason about images before generating
- 400K token context window

**Weaknesses:**
- Most expensive per image
- Slower generation
- Mandatory reasoning adds latency

**Modalities:** Input: text, image, file | Output: text, image
**Pricing:** $10/M input tokens, $40/M image output tokens
**Context:** 400,000 tokens

### NanoBanana Pro (`google/gemini-3-pro-image-preview`)

**Strengths:**
- Most advanced Google image model
- Fine-grained creative controls (localized edits, lighting, focus, camera)
- 2K/4K output with flexible aspect ratios
- Multi-image blending
- Identity preservation across subjects
- Industry-leading text rendering (second only to GPT-5)

**Weaknesses:**
- Preview model — may have availability fluctuations
- Higher cost than base NanoBanana

**Modalities:** Input: text, image | Output: text, image
**Pricing:** $2/M input, $12/M output tokens
**Context:** 65,536 tokens

### NanoBanana (`google/gemini-2.5-flash-image`)

**Strengths:**
- Extremely cheap (~$0.0004 per image)
- Fast generation
- Decent quality for the price
- Supports both generation and editing

**Weaknesses:**
- Lower quality than Pro/Flux/GPT-5
- Weaker text rendering
- Smaller context window

**Modalities:** Input: text, image | Output: text, image
**Pricing:** $0.1/M input, $0.4/M output tokens

---

## Aspect Ratio Support

| Ratio | Flux Pro | Flux Klein | GPT-5 Image | NanoBanana Pro | NanoBanana |
|-------|:---:|:---:|:---:|:---:|:---:|
| 1:1 | Y | Y | Y | Y | Y |
| 2:3 | Y | Y | - | Y | Y |
| 3:2 | Y | Y | - | Y | Y |
| 3:4 | Y | Y | - | Y | Y |
| 4:3 | Y | Y | - | Y | Y |
| 4:5 | Y | Y | - | Y | Y |
| 5:4 | Y | Y | - | Y | Y |
| 9:16 | Y | Y | - | Y | Y |
| 16:9 | Y | Y | - | Y | Y |
| 21:9 | Y | Y | - | Y | Y |

GPT-5 Image uses fixed sizes (1024x1024, 1536x1024, 1024x1536) rather than aspect ratios.

## Image Size Support

| Size | Flux Pro | Flux Klein | GPT-5 Image | NanoBanana Pro | NanoBanana |
|------|:---:|:---:|:---:|:---:|:---:|
| 1K | Y | Y | Y (1024px) | Y | Y |
| 2K | Y | Y | Y (1536px) | Y | Y |
| 4K | Y | - | - | Y | - |

---

## Image Input for Editing

| Feature | Flux Pro | Flux Klein | GPT-5 Image | NanoBanana Pro | NanoBanana |
|---------|:---:|:---:|:---:|:---:|:---:|
| Chat-based edit | Y (ref images) | N | Y | Y | Y |
| Mask inpainting | N | N | Y (via OpenAI API) | N | N |
| Multi-image blend | N | N | N | Y | N |
| Style transfer | Y | N | Y | Y | Y |
