#!/usr/bin/env python3
"""Generates multi-view character sheets using the existing image-gen script."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str) -> None:
    eprint(f"ERROR: {msg}")
    sys.exit(1)


def load_character(value: str) -> dict[str, Any]:
    path = Path(value)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def pick_first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data[key] not in (None, "", []):
            return data[key]
    return None


def build_character_prompt(character: dict[str, Any]) -> str:
    appearance = character.get("appearance", {}) if isinstance(character.get("appearance"), dict) else {}
    wardrobe = character.get("wardrobe", {}) if isinstance(character.get("wardrobe"), dict) else {}

    age = pick_first(character, "age") or "adult"
    ethnicity = pick_first(character, "ethnicity") or ""
    gender = pick_first(character, "gender") or "person"

    skin_tone = pick_first(appearance, "skin_tone") or "natural"
    face_shape = pick_first(appearance, "face_shape") or "balanced"
    eye_color = pick_first(appearance, "eye_color") or "brown"
    hair_length = pick_first(appearance, "hair_length") or "medium-length"
    hair_color = pick_first(appearance, "hair_color") or "dark"
    hair_style = pick_first(appearance, "hair_style") or "neat"
    build = pick_first(appearance, "build") or "average"

    top = pick_first(wardrobe, "top") or "a fitted top"
    bottom = pick_first(wardrobe, "bottom") or "tailored pants"
    shoes = pick_first(wardrobe, "shoes") or "casual shoes"

    primary = (
        f"{age} year old {ethnicity} {gender} with {skin_tone} skin, {face_shape} face, "
        f"{eye_color} eyes, {hair_length} {hair_color} {hair_style} hair, {build} build, "
        f"wearing {top}, {bottom}, {shoes}"
    )

    features = appearance.get("distinguishing_features")
    if isinstance(features, list) and features:
        primary += ", distinguishing features: " + ", ".join(str(x) for x in features)

    accessories = appearance.get("accessories")
    if isinstance(accessories, list) and accessories:
        primary += ", accessories: " + ", ".join(str(x) for x in accessories)

    desc = pick_first(character, "description", "consistency_notes")
    if desc:
        primary += f". Character notes: {desc}"

    return primary


def normalize_views(views_raw: str, tier: str) -> list[str]:
    requested = [v.strip() for v in views_raw.split(",") if v.strip()]
    canonical = [
        "front",
        "profile_left",
        "profile_right",
        "three_quarter_left",
        "three_quarter_right",
        "full_body_front",
    ]

    merged: list[str] = []
    for item in requested + canonical:
        if item not in merged:
            merged.append(item)

    target = 2 if tier == "budget" else 6
    return merged[:target]


def view_suffix(view: str) -> str:
    mapping = {
        "front": "front-facing portrait",
        "profile": "profile view facing left",
        "profile_left": "profile view facing left",
        "profile_right": "profile view facing right",
        "three_quarter": "3/4 view",
        "three_quarter_left": "3/4 view facing left",
        "three_quarter_right": "3/4 view facing right",
        "full_body_front": "full body front-facing portrait",
    }
    return mapping.get(view, f"{view.replace('_', ' ')} view")


def safe_view_token(view: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in view).strip("_") or "view"


def parse_json_stdout(raw: str, source: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        raise ValueError(f"{source} returned empty stdout")

    lines = [line for line in text.splitlines() if line.strip()]
    for candidate in reversed(lines):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"{source} did not return valid JSON. stdout={text[:500]}")


def parse_cost_value(payload: dict[str, Any]) -> float:
    for key in ("cost_usd", "cost", "cost_estimate"):
        raw = payload.get(key)
        if raw is None:
            continue
        if isinstance(raw, (int, float)):
            return round(float(raw), 4)
        text = str(raw).strip().replace("~", "").replace("$", "")
        try:
            return round(float(text), 4)
        except ValueError:
            continue
    return 0.0


def resolve_image_gen() -> str:
    """Resolve path to image-gen generate.py script.

    Resolution order:
    1. IMAGE_GEN_SCRIPT environment variable
    2. Peer skill auto-discovery (../image-gen/scripts/generate.py relative to skill root)
    3. Actionable error message
    """
    env_path = os.environ.get("IMAGE_GEN_SCRIPT")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return str(path)
        fail(f"IMAGE_GEN_SCRIPT points to non-existent path: {env_path}")

    skill_root = Path(__file__).resolve().parent.parent
    peer = skill_root.parent / "image-gen" / "scripts" / "generate.py"
    if peer.exists():
        return str(peer)

    fail(
        "Image generation requires the image-gen skill.\n"
        "Install it as a peer under skills/ or set IMAGE_GEN_SCRIPT=/path/to/generate.py"
    )
    raise RuntimeError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate character sheet images via image-gen.")
    parser.add_argument("--character-json", required=True, help="Path to character JSON file OR inline JSON string.")
    parser.add_argument("--character-id", required=True, help="Character ID used in output filenames.")
    parser.add_argument("--output-dir", required=True, help="Directory where character images are saved.")
    parser.add_argument(
        "--views",
        default="front,profile,three_quarter",
        help="Comma-separated requested views (default: front,profile,three_quarter).",
    )
    parser.add_argument(
        "--tier",
        default="standard",
        choices=["budget", "standard", "premium", "ultra"],
        help="Tier controls number of rendered views (budget=2, standard+=6).",
    )
    args = parser.parse_args()

    image_gen = Path(resolve_image_gen())

    try:
        character = load_character(args.character_json)
    except Exception as exc:
        eprint(f"ERROR: Failed to parse --character-json: {exc}")
        sys.exit(1)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    views = normalize_views(args.views, args.tier)
    base_prompt = build_character_prompt(character)

    image_model = "flux.2-klein" if args.tier == "budget" else "flux.2-pro"
    image_size = "1K" if args.tier == "budget" else "2K"

    results: list[dict[str, Any]] = []
    total_cost = 0.0

    for view in views:
        suffix = view_suffix(view)
        view_token = safe_view_token(view)
        output_file = out_dir / f"{args.character_id}_{view_token}.png"

        prompt = (
            f"{base_prompt}. {suffix}. "
            "Character sheet concept art, neutral studio lighting, clean backdrop, highly consistent identity across views, "
            "photoreal texture, no text, no watermark."
        )

        cmd = [
            sys.executable,
            str(image_gen),
            "--prompt",
            prompt,
            "--model",
            image_model,
            "--aspect-ratio",
            "1:1",
            "--size",
            image_size,
            "--output-file",
            str(output_file),
        ]

        eprint(f"Generating {args.character_id} view={view} -> {output_file}")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            eprint(f"ERROR: image-gen failed for view={view}")
            if proc.stderr.strip():
                eprint(proc.stderr.strip())
            if proc.stdout.strip():
                eprint(proc.stdout.strip())
            sys.exit(1)

        try:
            payload = parse_json_stdout(proc.stdout, "image-gen")
        except Exception as exc:
            eprint(f"ERROR: Failed to parse image-gen JSON for view={view}: {exc}")
            sys.exit(1)

        if not payload.get("success"):
            eprint(f"ERROR: image-gen returned success=false for view={view}: {payload}")
            sys.exit(1)

        view_cost = parse_cost_value(payload)
        total_cost += view_cost

        results.append(
            {
                "view": view,
                "path": str(Path(payload.get("path", str(output_file))).expanduser().resolve()),
                "model": payload.get("model", image_model),
                "cost_estimate": view_cost,
            }
        )

    output = {
        "success": True,
        "character_id": args.character_id,
        "tier": args.tier,
        "views_requested": views,
        "images": results,
        "total_cost_estimate": round(total_cost, 4),
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
