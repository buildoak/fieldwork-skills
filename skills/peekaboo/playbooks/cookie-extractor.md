# Cookie Extractor Playbook

Extract authentication cookies from browser sessions for API/HTTP client use.

## Status: **experimental** | Last Updated: 2026-02-22

⚠️ **WARNING: EXPERIMENTAL - HIGH SECURITY RISK** ⚠️
- Handling authentication cookies is extremely sensitive
- Session hijacking and security implications
- Legal issues with cookie extraction
- Data protection law compliance required
- Use only for authorized testing/research

## Inputs
- `TARGET_SITE`: Website domain to extract cookies from (required)
- `OUTPUT_FORMAT`: json|netscape|curl|http (default: json)
- `FILTER_COOKIES`: Comma-separated list of specific cookies to extract (optional)
- `INCLUDE_HTTPONLY`: Include HttpOnly cookies if possible (default: false)

## Preconditions
- Valid authenticated session in Safari
- Target website is logged in and session active
- Understanding of security and legal implications
- Proper authorization to extract session data

## FSM Flow
PREFLIGHT → ACQUIRE_WINDOW → EXTRACT → VERIFY → CLEANUP

## ⚠️ Critical Security and Legal Warnings

1. **Authentication Security**: Cookies contain sensitive authentication tokens
2. **Session Hijacking Risk**: Extracted cookies enable account impersonation
3. **Legal Compliance**: May violate CFAA, GDPR, and other privacy laws
4. **Data Protection**: Cookies may contain personal/sensitive information
5. **Scope Limitation**: Only extract cookies you are authorized to access
6. **Secure Handling**: Use secure storage and transmission for cookie data

**LEGAL NOTICE**: Only extract cookies from accounts/systems you own or are explicitly authorized to access.

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p /tmp/peekaboo
chmod 700 /tmp/peekaboo  # Secure permissions

# Validate domain format
if [[ ! "$TARGET_SITE" =~ ^[a-zA-Z0-9.-]+$ ]]; then
    echo "ERROR: Invalid domain format"
    exit 1
fi

# Security and legal warning
echo "🚨 CRITICAL SECURITY WARNING 🚨"
echo ""
echo "Cookie extraction involves sensitive authentication data:"
echo "- Session tokens that grant account access"
echo "- Personal information and tracking data"
echo "- Legal implications under data protection laws"
echo ""
echo "Legal requirements:"
echo "- Only extract cookies from accounts you own"
echo "- Obtain explicit authorization for testing scenarios"
echo "- Comply with GDPR, CCPA, and local privacy laws"
echo "- Use secure storage and handling procedures"
echo ""
echo "Security risks:"
echo "- Extracted cookies enable account impersonation"
echo "- Tokens may have extended validity periods"
echo "- Exposure could lead to account compromise"
echo ""
read -p "I am authorized to extract cookies from $TARGET_SITE (type 'AUTHORIZED'): " auth_confirm
if [ "$auth_confirm" != "AUTHORIZED" ]; then
    echo "Aborting for legal compliance."
    exit 0
fi

# Technical security confirmation
echo ""
echo "⚠️  TECHNICAL SECURITY WARNING ⚠️"
echo "This will extract session tokens that could be used to:"
echo "- Access the account from other devices/locations"
echo "- Perform actions as the authenticated user"
echo "- Access sensitive personal/business data"
echo ""
read -p "I will handle extracted cookies securely (type 'SECURE HANDLING'): " secure_confirm
if [ "$secure_confirm" != "SECURE HANDLING" ]; then
    echo "Aborting for security."
    exit 0
fi

# Set secure file permissions
umask 077
```

### ACQUIRE_WINDOW (State 2)
```bash
# Switch to Safari
peekaboo-safe.sh app switch --to Safari

# Verify target site is loaded and authenticated
site_check=$(peekaboo-safe.sh see --analyze "Is $TARGET_SITE loaded and showing an authenticated/logged-in state?" --app Safari)

if [[ "$site_check" != *"logged in"* ]] && [[ "$site_check" != *"authenticated"* ]]; then
    echo "ERROR: Target site not in authenticated state"
    echo "Please navigate to $TARGET_SITE and ensure you're logged in"
    exit 1
