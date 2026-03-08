# fal.ai API Reference

## Authentication

```bash
export FAL_KEY="your-api-key"
```

All requests use header: `Authorization: Key <FAL_KEY>`

Key management: https://fal.ai/dashboard/keys

## Queue-Based Generation Pattern

All video models use the same three-step queue pattern: **submit -> poll -> fetch**.

### Step 1: Submit

```bash
curl -X POST "https://queue.fal.run/{model-slug}" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat sitting on a windowsill"}'
```

Response:
```json
{
  "request_id": "abc123-def456",
  "response_url": "https://queue.fal.run/{model-slug}/requests/abc123-def456",
  "status_url": "https://queue.fal.run/{model-slug}/requests/abc123-def456/status",
  "cancel_url": "https://queue.fal.run/{model-slug}/requests/abc123-def456/cancel"
}
```

### Step 2: Poll Status

```bash
curl "https://queue.fal.run/{model-slug}/requests/{request_id}/status" \
  -H "Authorization: Key $FAL_KEY"
```

Response (in progress):
```json
{
  "status": "IN_QUEUE",
  "queue_position": 3
}
```

```json
{
  "status": "IN_PROGRESS",
  "logs": [
    {"message": "Generating video...", "timestamp": "2026-03-06T12:00:00Z"}
  ]
}
```

Status values: `IN_QUEUE`, `IN_PROGRESS`, `COMPLETED`, `FAILED`

### Step 3: Fetch Result

```bash
curl "https://queue.fal.run/{model-slug}/requests/{request_id}" \
  -H "Authorization: Key $FAL_KEY"
```

Response (standard video):
```json
{
  "video": {
    "url": "https://v3.fal.media/files/.../output.mp4",
    "file_size": 8431922,
    "content_type": "video/mp4"
  }
}
```

The video URL is hosted on fal CDN temporarily. Download and persist to your own storage.

### Cancel a Request

```bash
curl -X PUT "https://queue.fal.run/{model-slug}/requests/{request_id}/cancel" \
  -H "Authorization: Key $FAL_KEY"
```

## Rate Limits

- Max 2 concurrent requests per user across ALL endpoints
- Exponential backoff on rate limit errors (HTTP 429)
- Queue system provides automatic retry semantics

## Error Responses

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process result |
| 400 | Bad request | Check payload parameters |
| 401 | Unauthorized | Check FAL_KEY |
| 402 | Payment required | Add credits |
| 404 | Not found | Check model slug |
| 422 | Unprocessable | Safety filter or invalid params |
| 429 | Rate limited | Wait + retry with backoff |
| 500 | Server error | Retry after delay |

### Error Response Format

```json
{
  "detail": "Error message explaining what went wrong"
}
```

## File Upload

For image-to-video, local images must be uploaded first:

### Step 1: Request upload URLs

```bash
curl -X POST "https://fal.ai/api/storage/upload/url" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_name":"image.jpg","content_type":"image/jpeg"}'
```

Response:

```json
{
  "file_url": "https://v3.fal.media/files/.../image.jpg",
  "upload_url": "https://storage.googleapis.com/..."
}
```

### Step 2: PUT file bytes to `upload_url`

```bash
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary "@/path/to/image.jpg"
```

Use `file_url` in model payloads as `image_url`.

Alternative: use any publicly accessible URL (the model will fetch it directly).

## Common API Parameters

These vary by model but follow general patterns:

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Required for all T2V |
| `image_url` | string | Required for I2V (URL, not local path) |
| `duration` | string/int | "4s", "8s" or integer seconds |
| `resolution` | string | "720p", "1080p" |
| `aspect_ratio` | string | "16:9", "9:16", "1:1" |
| `generate_audio` | boolean | Enable audio generation |
| `negative_prompt` | string | Exclude unwanted elements |
| `seed` | int | Reproducibility |
| `enhance_prompt` | boolean | Auto-improve prompt (Veo) |
| `cfg_scale` | float | Guidance strength |

## SDKs Available

- Python: `pip install fal-client`
- JavaScript: `npm install @fal-ai/client`
- Swift, Java/Kotlin, Dart/Flutter also available

Our generate.sh uses curl directly (no SDK dependency).

## Webhook Alternative

Instead of polling, provide a webhook URL at submit time:

```json
{
  "prompt": "...",
  "webhook_url": "https://your-server.com/callback"
}
```

fal.ai will POST the result to your webhook when generation completes. Not used in generate.sh (we poll instead for simplicity).
