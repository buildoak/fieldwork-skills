# Video Generation Pricing

All models via fal.ai. Per-second pricing unless noted. No minimums.

## Cost Per Second by Model

| Model | Friendly Name | Video Only | With Audio | Notes |
|-------|--------------|-----------|-----------|-------|
| **Wan 2.6** | `wan` | $0.05/s | $0.10/s | Cheapest |
| **LTX-2.3 Fast** | `ltx-2.3 --quality fast` | $0.04/s | $0.04/s* | Open source, 1080p |
| **LTX-2.3 Standard** | `ltx-2.3` | $0.06/s | $0.06/s* | Better quality |
| **LTX-2.3 4K** | `ltx-2.3 --resolution 4k` | $0.24/s | $0.24/s* | Only 4K option |
| **Hailuo Standard** | `hailuo` | $0.045/s | N/A | 768p |
| **Hailuo Pro** | `hailuo --quality pro` | $0.08/s | N/A | 1080p |
| **Grok Imagine** | `grok` | $0.05/s | incl. | I2V only, fastest |
| **PixVerse v5.5** | `pixverse` | $0.15-0.40/gen | incl. | Per generation |
| **Cosmos 2.5** | `cosmos` | $0.20/video | N/A | Flat per-video |
| **Kling 2.6 Pro** | `kling-2.6` | $0.07/s | $0.14/s | Single-shot quality |
| **Kling 3.0 Std** | `kling-v3` | $0.168/s | $0.336/s | Multi-shot |
| **Kling 3.0 Voice** | `kling-v3` (voice) | — | $0.392/s | Voice control |
| **Veo 3.1 Fast** | `veo-3 --quality fast` | $0.10/s | $0.15/s | Draft quality |
| **Veo 3.1 Standard** | `veo-3` | $0.20/s | $0.40/s | Premium quality |
| **Sora 2 (720p)** | `sora-2 --resolution 720p` | $0.30/s | incl. | Audio included |
| **Sora 2 (1080p)** | `sora-2` | $0.50/s | incl. | Most expensive |

*LTX audio pricing bundled into base rate.

## Quick Cost Calculator (5-Second Clip)

| Tier | Models | Video Only | With Audio |
|------|--------|-----------|-----------|
| **Budget** | LTX Fast, Wan | $0.20-0.25 | $0.20-0.50 |
| **Mid** | LTX Std, Hailuo, Grok | $0.25-0.40 | $0.30-0.40 |
| **Premium** | Kling V3, Veo 3.1 | $0.84-1.00 | $1.68-2.00 |
| **Ultra** | Sora 2 (1080p) | $2.50 | $2.50 (incl.) |

## Common Scenario Costs

| Scenario | Model | Calculation | Total |
|----------|-------|-------------|-------|
| Quick draft, 8s, 1080p | LTX Fast | 8 x $0.04 | **$0.32** |
| Social media clip, 5s | Wan | 5 x $0.05 | **$0.25** |
| Cinematic clip, 6s with audio | Veo 3.1 | 6 x $0.40 | **$2.40** |
| Multi-shot narrative, 10s | Kling V3 + audio | 10 x $0.336 | **$3.36** |
| Long clip, 25s, 1080p | Sora 2 Pro | 25 x $0.50 | **$12.50** |
| 4K output, 6s | LTX Std | 6 x $0.24 | **$1.44** |
| Iteration batch (10 drafts, 4s) | LTX Fast | 10 x 4 x $0.04 | **$1.60** |
| Veo fast draft, 4s, no audio | Veo Fast | 4 x $0.10 | **$0.40** |

## Cost Optimization Tips

1. **Always prototype with LTX Fast or Wan** ($0.04-0.05/s) -- upgrade only for final output
2. **Disable audio** when not needed (saves 33-50% on Veo and Kling)
3. **Use `--dry-run`** to preview cost before generating
4. **Start at 4s, 720p** when iterating on prompts -- scale up only after prompt is validated
5. **Two 4s clips > one 8s clip** (better quality, same cost, more control)
6. **Use Veo Fast** for prompt exploration ($0.10/s vs $0.20/s standard)
7. **4K is 4x the cost of 1080p** on LTX -- use only when resolution truly matters

## Audio Cost Impact

| Model | Video Only | With Audio | Audio Premium |
|-------|-----------|-----------|--------------|
| Veo 3.1 | $0.20/s | $0.40/s | +100% |
| Kling V3 | $0.168/s | $0.336/s | +100% |
| Wan | $0.05/s | $0.10/s | +100% |
| Sora 2 | $0.30-0.50/s | included | +0% |
| Grok | $0.05/s | included | +0% |
