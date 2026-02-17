#!/usr/bin/env python3
"""
Image generation via OpenRouter API.

Supports:
- Text-to-image (Flux 2 Pro/Klein, GPT-5 Image, NanoBanana Pro)
- Image editing via chat-based input (send image + edit prompt)

Usage:
  python generate.py --prompt "A red fox in a snowy forest" --model flux.2-pro
  python generate.py --prompt "Make it sunset" --input-image /path/to/image.png --model gpt-5-image
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Model Registry ──────────────────────────────────────────────────────────

MODELS = {
    "flux.2-pro": {
        "id": "black-forest-labs/flux.2-pro",
        "modalities": ["image"],
        "supports_image_input": True,
        "supports_text_output": False,
        "cost_per_mp": 0.03,  # first MP
    },
    "flux.2-klein": {
        "id": "black-forest-labs/flux.2-klein-4b",
        "modalities": ["image"],
        "supports_image_input": False,
        "supports_text_output": False,
        "cost_per_mp": 0.014,
    },
    "gpt-5-image": {
        "id": "openai/gpt-5-image",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "cost_per_1m_input": 10.0,
        "cost_per_1m_output": 40.0,
    },
    "nanobanana-pro": {
        "id": "google/gemini-3-pro-image-preview",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "cost_per_1m_input": 2.0,
        "cost_per_1m_output": 12.0,
    },
    "nanobanana": {
        "id": "google/gemini-2.5-flash-image",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "cost_per_1m_input": 0.1,
        "cost_per_1m_output": 0.4,
    },
}

ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]
IMAGE_SIZES = ["1K", "2K", "4K"]

# ── Helpers ─────────────────────────────────────────────────────────────────


def resolve_model(alias: str) -> dict:
    """Resolve model alias to full config."""
    if alias in MODELS:
        return MODELS[alias]
    # Try matching by full ID
    for cfg in MODELS.values():
        if cfg["id"] == alias:
            return cfg
    # Fallback: treat as raw OpenRouter model ID
    return {
        "id": alias,
        "modalities": ["image", "text"],
        "supports_image_input": True,
        "supports_text_output": True,
    }


def load_image_as_base64(path: str) -> str:
    """Read an image file and return base64-encoded data URI."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    suffix = p.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp", ".gif": "image/gif"}
    mime = mime_map.get(suffix, "image/png")

    with open(p, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def generate_filename(output_dir: str, model_alias: str) -> str:
    """Generate a timestamped filename for the output image."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = model_alias.replace(".", "-").replace("/", "-")
    return str(Path(output_dir) / f"{ts}-{slug}.png")


def estimate_cost(model_cfg: dict, aspect_ratio: str, size: str) -> str:
    """Rough cost estimate based on model and output resolution."""
    # Megapixel estimates by size
    mp_map = {"1K": 1.0, "2K": 4.0, "4K": 8.3}
    mp = mp_map.get(size, 1.0)

    if "cost_per_mp" in model_cfg:
        cost = model_cfg["cost_per_mp"] * mp
        return f"~${cost:.3f}"
    elif "cost_per_1m_output" in model_cfg:
        # Token-based models: rough estimate ~1K output tokens for image
        cost = model_cfg["cost_per_1m_output"] * 0.001  # 1K tokens
        return f"~${cost:.4f}"
    return "unknown"


def extract_images_from_response(data: dict) -> list[str]:
    """Extract base64 image data from OpenRouter response.

    Returns list of base64-encoded PNG strings (without data URI prefix).
    """
    images = []

    for choice in data.get("choices", []):
        msg = choice.get("message", {})

        # Primary path: images array in message
        for img in msg.get("images", []):
            url = ""
            if isinstance(img, dict):
                url = img.get("image_url", {}).get("url", "")
                if not url:
                    url = img.get("url", "")
            if url and "base64," in url:
                images.append(url.split("base64,", 1)[1])

        # Fallback: check content array for image parts
        content = msg.get("content", "")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "image_url":
                    url = part.get("image_url", {}).get("url", "")
                    if url and "base64," in url:
                        images.append(url.split("base64,", 1)[1])

    return images


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Generate images via OpenRouter")
    parser.add_argument("--prompt", required=True, help="Text prompt for generation")
    parser.add_argument("--model", default="flux.2-pro",
                        help="Model alias or full ID (default: flux.2-pro)")
    parser.add_argument("--aspect-ratio", default="1:1",
                        help=f"Aspect ratio: {', '.join(ASPECT_RATIOS)}")
    parser.add_argument("--size", default="2K",
                        help=f"Image size: {', '.join(IMAGE_SIZES)}")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: data/ in skill directory)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--input-image", default=None,
                        help="Path to input image for editing")
    parser.add_argument("--output-file", default=None,
                        help="Explicit output filename (overrides auto-naming)")
    args = parser.parse_args()

    # Resolve output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Default: skill_root/data
        script_dir = Path(__file__).resolve().parent
        skill_root = script_dir.parent
        output_dir = str(skill_root / "data")

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load API key
    api_key = os.environ.get("OPENROUTER_API_KEY_IMAGES") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "No API key found. Set OPENROUTER_API_KEY_IMAGES or OPENROUTER_API_KEY",
            "success": False,
        }))
        sys.exit(1)

    # Resolve model
    model_cfg = resolve_model(args.model)
    model_id = model_cfg["id"]

    # Build message content
    if args.input_image:
        # Image editing: multipart content with image + text
        image_data_uri = load_image_as_base64(args.input_image)
        content = [
            {"type": "text", "text": args.prompt},
            {"type": "image_url", "image_url": {"url": image_data_uri}},
        ]
    else:
        # Text-to-image: simple string content
        content = args.prompt

    # Build request body
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": content}],
    }

    # Set modalities based on model type
    if model_cfg.get("supports_text_output"):
        body["modalities"] = ["text", "image"]
    else:
        body["modalities"] = ["image"]

    # Image config
    image_config = {}
    if args.aspect_ratio != "1:1":
        image_config["aspect_ratio"] = args.aspect_ratio
    if args.size != "1K":
        image_config["image_size"] = args.size
    if image_config:
        body["image_config"] = image_config

    # Seed
    if args.seed is not None:
        body["seed"] = args.seed

    # Make request
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/buildoak/fieldwork-skills",
        "X-Title": "R. Jenkins Image Gen",
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    start_ms = time.time() * 1000

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        elapsed = int(time.time() * 1000 - start_ms)
        print(json.dumps({
            "error": f"HTTP {e.code}: {e.reason}",
            "details": error_body[:500],
            "model": model_id,
            "success": False,
            "generation_time_ms": elapsed,
        }))
        sys.exit(1)
    except urllib.error.URLError as e:
        elapsed = int(time.time() * 1000 - start_ms)
        print(json.dumps({
            "error": f"Network error: {str(e.reason)}",
            "model": model_id,
            "success": False,
            "generation_time_ms": elapsed,
        }))
        sys.exit(1)
    except Exception as e:
        elapsed = int(time.time() * 1000 - start_ms)
        print(json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "model": model_id,
            "success": False,
            "generation_time_ms": elapsed,
        }))
        sys.exit(1)

    elapsed = int(time.time() * 1000 - start_ms)

    # Extract images
    images = extract_images_from_response(resp_data)

    if not images:
        # Dump response for debugging
        print(json.dumps({
            "error": "No images found in response",
            "model": model_id,
            "success": False,
            "generation_time_ms": elapsed,
            "raw_response_keys": list(resp_data.keys()),
            "choices_count": len(resp_data.get("choices", [])),
            "first_choice_message_keys": list(resp_data.get("choices", [{}])[0].get("message", {}).keys()) if resp_data.get("choices") else [],
        }))
        sys.exit(1)

    # Save image(s)
    results = []
    for i, img_b64 in enumerate(images):
        if args.output_file and i == 0:
            output_path = args.output_file
        else:
            base = generate_filename(output_dir, args.model)
            if i > 0:
                base = base.replace(".png", f"-{i+1}.png")
            output_path = base

        img_bytes = base64.b64decode(img_b64)
        with open(output_path, "wb") as f:
            f.write(img_bytes)

        results.append(output_path)

    # Extract text response if present
    text_response = None
    if model_cfg.get("supports_text_output"):
        for choice in resp_data.get("choices", []):
            msg = choice.get("message", {})
            c = msg.get("content", "")
            if isinstance(c, str) and c.strip():
                text_response = c.strip()
                break
            elif isinstance(c, list):
                for part in c:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_response = part.get("text", "").strip()
                        break

    # Usage stats
    usage = resp_data.get("usage", {})

    output = {
        "success": True,
        "path": results[0],
        "all_paths": results,
        "model": model_id,
        "prompt": args.prompt,
        "aspect_ratio": args.aspect_ratio,
        "size": args.size,
        "cost_estimate": estimate_cost(model_cfg, args.aspect_ratio, args.size),
        "generation_time_ms": elapsed,
        "image_count": len(results),
    }

    if args.seed is not None:
        output["seed"] = args.seed
    if text_response:
        output["text_response"] = text_response
    if usage:
        output["usage"] = usage
    if args.input_image:
        output["input_image"] = args.input_image

    print(json.dumps(output))


if __name__ == "__main__":
    main()
