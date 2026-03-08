#!/usr/bin/env python3
"""Builds a decomposition prompt that asks Claude to output a valid story.json."""

import argparse
import json
import sys
from pathlib import Path


STORY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "story.json schema",
    "type": "object",
    "required": [
        "title",
        "logline",
        "style",
        "aspect_ratio",
        "target_duration_sec",
        "tier",
        "characters",
        "scenes",
        "shots",
    ],
    "properties": {
        "title": {"type": "string", "minLength": 3},
        "logline": {"type": "string", "minLength": 10},
        "style": {"type": "string", "enum": ["cinematic", "anime", "documentary", "social_media"]},
        "aspect_ratio": {"type": "string", "enum": ["16:9", "9:16", "1:1"]},
        "target_duration_sec": {"type": "integer", "minimum": 6, "maximum": 180},
        "tier": {"type": "string", "enum": ["budget", "standard", "premium", "ultra"]},
        "theme": {"type": "string"},
        "tone": {"type": "string"},
        "characters": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/character"},
        },
        "scenes": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/scene"},
        },
        "shots": {
            "type": "array",
            "minItems": 2,
            "items": {"$ref": "#/$defs/shot"},
        },
        "audio": {
            "type": "object",
            "properties": {
                "voiceover_script": {"type": "string"},
                "music_direction": {"type": "string"},
                "sfx_notes": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": True,
        },
    },
    "$defs": {
        "character": {
            "type": "object",
            "required": ["id", "name", "role", "description", "appearance", "wardrobe"],
            "properties": {
                "id": {"type": "string", "pattern": "^[a-z0-9_\\-]+$"},
                "name": {"type": "string"},
                "role": {"type": "string"},
                "description": {"type": "string"},
                "age": {"type": ["integer", "string"]},
                "ethnicity": {"type": "string"},
                "gender": {"type": "string"},
                "appearance": {
                    "type": "object",
                    "properties": {
                        "skin_tone": {"type": "string"},
                        "face_shape": {"type": "string"},
                        "eye_color": {"type": "string"},
                        "hair_length": {"type": "string"},
                        "hair_color": {"type": "string"},
                        "hair_style": {"type": "string"},
                        "build": {"type": "string"},
                        "distinguishing_features": {"type": "array", "items": {"type": "string"}},
                        "accessories": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                },
                "wardrobe": {
                    "type": "object",
                    "properties": {
                        "top": {"type": "string"},
                        "bottom": {"type": "string"},
                        "shoes": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
                "consistency_notes": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "scene": {
            "type": "object",
            "required": ["scene_id", "summary", "location", "shot_ids"],
            "properties": {
                "scene_id": {"type": "string", "pattern": "^scene_[0-9]{2,3}$"},
                "summary": {"type": "string"},
                "location": {"type": "string"},
                "time_of_day": {"type": "string"},
                "mood": {"type": "string"},
                "palette": {"type": "array", "items": {"type": "string"}},
                "beats": {"type": "array", "items": {"type": "string"}},
                "shot_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            },
            "additionalProperties": True,
        },
        "shot": {
            "type": "object",
            "required": [
                "shot_id",
                "scene_id",
                "duration_sec",
                "prompt",
                "keyframe_prompt",
                "motion_prompt",
                "camera",
                "characters",
                "transition_to_next",
            ],
            "properties": {
                "shot_id": {"type": "string", "pattern": "^shot_[0-9]{2,3}$"},
                "scene_id": {"type": "string", "pattern": "^scene_[0-9]{2,3}$"},
                "start_sec": {"type": "number", "minimum": 0},
                "end_sec": {"type": "number", "minimum": 0},
                "duration_sec": {"type": "number", "minimum": 2, "maximum": 10},
                "prompt": {"type": "string"},
                "keyframe_prompt": {"type": "string"},
                "motion_prompt": {"type": "string"},
                "negative_prompt": {"type": "string"},
                "camera": {
                    "type": "object",
                    "properties": {
                        "framing": {"type": "string"},
                        "movement": {"type": "string"},
                        "lens": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
                "location": {"type": "string"},
                "mood": {"type": "string"},
                "characters": {"type": "array", "items": {"type": "string"}},
                "continuity_notes": {"type": "string"},
                "transition_to_next": {
                    "type": "object",
                    "required": ["type", "duration_sec"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "cut",
                                "fade",
                                "dissolve",
                                "wipe_left",
                                "wipe_right",
                                "slide_left",
                                "slide_right",
                            ],
                        },
                        "duration_sec": {"type": "number", "minimum": 0, "maximum": 2},
                    },
                    "additionalProperties": True,
                },
            },
            "additionalProperties": True,
        },
    },
    "additionalProperties": True,
}


def build_prompt(idea: str, style: str, aspect_ratio: str, duration: int, tier: str) -> str:
    schema_text = json.dumps(STORY_SCHEMA, indent=2)
    character_schema_text = json.dumps(STORY_SCHEMA["$defs"]["character"], indent=2)
    scene_schema_text = json.dumps(STORY_SCHEMA["$defs"]["scene"], indent=2)
    shot_schema_text = json.dumps(STORY_SCHEMA["$defs"]["shot"], indent=2)

    return f"""You are a story decomposition planner for a text-to-image-to-video pipeline.

Task:
Transform the user idea into a complete `story.json` that is VALID against the schema below.

Context:
- Requested style: {style}
- Requested aspect ratio: {aspect_ratio}
- Requested target duration: {duration} seconds
- Requested tier: {tier}
- User input: {idea}

Critical guidelines:
1. Shot duration must be between 2 and 10 seconds.
2. Total sum of shot durations should match {duration}s as closely as possible (<= +/-2s).
3. Character consistency is mandatory:
   - Reuse exact character IDs across all shots.
   - Keep stable appearance descriptors (face, hair, clothing core silhouette, accessories).
   - If wardrobe changes are needed, make them explicit and scene-justified.
4. Transition planning is mandatory:
   - Every shot must define `transition_to_next`.
   - Prefer motivated transitions (cut for action beat changes, dissolve/fade for time shift, wipe/slide for stylized movement).
   - Keep transition durations short (typically 0.1-0.6s).
5. Ensure each shot has:
   - `keyframe_prompt` (single still image composition)
   - `motion_prompt` (temporal action and camera motion)
   - Clear camera/framing details and continuity notes.
6. Output MUST be strict JSON only. No markdown. No explanation.

Full story.json schema:
{schema_text}

Character JSON schema:
{character_schema_text}

Scene JSON schema:
{scene_schema_text}

Shot JSON schema:
{shot_schema_text}

Return only one valid JSON object suitable for saving as `story.json`.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a decomposition prompt for Claude to produce story.json.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--idea", help="High-level story idea as plain text.")
    group.add_argument("--script", help="Path to text file containing idea/script input.")

    parser.add_argument(
        "--style",
        default="cinematic",
        choices=["cinematic", "anime", "documentary", "social_media"],
        help="Target visual storytelling style (default: cinematic).",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["16:9", "9:16", "1:1"],
        help="Target output aspect ratio (default: 16:9).",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Target total duration in seconds (default: 30).",
    )
    parser.add_argument(
        "--tier",
        default="standard",
        choices=["budget", "standard", "premium", "ultra"],
        help="Production tier for downstream generation constraints (default: standard).",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output file path. Use '-' for stdout (default).",
    )

    args = parser.parse_args()

    try:
        if args.script:
            script_path = Path(args.script)
            if not script_path.is_file():
                print(f"ERROR: script file not found: {script_path}", file=sys.stderr)
                sys.exit(1)
            idea_text = script_path.read_text(encoding="utf-8").strip()
        else:
            idea_text = (args.idea or "").strip()

        if not idea_text:
            print("ERROR: Input idea/script is empty.", file=sys.stderr)
            sys.exit(1)

        prompt = build_prompt(
            idea=idea_text,
            style=args.style,
            aspect_ratio=args.aspect_ratio,
            duration=args.duration,
            tier=args.tier,
        )

        if args.output == "-":
            print(prompt)
        else:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(prompt, encoding="utf-8")
            print(json.dumps({"success": True, "output": str(out_path)}))
            print(f"Wrote prompt to {out_path}", file=sys.stderr)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
