#!/usr/bin/env python3
"""video-gen preview.py — Quick preview via LTX fast (cheapest, fastest)."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

GENERATE_SCRIPT = Path(__file__).resolve().parent / "generate.py"


def preview_file(path):
    """Open file in system viewer. macOS: QuickLook. Linux: xdg-open."""
    import platform
    if platform.system() == "Darwin":
        subprocess.run(["qlmanage", "-p", path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["xdg-open", path])


def main() -> None:
    # If called with a single file arg (no flags), just preview it
    if len(sys.argv) == 2 and not sys.argv[1].startswith("--") and Path(sys.argv[1]).is_file():
        preview_file(sys.argv[1])
        return

    parser = argparse.ArgumentParser(description="Quick LTX preview (cheapest, fastest)")
    parser.add_argument("--prompt", required=True, help="Video description")
    parser.add_argument("--mode", default="t2v", choices=["t2v", "i2v"], help="t2v or i2v")
    parser.add_argument("--image", default="", help="Source image for i2v mode")
    parser.add_argument("--output", default="", help="Custom output path")
    args = parser.parse_args()

    if args.mode == "i2v" and not args.image:
        print("i2v mode requires --image", file=sys.stderr)
        sys.exit(1)

    # Build generate.py command with locked fast params
    cmd = [
        sys.executable, str(GENERATE_SCRIPT),
        "--prompt", args.prompt,
        "--mode", args.mode,
        "--model", "ltx-2.3",
        "--quality", "fast",
        "--duration", "6",
        "--resolution", "720p",
        "--no-preview",
        "--json",
    ]
    if args.mode == "i2v" and args.image:
        cmd.extend(["--image", args.image])
    if args.output:
        cmd.extend(["--output", args.output])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.stdout:
        sys.stdout.write(result.stdout)

    if result.returncode == 0:
        try:
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            payload = json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            print("generate.py returned non-JSON output", file=sys.stderr)
            sys.exit(1)

        output_file = payload.get("file") or payload.get("path")
        if not output_file:
            print("generate.py success response missing output file path", file=sys.stderr)
            sys.exit(1)
        preview_file(output_file)

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
