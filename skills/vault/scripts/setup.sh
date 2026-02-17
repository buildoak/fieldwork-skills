#!/usr/bin/env bash
set -euo pipefail

# setup.sh -- One-command vault setup
# Creates an encrypted secrets vault using age + sops.
# Run once. Takes about 30 seconds.

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

info()    { printf "${BLUE}[info]${NC} %s\n" "$*"; }
success() { printf "${GREEN}[ok]${NC} %s\n" "$*"; }
warn()    { printf "${YELLOW}[warn]${NC} %s\n" "$*"; }
error()   { printf "${RED}[error]${NC} %s\n" "$*" >&2; }

# --- Configuration ---
# Customize this path. The default is intentionally misleading.
# Pick something that makes sense for your threat model.
VAULT_DIR="${VAULT_DIR:-$HOME/.shit}"

info "Vault will be created at: ${BOLD}$VAULT_DIR${NC}"
echo ""

# --- Step 1: Check/install dependencies ---
info "Checking dependencies..."

install_with_brew() {
    local pkg="$1"
    if command -v brew >/dev/null 2>&1; then
        info "Installing $pkg via Homebrew..."
        brew install "$pkg"
    else
        error "$pkg not found and Homebrew is not available."
        echo ""
        echo "Install manually:"
        echo "  age:  https://github.com/FiloSottile/age#installation"
        echo "  sops: https://github.com/getsops/sops#install"
        echo ""
        echo "Linux (apt):  sudo apt install age && sudo apt install sops"
        echo "Linux (snap): sudo snap install sops"
        echo "Go:           go install github.com/getsops/sops/v3/cmd/sops@latest"
        exit 1
    fi
}

if ! command -v age >/dev/null 2>&1; then
    warn "age not found."
    install_with_brew age
else
    success "age found: $(age --version 2>&1 | head -1)"
fi

if ! command -v sops >/dev/null 2>&1; then
    warn "sops not found."
    install_with_brew sops
else
    success "sops found: $(sops --version 2>&1 | head -1)"
fi

if ! command -v jq >/dev/null 2>&1; then
    warn "jq not found (needed for safe value encoding)."
    install_with_brew jq
else
    success "jq found: $(jq --version 2>&1 | head -1)"
fi

echo ""

# --- Step 2: Create vault directory ---
if [[ -d "$VAULT_DIR" ]]; then
    warn "Vault directory already exists at $VAULT_DIR"
    if [[ -f "$VAULT_DIR/vault.enc.yaml" ]]; then
        error "Vault already set up. Run 'vault.sh verify' to check it."
        exit 1
    fi
else
    info "Creating vault directory..."
    mkdir -p "$VAULT_DIR"
fi

chmod 700 "$VAULT_DIR"
success "Vault directory: $VAULT_DIR (permissions: 700)"

# --- Step 3: Generate age identity ---
IDENTITY_FILE="$VAULT_DIR/.age-identity"
if [[ -f "$IDENTITY_FILE" ]]; then
    warn "Age identity already exists. Keeping existing key."
else
    info "Generating age encryption key..."
    age-keygen -o "$IDENTITY_FILE" 2>/dev/null
fi

chmod 600 "$IDENTITY_FILE"
success "Age identity: $IDENTITY_FILE (permissions: 600)"

# Extract public key
PUBLIC_KEY=$(grep -o 'age1[a-z0-9]*' "$IDENTITY_FILE" | head -1)
if [[ -z "$PUBLIC_KEY" ]]; then
    error "Could not extract public key from identity file."
    exit 1
fi
success "Public key: $PUBLIC_KEY"

echo ""

# --- Step 4: Create .sops.yaml ---
SOPS_CONFIG="$VAULT_DIR/.sops.yaml"
info "Creating SOPS config..."

cat > "$SOPS_CONFIG" <<EOF
creation_rules:
  - age: >-
      $PUBLIC_KEY
EOF

success "SOPS config: $SOPS_CONFIG"

# --- Step 5: Create initial empty vault ---
VAULT_FILE="$VAULT_DIR/vault.enc.yaml"
info "Creating initial encrypted vault..."

# Create a minimal YAML with one placeholder, then remove it
# SOPS needs at least one key to encrypt
cd "$VAULT_DIR" && echo '_INIT: placeholder' | sops encrypt --input-type yaml --output-type yaml /dev/stdin > "$VAULT_FILE" 2>/dev/null

# Remove the placeholder
cd "$VAULT_DIR" && sops set "$VAULT_FILE" '["_INIT"]' 'null' 2>/dev/null && \
    sops decrypt "$VAULT_FILE" 2>/dev/null | grep -qv '_INIT' || true

success "Encrypted vault: $VAULT_FILE"

echo ""

# --- Step 6: Verify everything works ---
info "Verifying vault..."

# Test decrypt
if cd "$VAULT_DIR" && sops decrypt "$VAULT_FILE" >/dev/null 2>&1; then
    success "Vault decrypts successfully"
else
    error "Vault decrypt failed. Something went wrong."
    exit 1
fi

echo ""

# --- Step 7: Shell integration hint ---
printf "${GREEN}${BOLD}Setup complete!${NC}\n"
echo ""
echo "Your vault is ready at: $VAULT_DIR"
echo ""
echo "Next steps:"
echo ""
echo "  1. Add your first secret:"
echo "     ./scripts/vault.sh set MY_API_KEY \"sk-your-key-here\""
echo ""
echo "  2. Retrieve it:"
echo "     ./scripts/vault.sh get MY_API_KEY"
echo ""
echo "  3. (Optional) Add to your shell profile for global access:"
echo "     echo 'export SOPS_AGE_KEY_FILE=\"$IDENTITY_FILE\"' >> ~/.zshrc"
echo ""
echo "  4. Run the health check:"
echo "     ./scripts/vault.sh doctor"
echo ""
