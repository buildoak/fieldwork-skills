#!/usr/bin/env python3
"""
Vision-based image quality review.

Outputs a structured review prompt for your AI agent to evaluate via Claude vision,
OR performs direct evaluation via Anthropic API if ANTHROPIC_API_KEY is available.

Usage:
  python review.py --image /path/to/image.png --original-prompt "A red fox in snow"
  python review.py --image /path/to/image.png --original-prompt "prompt" --auto
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


REVIEW_SYSTEM_PROMPT = """You are an expert image quality reviewer. Evaluate the generated image against the original prompt.

Score each dimension from 1-10:

1. **prompt_adherence** — Does the image match what was requested? Are all described elements present?
2. **technical_quality** — Resolution, artifacts, noise, sharpness, color accuracy
3. **composition** — Layout, balance, focal point, use of space
4. **overall** — Holistic quality combining all factors

Then provide:
- **verdict**: "accept" (overall >= 7), "refine" (4-6), "reject" (< 4)
- **critique**: 1-2 sentences on what works and what doesn't
- **suggested_refinement**: If verdict is "refine", a specific prompt modification to improve the result. If "accept", leave empty.

Respond with ONLY valid JSON in this exact format:
{
  "score": <overall 1-10>,
  "prompt_adherence": <1-10>,
  "technical_quality": <1-10>,
  "composition": <1-10>,
  "verdict": "accept|refine|reject",
  "critique": "...",
  "suggested_refinement": "..."
}"""


def load_image_b64(path: str) -> tuple[str, str]:
    """Load image as base64 and determine MIME type."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    suffix = p.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp", ".gif": "image/gif"}
    mime = mime_map.get(suffix, "image/png")

    with open(p, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return encoded, mime


def review_via_anthropic(image_path: str, original_prompt: str, api_key: str) -> dict:
    """Direct review via Anthropic Claude vision API."""

    img_b64, mime = load_image_b64(image_path)

    body = {
        "model": "claude-sonnet-4-5-20250514",
        "max_tokens": 1024,
        "system": REVIEW_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": img_b64,
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Original prompt: \"{original_prompt}\"\n\nReview this generated image."
                    }
                ]
            }
        ]
    }

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers=headers, method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body[:300]}
    except Exception as e:
        return {"error": str(e)}

    # Extract text response
    text = ""
    for block in resp_data.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "")

    # Parse JSON from response
    text = text.strip()
    # Handle potential markdown code block wrapping
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        review = json.loads(text)
        return review
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse review JSON",
            "raw_response": text[:500],
        }


def generate_review_prompt(image_path: str, original_prompt: str) -> dict:
    """Generate a structured review prompt for your AI agent to evaluate."""

    img_b64, mime = load_image_b64(image_path)
    data_uri = f"data:{mime};base64,{img_b64}"

    return {
        "mode": "prompt",
        "system_prompt": REVIEW_SYSTEM_PROMPT,
        "user_message": f'Original prompt: "{original_prompt}"\n\nReview this generated image.',
        "image_data_uri": data_uri,
        "image_path": image_path,
        "instructions": "Feed this system prompt, user message, and image to Claude vision. Parse the JSON response.",
    }


def main():
    parser = argparse.ArgumentParser(description="Review generated image quality")
    parser.add_argument("--image", required=True, help="Path to generated image")
    parser.add_argument("--original-prompt", required=True, help="The prompt used for generation")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-review via Anthropic API (requires ANTHROPIC_API_KEY)")
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(json.dumps({"error": f"Image not found: {args.image}", "success": False}))
        sys.exit(1)

    if args.auto:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print(json.dumps({
                "error": "ANTHROPIC_API_KEY not set. Run without --auto for prompt-only mode.",
                "success": False,
            }))
            sys.exit(1)

        review = review_via_anthropic(args.image, args.original_prompt, api_key)

        if "error" in review:
            print(json.dumps({"success": False, **review}))
            sys.exit(1)

        print(json.dumps({
            "success": True,
            "mode": "auto",
            "image": args.image,
            "original_prompt": args.original_prompt,
            **review,
        }))
    else:
        # Output prompt for your AI agent to evaluate
        prompt_data = generate_review_prompt(args.image, args.original_prompt)
        print(json.dumps({
            "success": True,
            **prompt_data,
        }))


if __name__ == "__main__":
    main()
