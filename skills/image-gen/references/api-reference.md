# API Reference — OpenRouter Image Generation

Endpoint: `https://openrouter.ai/api/v1/chat/completions`
Auth: `Authorization: Bearer $OPENROUTER_API_KEY_IMAGES`

---

## Request Format

### Text-to-Image (Image-Only Models: Flux)

```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY_IMAGES" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "black-forest-labs/flux.2-pro",
    "messages": [
      {
        "role": "user",
        "content": "A red fox sitting in a snowy forest, golden hour lighting, photorealistic"
      }
    ],
    "modalities": ["image"],
    "image_config": {
      "aspect_ratio": "16:9",
      "image_size": "2K"
    }
  }'
```

### Text-to-Image (Text+Image Models: GPT-5, NanoBanana)

```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY_IMAGES" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-5-image",
    "messages": [
      {
        "role": "user",
        "content": "Generate a minimalist logo for a coffee shop called Morning Brew"
      }
    ],
    "modalities": ["text", "image"]
  }'
```

### Image Editing (Chat-Based)

Send the original image as base64 in the message content array.

```bash
curl -X POST https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY_IMAGES" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/gemini-3-pro-image-preview",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Change the background to a sunset beach scene"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/png;base64,iVBORw0KGgo..."
            }
          }
        ]
      }
    ],
    "modalities": ["text", "image"],
    "image_config": {
      "aspect_ratio": "16:9",
      "image_size": "2K"
    }
  }'
```

---

## image_config Parameters

| Parameter | Type | Values | Default | Notes |
|-----------|------|--------|---------|-------|
| `aspect_ratio` | string | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` | `1:1` | Not all models support all ratios |
| `image_size` | string | `1K`, `2K`, `4K` | `1K` | 4K only supported by Flux Pro and NanoBanana Pro |

---

## Response Format

### Image-Only Response (Flux models)

```json
{
  "id": "gen-abc123",
  "model": "black-forest-labs/flux.2-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "images": [
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
            }
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 0,
    "total_tokens": 15
  }
}
```

### Text+Image Response (GPT-5, NanoBanana)

```json
{
  "id": "gen-xyz789",
  "model": "openai/gpt-5-image",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here's your coffee shop logo with a minimalist design...",
        "images": [
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
            }
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 1200,
    "total_tokens": 1225
  }
}
```

---

## Extracting Images from Response

The base64 image data lives at:
```
response.choices[0].message.images[0].image_url.url
```

Strip the `data:image/png;base64,` prefix to get raw base64, then decode to bytes.

**Python extraction:**
```python
import base64

for choice in response["choices"]:
    for img in choice["message"].get("images", []):
        url = img["image_url"]["url"]
        b64_data = url.split("base64,", 1)[1]
        img_bytes = base64.b64decode(b64_data)
        with open("output.png", "wb") as f:
            f.write(img_bytes)
```

**Fallback:** Some models may return images in the content array instead:
```json
{
  "content": [
    {"type": "text", "text": "Here's your image"},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
  ]
}
```

The generate.py script handles both paths automatically.

---

## Error Codes

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request (invalid model, params) | Check model ID and parameters |
| 401 | Invalid API key | Verify OPENROUTER_API_KEY_IMAGES |
| 402 | Insufficient credits | Top up OpenRouter account |
| 429 | Rate limited | Wait and retry with exponential backoff |
| 500 | Server error | Retry after 5s |
| 502/503 | Provider unavailable | Try different model or wait |

**Error response shape:**
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "metadata": {
      "provider_name": "Black Forest Labs"
    }
  }
}
```

---

## Rate Limits

OpenRouter enforces per-key rate limits. Typical limits:
- Free tier: 20 requests/minute
- Paid tier: 200 requests/minute
- Per-model limits may be lower (check model page)

---

## OpenAI Direct API (Mask-Based Editing)

For mask-based inpainting, use OpenAI's `/v1/images/edits` endpoint directly.

```bash
curl -X POST https://api.openai.com/v1/images/edits \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "image=@input.png" \
  -F "mask=@mask.png" \
  -F "prompt=A cute cat sitting on the grass" \
  -F "model=gpt-image-1" \
  -F "size=1024x1024" \
  -F "response_format=b64_json"
```

**Response:**
```json
{
  "created": 1706000000,
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ]
}
```

**Mask format:** PNG with transparent areas marking regions to edit. Opaque areas are preserved.

**Available sizes:** `1024x1024`, `1536x1024`, `1024x1536`
**Quality options:** `low`, `medium`, `high`, `auto`

---

## Headers

### Required
```
Authorization: Bearer $API_KEY
Content-Type: application/json
```

### Optional (recommended)
```
HTTP-Referer: https://your-app.com
X-Title: Your App Name
```

These allow your usage to appear on OpenRouter leaderboards.

---

## Seed Parameter

Supported by: GPT-5 Image, NanoBanana Pro, NanoBanana.
NOT supported by: Flux models (via OpenRouter).

```json
{
  "seed": 42,
  "model": "openai/gpt-5-image",
  ...
}
```

**Note:** Seed reproducibility is not guaranteed across different providers or model versions. It provides best-effort determinism.
