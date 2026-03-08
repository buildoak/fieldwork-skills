#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


TIER_TO_VIDEO_MODEL = {
    "budget": "ltx-2.3",
    "standard": "kling-v3",
    "premium": "kling-v3",
    "ultra": "veo-3",
}

TIER_TO_IMAGE_MODEL = {
    "budget": "flux.2-klein",
    "standard": "flux.2-pro",
    "premium": "flux.2-pro",
    "ultra": "flux.2-pro",
}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def iso_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_kebab_case(value: str) -> bool:
    if not value or value.startswith("-") or value.endswith("-"):
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if any(ch not in allowed for ch in value):
        return False
    if "--" in value:
        return False
    return True


def build_title(name: str) -> str:
    return name.replace("-", " ").title()


def build_manifest(
    title: str,
    logline: str,
    style: str,
    aspect: str,
    tier: str,
    budget: float,
    scenes: int,
) -> str:
    video_model = TIER_TO_VIDEO_MODEL[tier]
    image_model = TIER_TO_IMAGE_MODEL[tier]
    lines = [
        f"# {title} -- Production Manifest",
        "",
        f"**Logline:** {logline}",
        f"**Style:** {style} | **Aspect:** {aspect} | **Tier:** {tier}",
        f"**Model (image):** {image_model} | **Model (video):** {video_model}",
        f"**Style keywords:** {style}",
        f"**Budget:** ${budget:.2f} | **Spent:** $0.00",
        "",
        "## Scenes",
        "",
        "| # | Name | Prompt | Image | Video | Duration | Transition |",
        "|---|------|--------|-------|-------|----------|------------|",
    ]

    for idx in range(1, scenes + 1):
        scene_name = f"Scene {idx:02d}"
        lines.append(
            f"| {idx} | {scene_name} | -- | -- | -- | 6s | dissolve |"
        )

    lines.extend(
        [
            "",
            "## Style Keywords",
            style,
            "",
            "## Audio Direction",
            "(to be filled)",
            "",
            "## Production Notes",
            "(to be filled)",
            "",
        ]
    )
    return "\n".join(lines)


def build_state(
    name: str,
    title: str,
    timestamp: str,
    tier: str,
    style: str,
    aspect: str,
    scenes: int,
    budget: float,
) -> dict:
    return {
        "project": {
            "name": name,
            "title": title,
            "created": timestamp,
            "updated": timestamp,
            "tier": tier,
            "style": style,
            "aspect_ratio": aspect,
            "target_duration_sec": scenes * 6,
            "running_cost_usd": 0.0,
            "budget_usd": budget,
        },
        "scenes": {},
        "sequence_locked": False,
        "assembly": {"status": "pending", "path": None},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a video-gen interactive project folder."
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Project name in kebab-case, used as folder name.",
    )
    parser.add_argument(
        "--scenes",
        required=True,
        type=int,
        help="Number of scenes (int, >= 1).",
    )
    parser.add_argument(
        "--aspect",
        default="16:9",
        choices=["16:9", "9:16", "1:1"],
        help="Aspect ratio (default: 16:9).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Parent directory where project folder is created.",
    )
    parser.add_argument(
        "--style",
        default="cinematic",
        help="Style keywords (comma-separated).",
    )
    parser.add_argument(
        "--tier",
        default="standard",
        choices=["budget", "standard", "premium", "ultra"],
        help="Generation tier (default: standard).",
    )
    parser.add_argument(
        "--logline",
        default="",
        help="One-line description.",
    )
    parser.add_argument(
        "--budget",
        default=50.0,
        type=float,
        help="Max spend in USD (default: 50.0).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not is_kebab_case(args.name):
        eprint(
            "Error: --name must be kebab-case using lowercase letters, digits, and hyphens (example: noir-detective)."
        )
        return 2
    if args.scenes < 1:
        eprint("Error: --scenes must be >= 1.")
        return 2
    if args.budget < 0:
        eprint("Error: --budget must be >= 0.")
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    project_dir = output_dir / args.name
    manifest_path = project_dir / "manifest.md"
    state_path = project_dir / "state.json"

    if project_dir.exists():
        eprint(
            f"Error: project directory already exists: {project_dir}. "
            "Choose a different --name or remove the existing directory."
        )
        return 1

    eprint(f"Creating project directory: {project_dir}")
    project_dir.mkdir(parents=True, exist_ok=False)

    eprint("Creating subdirectories...")
    for dirname in ["scenes", "characters", "audio", "output"]:
        (project_dir / dirname).mkdir(exist_ok=True)

    title = build_title(args.name)
    timestamp = iso_timestamp()

    eprint("Writing manifest.md...")
    manifest = build_manifest(
        title=title,
        logline=args.logline,
        style=args.style,
        aspect=args.aspect,
        tier=args.tier,
        budget=args.budget,
        scenes=args.scenes,
    )
    manifest_path.write_text(manifest, encoding="utf-8")

    eprint("Writing state.json...")
    state = build_state(
        name=args.name,
        title=title,
        timestamp=timestamp,
        tier=args.tier,
        style=args.style,
        aspect=args.aspect,
        scenes=args.scenes,
        budget=args.budget,
    )
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    result = {
        "success": True,
        "project_dir": str(project_dir),
        "manifest": str(manifest_path),
        "state": str(state_path),
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
