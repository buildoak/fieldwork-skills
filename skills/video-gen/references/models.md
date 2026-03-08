# Video Model Catalog

Complete catalog of video models available via fal.ai. Organized by tier.

## Tier 1: Premium Models

### Veo 3.1 (Google DeepMind)

| Spec | Value |
|------|-------|
| Friendly name | `veo-3` |
| T2V endpoint | `fal-ai/veo3` (standard), `fal-ai/veo3/fast` |
| I2V endpoint | `fal-ai/veo3/image-to-video`, `fal-ai/veo3/fast/image-to-video` |
| Special | `fal-ai/veo3/reference-to-video` |
| Modes | T2V, I2V, Reference-to-Video |
| Resolution | 720p, 1080p |
| Duration | 4s, 6s, 8s |
| FPS | 24 |
| Audio | Native -- dialogue, SFX, ambient. Best-in-class lip sync |
| Aspect Ratios | 16:9, 9:16, 1:1 |
| Pricing (standard) | $0.20/s (no audio), $0.40/s (with audio) |
| Pricing (fast) | $0.10-0.15/s |
| Latency | Standard: 90-120s. Fast: 45-70s |
| Best for | Dialogue, talking heads, lip sync, audio-critical production |

### Sora 2 (OpenAI)

| Spec | Value |
|------|-------|
| Friendly name | `sora-2` |
| T2V endpoint | `fal-ai/sora-2/text-to-video` (standard), `fal-ai/sora-2/text-to-video/pro` |
| I2V endpoint | `fal-ai/sora-2/image-to-video`, `fal-ai/sora-2/image-to-video/pro` |
| Special | `fal-ai/sora-2/video-to-video/remix` (V2V) |
| Modes | T2V, I2V, V2V Remix |
| Resolution | 720p, 1080p. Pro: 1024x1792, 1792x1024 |
| Duration | 4s, 8s, 12s. Pro: up to 25s |
| Audio | Native -- dialogue, ambient, synchronized |
| Aspect Ratios | 16:9, 9:16. Pro adds 1024x1792 |
| Pricing | $0.30/s (720p), $0.50/s (1080p) |
| Best for | Complex scenes, precision, long clips, remix/editing |

### Kling 3.0 (Kuaishou)

| Spec | Value |
|------|-------|
| Friendly name | `kling-v3` |
| T2V endpoint | `fal-ai/kling-video/v3/pro/text-to-video` |
| I2V endpoint | `fal-ai/kling-video/v3/pro/image-to-video` |
| Also available | `kling-2.6`: `fal-ai/kling-video/v2.6/pro/image-to-video` |
| O3 variant | `fal-ai/kling-video/o3/standard/image-to-video` |
| Modes | T2V, I2V, Start+End Frame, Multi-Shot, Motion Control, Element Reference |
| Resolution | Up to 1080p |
| Duration | 3-15s (flexible) |
| Audio | Chinese, English, Japanese, Korean, Spanish. Lip sync, dialogue, singing |
| Pricing (V3 Std) | $0.168/s (no audio), $0.336/s (audio) |
| Pricing (V2.6) | $0.07/s (video), $0.14/s (audio) |
| Best for | Cinematic multi-shot narratives, character consistency |

## Tier 2: Value Models

### LTX-2.3 (Lightricks, Open Source)

| Spec | Value |
|------|-------|
| Friendly name | `ltx-2.3` |
| T2V endpoint | `fal-ai/ltx-2.3/text-to-video`, `fal-ai/ltx-2.3/text-to-video/fast` |
| I2V endpoint | `fal-ai/ltx-2.3/image-to-video` |
| Special | `fal-ai/ltx-2.3/audio-to-video`, `fal-ai/ltx-2.3/extend-video`, `fal-ai/ltx-2.3/retake-video` |
| Modes | T2V, I2V, Audio-to-Video, Extend, Retake |
| Resolution | 1080p, 1440p, 2160p (4K) |
| Duration | Up to 20s |
| FPS | 24 or 48 |
| Audio | Native (cleaner in 2.3) |
| Pricing | Fast: $0.04/s (1080p). Standard: $0.06/s (1080p). 4K: $0.24/s |
| License | Apache 2.0 (open source, self-hostable) |
| Best for | Budget, iteration, LoRA fine-tuning, 4K, audio-to-video |

