#!/usr/bin/env bash
set -euo pipefail

printf 'Checking web-search dependencies...\n'

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required but was not found."
    exit 1
fi

python3 - <<'PY'
import importlib

def check_module(name):
    try:
        importlib.import_module(name)
        print(f"  - {name}: available")
    except Exception as exc:
        raise SystemExit(f"  - {name}: unavailable ({exc})")

check_module("duckduckgo_search")
check_module("crawl4ai")
print("All core modules are importable.")
PY

if ! command -v crawl4ai-setup >/dev/null 2>&1; then
    user_bin="$(python3 -m site --user-base)/bin"
    if [[ ! -x "$user_bin/crawl4ai-setup" ]]; then
        echo "crawl4ai-setup is not installed. Run ./scripts/setup.sh first."
        exit 1
    fi
fi

echo "Dependency check complete."
