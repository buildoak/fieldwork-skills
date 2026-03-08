#!/usr/bin/env python3
"""Assembles shot clips into a final video with optional transitions and audio mixing."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def fail(msg: str) -> None:
    eprint(f"ERROR: {msg}")
    sys.exit(1)


def run_checked(cmd: list[str], label: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        fail(f"Command not found while running {label}: {cmd[0]}")
    except OSError as exc:
        fail(f"Failed to run {label}: {exc}")
    raise RuntimeError("unreachable")


def natural_shot_key(path: Path) -> tuple[int, str]:
    m = re.search(r"shot_(\d+)", path.stem)
    return (int(m.group(1)) if m else 10**9, str(path))


def discover_clips(clips_dir: Path) -> list[Path]:
    flat = list(clips_dir.glob("shot_*.mp4"))
    project_mode = list(clips_dir.glob("scenes/*/shot_*.mp4"))
    merged = {p.resolve(): p for p in (flat + project_mode)}
    clips = sorted(merged.values(), key=natural_shot_key)
    if not clips:
        fail(
            f"No clips found under {clips_dir}. Expected either shot_*.mp4 in --clips-dir "
            "or scenes/*/shot_*.mp4 in project mode."
        )
    return clips


def ffprobe_video(path: Path) -> dict[str, float | int]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    proc = run_checked(cmd, "ffprobe")
    if proc.returncode != 0:
        fail(f"ffprobe failed for {path}: {proc.stderr.strip() or proc.stdout.strip()}")

    try:
        data = json.loads(proc.stdout)
        stream = data.get("streams", [{}])[0]
        duration = float(data.get("format", {}).get("duration", 0.0) or 0.0)
        width = int(stream.get("width", 0) or 0)
        height = int(stream.get("height", 0) or 0)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        fail(f"Failed to parse ffprobe output for {path}: {exc}")

    if width <= 0 or height <= 0:
        fail(f"Could not determine resolution for {path}")
    if duration <= 0:
        duration = 0.01

    return {"width": width, "height": height, "duration": duration}


def load_story_transitions(story_path: Path | None) -> dict[str, str]:
    if not story_path:
        return {}
    if not story_path.is_file():
        fail(f"--story not found: {story_path}")

    try:
        story = json.loads(story_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in story file {story_path}: {exc}")

    shot_map: dict[str, str] = {}
    for shot in story.get("shots", []):
        if not isinstance(shot, dict):
            continue
        shot_id = str(shot.get("shot_id", "")).strip()
        if not shot_id:
            continue

        transition = "fade"
        raw = shot.get("transition_to_next", shot.get("transition"))
        if isinstance(raw, dict):
            transition = str(raw.get("type", "fade") or "fade")
        elif isinstance(raw, str) and raw.strip():
            transition = raw.strip()

        shot_map[shot_id] = transition
    return shot_map


def map_transition(name: str, crossfade: float) -> tuple[str, float]:
    n = (name or "fade").strip().lower()
    mapping = {
        "fade": "fade",
        "dissolve": "dissolve",
        "wipe_left": "wipeleft",
        "wipe_right": "wiperight",
        "slide_left": "slideleft",
        "slide_right": "slideright",
        "cut": "fade",
    }
    effect = mapping.get(n, "fade")
    if n == "cut":
        return effect, min(crossfade, 0.001)
    return effect, crossfade


def shot_id_from_clip(path: Path) -> str:
    m = re.search(r"(shot_\d+)", path.stem)
    return m.group(1) if m else path.stem


def build_filter_complex(
    clips: list[Path],
    metas: list[dict[str, float | int]],
    crossfade: float,
    transition_by_shot: dict[str, str],
    include_voiceover: bool,
    include_music: bool,
) -> tuple[str, str, str | None]:
    base_w = int(metas[0]["width"])
    base_h = int(metas[0]["height"])

    parts: list[str] = []
    for i in range(len(clips)):
        parts.append(
            f"[{i}:v]scale={base_w}:{base_h}:force_original_aspect_ratio=decrease,"
            f"pad={base_w}:{base_h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v{i}]"
        )

    if len(clips) == 1:
        video_label = "[v0]"
    else:
        prev_label = "[v0]"
        offset = max(float(metas[0]["duration"]) - crossfade, 0.0)

        for i in range(1, len(clips)):
            prev_shot = shot_id_from_clip(clips[i - 1])
            transition_name = transition_by_shot.get(prev_shot, "fade")
            effect, local_crossfade = map_transition(transition_name, crossfade)
            x_label = f"[vx{i}]"
            parts.append(
                f"{prev_label}[v{i}]xfade=transition={effect}:duration={local_crossfade}:offset={offset}{x_label}"
            )
            prev_label = x_label
            offset += max(float(metas[i]["duration"]) - local_crossfade, 0.0)

        video_label = prev_label

    audio_label: str | None = None
    audio_base_idx = len(clips)
    next_audio_idx = audio_base_idx

    if include_voiceover and include_music:
        voice_idx = next_audio_idx
        music_idx = next_audio_idx + 1
        parts.append(f"[{music_idx}:a]volume=0.25[bgm]")
        parts.append(f"[{voice_idx}:a][bgm]amix=inputs=2:duration=longest:dropout_transition=2[aout]")
        audio_label = "[aout]"
    elif include_voiceover:
        voice_idx = next_audio_idx
        parts.append(f"[{voice_idx}:a]anull[aout]")
        audio_label = "[aout]"
    elif include_music:
        music_idx = next_audio_idx
        parts.append(f"[{music_idx}:a]volume=0.25[aout]")
        audio_label = "[aout]"

    return ";".join(parts), video_label, audio_label


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble shot clips into final video using ffmpeg.")
    parser.add_argument(
        "--clips-dir",
        required=True,
        help="Directory containing shot_*.mp4 clips (flat) or scenes/*/shot_*.mp4 (project mode).",
    )
    parser.add_argument("--output", required=True, help="Output final video path.")
    parser.add_argument("--story", default=None, help="Optional story.json for per-shot transitions.")
    parser.add_argument("--audio", default=None, help="Optional voiceover audio file path.")
    parser.add_argument("--music", default=None, help="Optional background music file path.")
    parser.add_argument("--crossfade", type=float, default=0.3, help="Crossfade duration in seconds (default: 0.3).")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        fail("ffmpeg not found in PATH. Install ffmpeg and retry.")
    if shutil.which("ffprobe") is None:
        fail("ffprobe not found in PATH. Install ffmpeg (includes ffprobe) and retry.")

    clips_dir = Path(args.clips_dir)
    if not clips_dir.is_dir():
        fail(f"--clips-dir is not a directory: {clips_dir}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clips = discover_clips(clips_dir)
    metas = [ffprobe_video(c) for c in clips]

    transition_map = load_story_transitions(Path(args.story) if args.story else None)

    voiceover = Path(args.audio) if args.audio else None
    music = Path(args.music) if args.music else None

    if voiceover and not voiceover.is_file():
        fail(f"--audio file not found: {voiceover}")
    if music and not music.is_file():
        fail(f"--music file not found: {music}")

    include_voiceover = bool(voiceover)
    include_music = bool(music)

    crossfade = max(float(args.crossfade), 0.0)
    filter_complex, video_label, audio_label = build_filter_complex(
        clips=clips,
        metas=metas,
        crossfade=crossfade,
        transition_by_shot=transition_map,
        include_voiceover=include_voiceover,
        include_music=include_music,
    )

    cmd: list[str] = ["ffmpeg", "-y"]
    for clip in clips:
        cmd.extend(["-i", str(clip)])
    if voiceover:
        cmd.extend(["-i", str(voiceover)])
    if music:
        cmd.extend(["-i", str(music)])

    cmd.extend(["-filter_complex", filter_complex, "-map", video_label])

    if audio_label:
        cmd.extend(["-map", audio_label, "-c:a", "aac", "-b:a", "192k", "-shortest"]
        )
    else:
        cmd.append("-an")

    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )

    eprint(f"Assembling {len(clips)} clip(s) -> {output_path}")
    proc = run_checked(cmd, "ffmpeg assemble")
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        fail(f"ffmpeg assembly failed: {stderr[:1000]}")

    if not output_path.is_file() or output_path.stat().st_size == 0:
        fail(f"Output not created or empty: {output_path}")

    report: dict[str, Any] = {
        "success": True,
        "output": str(output_path),
        "clip_count": len(clips),
        "crossfade": crossfade,
        "audio_included": bool(audio_label),
        "resolution": f"{int(metas[0]['width'])}x{int(metas[0]['height'])}",
        "filter_complex": filter_complex,
    }
    print(json.dumps(report))


if __name__ == "__main__":
    main()
