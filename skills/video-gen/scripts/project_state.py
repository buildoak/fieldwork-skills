#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GATES = ("prompt", "image", "video")
STATUSES = ("pending", "draft", "locked", "approved")
PRINT_STATUS_SENTINEL = "__PRINT_STATUS__"


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def iso_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_kebab_case(value: str) -> bool:
    if not value:
        return False
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value))


def format_scene_key(scene_number: int, scene_name: str) -> str:
    return f"{scene_number:02d}-{scene_name}"


def default_scene_name(scene_number: int) -> str:
    return f"scene-{scene_number:02d}"


def default_gate_state() -> dict[str, Any]:
    return {"status": "pending", "path": None}


def default_scene_state() -> dict[str, Any]:
    return {
        "prompt": default_gate_state(),
        "image": default_gate_state(),
        "video": default_gate_state(),
    }


def load_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        raise FileNotFoundError(f"state.json not found: {state_path}")
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {state_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("state.json root must be an object")

    data.setdefault("project", {})
    if not isinstance(data["project"], dict):
        data["project"] = {}

    data.setdefault("scenes", {})
    if not isinstance(data["scenes"], dict):
        raise ValueError("state.json 'scenes' must be an object mapping scene keys to scene state")

    data.setdefault("sequence_locked", False)
    data.setdefault("assembly", {"status": "pending", "path": None})

    return data


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(directory))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def parse_scene_number_from_key(scene_key: str) -> int:
    try:
        return int(scene_key.split("-", 1)[0])
    except (ValueError, IndexError):
        return 999999


def scene_sort_key(scene_key: str) -> tuple[int, str]:
    return (parse_scene_number_from_key(scene_key), scene_key)


def find_scene_key_by_number(scenes: dict[str, Any], scene_number: int) -> str | None:
    prefix = f"{scene_number:02d}-"
    matches = [key for key in scenes.keys() if key.startswith(prefix)]
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous scene number {scene_number}: multiple keys found {sorted(matches)}"
        )
    return matches[0]


def ensure_scene(scenes: dict[str, Any], scene_number: int) -> str:
    scene_key = find_scene_key_by_number(scenes, scene_number)
    if scene_key is None:
        scene_key = format_scene_key(scene_number, default_scene_name(scene_number))
        scenes[scene_key] = default_scene_state()
        return scene_key

    scene_obj = scenes.get(scene_key)
    if not isinstance(scene_obj, dict):
        scene_obj = {}
        scenes[scene_key] = scene_obj

    for gate in GATES:
        gate_obj = scene_obj.get(gate)
        if not isinstance(gate_obj, dict):
            gate_obj = default_gate_state()
            scene_obj[gate] = gate_obj
        gate_obj.setdefault("status", "pending")
        gate_obj.setdefault("path", None)

    return scene_key