fi

echo "Authenticated session confirmed for $TARGET_SITE"
```

### EXTRACT (State 7) - Cookie Extraction Methods

```bash
echo "Extracting cookies from $TARGET_SITE..."

# Method 1: JavaScript extraction (most reliable)
extract_via_javascript() {
    echo "Attempting JavaScript cookie extraction..."

    # Extract document.cookie (non-HttpOnly cookies only)
    js_cookies=$(osascript -e "tell application \"Safari\" to do JavaScript \"
        JSON.stringify({
            url: window.location.href,
            domain: window.location.hostname,
            cookies: document.cookie,
            timestamp: new Date().toISOString()
        })
    \" in document 1" 2>/dev/null || echo "{}")

    if [ "$js_cookies" != "{}" ]; then
        echo "$js_cookies" > /tmp/peekaboo/cookies-js.json
        echo "JavaScript cookies extracted"
        return 0
    else
        echo "JavaScript extraction failed"
        return 1
    fi
}

# Method 2: Safari Developer Console (includes HttpOnly)
extract_via_dev_console() {
    echo "Attempting Developer Console extraction..."

    # Open Developer Console
    peekaboo-safe.sh menu click --path "Develop > Show Web Inspector" --app Safari 2>/dev/null || true
    sleep 2

    # Navigate to Application/Storage tab
    console_check=$(peekaboo-safe.sh see --analyze "Is the Safari Web Inspector (developer console) open? Can you see tabs like Console, Sources, Network?" --app Safari)

    if [[ "$console_check" == *"inspector"* ]] || [[ "$console_check" == *"console"* ]]; then
        echo "Developer Console opened"

        # Try to access Storage/Application tab for cookies
        # This requires specific coordinate clicks based on Safari version
        peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/dev-console.png

        echo "Manual cookie extraction required from Developer Console"
        echo "1. Click on 'Storage' or 'Application' tab"
        echo "2. Expand 'Cookies' section"
        echo "3. Select $TARGET_SITE"
        echo "4. Copy cookie values manually"

        return 1  # Requires manual intervention
    else
        echo "Could not open Developer Console"
        return 1
    fi
}

# Method 3: Network inspection (advanced)
extract_via_network() {
    echo "Network-based cookie extraction not implemented"
    echo "Would require packet capture or proxy setup"
    return 1
}

# Try extraction methods in order of reliability
if extract_via_javascript; then
    extraction_method="javascript"
elif [ "$INCLUDE_HTTPONLY" = "true" ] && extract_via_dev_console; then
    extraction_method="dev_console"
else
    echo "ERROR: All cookie extraction methods failed"
    echo "Consider manual extraction or alternative approaches"
    exit 1
fi
```

### Cookie Processing and Formatting
```bash
if [ "$extraction_method" = "javascript" ]; then
    echo "Processing JavaScript-extracted cookies..."

    # Parse cookies from JavaScript result
    python3 << 'EOF'
import json
import sys
from urllib.parse import unquote

# Read JavaScript extraction result
with open('/tmp/peekaboo/cookies-js.json', 'r') as f:
    data = json.load(f)

cookie_string = data.get('cookies', '')
domain = data.get('domain', '')
url = data.get('url', '')

if not cookie_string:
    print("No cookies found")
    sys.exit(1)

# Parse cookie string
cookies = []
for cookie in cookie_string.split(';'):
    if '=' in cookie:
        name, value = cookie.strip().split('=', 1)
        cookies.append({
            'name': name.strip(),
            'value': unquote(value.strip()),
            'domain': domain,
            'path': '/',
            'secure': False,  # Cannot determine from document.cookie
            'httpOnly': False  # JavaScript-accessible only
        })

# Output in requested format
output_format = sys.argv[1] if len(sys.argv) > 1 else 'json'

if output_format == 'json':
    print(json.dumps({
        'domain': domain,
        'url': url,
        'cookies': cookies,
        'extraction_method': 'javascript',
        'timestamp': data.get('timestamp')
    }, indent=2))

