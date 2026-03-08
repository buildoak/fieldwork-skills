#!/usr/bin/env python3
"""Generate a scene keyframe image for story-gen projects."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ANTI_PAINTING_SUFFIX = (
    "Photographic quality, realistic textures, cinematic lighting. "
    "Not a painting, not an illustration, not digital art."
)


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def fail(message: str) -> None:
    eprint(f"ERROR: {message}")
    sys.exit(1)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at {path}: {exc}") from exc


def parse_last_json_line(stdout_text: str, source: str) -> dict[str, Any]:
    lines = [line.strip() for line in (stdout_text or "").splitlines() if line.strip()]
    for line in reversed(lines):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError(f"{source} did not emit a JSON object on stdout")


def find_scene_key(state: dict[str, Any], project_dir: Path, scene_number: int) -> str:
    scene_prefix = f"{scene_number:02d}-"
    scenes_obj = state.get("scenes")

    if isinstance(scenes_obj, dict):
        for key in scenes_obj:
            if isinstance(key, str) and key.startswith(scene_prefix):
                return key

        for key, value in scenes_obj.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            num = value.get("number")
            if num is None:
                num = value.get("scene")
            if num is None:
                num = value.get("index")
            if isinstance(num, int) and num == scene_number:
                return key

    if isinstance(scenes_obj, list):
        for item in scenes_obj:
            if not isinstance(item, dict):
                continue
            num = item.get("number")
            if num is None:
                num = item.get("scene")
            if num is None:
                num = item.get("index")
            if isinstance(num, int) and num == scene_number:
                key = item.get("key") or item.get("scene_key") or item.get("id")
                if isinstance(key, str) and key.strip():
                    return key.strip()

    scenes_dir = project_dir / "scenes"
    if scenes_dir.is_dir():
        candidates = sorted(
            p.name for p in scenes_dir.iterdir() if p.is_dir() and p.name.startswith(scene_prefix)
        )
        if candidates:
            return candidates[0]

    raise ValueError(f"Could not resolve scene key for scene {scene_number}")


def extract_section(markdown_text: str, heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)",
    )
    match = pattern.search(markdown_text)
    if not match:
        raise ValueError(f"Section '## {heading}' not found")
    value = match.group(1).strip()
    if not value:
        raise ValueError(f"Section '## {heading}' is empty")
    return value


def resolve_style_keywords(project_dir: Path, state: dict[str, Any], override: str | None) -> str:
    if override and override.strip():
        return override.strip()

    manifest_path = project_dir / "manifest.md"
    if manifest_path.is_file():
        text = manifest_path.read_text(encoding="utf-8")
        try:
            section = extract_section(text, "Style Keywords")
            return " ".join(section.split())
        except ValueError:
            pass

    project = state.get("project") if isinstance(state.get("project"), dict) else {}
    style = project.get("style")
    if isinstance(style, str) and style.strip():
        return style.strip()

    return ""


def needs_anti_painting(style_intent: str) -> bool:
    text = style_intent.lower()
    return "cinematic" in text or "photorealistic" in text


def archive_existing_keyframe(keyframe_path: Path) -> None:
    if not keyframe_path.exists():
        return

    idx = 1
    while True:
        draft_path = keyframe_path.with_name(f"keyframe-draft-{idx}.png")
        if not draft_path.exists():
            keyframe_path.rename(draft_path)
            eprint(f"Archived existing keyframe -> {draft_path}")
            return
        idx += 1


def parse_cost_usd(payload: dict[str, Any]) -> float:
    for key in ("cost_usd", "cost", "cost_estimate"):
        if key not in payload:
            continue
        raw = payload.get(key)
        if raw is None:
            continue
        if isinstance(raw, (int, float)):
            return round(float(raw), 4)
        text = str(raw).strip().replace("$", "").replace("~", "")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reference keyframe image for a story-gen scene.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--project", required=True, help="Path to project directory.")
    parser.add_argument("--scene", required=True, type=int, help="Scene number (int).")
    parser.add_argument(
        "--style-keywords",
        default=None,
        help="Explicit style keywords (comma-separated string). Overrides manifest style.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override image model. Default is auto-selected from tier.",
    )
    parser.add_argument(
        "--no-state-update",
        action="store_true",
        help="Skip state update call (useful for testing).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    project_dir = Path(args.project).expanduser().resolve()
    if not project_dir.is_dir():
        eprint(f"ERROR: project directory not found: {project_dir}")
        return 1

    state_path = project_dir / "state.json"
    if not state_path.is_file():
        eprint(f"ERROR: state.json not found: {state_path}")
        return 1

    try:
        state = load_json(state_path)
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 1

    try:
        scene_key = find_scene_key(state, project_dir, args.scene)
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 1

    prompt_path = project_dir / "scenes" / scene_key / "prompt.md"
    if not prompt_path.is_file():
        eprint(f"ERROR: prompt.md not found for scene {args.scene}: {prompt_path}")
        return 1

    try:
        prompt_markdown = prompt_path.read_text(encoding="utf-8")
        keyframe_prompt = extract_section(prompt_markdown, "Keyframe Prompt")
    except Exception as exc:
        eprint(f"ERROR: failed to read keyframe prompt: {exc}")
        return 1

    style_keywords = resolve_style_keywords(project_dir, state, args.style_keywords)
    style_intent = style_keywords

    parts = [keyframe_prompt]
    if style_keywords:
        parts.append(style_keywords)
    if needs_anti_painting(style_intent):
        parts.append(ANTI_PAINTING_SUFFIX)
    full_prompt = " ".join(part.strip() for part in parts if part and part.strip())

    project_meta = state.get("project") if isinstance(state.get("project"), dict) else {}
    tier = str(project_meta.get("tier", "standard")).strip().lower()
    model = args.model.strip() if isinstance(args.model, str) and args.model.strip() else (
        "flux.2-klein" if tier == "budget" else "flux.2-pro"
    )
    size = "1K" if tier == "budget" else "2K"
    aspect = str(project_meta.get("aspect_ratio", "16:9"))

    script_dir = Path(__file__).resolve().parent
    image_gen_script = Path(resolve_image_gen())

    scene_dir = project_dir / "scenes" / scene_key
    scene_dir.mkdir(parents=True, exist_ok=True)
    keyframe_path = scene_dir / "keyframe.png"

    archive_existing_keyframe(keyframe_path)

    cmd = [
        "python3",
        str(image_gen_script),
        "--prompt",
        full_prompt,
        "--model",
        model,
        "--aspect-ratio",
        aspect,
        "--size",
        size,
        "--output-file",
        str(keyframe_path),
    ]

    eprint(f"Generating keyframe for scene {args.scene} ({scene_key})...")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        eprint("ERROR: image-gen failed")
        if proc.stderr.strip():
            eprint(proc.stderr.strip())
        if proc.stdout.strip():
            eprint(proc.stdout.strip())
        return 1

    try:
        image_payload = parse_last_json_line(proc.stdout, "image-gen")
    except Exception as exc:
        eprint(f"ERROR: failed to parse image-gen output: {exc}")
        if proc.stdout.strip():
            eprint(proc.stdout.strip())
        return 1

    if not image_payload.get("success", False):
        eprint(f"ERROR: image-gen returned success=false: {image_payload}")
        return 1

    cost_usd = parse_cost_usd(image_payload)

    relative_keyframe_path = f"scenes/{scene_key}/keyframe.png"

    if not args.no_state_update:
        update_state_script = script_dir / "project_state.py"
        if not update_state_script.is_file():
            eprint(f"ERROR: project_state.py not found: {update_state_script}")
            return 1

        update_cmd = [
            "python3",
            str(update_state_script),
            "--project",
            str(project_dir),
            "--scene",
            str(args.scene),
            "--gate",
            "image",
            "--status",
            "locked",
            "--path",
            relative_keyframe_path,
            "--cost",
            f"{cost_usd:.4f}",
        ]
        eprint("Updating state...")
        update_proc = subprocess.run(update_cmd, capture_output=True, text=True)
        if update_proc.returncode != 0:
            eprint("ERROR: project_state.py failed")
            if update_proc.stderr.strip():
                eprint(update_proc.stderr.strip())
            if update_proc.stdout.strip():
                eprint(update_proc.stdout.strip())
            return 1

    result = {
        "success": True,
        "path": str(keyframe_path),
        "model": model,
        "cost_usd": cost_usd,
        "style_keywords": style_keywords,
        "description": "Generated keyframe from prompt.md",
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
