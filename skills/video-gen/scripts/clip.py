#!/usr/bin/env python3
"""Generate a video clip for a story-gen scene using the locked keyframe."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


MODEL_CLI_MAP = {
    "ltx": "ltx-2.3",
    "kling": "kling-v3",
    "veo": "veo-3",
    "sora": "sora-2",
}

MODEL_BY_TIER = {
    "budget": "ltx-2.3",
    "standard": "kling-v3",
    "premium": "kling-v3",
    "ultra": "veo-3",
}

QUALITY_BY_TIER = {
    "budget": "fast",
    "standard": "standard",
    "premium": "pro",
    "ultra": "standard",
}

COST_PER_SEC = {
    "ltx-2.3": 0.04,
    "kling-v3": 0.168,
    "veo-3": 0.20,
    "sora-2": 0.30,
}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


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
    """Resolve scene number to scene key (e.g., '03-rocket-departure')."""
    scene_prefix = f"{scene_number:02d}-"
    scenes_obj = state.get("scenes")

    if isinstance(scenes_obj, dict):
        for key in scenes_obj:
            if isinstance(key, str) and key.startswith(scene_prefix):
                return key
        # Fallback: check by number field
        for key, value in scenes_obj.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            for num_key in ("number", "scene", "index"):
                num = value.get(num_key)
                if isinstance(num, int) and num == scene_number:
                    return key

    if isinstance(scenes_obj, list):
        for item in scenes_obj:
            if not isinstance(item, dict):
                continue
            for num_key in ("number", "scene", "index"):
                num = item.get(num_key)
                if isinstance(num, int) and num == scene_number:
                    key = item.get("key") or item.get("scene_key") or item.get("id")
                    if isinstance(key, str) and key.strip():
                        return key.strip()

    # Fallback: check filesystem
    scenes_dir = project_dir / "scenes"
    if scenes_dir.is_dir():
        candidates = sorted(
            p.name for p in scenes_dir.iterdir() if p.is_dir() and p.name.startswith(scene_prefix)
        )
        if candidates:
            return candidates[0]

    raise ValueError(f"Could not resolve scene key for scene {scene_number}")


def find_prev_scene_key(state: dict[str, Any], project_dir: Path, scene_number: int) -> str | None:
    """Find the scene key for scene_number - 1."""
    if scene_number <= 1:
        return None
    try:
        return find_scene_key(state, project_dir, scene_number - 1)
    except ValueError:
        return None


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


def archive_existing_clip(clip_path: Path) -> None:
    """Rename existing clip to clip-draft-N.mp4."""
    if not clip_path.exists():
        return

    idx = 1
    while True:
        draft_path = clip_path.with_name(f"clip-draft-{idx}.mp4")
        if not draft_path.exists():
            clip_path.rename(draft_path)
            eprint(f"Archived existing clip -> {draft_path}")
            return
        idx += 1


def extract_bridge_frame(prev_clip_path: Path, bridge_output: Path) -> bool:
    """Extract last frame of previous clip using ffmpeg."""
    if not shutil.which("ffmpeg"):
        eprint("WARNING: ffmpeg not found, cannot extract bridge frame")
        return False

    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-0.1",
        "-i", str(prev_clip_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(bridge_output),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode == 0 and bridge_output.is_file() and bridge_output.stat().st_size > 0:
        return True
    eprint(f"WARNING: bridge frame extraction failed: {proc.stderr[:500] if proc.stderr else 'unknown error'}")
    return False


def parse_cost_usd(payload: dict[str, Any], default: float = 0.0) -> float:
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
    return default


def scene_number_from_key(scene_key: str, fallback: int) -> int:
    match = re.match(r"^(\d+)", scene_key)
    if not match:
        return fallback
    try:
        return int(match.group(1))
    except ValueError:
        return fallback


def shot_filename(scene_key: str, fallback_scene_number: int) -> str:
    scene_num = scene_number_from_key(scene_key, fallback_scene_number)
    return f"shot_{scene_num:02d}.mp4"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a video clip for a story-gen scene using the locked keyframe.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--project", required=True, help="Path to project directory.")
    parser.add_argument("--scene", required=True, type=int, help="Scene number (int).")
    parser.add_argument(
        "--model",
        default=None,
        choices=list(MODEL_CLI_MAP.keys()),
        help="Video model override. Default: auto from tier.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=6,
        help="Clip duration in seconds. LTX only accepts 6, 8, 10.",
    )
    parser.add_argument(
        "--bridge",
        action="store_true",
        help="Use temporal bridging from previous scene's last frame.",
    )
    parser.add_argument(
        "--quality",
        default=None,
        choices=["fast", "standard", "pro"],
        help="Override quality tier.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Reproducibility seed.",
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

    # Resolve scene key
    try:
        scene_key = find_scene_key(state, project_dir, args.scene)
    except Exception as exc:
        eprint(f"ERROR: {exc}")
        return 1

    # Read motion prompt from prompt.md
    prompt_path = project_dir / "scenes" / scene_key / "prompt.md"
    if not prompt_path.is_file():
        eprint(f"ERROR: prompt.md not found for scene {args.scene}: {prompt_path}")
        return 1

    try:
        prompt_markdown = prompt_path.read_text(encoding="utf-8")
        motion_prompt = extract_section(prompt_markdown, "Motion Prompt")
    except Exception as exc:
        eprint(f"ERROR: failed to read motion prompt: {exc}")
        return 1

    # Resolve keyframe path from state.json
    scenes_state = state.get("scenes", {})
    scene_state = scenes_state.get(scene_key, {}) if isinstance(scenes_state, dict) else {}
    image_state = scene_state.get("image", {}) if isinstance(scene_state, dict) else {}
    keyframe_rel = image_state.get("path")

    if keyframe_rel and isinstance(keyframe_rel, str):
        keyframe_path = project_dir / keyframe_rel
    else:
        keyframe_path = project_dir / "scenes" / scene_key / "keyframe.png"

    if not keyframe_path.is_file():
        eprint(f"ERROR: keyframe not found for scene {args.scene}: {keyframe_path}")
        return 1

    # Resolve model and quality from tier
    project_meta = state.get("project") if isinstance(state.get("project"), dict) else {}
    tier = str(project_meta.get("tier", "standard")).strip().lower()

    if args.model:
        model_cli = MODEL_CLI_MAP[args.model]
    else:
        model_cli = MODEL_BY_TIER.get(tier, "kling-v3")

    quality = args.quality if args.quality else QUALITY_BY_TIER.get(tier, "standard")
    aspect = str(project_meta.get("aspect_ratio", "16:9"))
    duration = args.duration

    # Temporal bridging
    bridge_used = False
    image_input = keyframe_path

    if args.bridge and args.scene > 1:
        prev_key = find_prev_scene_key(state, project_dir, args.scene)
        if prev_key:
            prev_scene_state = scenes_state.get(prev_key, {}) if isinstance(scenes_state, dict) else {}
            prev_video = prev_scene_state.get("video", {}) if isinstance(prev_scene_state, dict) else {}
            prev_clip_rel = prev_video.get("path")

            if prev_clip_rel and isinstance(prev_clip_rel, str):
                prev_clip_path = project_dir / prev_clip_rel
            else:
                prev_shot_name = shot_filename(prev_key, args.scene - 1)
                prev_clip_path = project_dir / "scenes" / prev_key / prev_shot_name
                if not prev_clip_path.is_file():
                    prev_clip_path = project_dir / "scenes" / prev_key / "clip.mp4"

            if prev_clip_path.is_file():
                bridge_frame = project_dir / "scenes" / scene_key / "bridge-frame.jpg"
                bridge_frame.parent.mkdir(parents=True, exist_ok=True)
                if extract_bridge_frame(prev_clip_path, bridge_frame):
                    image_input = bridge_frame
                    bridge_used = True
                    eprint(f"Using bridge frame from scene {args.scene - 1}")
                else:
                    eprint(f"Falling back to keyframe for scene {args.scene}")
            else:
                eprint(f"Previous scene clip not found: {prev_clip_path}, using keyframe")

    # Locate video-gen script
    script_dir = Path(__file__).resolve().parent
    video_gen_script = script_dir / "generate.py"
    if not video_gen_script.is_file():
        eprint(f"ERROR: video-gen script not found: {video_gen_script}")
        return 1

    # Prepare output path
    scene_dir = project_dir / "scenes" / scene_key
    scene_dir.mkdir(parents=True, exist_ok=True)
    clip_name = shot_filename(scene_key, args.scene)
    clip_path = scene_dir / clip_name

    archive_existing_clip(clip_path)

    # Build command
    cmd = [
        "python3",
        str(video_gen_script),
        "--model", model_cli,
        "--mode", "i2v",
        "--image", str(image_input),
        "--prompt", motion_prompt,
        "--duration", str(duration),
        "--aspect", aspect,
        "--quality", quality,
        "--no-audio",
        "--no-preview",
        "--json",
        "--output", str(clip_path),
    ]

    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])

    eprint(f"Generating clip for scene {args.scene} ({scene_key})...")
    eprint(f"  Model: {model_cli} | Duration: {duration}s | Quality: {quality}")
    eprint(f"  Image input: {image_input}")

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        eprint("ERROR: video-gen failed")
        if proc.stderr.strip():
            eprint(proc.stderr.strip())
        if proc.stdout.strip():
            eprint(proc.stdout.strip())
        return 1

    try:
        video_payload = parse_last_json_line(proc.stdout, "video-gen")
    except Exception as exc:
        eprint(f"ERROR: failed to parse video-gen output: {exc}")
        if proc.stdout.strip():
            eprint(proc.stdout.strip())
        return 1

    if not video_payload.get("success", False):
        eprint(f"ERROR: video-gen returned success=false: {video_payload}")
        return 1

    # Calculate cost
    est_cost = round(duration * COST_PER_SEC.get(model_cli, 0.10), 4)
    reported_cost = parse_cost_usd(video_payload, est_cost)
    cost_usd = est_cost if reported_cost <= 0 else reported_cost

    relative_clip_path = f"scenes/{scene_key}/{clip_name}"

    # Update state
    if not args.no_state_update:
        update_state_script = script_dir / "update_state.py"
        if not update_state_script.is_file():
            eprint(f"ERROR: update_state.py not found: {update_state_script}")
            return 1

        update_cmd = [
            "python3",
            str(update_state_script),
            "--project", str(project_dir),
            "--scene", str(args.scene),
            "--gate", "video",
            "--status", "locked",
            "--path", relative_clip_path,
            "--cost", f"{cost_usd:.4f}",
            "--model", model_cli,
            "--duration", str(duration),
        ]
        eprint("Updating state...")
        update_proc = subprocess.run(update_cmd, capture_output=True, text=True, check=False)
        if update_proc.returncode != 0:
            eprint("ERROR: update_state.py failed")
            if update_proc.stderr.strip():
                eprint(update_proc.stderr.strip())
            if update_proc.stdout.strip():
                eprint(update_proc.stdout.strip())
            return 1

    result = {
        "success": True,
        "path": str(clip_path),
        "model": model_cli,
        "cost_usd": cost_usd,
        "duration_sec": duration,
        "bridge_used": bridge_used,
        "description": "Generated clip from keyframe + motion prompt",
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
