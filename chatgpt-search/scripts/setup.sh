#!/bin/bash
# Setup script for chatgpt-search
# Builds the FTS5 index from conversations.json

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEFAULT_EXPORT=""
DEFAULT_DB="$HOME/.chatgpt-search/index.db"

echo "chatgpt-search setup"
echo "===================="

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install scikit-learn langdetect
echo ""

# Check that conversations.json exists
EXPORT_PATH="${1:-$DEFAULT_EXPORT}"
if [ -z "$EXPORT_PATH" ]; then
    echo "Error: You must provide a path to conversations.json"
    echo "Usage: ./scripts/setup.sh /path/to/conversations.json"
    exit 1
fi

if [ ! -f "$EXPORT_PATH" ]; then
    echo "Error: conversations.json not found at $EXPORT_PATH"
    echo "Usage: ./scripts/setup.sh /path/to/conversations.json"
    exit 1
fi

# Create DB directory
mkdir -p "$(dirname "$DEFAULT_DB")"

# Build index
echo "Building index from: $EXPORT_PATH"
echo "Database location: $DEFAULT_DB"
echo ""

PYTHONPATH="$REPO_DIR/src" python3 -m chatgpt_search.cli --rebuild --export "$EXPORT_PATH" --db "$DEFAULT_DB"

echo ""
echo "Setup complete. Usage:"
echo "  PYTHONPATH=$REPO_DIR/src python3 -m chatgpt_search.cli \"your query\""
echo "  PYTHONPATH=$REPO_DIR/src python3 -m chatgpt_search.cli \"query\" --lang ru"
echo ""
echo "Or add to your shell profile:"
echo "  alias chatgpt-search='PYTHONPATH=$REPO_DIR/src python3 -m chatgpt_search.cli'"
