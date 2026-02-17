#!/usr/bin/env bash
# Browser health check for browser-ops skill.
# Verifies agent-browser CLI is available, browser daemon status, and stealth config.
#
# Usage:
#   browser-check.sh              -- Full health check
#   browser-check.sh quick        -- Quick check (CLI available + daemon)
#   browser-check.sh stealth      -- Show current stealth configuration

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }

check_cli() {
    echo "=== agent-browser CLI ==="
    if command -v agent-browser &>/dev/null; then
        local version
        version=$(agent-browser --version 2>/dev/null || echo "unknown")
        ok "agent-browser found: $version"
    else
        fail "agent-browser not found on PATH"
        echo "  Install: npm install -g agent-browser"
        return 1
    fi
}

check_daemon() {
    echo ""
    echo "=== Browser Daemon ==="
    # Try to get current URL -- if it works, daemon is running
    local result
    result="$(agent-browser --session mcp --json get url 2>/dev/null || true)"
    if [[ -z "$result" ]] || [[ "$result" == *"error"* ]]; then
        warn "Browser daemon not currently running (starts on first navigate)"
    else
        ok "Browser daemon is running"
        echo "  Current URL: $result"
    fi
}

check_stealth() {
    echo ""
    echo "=== Stealth Configuration ==="

    if [[ "${AGENT_BROWSER_HEADED:-}" == "1" ]]; then
        ok "Headed mode: ON"
    else
        warn "Headed mode: OFF (headless -- more detectable)"
    fi

    if [[ -n "${AGENT_BROWSER_USER_AGENT:-}" ]]; then
        ok "Custom UA: ${AGENT_BROWSER_USER_AGENT:0:50}..."
    else
        warn "Custom UA: NOT SET (using default Playwright UA)"
    fi

    if [[ -n "${AGENT_BROWSER_PROFILE:-}" ]]; then
        if [[ -d "${AGENT_BROWSER_PROFILE}" ]]; then
            ok "Persistent profile: $AGENT_BROWSER_PROFILE"
        else
            warn "Profile path set but directory missing: $AGENT_BROWSER_PROFILE"
            echo "  Fix: mkdir -p $AGENT_BROWSER_PROFILE"
        fi
    else
        warn "Persistent profile: NOT SET (ephemeral sessions)"
    fi

    if [[ "${AGENT_BROWSER_ARGS:-}" == *"AutomationControlled"* ]]; then
        ok "Automation flag disabled: YES"
    else
        warn "Automation flag: NOT disabled (navigator.webdriver = true)"
    fi

    if [[ -n "${AGENT_BROWSER_PROXY:-}" ]]; then
        ok "Proxy configured: ${AGENT_BROWSER_PROXY:0:30}..."
    else
        echo "  Proxy: not configured (direct connection)"
    fi

    if [[ -n "${AGENT_BROWSER_PROVIDER:-}" ]]; then
        ok "Cloud provider: $AGENT_BROWSER_PROVIDER"
    else
        echo "  Cloud provider: none (local browser)"
    fi

    # Check rebrowser-patches
    if command -v npm >/dev/null 2>&1; then
        local ab_path
        ab_path="$(npm root -g 2>/dev/null)/agent-browser"
        if [[ -d "$ab_path" ]]; then
            if [[ -n "${REBROWSER_PATCHES_RUNTIME_FIX_MODE:-}" ]]; then
                ok "rebrowser-patches: configured"
            else
                local patched
                patched=$(grep -r "rebrowser" "$ab_path/node_modules/playwright-core/" 2>/dev/null | head -1 || true)
                if [[ -n "$patched" ]]; then
                    ok "rebrowser-patches: applied to playwright-core"
                else
                    warn "rebrowser-patches: NOT applied (CDP leak vulnerable)"
                    echo "  Fix: cd $ab_path && npx rebrowser-patches@latest patch"
                fi
            fi
        fi
    else
        warn "npm not found; skipping rebrowser-patches detection"
    fi
}

check_agentmail() {
    echo ""
    echo "=== AgentMail ==="
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local venv_dir="$script_dir/venv"
    local mailbox_script="$script_dir/mailbox.py"

    if [[ -f "$mailbox_script" ]]; then
        ok "mailbox.py: $mailbox_script"
    else
        fail "mailbox.py: missing (expected at $mailbox_script)"
    fi

    if [[ -f "$venv_dir/bin/activate" ]]; then
        ok "Python venv: $venv_dir"
    else
        warn "Python venv: missing — run ./scripts/agentmail.sh setup"
    fi

    if [[ -f "$script_dir/requirements.txt" ]]; then
        ok "requirements.txt: present"
    else
        warn "requirements.txt: missing"
    fi
}

case "${1:-full}" in
    quick)
        check_cli
        check_daemon
        ;;
    stealth)
        check_stealth
        ;;
    full|*)
        check_cli
        check_daemon
        check_stealth
        check_agentmail
        echo ""
        echo "=== Summary ==="
        echo "Run 'browser-check.sh stealth' for stealth config details"
        echo "Run 'browser-check.sh quick' for fast CLI check"
        ;;
esac
