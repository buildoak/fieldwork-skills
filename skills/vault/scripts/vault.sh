#!/usr/bin/env bash
set -euo pipefail

# vault.sh -- Encrypted secrets vault using age + sops
# Secrets are encrypted at rest. Decrypted values never touch disk.
# All output goes to stdout (values) or stderr (messages).

# --- Configuration (override via env vars) ---
VAULT_DIR="${VAULT_DIR:-$HOME/.config/vault}"
VAULT_FILE="${VAULT_FILE:-$VAULT_DIR/vault.enc.yaml}"
SOPS_CONFIG="$VAULT_DIR/.sops.yaml"
export SOPS_AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$VAULT_DIR/.age-identity}"

# --- Colors (disabled if not a terminal) ---
if [[ -t 2 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    DIM='\033[2m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' DIM='' NC=''
fi

ok()    { printf "${GREEN}ok:${NC} %s\n" "$*" >&2; }
warn()  { printf "${YELLOW}warn:${NC} %s\n" "$*" >&2; }
err()   { printf "${RED}error:${NC} %s\n" "$*" >&2; }

# --- Key validation ---
validate_key() {
    local key="$1"
    if [[ ! "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
        err "Invalid key name '$key'"
        echo "  Keys must match pattern: [A-Za-z_][A-Za-z0-9_]*" >&2
        echo "  Examples: MY_API_KEY, DATABASE_URL, SECRET_TOKEN" >&2
        exit 1
    fi
}

# --- Help ---
usage() {
    cat <<'EOF'
vault.sh -- Encrypted secrets vault

Usage: vault.sh <command> [args]

Commands:
  get <KEY>           Get a single secret (outputs to stdout)
  set <KEY> <VALUE>   Add or update a secret
  list                Show all secret names (not values)
  source              Output export statements for all secrets (pipe to eval)
  exec <command...>   Run a command with all secrets as env vars
  verify              Check that the vault is accessible
  doctor              Comprehensive health check
  setup               Run first-time setup
  help                Show this help

EOF
}

help_get() {
    cat <<'EOF'
vault.sh get <KEY>

Decrypt and output a single secret value to stdout.
No trailing newline -- safe for variable assignment.

Examples:
  vault.sh get MY_API_KEY
  export TOKEN=$(vault.sh get MY_API_KEY)
  curl -H "Authorization: Bearer $(vault.sh get MY_API_KEY)" https://api.example.com
EOF
}

help_set() {
    cat <<'EOF'
vault.sh set <KEY> <VALUE>

Add or update a secret in the vault.
The operation is atomic -- no plaintext is written to disk.
Key names must be SCREAMING_SNAKE_CASE (letters, digits, underscores).

Examples:
  vault.sh set MY_API_KEY "sk-abc123"
  vault.sh set DATABASE_URL "postgres://user:pass@localhost/db"
EOF
}

help_exec() {
    cat <<'EOF'
vault.sh exec <command> [args...]

Run a command with all vault secrets injected as environment variables.
Secrets are scoped to the subprocess only -- they don't leak to your shell.

Examples:
  vault.sh exec env                     # See all injected vars
  vault.sh exec node server.js          # Start server with secrets
  vault.sh exec python manage.py migrate
EOF
}

help_doctor() {
    cat <<'EOF'
vault.sh doctor

Comprehensive health check. Verifies:
  - Required tools installed (age, sops, jq)
  - Vault directory exists with correct permissions
  - Age identity exists with correct permissions
  - SOPS config exists and references the right key
  - Vault file can be decrypted
  - Round-trip encryption test (set + get + delete)
EOF
}

# --- Preflight checks ---

check_deps() {
    local missing=0
    if ! command -v sops >/dev/null 2>&1; then
        err "sops not found. Install: brew install sops"
        missing=1
    fi
    if ! command -v age >/dev/null 2>&1; then
        err "age not found. Install: brew install age"
        missing=1
    fi
    if ! command -v jq >/dev/null 2>&1; then
        err "jq not found. Install: brew install jq"
        missing=1
    fi
    if [[ "$missing" -eq 1 ]]; then
        exit 1
    fi
}

check_vault() {
    check_deps

    if [[ ! -f "$SOPS_AGE_KEY_FILE" ]]; then
        err "Age identity not found at $SOPS_AGE_KEY_FILE"
        echo "  Run: vault.sh setup" >&2
        exit 1
    fi
    if [[ ! -f "$VAULT_FILE" ]]; then
        err "Encrypted vault not found at $VAULT_FILE"
        echo "  Run: vault.sh setup" >&2
        exit 1
    fi
    if [[ ! -f "$SOPS_CONFIG" ]]; then
        err "SOPS config not found at $SOPS_CONFIG"
        echo "  Run: vault.sh setup" >&2
        exit 1
    fi

    # Auto-fix permissions if too open
    local key_perms vault_perms
    key_perms=$(stat -f '%Lp' "$SOPS_AGE_KEY_FILE" 2>/dev/null || stat -c '%a' "$SOPS_AGE_KEY_FILE" 2>/dev/null)
    vault_perms=$(stat -f '%Lp' "$VAULT_DIR" 2>/dev/null || stat -c '%a' "$VAULT_DIR" 2>/dev/null)

    if [[ "$key_perms" != "600" ]]; then
        warn "Age identity has permissions $key_perms (expected 600). Fixing..."
        chmod 600 "$SOPS_AGE_KEY_FILE"
    fi
    if [[ "$vault_perms" != "700" ]]; then
        warn "Vault dir has permissions $vault_perms (expected 700). Fixing..."
        chmod 700 "$VAULT_DIR"
    fi
}

# --- Commands ---

cmd_get() {
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        help_get; return
    fi

    local key="${1:-}"
    if [[ -z "$key" ]]; then
        err "Missing key name"
        echo "  Usage: vault.sh get <KEY>" >&2
        exit 1
    fi
    validate_key "$key"
    check_vault

    local value
    value=$(cd "$VAULT_DIR" && sops decrypt --extract "[\"$key\"]" "$VAULT_FILE" 2>/dev/null) || {
        err "Key '$key' not found or decrypt failed"
        echo "  Available keys: $(cmd_list 2>/dev/null | tr '\n' ', ' | sed 's/,$//')" >&2
        exit 1
    }
    printf '%s' "$value"
}

cmd_set() {
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        help_set; return
    fi

    local key="${1:-}"
    local value="${2:-}"
    if [[ -z "$key" || -z "$value" ]]; then
        err "Missing key or value"
        echo "  Usage: vault.sh set <KEY> <VALUE>" >&2
        exit 1
    fi
    validate_key "$key"
    check_vault

    # JSON-encode the value to handle quotes, backslashes, special chars
    local json_value
    json_value=$(printf '%s' "$value" | jq -Rs .)

    cd "$VAULT_DIR" && sops set "$VAULT_FILE" "[\"$key\"]" "$json_value" 2>/dev/null || {
        err "Failed to set key '$key'"
        exit 1
    }
    ok "Set '$key'"
}

cmd_list() {
    check_vault

    cd "$VAULT_DIR" && sops decrypt "$VAULT_FILE" 2>/dev/null | \
        grep -E '^[A-Za-z_][A-Za-z0-9_]*:' | \
        cut -d: -f1
}

cmd_source() {
    check_vault

    # Safe export generation: fetch each value individually and shell-escape it.
    # Uses printf %q to prevent injection when piped to eval.
    local keys
    keys=$(cmd_list)

    while IFS= read -r key; do
        [[ -z "$key" ]] && continue
        local value
        value=$(cd "$VAULT_DIR" && sops decrypt --extract "[\"$key\"]" "$VAULT_FILE" 2>/dev/null) || continue
        printf 'export %s=%q\n' "$key" "$value"
    done <<< "$keys"
}

cmd_exec() {
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        help_exec; return
    fi

    if [[ $# -eq 0 ]]; then
        err "Missing command"
        echo "  Usage: vault.sh exec <command> [args...]" >&2
        exit 1
    fi
    check_vault

    # Build properly escaped command string preserving argument boundaries
    local escaped_cmd
    escaped_cmd=$(printf '%q ' "$@")

    cd "$VAULT_DIR" && sops exec-env "$VAULT_FILE" "$escaped_cmd"
}

cmd_verify() {
    check_vault

    local key_count
    key_count=$(cd "$VAULT_DIR" && sops decrypt "$VAULT_FILE" 2>/dev/null | grep -cE '^[A-Za-z_][A-Za-z0-9_]*:' || true)

    if [[ "$key_count" -gt 0 ]]; then
        ok "Vault accessible, $key_count secret(s) found"
    else
        ok "Vault accessible, empty (no secrets yet)"
    fi
}

cmd_doctor() {
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        help_doctor; return
    fi

    local issues=0
    printf "${BOLD}Vault Health Check${NC}\n" >&2
    echo "==================" >&2
    echo "" >&2

    # 1. Tools
    printf "${BOLD}Tools:${NC}\n" >&2
    for tool in age sops jq; do
        if command -v "$tool" >/dev/null 2>&1; then
            local ver
            ver=$("$tool" --version 2>&1 | head -1)
            printf "  ${GREEN}+${NC} %-6s %s\n" "$tool" "$ver" >&2
        else
            printf "  ${RED}x${NC} %-6s not installed\n" "$tool" >&2
            issues=$((issues + 1))
        fi
    done
    echo "" >&2

    # 2. Files & permissions
    printf "${BOLD}Files:${NC}\n" >&2

    if [[ -d "$VAULT_DIR" ]]; then
        local vault_perms
        vault_perms=$(stat -f '%Lp' "$VAULT_DIR" 2>/dev/null || stat -c '%a' "$VAULT_DIR" 2>/dev/null)
        if [[ "$vault_perms" == "700" ]]; then
            printf "  ${GREEN}+${NC} vault dir     %s (700)\n" "$VAULT_DIR" >&2
        else
            printf "  ${YELLOW}!${NC} vault dir     %s (%s, should be 700)\n" "$VAULT_DIR" "$vault_perms" >&2
            issues=$((issues + 1))
        fi
    else
        printf "  ${RED}x${NC} vault dir     %s (missing)\n" "$VAULT_DIR" >&2
        issues=$((issues + 1))
    fi

    if [[ -f "$SOPS_AGE_KEY_FILE" ]]; then
        local key_perms
        key_perms=$(stat -f '%Lp' "$SOPS_AGE_KEY_FILE" 2>/dev/null || stat -c '%a' "$SOPS_AGE_KEY_FILE" 2>/dev/null)
        if [[ "$key_perms" == "600" ]]; then
            printf "  ${GREEN}+${NC} age identity  %s (600)\n" "$SOPS_AGE_KEY_FILE" >&2
        else
            printf "  ${YELLOW}!${NC} age identity  %s (%s, should be 600)\n" "$SOPS_AGE_KEY_FILE" "$key_perms" >&2
            issues=$((issues + 1))
        fi
    else
        printf "  ${RED}x${NC} age identity  %s (missing)\n" "$SOPS_AGE_KEY_FILE" >&2
        issues=$((issues + 1))
    fi

    if [[ -f "$SOPS_CONFIG" ]]; then
        printf "  ${GREEN}+${NC} sops config   %s\n" "$SOPS_CONFIG" >&2
    else
        printf "  ${RED}x${NC} sops config   %s (missing)\n" "$SOPS_CONFIG" >&2
        issues=$((issues + 1))
    fi

    if [[ -f "$VAULT_FILE" ]]; then
        printf "  ${GREEN}+${NC} vault file    %s\n" "$VAULT_FILE" >&2
    else
        printf "  ${RED}x${NC} vault file    %s (missing)\n" "$VAULT_FILE" >&2
        issues=$((issues + 1))
    fi
    echo "" >&2

    # 3. Encryption test
    printf "${BOLD}Encryption:${NC}\n" >&2
    if [[ -f "$VAULT_FILE" ]] && [[ -f "$SOPS_AGE_KEY_FILE" ]]; then
        if cd "$VAULT_DIR" && sops decrypt "$VAULT_FILE" >/dev/null 2>&1; then
            local key_count
            key_count=$(cd "$VAULT_DIR" && sops decrypt "$VAULT_FILE" 2>/dev/null | grep -cE '^[A-Za-z_][A-Za-z0-9_]*:' || true)
            printf "  ${GREEN}+${NC} decrypt       works ($key_count secret(s))\n" >&2

            # Round-trip test
            local test_key="_VAULT_DOCTOR_TEST"
            local test_val="doctor-$(date +%s)"
            if cd "$VAULT_DIR" && sops set "$VAULT_FILE" "[\"$test_key\"]" "\"$test_val\"" 2>/dev/null; then
                local got_val
                got_val=$(cd "$VAULT_DIR" && sops decrypt --extract "[\"$test_key\"]" "$VAULT_FILE" 2>/dev/null) || true
                # Clean up test key by setting to null (sops doesn't have delete)
                cd "$VAULT_DIR" && sops set "$VAULT_FILE" "[\"$test_key\"]" 'null' 2>/dev/null || true
                if [[ "$got_val" == "$test_val" ]]; then
                    printf "  ${GREEN}+${NC} round-trip    set -> get -> cleanup passed\n" >&2
                else
                    printf "  ${RED}x${NC} round-trip    value mismatch (got: $got_val)\n" >&2
                    issues=$((issues + 1))
                fi
            else
                printf "  ${RED}x${NC} round-trip    set failed\n" >&2
                issues=$((issues + 1))
            fi
        else
            printf "  ${RED}x${NC} decrypt       failed\n" >&2
            issues=$((issues + 1))
        fi
    else
        printf "  ${DIM}-${NC} decrypt       skipped (missing files)\n" >&2
    fi
    echo "" >&2

    # 4. Summary
    if [[ "$issues" -eq 0 ]]; then
        printf "${GREEN}${BOLD}All checks passed.${NC}\n" >&2
    else
        printf "${YELLOW}${BOLD}$issues issue(s) found.${NC}\n" >&2
    fi

    return "$issues"
}

cmd_setup() {
    # Find setup.sh relative to this script
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$script_dir/setup.sh" ]]; then
        exec bash "$script_dir/setup.sh"
    else
        err "setup.sh not found in $script_dir"
        exit 1
    fi
}

# --- Dispatch ---

command="${1:-help}"
shift || true

case "$command" in
    get)    cmd_get "$@" ;;
    set)    cmd_set "$@" ;;
    list)   cmd_list ;;
    source) cmd_source ;;
    exec)   cmd_exec "$@" ;;
    verify) cmd_verify ;;
    doctor) cmd_doctor "$@" ;;
    setup)  cmd_setup ;;
    help|--help|-h) usage ;;
    *)
        err "Unknown command '$command'"
        echo "" >&2
        usage >&2
        exit 1
        ;;
esac
