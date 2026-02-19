#!/usr/bin/env python3
"""
Image generation via OpenRouter API.

Supports:
- Text-to-image (Flux 2 Pro/Klein, GPT-5 Image, NanoBanana Pro)
- Image editing via chat-based input (send image + edit prompt)
- Style presets (--preset) for consistent series generation
- Style reference images (--style-ref) for visual anchoring
- Prompt upsampling (--prompt-upsampling) for Flux models
- System messages for text+image models via presets

Usage:
  python generate.py --prompt "A red fox in a snowy forest" --model flux.2-pro
  python generate.py --prompt "Make it sunset" --input-image /path/to/image.png --model gpt-5-image
  python generate.py --prompt "Scene description" --preset my-preset --model flux.2-pro
  python generate.py --prompt "Scene" --style-ref /path/to/golden.png --model flux.2-pro
"""

import argparse
import base64
import binascii
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
        "supports_system_message": False,
        "supports_prompt_upsampling": True,
        "prompt_format": "flux",
        "cost_per_mp": 0.03,  # first MP
    },
    "flux.2-klein": {
        "id": "black-forest-labs/flux.2-klein-4b",
        "modalities": ["image"],
        "supports_image_input": False,
        "supports_text_output": False,
        "supports_system_message": False,
        "supports_prompt_upsampling": True,
        "prompt_format": "flux",
        "cost_per_mp": 0.014,
    },
    "gpt-5-image": {
        "id": "openai/gpt-5-image",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "supports_system_message": True,
        "supports_prompt_upsampling": False,
        "prompt_format": "natural",
        "cost_per_1m_input": 10.0,
        "cost_per_1m_output": 40.0,
    },
    "nanobanana-pro": {
        "id": "google/gemini-3-pro-image-preview",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "supports_system_message": True,
        "supports_prompt_upsampling": False,
        "prompt_format": "structured",
        "cost_per_1m_input": 2.0,
        "cost_per_1m_output": 12.0,
    },
    "nanobanana": {
        "id": "google/gemini-2.5-flash-image",
        "modalities": ["text", "image"],
        "supports_image_input": True,
        "supports_text_output": True,
        "supports_system_message": True,
        "supports_prompt_upsampling": False,
        "prompt_format": "structured",
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
        "supports_system_message": True,
        "supports_prompt_upsampling": False,
        "prompt_format": "natural",
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


# ── Preset System ──────────────────────────────────────────────────────────


def resolve_preset_path(preset_name: str) -> Path:
    """Resolve a preset name to its JSON file path.

    Search order:
    1. Absolute path (if preset_name is a file path)
    2. skill_dir/presets/{name}.json
    """
    # If it's already a path to a file
    p = Path(preset_name)
    if p.is_file():
        return p

    # Look in skill_dir/presets/
    skill_dir = Path(__file__).resolve().parent.parent
    preset_file = skill_dir / "presets" / f"{preset_name}.json"
    if preset_file.is_file():
        return preset_file

    # Try with .json extension already included
    preset_file = skill_dir / "presets" / preset_name
    if preset_file.is_file():
        return preset_file

    return None


def load_preset(preset_name: str) -> dict:
    """Load a preset JSON file and return its contents."""
    path = resolve_preset_path(preset_name)
    if path is None:
        print(json.dumps({
            "error": f"Preset not found: '{preset_name}'. Check presets/ directory.",
            "success": False,
        }), file=sys.stderr)
        return {}

    with open(path, "r") as f:
        preset = json.load(f)

    return preset


def apply_preset_to_prompt(prompt: str, preset: dict, model_cfg: dict) -> str:
    """Enhance a prompt with preset style information.

    For Flux models: builds JSON structured prompt when preset provides style data.
    For text+image models: prepends style block as natural language.
    """
    if not preset:
        return prompt

    prompt_format = model_cfg.get("prompt_format", "natural")
    style = preset.get("style", {})

    if not style:
        return prompt

    if prompt_format == "flux":
        return _build_flux_prompt(prompt, style, preset)
    else:
        return _build_natural_prompt(prompt, style, preset)


def _build_flux_prompt(prompt: str, style: dict, preset: dict) -> str:
    """Build a JSON structured prompt for Flux models.

    Flux natively interprets JSON in the prompt text. Structured prompts
    prevent concept bleeding between style and content elements.
    """
    structured = {}

    # Scene from user prompt
    structured["scene"] = prompt

    # Style from preset
    if style.get("description"):
        structured["style"] = style["description"]

    # Color palette with HEX values
    if style.get("color_palette"):
        structured["color_palette"] = style["color_palette"]

    # Mood
    if style.get("mood"):
        structured["mood"] = style["mood"]

    # Lighting
    if style.get("lighting"):
        structured["lighting"] = style["lighting"]

    # Composition
    if style.get("composition"):
        structured["composition"] = style["composition"]

    # Camera defaults from preset
    if style.get("camera"):
        structured["camera"] = style["camera"]

    # Anti-patterns as rendering constraints
    if style.get("rendering"):
        structured["rendering"] = style["rendering"]

    return json.dumps(structured, indent=None)


def _build_natural_prompt(prompt: str, style: dict, preset: dict) -> str:
    """Build a natural language prompt with style block prepended.

    Used for GPT-5 Image and NanoBanana models.
    """
    style_parts = []

    if style.get("description"):
        style_parts.append(f"Style: {style['description']}")

    if style.get("color_palette"):
        hex_list = ", ".join(style["color_palette"])
        style_parts.append(f"Color palette: {hex_list}")

    if style.get("mood"):
        style_parts.append(f"Mood: {style['mood']}")

    if style.get("lighting"):
        style_parts.append(f"Lighting: {style['lighting']}")

    if style.get("composition"):
        style_parts.append(f"Composition: {style['composition']}")

    if style.get("rendering"):
        style_parts.append(f"Rendering: {style['rendering']}")

    if style.get("anti_patterns"):
        anti = ", ".join(style["anti_patterns"])
        style_parts.append(f"Avoid: {anti}")

    if style_parts:
        style_block = "\n".join(style_parts)
        return f"{style_block}\n\nScene: {prompt}"

    return prompt


def get_system_message(preset: dict, model_cfg: dict) -> str:
    """Extract system message from preset if model supports it."""
    if not model_cfg.get("supports_system_message"):
        return None

    # Explicit system message in preset
    if preset.get("system_message"):
        return preset["system_message"]

    return None


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Generate images via OpenRouter")
    parser.add_argument("--prompt", required=True, help="Text prompt for generation")
    parser.add_argument("--model", default=None,
                        help="Model alias or full ID (default: flux.2-pro, overridden by preset)")
    parser.add_argument("--aspect-ratio", default=None,
                        help=f"Aspect ratio: {', '.join(ASPECT_RATIOS)}")
    parser.add_argument("--size", default=None,
                        help=f"Image size: {', '.join(IMAGE_SIZES)}")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: data/ in skill directory)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--input-image", default=None,
                        help="Path to input image for editing")
    parser.add_argument("--output-file", default=None,
                        help="Explicit output filename (overrides auto-naming)")
    # Preset and style flags
    parser.add_argument("--preset", default=None,
                        help="Style preset name or path to JSON preset file")
    parser.add_argument("--style-ref", default=None, action="append",
                        help="Path to style reference image (repeatable, up to 8)")
    parser.add_argument("--prompt-upsampling", default=None, action="store_true",
                        help="Enable Flux prompt_upsampling (auto-enhances prompts)")
    parser.add_argument("--no-prompt-upsampling", dest="prompt_upsampling", action="store_false",
                        help="Disable prompt_upsampling")
    parser.add_argument("--system-prompt", default=None,
                        help="Explicit system message (overrides preset system_message)")
    args = parser.parse_args()

    # ── Load preset ────────────────────────────────────────────────────────
    preset = {}
    if args.preset:
        preset = load_preset(args.preset)
        if not preset:
            # load_preset already printed error
            sys.exit(1)

    # ── Resolve defaults (CLI > preset > hardcoded) ────────────────────────
    model_alias = args.model or preset.get("defaults", {}).get("model") or "flux.2-pro"
    aspect_ratio = args.aspect_ratio or preset.get("defaults", {}).get("aspect_ratio") or "1:1"
    size = args.size or preset.get("defaults", {}).get("size") or "2K"

    # ── Validate resolved values ───────────────────────────────────────────
    if aspect_ratio not in ASPECT_RATIOS:
        print(json.dumps({
            "error": f"Invalid --aspect-ratio '{aspect_ratio}'. Choose one of: {', '.join(ASPECT_RATIOS)}",
            "success": False,
        }))
        sys.exit(1)
    if size not in IMAGE_SIZES:
        print(json.dumps({
            "error": f"Invalid --size '{size}'. Choose one of: {', '.join(IMAGE_SIZES)}",
            "success": False,
        }))
        sys.exit(1)

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
    model_cfg = resolve_model(model_alias)
    model_id = model_cfg["id"]
    if args.input_image and not model_cfg.get("supports_image_input", False):
        print(json.dumps({
            "error": f"Model '{model_alias}' does not support --input-image editing",
            "success": False,
        }))
        sys.exit(1)

    # ── Apply preset to prompt ─────────────────────────────────────────────
    enhanced_prompt = apply_preset_to_prompt(args.prompt, preset, model_cfg)

    # ── Build message content ──────────────────────────────────────────────
    content_parts = []

    # Style reference images (separate from --input-image editing)
    style_refs = args.style_ref or []
    if preset.get("style", {}).get("reference_images"):
        # Add preset reference images that exist
        for ref_path in preset["style"]["reference_images"]:
            if Path(ref_path).is_file() and ref_path not in style_refs:
                style_refs.append(ref_path)

    if args.input_image:
        # Image editing mode: input image + prompt
        image_data_uri = load_image_as_base64(args.input_image)
        content_parts.append({"type": "text", "text": enhanced_prompt})
        content_parts.append({"type": "image_url", "image_url": {"url": image_data_uri}})
        # Add style refs alongside edit input
        for ref_path in style_refs:
            ref_uri = load_image_as_base64(ref_path)
            content_parts.append({"type": "image_url", "image_url": {"url": ref_uri}})
        content = content_parts
    elif style_refs:
        # Style reference mode: refs + prompt
        style_instruction = "Generate a new image in the exact visual style of the provided reference image(s). "
        content_parts.append({"type": "text", "text": style_instruction + enhanced_prompt})
        for ref_path in style_refs:
            ref_uri = load_image_as_base64(ref_path)
            content_parts.append({"type": "image_url", "image_url": {"url": ref_uri}})
        content = content_parts
    else:
        # Text-to-image: simple string content
        content = enhanced_prompt

    # ── Build request body ─────────────────────────────────────────────────
    messages = []

    # System message (CLI flag > preset > none)
    system_msg = args.system_prompt or get_system_message(preset, model_cfg)
    if system_msg and model_cfg.get("supports_system_message"):
        messages.append({"role": "system", "content": system_msg})

    messages.append({"role": "user", "content": content})

    body = {
        "model": model_id,
        "messages": messages,
    }

    # Set modalities based on model type
    if model_cfg.get("supports_text_output"):
        body["modalities"] = ["text", "image"]
    else:
        body["modalities"] = ["image"]

    # Image config
    image_config = {}
    if aspect_ratio != "1:1":
        image_config["aspect_ratio"] = aspect_ratio
    if size != "1K":
        image_config["image_size"] = size
    if image_config:
        body["image_config"] = image_config

    # Prompt upsampling (Flux only)
    # Default: on for Flux models unless explicitly disabled
    if model_cfg.get("supports_prompt_upsampling"):
        if args.prompt_upsampling is None:
            # Default on for Flux
            body["prompt_upsampling"] = True
        else:
            body["prompt_upsampling"] = args.prompt_upsampling

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
            base = generate_filename(output_dir, model_alias)
            if i > 0:
                base = base.replace(".png", f"-{i+1}.png")
            output_path = base

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img_bytes = base64.b64decode(img_b64)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
        except (binascii.Error, OSError) as exc:
            print(json.dumps({
                "error": f"Failed to save generated image: {exc}",
                "success": False,
                "model": model_id,
                "generation_time_ms": elapsed,
            }))
            sys.exit(1)

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
        "enhanced_prompt": enhanced_prompt if enhanced_prompt != args.prompt else None,
        "aspect_ratio": aspect_ratio,
        "size": size,
        "cost_estimate": estimate_cost(model_cfg, aspect_ratio, size),
        "generation_time_ms": elapsed,
        "image_count": len(results),
    }

    # Strip None values
    output = {k: v for k, v in output.items() if v is not None}

    if args.preset:
        output["preset"] = args.preset
    if args.seed is not None:
        output["seed"] = args.seed
    if text_response:
        output["text_response"] = text_response
    if usage:
        output["usage"] = usage
    if args.input_image:
        output["input_image"] = args.input_image
    if style_refs:
        output["style_refs"] = style_refs
    if system_msg:
        output["system_message_used"] = True

    print(json.dumps(output))


if __name__ == "__main__":
    main()
