#!/usr/bin/env bash
# AgentMail CLI wrapper for browser-ops skill.
# Creates disposable email inboxes, polls for incoming messages, extracts OTP codes.
#
# Self-contained: all dependencies live inside this skill directory.
#
# Prerequisites:
#   - API key from AGENTMAIL_API_KEY in environment or shell profile
#   - Run 'agentmail.sh setup' once to create venv and install dependencies
#
# Usage:
#   agentmail.sh setup                       -- Create venv and install dependencies
#   agentmail.sh create <username>           -- Create inbox: username@agentmail.to
#   agentmail.sh poll <email> [--timeout N]  -- Poll inbox for new messages (default: 120s)
#   agentmail.sh extract <inbox_id> <msg_id> -- Extract OTP/link from message
#   agentmail.sh status                      -- Check AgentMail availability

set -euo pipefail

# Resolve skill root (scripts/ is one level below skill root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

VENV_DIR="$SCRIPT_DIR/venv"
VENV_ACTIVATE="$VENV_DIR/bin/activate"
MAILBOX_SCRIPT="$SCRIPT_DIR/mailbox.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

usage() {
    cat <<'EOF'
AgentMail CLI for browser-ops

Commands:
  setup                          Create venv and install dependencies (run once)
  create <username>              Create inbox: username@agentmail.to
  poll <email> [--timeout N]     Poll for messages (default timeout: 120s)
  extract <inbox_id> <msg_id>    Extract OTP code or verification link
  status                         Check AgentMail availability

Examples:
  agentmail.sh setup
  agentmail.sh create browser-task-01
  agentmail.sh poll your-mailbox@agentmail.to --timeout 60
  agentmail.sh extract abc123 msg456
EOF
    exit 1
}

do_setup() {
    echo "Setting up AgentMail venv at $VENV_DIR ..."
    if ! command -v python3 >/dev/null 2>&1; then
        echo "ERROR: python3 is required but was not found on PATH"
        exit 1
    fi
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo "  Created venv"
    else
        echo "  Venv already exists"
    fi
    if [ ! -f "$VENV_ACTIVATE" ]; then
        echo "ERROR: venv activation script missing at $VENV_ACTIVATE"
        exit 1
    fi
    source "$VENV_ACTIVATE"
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r "$REQUIREMENTS"
    echo "  Dependencies installed"
    echo "Setup complete."
}

check_setup() {
    if [ ! -f "$MAILBOX_SCRIPT" ]; then
        echo "ERROR: mailbox.py not found at $MAILBOX_SCRIPT"
        exit 1
    fi
    if [ ! -f "$VENV_ACTIVATE" ]; then
        echo "ERROR: Python venv not found at $VENV_DIR/"
        echo "Run: $0 setup"
        exit 1
    fi
}

run_mailbox() {
    source "$VENV_ACTIVATE"
    python "$MAILBOX_SCRIPT" "$@"
}

case "${1:-}" in
    setup)
        do_setup
        ;;
    create)
        check_setup
        shift
        if [ $# -lt 1 ]; then
            echo "ERROR: Username required"
            echo "Usage: $0 create <username>"
            exit 1
        fi
        run_mailbox create --username "$1"
        ;;
    poll)
        check_setup
        shift
        if [ $# -lt 1 ]; then
            echo "ERROR: Inbox email required"
            echo "Usage: $0 poll <email> [--timeout N]"
            exit 1
        fi
        run_mailbox poll "$@"
        ;;
    extract)
        check_setup
        shift
        if [ $# -lt 2 ]; then
            echo "ERROR: inbox_id and msg_id are required"
            echo "Usage: $0 extract <inbox_id> <msg_id>"
            exit 1
        fi
        run_mailbox extract "$@"
        ;;
    status)
        check_setup
        echo "AgentMail skill dir: $SKILL_ROOT"
        echo "Mailbox script: $MAILBOX_SCRIPT"
        echo "Venv: $VENV_DIR"
        echo "Status: OK"
        ;;
    *)
        usage
        ;;
esac