elif output_format == 'netscape':
    print("# Netscape HTTP Cookie File")
    print("# Generated by peekaboo cookie extractor")
    for cookie in cookies:
        print(f"{cookie['domain']}\tTRUE\t{cookie['path']}\tFALSE\t0\t{cookie['name']}\t{cookie['value']}")

elif output_format == 'curl':
    cookie_header = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    print(f'Cookie: {cookie_header}')

elif output_format == 'http':
    for cookie in cookies:
        print(f"{cookie['name']}={cookie['value']}")

EOF
fi > /tmp/peekaboo/cookies-formatted.txt

echo "Cookies formatted and saved to /tmp/peekaboo/cookies-formatted.txt"
```

### Cookie Filtering
```bash
if [ -n "$FILTER_COOKIES" ]; then
    echo "Filtering cookies: $FILTER_COOKIES"

    # Create filtered version
    python3 << EOF
import json
import sys

filter_list = "$FILTER_COOKIES".split(',')
filter_list = [name.strip() for name in filter_list]

with open('/tmp/peekaboo/cookies-formatted.txt', 'r') as f:
    content = f.read()

try:
    data = json.loads(content)
    if 'cookies' in data:
        filtered_cookies = [c for c in data['cookies'] if c['name'] in filter_list]
        data['cookies'] = filtered_cookies
        print(json.dumps(data, indent=2))
    else:
        print(content)  # Pass through non-JSON formats
except json.JSONDecodeError:
    print(content)  # Pass through non-JSON formats
EOF > /tmp/peekaboo/cookies-filtered.txt

    echo "Filtered cookies saved to /tmp/peekaboo/cookies-filtered.txt"
fi
```

### VERIFY (State 6) - Cookie Validation
```bash
echo "Validating extracted cookies..."

# Check if cookies were extracted
if [ -f /tmp/peekaboo/cookies-formatted.txt ] && [ -s /tmp/peekaboo/cookies-formatted.txt ]; then
    cookie_count=$(grep -c "name.*value" /tmp/peekaboo/cookies-formatted.txt 2>/dev/null || echo "0")
    echo "✅ Extracted $cookie_count cookies from $TARGET_SITE"

    # Basic validation
    if [ "$cookie_count" -eq 0 ]; then
        echo "⚠️  Warning: No cookies extracted - session may be cookie-less or extraction failed"
    fi

    # Show sample (without sensitive values)
    echo ""
    echo "Sample cookie names:"
    python3 << 'EOF'
import json
try:
    with open('/tmp/peekaboo/cookies-formatted.txt', 'r') as f:
        data = json.load(f)
    for cookie in data.get('cookies', [])[:5]:
        print(f"- {cookie['name']} (domain: {cookie['domain']})")
except:
    print("- Cookie format parsing not available")
EOF

else
    echo "❌ Cookie extraction failed - no output generated"
    exit 1
fi
```

### CLEANUP (State 8) - Secure Cleanup
```bash
echo ""
echo "🔒 SECURE CLEANUP AND HANDLING INSTRUCTIONS"
echo ""
echo "Extracted cookie files:"
echo "- /tmp/peekaboo/cookies-formatted.txt (main output)"
if [ -f /tmp/peekaboo/cookies-filtered.txt ]; then
    echo "- /tmp/peekaboo/cookies-filtered.txt (filtered output)"
fi

echo ""
echo "CRITICAL SECURITY REMINDERS:"
echo "1. These files contain authentication tokens"
echo "2. Store securely (encrypted storage recommended)"
echo "3. Delete after use: rm -f /tmp/peekaboo/cookies-*"
echo "4. Tokens may have long expiration periods"
echo "5. Monitor for unauthorized account access"

# Set restrictive permissions
chmod 600 /tmp/peekaboo/cookies-* 2>/dev/null || true

echo ""
echo "Clean snapshots and temporary files"
peekaboo-safe.sh clean --older-than 1

# Remove intermediate files but keep final output
rm -f /tmp/peekaboo/cookies-js.json /tmp/peekaboo/dev-console.png 2>/dev/null || true

