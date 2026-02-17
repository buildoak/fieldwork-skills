#!/usr/bin/env python3
"""
Image editing via OpenRouter (chat-based) or OpenAI (mask-based inpainting).

Modes:
  openrouter — Send image + edit prompt via chat completions (all models)
  openai     — Use OpenAI /v1/images/edits endpoint (mask-based inpainting)

Usage:
  python edit.py --mode openrouter --input-image photo.png --prompt "Make it sunset" --model gpt-5-image
  python edit.py --mode openai --input-image photo.png --mask mask.png --prompt "Add a cat"
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

# Import shared model registry from generate
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from generate import MODELS, resolve_model, load_image_as_base64, generate_filename, extract_images_from_response


# ── OpenRouter Chat-Based Editing ───────────────────────────────────────────


def edit_via_openrouter(args, api_key: str) -> dict:
    """Edit image using OpenRouter chat completions with image input."""

    model_cfg = resolve_model(args.model)
    model_id = model_cfg["id"]

    image_data_uri = load_image_as_base64(args.input_image)

    content = [
        {"type": "text", "text": args.prompt},
        {"type": "image_url", "image_url": {"url": image_data_uri}},
    ]

    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": content}],
    }

    if model_cfg.get("supports_text_output"):
        body["modalities"] = ["text", "image"]
    else:
        body["modalities"] = ["image"]

    # Image config
    image_config = {}
    if args.aspect_ratio and args.aspect_ratio != "1:1":
        image_config["aspect_ratio"] = args.aspect_ratio
    if args.size and args.size != "1K":
        image_config["image_size"] = args.size
    if image_config:
        body["image_config"] = image_config

    if args.seed is not None:
        body["seed"] = args.seed

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/buildoak/fieldwork-skills",
        "X-Title": "R. Jenkins Image Edit",
    }

    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers=headers, method="POST",
    )

    start_ms = time.time() * 1000

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        elapsed = int(time.time() * 1000 - start_ms)
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body[:500],
                "model": model_id, "success": False, "generation_time_ms": elapsed}
    except Exception as e:
        elapsed = int(time.time() * 1000 - start_ms)
        return {"error": str(e), "model": model_id, "success": False,
                "generation_time_ms": elapsed}

    elapsed = int(time.time() * 1000 - start_ms)

    images = extract_images_from_response(resp_data)
    if not images:
        return {"error": "No images in response", "model": model_id,
                "success": False, "generation_time_ms": elapsed}

    return {
        "success": True,
        "images_b64": images,
        "model": model_id,
        "generation_time_ms": elapsed,
        "usage": resp_data.get("usage", {}),
    }


# ── OpenAI Mask-Based Inpainting ───────────────────────────────────────────


def edit_via_openai(args, api_key: str) -> dict:
    """Edit image using OpenAI /v1/images/edits (mask-based inpainting)."""

    start_ms = time.time() * 1000

    # Build multipart form data
    boundary = f"----FormBoundary{int(time.time() * 1000)}"

    parts = []

    # Prompt
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="prompt"\r\n\r\n'
        f'{args.prompt}\r\n'
    )

    # Model
    model = args.openai_model or "gpt-image-1"
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="model"\r\n\r\n'
        f'{model}\r\n'
    )

    # Size
    if args.openai_size:
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="size"\r\n\r\n'
            f'{args.openai_size}\r\n'
        )

    # Quality
    if args.openai_quality:
        parts.append(
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="quality"\r\n\r\n'
            f'{args.openai_quality}\r\n'
        )

    # Response format — always b64_json for programmatic use
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="response_format"\r\n\r\n'
        f'b64_json\r\n'
    )

    # Image file
    img_path = Path(args.input_image)
    with open(img_path, "rb") as f:
        img_data = f.read()
    parts.append(
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{img_path.name}"\r\n'
        f'Content-Type: image/png\r\n\r\n'
    )

    # Mask file (optional)
    mask_data = None
    if args.mask:
        mask_path = Path(args.mask)
        with open(mask_path, "rb") as f:
            mask_data = f.read()

    # Assemble body
    body_parts = []
    for p in parts:
        body_parts.append(p.encode("utf-8"))
    # Append image binary
    body_parts.append(img_data)
    body_parts.append(b"\r\n")

    # Append mask if present
    if mask_data:
        mask_header = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="mask"; filename="{Path(args.mask).name}"\r\n'
            f'Content-Type: image/png\r\n\r\n'
        )
        body_parts.append(mask_header.encode("utf-8"))
        body_parts.append(mask_data)
        body_parts.append(b"\r\n")

    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(body_parts)

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
    url = f"{base_url}/v1/images/edits"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        elapsed = int(time.time() * 1000 - start_ms)
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body[:500],
                "model": model, "success": False, "generation_time_ms": elapsed}
    except Exception as e:
        elapsed = int(time.time() * 1000 - start_ms)
        return {"error": str(e), "model": model, "success": False,
                "generation_time_ms": elapsed}

    elapsed = int(time.time() * 1000 - start_ms)

    # Extract images from OpenAI response
    images = []
    for item in resp_data.get("data", []):
        b64 = item.get("b64_json", "")
        if b64:
            images.append(b64)

    if not images:
        return {"error": "No images in OpenAI response", "model": model,
                "success": False, "generation_time_ms": elapsed}

    return {
        "success": True,
        "images_b64": images,
        "model": model,
        "generation_time_ms": elapsed,
        "usage": resp_data.get("usage", {}),
    }


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Edit images via OpenRouter or OpenAI")
    parser.add_argument("--mode", required=True, choices=["openrouter", "openai"],
                        help="Editing mode: openrouter (chat-based) or openai (mask-based)")
    parser.add_argument("--input-image", required=True, help="Path to input image")
    parser.add_argument("--prompt", required=True, help="Edit instruction")
    parser.add_argument("--mask", default=None, help="Mask image path (openai mode only)")
    parser.add_argument("--model", default="gpt-5-image",
                        help="Model alias for openrouter mode (default: gpt-5-image)")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (openrouter mode)")
    parser.add_argument("--size", default="2K", help="Image size (openrouter mode)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    parser.add_argument("--output-file", default=None, help="Explicit output filename")
    parser.add_argument("--openai-model", default="gpt-image-1",
                        help="OpenAI model for mask editing (default: gpt-image-1)")
    parser.add_argument("--openai-size", default=None,
                        help="Size for OpenAI mode: 1024x1024, 1536x1024, etc.")
    parser.add_argument("--openai-quality", default=None,
                        help="Quality for OpenAI mode: low, medium, high, auto")
    args = parser.parse_args()

    # Verify input image exists
    if not Path(args.input_image).exists():
        print(json.dumps({"error": f"Input image not found: {args.input_image}", "success": False}))
        sys.exit(1)

    # Resolve output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        script_dir = Path(__file__).resolve().parent
        skill_root = script_dir.parent
        output_dir = str(skill_root / "data")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Route to appropriate mode
    if args.mode == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY_IMAGES") or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print(json.dumps({"error": "Set OPENROUTER_API_KEY_IMAGES or OPENROUTER_API_KEY", "success": False}))
            sys.exit(1)
        result = edit_via_openrouter(args, api_key)
    elif args.mode == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print(json.dumps({"error": "Set OPENAI_API_KEY for OpenAI editing mode", "success": False}))
            sys.exit(1)
        result = edit_via_openai(args, api_key)
    else:
        print(json.dumps({"error": f"Unknown mode: {args.mode}", "success": False}))
        sys.exit(1)

    if not result.get("success"):
        print(json.dumps(result))
        sys.exit(1)

    # Save images
    images_b64 = result["images_b64"]
    paths = []
    for i, img_b64 in enumerate(images_b64):
        if args.output_file and i == 0:
            output_path = args.output_file
        else:
            model_slug = args.model if args.mode == "openrouter" else args.openai_model
            base = generate_filename(output_dir, f"edit-{model_slug}")
            if i > 0:
                base = base.replace(".png", f"-{i+1}.png")
            output_path = base

        img_bytes = base64.b64decode(img_b64)
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        paths.append(output_path)

    output = {
        "success": True,
        "path": paths[0],
        "all_paths": paths,
        "model": result["model"],
        "mode": args.mode,
        "prompt": args.prompt,
        "input_image": args.input_image,
        "generation_time_ms": result["generation_time_ms"],
        "image_count": len(paths),
    }

    if args.mask:
        output["mask"] = args.mask
    if result.get("usage"):
        output["usage"] = result["usage"]

    print(json.dumps(output))


if __name__ == "__main__":
    main()