### Wan 2.5/2.6 (Alibaba)

| Spec | Value |
|------|-------|
| Friendly name | `wan` |
| T2V endpoint | `fal-ai/wan-25-preview/text-to-video` |
| I2V endpoint | `fal-ai/wan-25-preview/image-to-video`, `wan/v2.6/image-to-video` |
| Resolution | 720p, 1080p |
| Duration | 5s, 10s |
| Audio | Native (2.5+) |
| Pricing | ~$0.05/s (cheapest), ~$0.10/s with audio |
| Best for | Fast iteration, social media, budget workflows |

### MiniMax Hailuo-02

| Spec | Value |
|------|-------|
| Friendly name | `hailuo` |
| T2V endpoint | `fal-ai/minimax/hailuo-02/pro/text-to-video` |
| I2V endpoint | `fal-ai/minimax/hailuo-02/standard/image-to-video`, `fal-ai/minimax/hailuo-02/pro/image-to-video` |
| Resolution | 512p, 768p (Standard), 1080p (Pro) |
| Duration | Up to 10s |
| FPS | 24-30 |
| Pricing | Standard 768p: $0.045/s. Pro 1080p: $0.08/s |
| Best for | Anime/stylization, micro-expressions, camera control |

## Tier 3: Specialized Models

### Cosmos Predict 2.5 (NVIDIA)

| Spec | Value |
|------|-------|
| Friendly name | `cosmos` |
| T2V endpoint | `fal-ai/cosmos-predict-2.5/text-to-video` |
| I2V endpoint | `fal-ai/cosmos-predict-2.5/image-to-video` |
| Special | `fal-ai/cosmos-predict-2.5/video-to-video` |
| Pricing | $0.20/video (flat) |
| Gen Time | ~7 minutes |
| Best for | Physics-accurate generation, robotics/simulation data |

### PixVerse v5.5

| Friendly name | `pixverse` |
| T2V | `fal-ai/pixverse/v5.5/text-to-video` |
| I2V | `fal-ai/pixverse/v5.5/image-to-video` |
| Pricing | $0.15-0.40/generation |
| Best for | Social media short-form, motion consistency, effects |

### Grok Imagine Video (xAI)

| Friendly name | `grok` |
| I2V | `xai/grok-imagine-video/image-to-video` |
| Pricing | ~$0.05/s |
| Speed | <15s for 6s clip (5-10x faster than most) |
| Note | I2V only -- no T2V endpoint |

### HeyGen Avatar 4

| Endpoint | `fal-ai/heygen/avatar4/image-to-video` |
| Special | `fal-ai/heygen/v2/translate/speed`, `fal-ai/heygen/v2/translate/precision` |
| Best for | Talking head avatars, multilingual lip sync, presentations |

### Other Models

| Model | Endpoint | Capability |
|-------|----------|------------|
| MultiShotMaster | `fal-ai/multishot-master` | Multi-shot narrative T2V |
| Lucy I2V | `fal-ai/decart/lucy-i2v` | Lightning-fast I2V |
| LTX Video 13B | `fal-ai/ltx-2-19b/image-to-video` | Distilled faster LTX |

## Quick Decision Matrix

| Use Case | Best Model | Why |
|----------|-----------|-----|
| Cinematic/film quality | `veo-3` | Best lip sync, audio, natural performances |
| Multi-shot narrative | `kling-v3` | Native 6-shot support, character consistency |
| Animation/stylized | `hailuo` | Anime support, style effects |
| Fast iteration/drafts | `wan` or `ltx-2.3 --quality fast` | $0.04-0.05/s |
| Long clips (>10s) | `sora-2 --quality pro` | Up to 25s |
| Image-to-video | `kling-v3` | Element referencing, text preservation |
| Audio sync/dialogue | `veo-3` | Best-in-class lip sync |
| Best cost/quality | `ltx-2.3` | $0.04-0.06/s, open source, 4K |
| Physics accuracy | `cosmos` | RL-trained on physics |
| 4K output | `ltx-2.3` | Only model with native 4K |
| Video editing/remix | `sora-2` with remix | Transform existing videos |
| Speed (fastest gen) | `grok` | <15s for 6s clip |