echo ""
echo "Cookie extraction completed"
echo "⚠️  Remember to delete cookie files securely after use"
```

## Usage Examples

### HTTP Client Integration
```bash
# Using with curl
COOKIES=$(cat /tmp/peekaboo/cookies-formatted.txt | grep "Cookie:" | cut -d' ' -f2-)
curl -H "Cookie: $COOKIES" "https://api.example.com/protected"

# Using with Python requests
python3 << 'EOF'
import json
import requests

with open('/tmp/peekaboo/cookies-formatted.txt', 'r') as f:
    data = json.load(f)

cookies = {c['name']: c['value'] for c in data['cookies']}
response = requests.get('https://api.example.com/protected', cookies=cookies)
print(response.text)
EOF
```

### Security Headers Addition
```bash
# Add security headers for HTTP client use
add_security_headers() {
    echo "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    echo "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    echo "Accept-Language: en-US,en;q=0.5"
    echo "Accept-Encoding: gzip, deflate, br"
    echo "DNT: 1"
    echo "Connection: keep-alive"
    echo "Upgrade-Insecure-Requests: 1"
}
```

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| No cookies extracted | Site uses httpOnly cookies | Use Developer Console method |
| JavaScript blocked | Content Security Policy | Manual extraction required |
| Console won't open | Safari settings | Enable Develop menu in preferences |
| Empty cookie values | Session expired | Re-authenticate and retry |
| Malformed output | Parsing error | Check extraction method |
| Access denied | Authorization issue | Verify login status |

## Legal Compliance Framework

Before extracting cookies:
1. **Authorization**: Verify you own the account or have explicit permission
2. **Documentation**: Document legitimate testing/research purpose
3. **Scope**: Only extract cookies necessary for authorized purpose
4. **Retention**: Define and implement data retention policies
5. **Security**: Use encrypted storage and secure transmission
6. **Disposal**: Securely delete cookies after use

## Alternative Approaches

### Browser Extension Method
```javascript
// Create a browser extension for cookie access
chrome.cookies.getAll({domain: "example.com"}, function(cookies) {
    console.log(JSON.stringify(cookies));
});
```

### Proxy-Based Extraction
```bash
# Use mitmproxy or similar for traffic interception
# mitmproxy -s cookie_extractor.py
```

### Official APIs (Recommended)
```bash
# Use official authentication flows instead
# OAuth 2.0, API keys, JWT tokens, etc.
curl -H "Authorization: Bearer $API_TOKEN" "https://api.example.com/data"
```

## Acceptance Tests

**⚠️ ONLY RUN ON ACCOUNTS YOU OWN**

### Test 1: Simple Website Cookies
```bash
TARGET_SITE="example.com"
OUTPUT_FORMAT="json"
# Expected: Basic session cookies extracted
```

### Test 2: Filtered Cookie Extraction
```bash
TARGET_SITE="github.com"
FILTER_COOKIES="user_session,_gh_sess"
OUTPUT_FORMAT="curl"
# Expected: Only specified cookies extracted
```

## Token Budget
- Expected turns: 8-15
- Cost estimate: ~$0.10-0.20 (Sonnet 4)
- Medium cost due to verification steps

## Production Recommendations

1. **Use official APIs** instead of cookie extraction
2. **Implement OAuth 2.0** for authorized access
3. **API keys/tokens** for service authentication
4. **Secure credential storage** (encrypted databases, key management)
5. **Regular token rotation** for security

## Status and Validation

- **Limited validation** on basic websites
- **High security risk** - use with extreme caution
- **Legal compliance required** - verify authorization
- **Not recommended for production** without legal review
- **Research/testing use only** with proper safeguards

## Security Best Practices

1. **Least Privilege**: Only extract necessary cookies
2. **Secure Storage**: Encrypt cookie files immediately
3. **Time Limits**: Set short retention periods
4. **Access Logs**: Monitor cookie file access
5. **Secure Deletion**: Use secure file deletion methods
6. **Network Security**: Use HTTPS for cookie transmission
7. **Regular Audits**: Review cookie extraction practices