def normalize_relative_path(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        raise ValueError("--path must be relative to the project directory")
    normalized = p.as_posix()
    return normalized


def gate_obj(scene: dict[str, Any], gate: str) -> dict[str, Any]:
    obj = scene.get(gate)
    if not isinstance(obj, dict):
        obj = default_gate_state()
        scene[gate] = obj
    obj.setdefault("status", "pending")
    obj.setdefault("path", None)
    return obj


def invalidate_gate(scene: dict[str, Any], gate: str) -> list[str]:
    cascaded: list[str] = []

    current = gate_obj(scene, gate)
    current["status"] = "pending"
    current["path"] = None

    if gate == "prompt":
        for dependent in ("image", "video"):
            dep_obj = gate_obj(scene, dependent)
            dep_obj["status"] = "pending"
            dep_obj["path"] = None
            cascaded.append(dependent)
    elif gate == "image":
        dep_obj = gate_obj(scene, "video")
        dep_obj["status"] = "pending"
        dep_obj["path"] = None
        cascaded.append("video")

    return cascaded


def recalc_running_cost_usd(state: dict[str, Any]) -> float:
    total = 0.0
    scenes = state.get("scenes", {})
    if isinstance(scenes, dict):
        for scene in scenes.values():
            if not isinstance(scene, dict):
                continue
            for gate in GATES:
                gate_state = scene.get(gate)
                if not isinstance(gate_state, dict):
                    continue
                cost = gate_state.get("cost")
                if isinstance(cost, (int, float)):
                    total += float(cost)
    total = round(total, 4)
    project = state.setdefault("project", {})
    if not isinstance(project, dict):
        state["project"] = {}
        project = state["project"]
    project["running_cost_usd"] = total
    return total


def touch_updated(state: dict[str, Any]) -> None:
    project = state.setdefault("project", {})
    if not isinstance(project, dict):
        state["project"] = {}
        project = state["project"]
    project["updated"] = iso_timestamp()


def render_status_table(state: dict[str, Any]) -> str:
    lines = [
        "Scene | Prompt | Image | Video | Notes",
        "----- | ------ | ----- | ----- | -----",
    ]
    scenes = state.get("scenes", {})
    if not isinstance(scenes, dict):
        scenes = {}

    for scene_key in sorted(scenes.keys(), key=scene_sort_key):
        scene = scenes.get(scene_key)
        scene = scene if isinstance(scene, dict) else {}

        values = []
        for gate in GATES:
            entry = scene.get(gate)
            if isinstance(entry, dict):
                values.append(str(entry.get("status") or "--"))
            else:
                values.append("--")

        notes: list[str] = []
        if scene.get("sequence") == "locked":
            notes.append("sequence:locked")

        lines.append(
            f"{scene_key} | {values[0]} | {values[1]} | {values[2]} | {'; '.join(notes)}"
        )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage story-gen interactive project state.json"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the project directory (contains state.json)",
    )
    parser.add_argument("--scene", type=int, help="Scene number (int)")
    parser.add_argument("--gate", choices=GATES, help="Gate to update")
    parser.add_argument(
        "--status",
        nargs="?",
        const=PRINT_STATUS_SENTINEL,
        help=(
            "Gate status (pending|draft|locked|approved) or use --status alone "
            "to print status table"
        ),
    )
    parser.add_argument(
        "--path",
        help="Relative file path to associate with gate",
    )
    parser.add_argument("--cost", type=float, help="Cost in USD")
    parser.add_argument("--model", help="Model used for generation")
    parser.add_argument("--duration", type=float, help="Duration in seconds")
    parser.add_argument(
        "--invalidate",
        choices=GATES,
        help="Gate to invalidate with cascade",
    )
    parser.add_argument("--add-scene", action="store_true", help="Add new scene")
    parser.add_argument("--scene-name", help="New scene name (kebab-case)")
    parser.add_argument("--scene-number", type=int, help="New scene number (int)")
    parser.add_argument(
        "--lock-sequence",
        action="store_true",
        help="Mark sequence as locked",
    )
    return parser.parse_args()


def validate_mode(args: argparse.Namespace) -> str:
    status_mode = args.status == PRINT_STATUS_SENTINEL

    modes: list[str] = []
    if status_mode:
        modes.append("print_status")
    if args.add_scene:
        modes.append("add_scene")
    if args.invalidate is not None:
        modes.append("invalidate")
    if args.gate is not None or (
        isinstance(args.status, str) and args.status != PRINT_STATUS_SENTINEL
    ):
        modes.append("update_gate")

    if len(modes) == 0:
        raise ValueError("No operation specified. Use --help for usage.")

    if len(set(modes)) > 1:
        raise ValueError("Conflicting operations requested. Use one mode per invocation.")

    mode = modes[0]

    if mode == "print_status":
        if any(
            value is not None
            for value in [
                args.scene,
                args.gate,
                args.path,
                args.cost,
                args.model,
                args.duration,
                args.invalidate,
                args.scene_name,
                args.scene_number,
            ]
        ) or args.add_scene or args.lock_sequence:
            raise ValueError("--status table mode cannot be combined with other operation flags.")
        return mode

    if mode == "add_scene":
        if args.scene_name is None or args.scene_number is None:
            raise ValueError("--add-scene requires --scene-name and --scene-number.")
        if not is_kebab_case(args.scene_name):
            raise ValueError("--scene-name must be kebab-case.")
        if args.scene_number < 1:
            raise ValueError("--scene-number must be >= 1.")
        if any(
            value is not None
            for value in [args.scene, args.gate, args.path, args.cost, args.model, args.duration, args.invalidate]
        ):
            raise ValueError("--add-scene cannot be combined with gate update/invalidate flags.")
        return mode

    if mode == "invalidate":
        if args.scene is None:
            raise ValueError("--invalidate requires --scene.")
        if args.scene < 1:
            raise ValueError("--scene must be >= 1.")
        if any(
            value is not None
            for value in [args.gate, args.path, args.cost, args.model, args.duration, args.scene_name, args.scene_number]
        ) or args.add_scene:
            raise ValueError("--invalidate cannot be combined with update/add-scene flags.")
        if isinstance(args.status, str) and args.status != PRINT_STATUS_SENTINEL:
            raise ValueError("--invalidate cannot be combined with gate --status values.")
        return mode

    # update_gate
    if args.scene is None:
        raise ValueError("gate update requires --scene.")
    if args.scene < 1:
        raise ValueError("--scene must be >= 1.")
    if args.gate is None:
        raise ValueError("gate update requires --gate.")
    if not isinstance(args.status, str) or args.status == PRINT_STATUS_SENTINEL:
        raise ValueError("gate update requires --status with a value.")
    if args.status not in STATUSES:
        raise ValueError(
            f"invalid --status '{args.status}' (choose from: {', '.join(STATUSES)})"
        )
    if any(value is not None for value in [args.scene_name, args.scene_number, args.invalidate]) or args.add_scene:
        raise ValueError("gate update cannot be combined with add-scene/invalidate flags.")

    if args.path is not None:
        normalize_relative_path(args.path)
    if args.cost is not None and args.cost < 0:
        raise ValueError("--cost must be >= 0")
    if args.duration is not None and args.duration < 0:
        raise ValueError("--duration must be >= 0")

    return mode


