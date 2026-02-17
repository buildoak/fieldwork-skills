#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required but was not found."
    exit 1
fi

python3 -m pip install --upgrade pip
python3 -m pip install --user crawl4ai duckduckgo-search

user_bin="$(python3 -m site --user-base)/bin"
if command -v crawl4ai-setup >/dev/null 2>&1; then
    crawl4ai-setup
elif [[ -x "$user_bin/crawl4ai-setup" ]]; then
    "$user_bin/crawl4ai-setup"
else
    echo "crawl4ai-setup is not on PATH. Install complete for libraries; browser setup may require manual Playwright install."
fi

echo "Setup complete."
