#!/usr/bin/env python3
"""video-gen generate.py — fal.ai multi-model video generation.

Queue-based: submit -> poll -> fetch -> download.
Returns JSON to stdout. Logs to stderr.
Python 3.10+, stdlib + requests only.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print(json.dumps({"success": False, "error": "Missing 'requests' library. Install: pip3 install requests"}))
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = Path.cwd() / "output"
FAL_BASE = "https://queue.fal.run"
POLL_INTERVAL = 3
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str, mode: str = "", model: str = "") -> None:
    log(f"ERROR: {msg}")
    print(json.dumps({"success": False, "error": msg, "mode": mode, "model": model}))
    sys.exit(1)


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]", "-", text.lower())
    s = re.sub(r"-+", "-", s).strip("-")[:40]
    return s or "video"


# ---------------------------------------------------------------------------
# Model slug resolution
# ---------------------------------------------------------------------------

MODEL_ENDPOINTS: dict[str, str] = {
    # Kling V3
    "kling-v3:t2v:fast":        "fal-ai/kling-video/v3/pro/text-to-video",
    "kling-v3:t2v:standard":    "fal-ai/kling-video/v3/pro/text-to-video",
    "kling-v3:t2v:pro":         "fal-ai/kling-video/v3/pro/text-to-video",
    "kling-v3:i2v:fast":        "fal-ai/kling-video/v3/pro/image-to-video",
    "kling-v3:i2v:standard":    "fal-ai/kling-video/v3/pro/image-to-video",
    "kling-v3:i2v:pro":         "fal-ai/kling-video/v3/pro/image-to-video",
    # Kling 2.6
    "kling-2.6:t2v:fast":       "fal-ai/kling-video/v2.6/pro/text-to-video",
    "kling-2.6:t2v:standard":   "fal-ai/kling-video/v2.6/pro/text-to-video",
    "kling-2.6:t2v:pro":        "fal-ai/kling-video/v2.6/pro/text-to-video",
    "kling-2.6:i2v:fast":       "fal-ai/kling-video/v2.6/pro/image-to-video",
    "kling-2.6:i2v:standard":   "fal-ai/kling-video/v2.6/pro/image-to-video",
    "kling-2.6:i2v:pro":        "fal-ai/kling-video/v2.6/pro/image-to-video",
    # Veo 3.1
    "veo-3:t2v:fast":           "fal-ai/veo3/fast",
    "veo-3:t2v:standard":       "fal-ai/veo3",
    "veo-3:t2v:pro":            "fal-ai/veo3",
    "veo-3:i2v:fast":           "fal-ai/veo3/fast/image-to-video",
    "veo-3:i2v:standard":       "fal-ai/veo3/image-to-video",
    "veo-3:i2v:pro":            "fal-ai/veo3/image-to-video",
    # Sora 2
    "sora-2:t2v:fast":          "fal-ai/sora-2/text-to-video",
    "sora-2:t2v:standard":      "fal-ai/sora-2/text-to-video",
    "sora-2:t2v:pro":           "fal-ai/sora-2/text-to-video/pro",
    "sora-2:i2v:fast":          "fal-ai/sora-2/image-to-video",
    "sora-2:i2v:standard":      "fal-ai/sora-2/image-to-video",
    "sora-2:i2v:pro":           "fal-ai/sora-2/image-to-video/pro",
    # LTX-2.3
    "ltx-2.3:t2v:fast":         "fal-ai/ltx-2.3/text-to-video/fast",
    "ltx-2.3:t2v:standard":     "fal-ai/ltx-2.3/text-to-video",
    "ltx-2.3:t2v:pro":          "fal-ai/ltx-2.3/text-to-video",
    "ltx-2.3:i2v:fast":         "fal-ai/ltx-2.3/image-to-video/fast",
    "ltx-2.3:i2v:standard":     "fal-ai/ltx-2.3/image-to-video",
    "ltx-2.3:i2v:pro":          "fal-ai/ltx-2.3/image-to-video",
    # Wan
    "wan:t2v:fast":              "fal-ai/wan-25-preview/text-to-video",
    "wan:t2v:standard":          "fal-ai/wan-25-preview/text-to-video",
    "wan:t2v:pro":               "fal-ai/wan-25-preview/text-to-video",
    "wan:i2v:fast":              "fal-ai/wan-25-preview/image-to-video",
    "wan:i2v:standard":          "fal-ai/wan-25-preview/image-to-video",
    "wan:i2v:pro":               "fal-ai/wan-25-preview/image-to-video",
    # Hailuo / MiniMax
    "hailuo:t2v:fast":          "fal-ai/minimax/hailuo-02/pro/text-to-video",
    "hailuo:t2v:standard":      "fal-ai/minimax/hailuo-02/pro/text-to-video",
    "hailuo:t2v:pro":           "fal-ai/minimax/hailuo-02/pro/text-to-video",
    "hailuo:i2v:fast":          "fal-ai/minimax/hailuo-02/standard/image-to-video",
    "hailuo:i2v:standard":      "fal-ai/minimax/hailuo-02/standard/image-to-video",
    "hailuo:i2v:pro":           "fal-ai/minimax/hailuo-02/pro/image-to-video",
    # Cosmos
    "cosmos:t2v:fast":           "fal-ai/cosmos-predict-2.5/text-to-video",
    "cosmos:t2v:standard":       "fal-ai/cosmos-predict-2.5/text-to-video",
    "cosmos:t2v:pro":            "fal-ai/cosmos-predict-2.5/text-to-video",
    "cosmos:i2v:fast":           "fal-ai/cosmos-predict-2.5/image-to-video",
    "cosmos:i2v:standard":       "fal-ai/cosmos-predict-2.5/image-to-video",
    "cosmos:i2v:pro":            "fal-ai/cosmos-predict-2.5/image-to-video",
    # PixVerse
    "pixverse:t2v:fast":         "fal-ai/pixverse/v5.5/text-to-video",
    "pixverse:t2v:standard":     "fal-ai/pixverse/v5.5/text-to-video",
    "pixverse:t2v:pro":          "fal-ai/pixverse/v5.5/text-to-video",
    "pixverse:i2v:fast":         "fal-ai/pixverse/v5.5/image-to-video",
    "pixverse:i2v:standard":     "fal-ai/pixverse/v5.5/image-to-video",
    "pixverse:i2v:pro":          "fal-ai/pixverse/v5.5/image-to-video",
    # Grok (i2v only)
    "grok:i2v:fast":             "xai/grok-imagine-video/image-to-video",
    "grok:i2v:standard":         "xai/grok-imagine-video/image-to-video",
    "grok:i2v:pro":              "xai/grok-imagine-video/image-to-video",
}

DURATION_CONSTRAINTS = {
    "ltx-2.3": {"min": 2, "max": 10, "step": None, "valid": [2, 4, 6, 8, 10]},
    "ltx": {"min": 2, "max": 10, "step": None, "valid": [2, 4, 6, 8, 10]},
    "kling-3.0": {"min": 5, "max": 10, "step": 5, "valid": [5, 10]},
    "kling": {"min": 5, "max": 10, "step": 5, "valid": [5, 10]},
    "veo-3.1": {"min": 5, "max": 8, "step": None, "valid": None},
    "veo": {"min": 5, "max": 8, "step": None, "valid": None},
    "sora-2": {"min": 5, "max": 20, "step": None, "valid": None},
    "sora": {"min": 5, "max": 20, "step": None, "valid": None},
    "hailuo-02": {"min": 4, "max": 6, "step": None, "valid": None},
    "hailuo": {"min": 4, "max": 6, "step": None, "valid": None},
    "wan-2.6": {"min": 3, "max": 5, "step": None, "valid": None},
    "wan-2.5": {"min": 3, "max": 5, "step": None, "valid": None},
    "wan": {"min": 3, "max": 5, "step": None, "valid": None},
    "cosmos-2.0": {"min": 5, "max": 9, "step": None, "valid": None},
    "cosmos": {"min": 5, "max": 9, "step": None, "valid": None},
    "kling-v3": {"min": 5, "max": 10, "step": 5, "valid": [5, 10]},
    "kling-2.6": {"min": 5, "max": 10, "step": 5, "valid": [5, 10]},
    "veo-3": {"min": 5, "max": 8, "step": None, "valid": None},
}

def resolve_slug(model: str, mode: str, quality: str) -> str:
    key = f"{model}:{mode}:{quality}"
    slug = MODEL_ENDPOINTS.get(key)
    if slug:
        return slug

    # Also try without quality for backward compat
    for q in ("fast", "standard", "pro"):
        fallback = MODEL_ENDPOINTS.get(f"{model}:{mode}:{q}")
        if fallback:
            return fallback

    fail(f"No fal.ai endpoint for model={model} mode={mode} quality={quality}. See references/models.md",
         mode=mode, model=model)
    return ""  # unreachable


def validate_duration(model: str, duration: int) -> None:
    """Validate duration against model constraints. Raises SystemExit on failure."""
    constraints = DURATION_CONSTRAINTS.get(model)
    if not constraints:
        return  # Unknown model, skip validation

    if constraints["valid"]:
        if duration not in constraints["valid"]:
            fail(f"Model '{model}' only supports durations: {constraints['valid']}. Got: {duration}")
    else:
        if duration < constraints["min"] or duration > constraints["max"]:
            fail(f"Model '{model}' supports duration {constraints['min']}-{constraints['max']}s. Got: {duration}s")


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------

def get_cost_per_second(model: str, quality: str, resolution: str, audio: bool) -> float:
    key = f"{model}:{quality}"

    if model == "ltx-2.3":
        if quality == "fast":
            return {"4k": 0.16, "1440p": 0.08}.get(resolution, 0.04)
        return {"4k": 0.24, "1440p": 0.12}.get(resolution, 0.06)

    if model == "wan":
        return 0.10 if audio else 0.05
    if model == "hailuo":
        return 0.08 if quality == "pro" else 0.045
    if model == "cosmos":
        return 0.04
    if model == "pixverse":
        return 0.06
    if model == "grok":
        return 0.05

    if model == "kling-v3":
        return 0.336 if audio else 0.168
    if model == "kling-2.6":
        return 0.14 if audio else 0.07

    if model == "veo-3":
        if quality == "fast":
            return 0.15 if audio else 0.10
        return 0.40 if audio else 0.20

    if model == "sora-2":
        return 0.50 if resolution == "1080p" else 0.30

    return 0.10  # fallback


def estimate_cost(model: str, quality: str, resolution: str, duration: int, audio: bool) -> float:
    rate = get_cost_per_second(model, quality, resolution, audio)
    return round(rate * duration, 2)


# ---------------------------------------------------------------------------
# Resolution normalization
# ---------------------------------------------------------------------------

RESOLUTION_MAP = {
    "720p": "720p", "1080p": "1080p", "1440p": "1440p",
    "4k": "4k", "4K": "4k", "2160p": "4k",
    "1920x1080": "1080p", "1280x720": "720p",
    "2560x1440": "1440p", "3840x2160": "4k",
}


# ---------------------------------------------------------------------------
# API key retrieval
# ---------------------------------------------------------------------------

def resolve_fal_key():
    """Resolve FAL_KEY: env var first, optional vault CLI fallback."""
    key = os.environ.get("FAL_KEY")
    if key:
        return key

    # Optional: try vault CLI if on PATH
    import shutil
    vault_bin = shutil.which("vault.sh") or shutil.which("vault")
    if vault_bin:
        try:
            result = subprocess.run([vault_bin, "get", "FAL_KEY"],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    fail("FAL_KEY not set. Export it or use your secrets manager.\n"
         "  export FAL_KEY='your-fal-ai-key'")
    return ""  # unreachable


# ---------------------------------------------------------------------------
# Image upload
# ---------------------------------------------------------------------------

SUPPORTED_IMAGE_EXTS = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "png": "image/png", "webp": "image/webp",
}


def upload_image(image_path: str, auth_header: str) -> str:
    """Upload local image to fal.ai storage. Returns the hosted URL."""
    p = Path(image_path)
    ext = p.suffix.lstrip(".").lower()
    content_type = SUPPORTED_IMAGE_EXTS.get(ext)
    if not content_type:
        fail(f"Unsupported image extension: .{ext} (supported: .jpg, .jpeg, .png, .webp)")

    log("Uploading image to fal.ai storage (two-step upload)...")

    # Step 1: get upload URL
    meta_resp = requests.post(
        "https://rest.alpha.fal.ai/storage/upload/initiate",
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
        json={"file_name": p.name, "content_type": content_type},
        timeout=30,
    )
    if not meta_resp.ok:
        detail = _extract_error(meta_resp)
        fail(f"Image upload init failed (HTTP {meta_resp.status_code}): {detail}")

    meta = meta_resp.json()
    file_url = meta.get("file_url", "")
    upload_url = meta.get("upload_url", "")
    if not file_url or not upload_url:
        fail(f"Image upload init returned invalid response: {json.dumps(meta)}")

    # Step 2: PUT file bytes
    with open(image_path, "rb") as f:
        put_resp = requests.put(
            upload_url,
            headers={"Content-Type": content_type},
            data=f,
            timeout=120,
        )
    if not put_resp.ok:
        fail(f"Image upload PUT failed (HTTP {put_resp.status_code})")

    log(f"Image uploaded: {file_url}")
    return file_url


# ---------------------------------------------------------------------------
# Per-model payload builders
# ---------------------------------------------------------------------------

def build_payload(
    model: str, mode: str, prompt: str, image_url: str,
    duration: int, resolution: str, aspect: str, fps: int,
    quality: str, generate_audio: bool, negative_prompt: str, seed: int | None,
) -> dict:
    payload: dict = {}

    match model:
        case "kling-v3" | "kling-2.6":
            payload = {"prompt": prompt, "duration": str(duration), "aspect_ratio": aspect}
            if mode == "i2v":
                payload["image_url"] = image_url
            if generate_audio:
                payload["generate_audio"] = True
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

        case "veo-3":
            payload = {
                "prompt": prompt,
                "duration": f"{duration}s",
                "aspect_ratio": aspect,
                "resolution": resolution,
            }
            if mode == "i2v":
                payload["image_url"] = image_url
            payload["generate_audio"] = generate_audio
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

        case "sora-2":
            payload = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect,
                "resolution": resolution,
            }
            if mode == "i2v":
                payload["image_url"] = image_url

        case "ltx-2.3":
            payload = {
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect,
                "fps": fps,
            }
            if mode == "i2v":
                payload["image_url"] = image_url
            if generate_audio:
                payload["generate_audio"] = True
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

        case "wan":
            payload = {"prompt": prompt, "resolution": resolution}
            if mode == "i2v":
                payload["image_url"] = image_url
            if generate_audio:
                payload["generate_audio"] = True
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt

        case "hailuo":
            payload = {"prompt": prompt, "resolution": resolution}
            if mode == "i2v":
                payload["image_url"] = image_url

        case "cosmos":
            payload = {"prompt": prompt}
            if mode == "i2v":
                payload["image_url"] = image_url

        case "pixverse":
            payload = {"prompt": prompt}
            if mode == "i2v":
                payload["image_url"] = image_url

        case "grok":
            payload = {"prompt": prompt, "image_url": image_url}

        case _:
            payload = {"prompt": prompt}
            if image_url:
                payload["image_url"] = image_url

    if seed is not None:
        payload["seed"] = seed

    return payload


# ---------------------------------------------------------------------------
# Error extraction helper
# ---------------------------------------------------------------------------

def _extract_error(resp: requests.Response) -> str:
    try:
        data = resp.json()
        return data.get("detail") or data.get("error") or data.get("message") or str(data)
    except Exception:
        return resp.text[:500]


# ---------------------------------------------------------------------------
# Video URL extraction from result
# ---------------------------------------------------------------------------

def extract_video_url(result: dict) -> str:
    """Try several known response shapes to find the video URL."""
    # Standard: {"video": {"url": "..."}}
    url = (result.get("video") or {}).get("url")
    if url:
        return url
    # {"output": {"video": {"url": "..."}}}
    url = ((result.get("output") or {}).get("video") or {}).get("url")
    if url:
        return url
    # {"data": {"video": {"url": "..."}}}
    url = ((result.get("data") or {}).get("video") or {}).get("url")
    if url:
        return url
    # {"video_url": "..."}
    url = result.get("video_url")
    if url:
        return url

    # Last resort: find any URL ending in .mp4 anywhere in the JSON
    def _find_mp4(obj: object) -> str | None:
        if isinstance(obj, str) and obj.startswith("https://") and ".mp4" in obj:
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                found = _find_mp4(v)
                if found:
                    return found
        if isinstance(obj, list):
            for v in obj:
                found = _find_mp4(v)
                if found:
                    return found
        return None

    return _find_mp4(result) or ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="fal.ai multi-model video generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", default="ltx-2.3", help="Model name (default: ltx-2.3)")
    parser.add_argument("--mode", default="t2v", choices=["t2v", "i2v"], help="t2v or i2v (default: t2v)")
    parser.add_argument("--prompt", required=True, help="Video description")
    parser.add_argument("--image", default="", help="Source image path or URL (i2v mode)")
    parser.add_argument("--duration", type=int, default=8, help="Duration in seconds (default: 8)")
    parser.add_argument("--resolution", default="1080p", help="720p, 1080p, 1440p, 4k (default: 1080p)")
    parser.add_argument("--aspect", default="16:9", choices=["16:9", "9:16", "1:1"], help="Aspect ratio")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second (default: 24)")
    parser.add_argument("--seed", type=int, default=None, help="Reproducibility seed")
    parser.add_argument("--output", default="", help="Custom output file path")
    parser.add_argument("--quality", default="standard", choices=["fast", "standard", "pro"], help="Quality tier")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Queue timeout in seconds")
    parser.add_argument("--negative-prompt", default="", help="What to exclude")
    parser.add_argument("--no-preview", action="store_true", help="Skip macOS QuickLook")
    parser.add_argument("--no-audio", action="store_true", help="Disable audio generation")
    parser.add_argument("--dry-run", action="store_true", help="Cost estimate only, no API call")
    parser.add_argument("--json", action="store_true", help="Output JSON only (suppress stderr logs)")

    args = parser.parse_args()

    # Model aliases for convenience
    MODEL_ALIASES = {
        "ltx": "ltx-2.3",
        "kling": "kling-v3",
        "veo": "veo-3",
        "sora": "sora-2",
    }
    model = MODEL_ALIASES.get(args.model, args.model)
    mode = args.mode
    prompt = args.prompt
    image = args.image
    duration = args.duration
    resolution = RESOLUTION_MAP.get(args.resolution, args.resolution)
    aspect = args.aspect
    fps = args.fps
    seed = args.seed
    output = args.output
    quality = args.quality
    timeout = args.timeout
    negative_prompt = args.negative_prompt
    no_preview = args.no_preview
    generate_audio = not args.no_audio
    dry_run = args.dry_run

    # Suppress stderr for --json mode
    if args.json:
        global log
        log = lambda msg: None  # noqa: E731

    # Validate
    if resolution not in ("720p", "1080p", "1440p", "4k"):
        fail(f"Invalid resolution: {resolution} (valid: 720p, 1080p, 1440p, 4k)", mode, model)
    if mode == "i2v" and not image:
        fail("i2v mode requires --image (path or URL)", mode, model)

    # Resolve endpoint
    fal_slug = resolve_slug(model, mode, quality)
    submit_url = f"{FAL_BASE}/{fal_slug}"

    # Cost estimate
    cost = estimate_cost(model, quality, resolution, duration, generate_audio)

    log("=== Pre-flight ===")
    log(f"Model: {model} | Endpoint: {fal_slug}")
    log(f"Mode: {mode} | Duration: {duration}s | Resolution: {resolution} | Aspect: {aspect} | FPS: {fps}")
    log(f"Quality: {quality} | Audio: {generate_audio}")
    log(f"Cost estimate: ${cost:.2f}")

    if dry_run:
        log("--- DRY RUN: no API call made ---")
        print(json.dumps({
            "success": True, "dry_run": True, "cost_estimate": f"${cost:.2f}",
            "mode": mode, "model": model, "fal_endpoint": fal_slug,
            "duration": duration, "resolution": resolution, "aspect_ratio": aspect,
            "fps": fps, "quality": quality, "audio": generate_audio,
        }))
        return

    validate_duration(model, duration)

    # Auth
    fal_key = resolve_fal_key()
    auth_header = f"Key {fal_key}"
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}

    # Handle image upload for i2v
    image_url = ""
    if image:
        if image.startswith("http://") or image.startswith("https://"):
            image_url = image
        else:
            if not Path(image).is_file():
                fail(f"Image file not found: {image}", mode, model)
            image_url = upload_image(image, auth_header)

    # Build payload
    payload = build_payload(
        model, mode, prompt, image_url,
        duration, resolution, aspect, fps,
        quality, generate_audio, negative_prompt, seed,
    )

    # Output file path
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(prompt)
    if output:
        output_path = Path(output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DEFAULT_OUTPUT_DIR / f"{ts}-{mode}-{slug}.mp4"
    output_path = output_path.resolve()

    log(f"Submit URL: {submit_url}")
    log(f"Payload: {json.dumps(payload)}")

    # --- Step 1: Submit to queue ---
    log("Submitting to fal.ai queue...")
    start_time = time.monotonic()

    try:
        submit_resp = requests.post(submit_url, headers=headers, json=payload, timeout=30)
    except requests.ConnectionError:
        fail("Connection refused. fal.ai may be down.", mode, model)
    except requests.Timeout:
        fail("Submit timeout. Check network connectivity.", mode, model)
    except requests.RequestException as exc:
        fail(f"Submit request failed: {exc}", mode, model)

    if not submit_resp.ok:
        detail = _extract_error(submit_resp)
        fail(f"Submit failed (HTTP {submit_resp.status_code}): {detail}", mode, model)

    submit_data = submit_resp.json()
    request_id = submit_data.get("request_id", "")
    if not request_id:
        fail(f"No request_id in submit response: {json.dumps(submit_data)}", mode, model)

    log(f"Queued: request_id={request_id}")

    # --- Step 2: Poll for completion ---
    # Use URLs from submit response (fal.ai strips endpoint variant from path)
    status_url = submit_data.get("status_url", f"{FAL_BASE}/{fal_slug}/requests/{request_id}/status")
    result_url = submit_data.get("response_url", f"{FAL_BASE}/{fal_slug}/requests/{request_id}")

    log(f"Polling for completion (timeout: {timeout}s)...")

    elapsed = 0
    while True:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        if elapsed > timeout:
            fail(f"Queue timeout after {timeout}s. Request {request_id} may still be processing on fal.ai.",
                 mode, model)

        try:
            status_resp = requests.get(status_url, headers={"Authorization": auth_header}, timeout=15)
        except requests.RequestException:
            log(f"  Poll failed (network), retrying...")
            continue

        if not status_resp.ok:
            log(f"  Poll returned HTTP {status_resp.status_code}, retrying...")
            continue

        status_data = status_resp.json()
        queue_status = status_data.get("status", "")

        if queue_status == "COMPLETED":
            log(f"  Status: COMPLETED ({elapsed}s)")
            break
        elif queue_status == "FAILED":
            err_msg = status_data.get("error", "Generation failed")
            fail(f"Generation failed: {err_msg}", mode, model)
        elif queue_status in ("IN_QUEUE", "IN_PROGRESS"):
            pos = status_data.get("queue_position")
            logs = status_data.get("logs", [])
            last_log = logs[-1].get("message", "") if logs else ""
            status_msg = f"  Status: {queue_status} ({elapsed}s)"
            if pos is not None:
                status_msg += f" pos={pos}"
            if last_log:
                status_msg += f" | {last_log}"
            log(status_msg)
        else:
            log(f"  Status: {queue_status} ({elapsed}s)")

    # --- Step 3: Fetch result ---
    log("Fetching result...")
    try:
        result_resp = requests.get(result_url, headers={"Authorization": auth_header}, timeout=30)
    except requests.RequestException as exc:
        fail(f"Failed to fetch result: {exc}", mode, model)

    if not result_resp.ok:
        detail = _extract_error(result_resp)
        fail(f"Fetch result failed (HTTP {result_resp.status_code}): {detail}", mode, model)

    result_data = result_resp.json()
    video_url = extract_video_url(result_data)
    if not video_url:
        fail(f"No video URL in result. Response: {json.dumps(result_data)[:500]}", mode, model)

    log(f"Video URL: {video_url}")

    # --- Step 4: Download video ---
    log("Downloading video...")
    try:
        dl_resp = requests.get(video_url, timeout=120, stream=True)
    except requests.RequestException as exc:
        fail(f"Video download failed: {exc}", mode, model)

    if not dl_resp.ok:
        fail(f"Video download failed (HTTP {dl_resp.status_code})", mode, model)

    with open(output_path, "wb") as f:
        for chunk in dl_resp.iter_content(chunk_size=65536):
            f.write(chunk)

    end_time = time.monotonic()
    gen_time_ms = int((end_time - start_time) * 1000)

    # Verify output
    file_size = output_path.stat().st_size
    if file_size == 0:
        output_path.unlink(missing_ok=True)
        fail("Downloaded file is empty (0 bytes)", mode, model)

    # Human-readable size
    if file_size > 1_048_576:
        size_human = f"{file_size / 1_048_576:.1f}MB"
    elif file_size > 1024:
        size_human = f"{file_size // 1024}KB"
    else:
        size_human = f"{file_size}B"

    log("=== Success ===")
    log(f"Output: {output_path}")
    log(f"Size: {size_human} ({file_size} bytes)")
    log(f"Generation time: ~{gen_time_ms // 1000}s")
    log(f"Cost: ~${cost:.2f}")

    # Preview
    if not no_preview:
        preview_script = SCRIPT_DIR / "preview.py"
        if preview_script.is_file():
            subprocess.Popen(
                [sys.executable, str(preview_script), str(output_path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

    # JSON report to stdout
    report = {
        "success": True,
        "file": str(output_path),
        "model": model,
        "mode": mode,
        "duration_sec": duration,
        "resolution": resolution,
        "cost_usd": cost,
        "seed": seed,
        "fal_request_id": request_id,
    }
    print(json.dumps(report))


if __name__ == "__main__":
    main()