def cmd_print_status(state: dict[str, Any]) -> int:
    print(render_status_table(state))
    return 0


def cmd_add_scene(state: dict[str, Any], scene_name: str, scene_number: int, lock_sequence: bool) -> dict[str, Any]:
    scenes = state["scenes"]
    existing = find_scene_key_by_number(scenes, scene_number)
    new_key = format_scene_key(scene_number, scene_name)

    if existing is not None and existing != new_key:
        raise ValueError(
            f"Scene number {scene_number} already exists as '{existing}'. Choose a different --scene-number."
        )
    if new_key in scenes:
        raise ValueError(f"Scene already exists: {new_key}")

    scenes[new_key] = default_scene_state()

    if lock_sequence:
        state["sequence_locked"] = True

    touch_updated(state)
    recalc_running_cost_usd(state)

    return {
        "success": True,
        "scene": new_key,
        "action": "add_scene",
        "status": "pending",
        "cascaded": [],
    }


def cmd_invalidate(state: dict[str, Any], scene_number: int, gate: str, lock_sequence: bool) -> dict[str, Any]:
    scenes = state["scenes"]
    scene_key = ensure_scene(scenes, scene_number)
    scene = scenes[scene_key]

    cascaded = invalidate_gate(scene, gate)

    if lock_sequence:
        state["sequence_locked"] = True

    touch_updated(state)
    recalc_running_cost_usd(state)

    return {
        "success": True,
        "scene": scene_key,
        "gate": gate,
        "status": "pending",
        "cascaded": cascaded,
    }


def cmd_update_gate(
    state: dict[str, Any],
    scene_number: int,
    gate: str,
    status: str,
    path: str | None,
    cost: float | None,
    model: str | None,
    duration: float | None,
    lock_sequence: bool,
) -> dict[str, Any]:
    scenes = state["scenes"]
    scene_key = ensure_scene(scenes, scene_number)
    scene = scenes[scene_key]
    target_gate = gate_obj(scene, gate)

    target_gate["status"] = status

    if path is not None:
        target_gate["path"] = normalize_relative_path(path)
    elif "path" not in target_gate:
        target_gate["path"] = None

    if cost is not None:
        target_gate["cost"] = round(float(cost), 4)
    if model is not None:
        target_gate["model"] = model
    if duration is not None:
        target_gate["duration"] = float(duration)

    if lock_sequence:
        state["sequence_locked"] = True

    touch_updated(state)
    recalc_running_cost_usd(state)

    return {
        "success": True,
        "scene": scene_key,
        "gate": gate,
        "status": status,
        "cascaded": [],
    }


def main() -> int:
    try:
        args = parse_args()
        mode = validate_mode(args)

        project_dir = Path(args.project).expanduser()
        if not project_dir.is_dir():
            raise FileNotFoundError(f"project directory not found: {project_dir}")

        state_path = project_dir / "state.json"
        state = load_state(state_path)

        if mode == "print_status":
            return cmd_print_status(state)

        if mode == "add_scene":
            summary = cmd_add_scene(
                state,
                scene_name=args.scene_name,
                scene_number=args.scene_number,
                lock_sequence=args.lock_sequence,
            )
        elif mode == "invalidate":
            summary = cmd_invalidate(
                state,
                scene_number=args.scene,
                gate=args.invalidate,
                lock_sequence=args.lock_sequence,
            )
        else:
            summary = cmd_update_gate(
                state,
                scene_number=args.scene,
                gate=args.gate,
                status=args.status,
                path=args.path,
                cost=args.cost,
                model=args.model,
                duration=args.duration,
                lock_sequence=args.lock_sequence,
            )

        atomic_write_json(state_path, state)
        print(json.dumps(summary))
        return 0
    except (ValueError, FileNotFoundError) as exc:
        eprint(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
