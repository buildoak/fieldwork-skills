# Instagram Monitor Playbook

Monitor Instagram for new posts, stories, DMs (read-only surveillance).

## Status: **experimental** | Last Updated: 2026-02-22

⚠️ **WARNING: EXPERIMENTAL - EXTREMELY HIGH RISK** ⚠️
- Meta has the most sophisticated anti-bot detection
- Instagram automation violates Terms of Service
- Account suspension almost guaranteed
- Legal implications for monitoring
- Strongly recommend Instagram Graph API instead

## Inputs
- `TARGET_ACCOUNT`: Instagram username to monitor (required)
- `MONITOR_TYPE`: posts|stories|feed (default: posts)
- `CHECK_INTERVAL`: Minutes between checks (minimum: 60)
- `ALERT_THRESHOLD`: New posts before alert (default: 1)

## Preconditions
- Valid Instagram account (burner account recommended)
- Manual login session established
- UI-TARS server running
- Understanding of legal/privacy implications

## FSM Flow
PREFLIGHT → ACQUIRE_WINDOW → NAVIGATE → DISCOVER → MONITOR → EXTRACT → CLEANUP

## ⚠️ Critical Risk and Legal Warnings

1. **Terms of Service**: Instagram strictly prohibits automation
2. **Meta Detection**: Most advanced anti-bot systems in social media
3. **Account Suspension**: Almost certain with automation
4. **Legal Issues**: Monitoring may violate privacy laws
5. **Stalking Concerns**: Automated monitoring can be legally problematic
6. **Data Protection**: GDPR/privacy law compliance issues

**LEGAL NOTICE**: This playbook is for educational purposes only. Monitoring individuals without consent may violate privacy laws.

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p ./tmp/peekaboo

# Check UI-TARS server
if ! curl -sf http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then
    echo "ERROR: UI-TARS server required for Instagram's complex interface"
    exit 1
fi

# Validate target account
if [[ ! "$TARGET_ACCOUNT" =~ ^[a-zA-Z0-9_.]+$ ]]; then
    echo "ERROR: Invalid Instagram username format"
    exit 1
fi

# Legal and ethical warning
echo "🚨 CRITICAL LEGAL WARNING 🚨"
echo ""
echo "Instagram monitoring may violate:"
echo "- Instagram Terms of Service (guaranteed suspension)"
echo "- Privacy laws (GDPR, CCPA, local privacy acts)"
echo "- Anti-stalking regulations"
echo "- Harassment laws"
echo ""
echo "This could result in:"
echo "- Account termination"
echo "- Legal action from Meta"
echo "- Privacy law violations"
echo "- Criminal charges in some jurisdictions"
echo ""
echo "Legitimate alternatives:"
echo "- Instagram Graph API for business accounts"
echo "- Manual monitoring"
echo "- Social media management tools"
read -p "I understand the legal risks and still want to proceed (type 'LEGAL RISK ACCEPTED'): " confirm
if [ "$confirm" != "LEGAL RISK ACCEPTED" ]; then
    echo "Aborting for legal safety."
    exit 0
fi

# Technical risk warning
echo ""
echo "⚠️  TECHNICAL RISK WARNING ⚠️"
echo "Meta's anti-bot detection is extremely sophisticated:"
echo "- Device fingerprinting"
echo "- Behavioral analysis"
echo "- IP reputation tracking"
echo "- Account correlation"
echo "- Real-time ML detection"
echo ""
echo "Account suspension is almost guaranteed."
echo ""
read -p "I accept account suspension risk (type 'ACCOUNT RISK ACCEPTED'): " tech_confirm
if [ "$tech_confirm" != "ACCOUNT RISK ACCEPTED" ]; then
    echo "Aborting for account safety."
    exit 0
fi
```

### ACQUIRE_WINDOW (State 2)
```bash
# Launch Safari
peekaboo-safe.sh app launch Safari --wait-until-ready
peekaboo-safe.sh app switch --to Safari

# Check for existing Instagram session
session_check=$(peekaboo-safe.sh see --analyze "Is Instagram loaded and are we logged in?" --app Safari)
if [[ "$session_check" != *"logged in"* ]] && [[ "$session_check" != *"Instagram"* ]]; then
    echo "ERROR: No Instagram session detected. Please log in manually first."
    echo "Recommendation: Use a burner account, not your main account."
    exit 1
fi

echo "Instagram session detected (account likely to be suspended)"
```

### NAVIGATE (State 3)
```bash
# Navigate to target account
instagram_url="https://www.instagram.com/$TARGET_ACCOUNT"
echo "Navigating to: $instagram_url"

peekaboo-safe.sh open "$instagram_url" --app Safari --wait-until-ready
sleep 8  # Instagram has slow loading

# Check for account accessibility
access_check=$(peekaboo-safe.sh see --analyze "Is the Instagram profile accessible? Are there posts visible, or is it private/restricted?" --app Safari)

if [[ "$access_check" == *"private"* ]]; then
    echo "ERROR: Target account is private - monitoring not possible without following"
    exit 1
fi

if [[ "$access_check" == *"not found"* ]] || [[ "$access_check" == *"doesn't exist"* ]]; then
    echo "ERROR: Instagram account '$TARGET_ACCOUNT' not found"
    exit 1
fi

echo "Target account accessible: $TARGET_ACCOUNT"
```

### DISCOVER (State 4)
```bash
# Discover profile structure (likely to trigger detection)
result=$(peekaboo-safe.sh see --app Safari --json --annotate --path ./tmp/peekaboo/)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id')

# Take screenshot for reference
peekaboo-safe.sh image --mode screen --path ./tmp/peekaboo/instagram-profile.png

# Check for posts
posts_check=$(peekaboo-safe.sh see --analyze "Are there Instagram posts visible? Can you see images in a grid layout?" --app Safari)
if [[ "$posts_check" != *"posts"* ]] && [[ "$posts_check" != *"images"* ]]; then
    echo "WARNING: No posts detected - account may be empty or detection triggered"
fi
```

### MONITOR (State 5) - High Detection Risk
```bash
echo "⚠️  Starting monitoring (detection imminent)..."

case "$MONITOR_TYPE" in
    "posts")
        monitor_posts
        ;;
    "stories")
        monitor_stories  # Extremely high risk
        ;;
    "feed")
        monitor_feed     # Extremely high risk
        ;;
    *)
        echo "ERROR: Unknown monitor type: $MONITOR_TYPE"
        exit 1
        ;;
esac
```

#### Posts Monitoring Function
```bash
monitor_posts() {
    echo "Monitoring posts for $TARGET_ACCOUNT..."

    # Get baseline post count/content
    baseline=$(peekaboo-safe.sh see --analyze "How many posts are visible in the grid? Describe the most recent post." --app Safari)
    echo "Baseline: $baseline" > ./tmp/peekaboo/baseline.txt

    # Single check (continuous monitoring guaranteed suspension)
    echo "WARNING: Continuous monitoring not implemented due to guaranteed detection"
    echo "Performing single content check only..."

    current_posts=$(peekaboo-safe.sh see --analyze "List the visible posts with descriptions. Note any new content since last check." --app Safari)
    echo "Current posts: $current_posts" >> ./tmp/peekaboo/posts-snapshot.txt

    echo "Single check completed - stopping to avoid detection"
}
```

#### Stories Monitoring Function
```bash
monitor_stories() {
    echo "⚠️  EXTREMELY HIGH RISK: Story monitoring"
    echo "Stories monitoring requires clicking story bubbles - guaranteed detection"

    # Look for story indicators
    story_check=$(peekaboo-safe.sh see --analyze "Are there story bubbles visible at the top of the profile?" --app Safari)

    if [[ "$story_check" == *"story"* ]]; then
        echo "Stories detected but not accessing due to detection risk"
        echo "Clicking story bubbles triggers immediate bot detection"
    else
        echo "No active stories detected for $TARGET_ACCOUNT"
    fi
}
```

#### Feed Monitoring Function
```bash
monitor_feed() {
    echo "⚠️  EXTREMELY HIGH RISK: Feed monitoring"
    echo "Feed monitoring requires navigation and scrolling - guaranteed detection"

    # Navigate to home feed (triggers detection)
    peekaboo-safe.sh open "https://www.instagram.com" --app Safari --wait-until-ready
    sleep 5

    echo "Feed monitoring not implemented - detection risk too high"
    echo "Manual feed checking recommended"
}
```

### EXTRACT (State 7)
```bash
# Take final screenshot
peekaboo-safe.sh image --mode screen --path ./tmp/peekaboo/instagram-final.png

# Extract visible content via analysis
extracted_content=$(peekaboo-safe.sh see --analyze "Extract all visible information from this Instagram profile: follower count, post count, bio, recent posts." --app Safari)

echo "=== INSTAGRAM MONITORING RESULTS ===" > ./tmp/peekaboo/instagram-extract.txt
echo "Target: @$TARGET_ACCOUNT" >> ./tmp/peekaboo/instagram-extract.txt
echo "Monitor Type: $MONITOR_TYPE" >> ./tmp/peekaboo/instagram-extract.txt
echo "Timestamp: $(date)" >> ./tmp/peekaboo/instagram-extract.txt
echo "" >> ./tmp/peekaboo/instagram-extract.txt
echo "$extracted_content" >> ./tmp/peekaboo/instagram-extract.txt
echo "====================================" >> ./tmp/peekaboo/instagram-extract.txt

echo "Content extracted - saved to ./tmp/peekaboo/instagram-extract.txt"
```

### Detection Check
```bash
# Check for immediate suspension indicators
suspension_check=$(peekaboo-safe.sh see --analyze "Are there any account warnings, restrictions, or unusual interface elements?" --app Safari)

if [[ "$suspension_check" == *"warning"* ]] || [[ "$suspension_check" == *"restricted"* ]] || [[ "$suspension_check" == *"suspended"* ]]; then
    echo "🚨 ACCOUNT ACTION DETECTED: $suspension_check"
    peekaboo-safe.sh image --mode screen --path ./tmp/peekaboo/instagram-suspended.png
    echo "Account likely suspended/restricted due to automation detection"
fi
```

### CLEANUP (State 8)
```bash
# Clean snapshots
peekaboo-safe.sh clean --older-than 1

# Keep evidence of what was extracted
echo "Monitoring session completed"
echo "Check ./tmp/peekaboo/instagram-extract.txt for results"
echo "Account suspension likely within 24 hours"
```

## Detection Indicators

Instagram will likely detect automation through:
- Unusual navigation patterns
- Rapid page loads
- Consistent timing intervals
- Missing touch/swipe gestures
- Browser automation signatures
- Device/IP correlation

## Failure Modes

| Symptom | Cause | Action |
|---------|--------|--------|
| Account suspended | Automation detected (expected) | Accept suspension |
| CAPTCHA appears | Bot detection triggered | Complete manually or abort |
| Profile not accessible | Account blocked/private | Find alternative approach |
| Interface changes | A/B testing or counter-measures | Stop immediately |
| Login required | Session expired | Re-login (risky) |
| Rate limited | Too many requests | Stop for 24+ hours |

## Legal Compliance Framework

Before any monitoring:
1. **Consent**: Obtain explicit consent from target
2. **Purpose**: Document legitimate purpose
3. **Legal Review**: Consult privacy lawyer
4. **Data Handling**: Implement privacy controls
5. **Retention**: Define data retention policies
6. **Disclosure**: Inform about monitoring if required by law

## Legitimate Alternatives

### Instagram Graph API (Recommended)
```bash
# For business/creator accounts
curl -G "https://graph.instagram.com/v12.0/me/media" \
  -d "fields=id,caption,media_type,media_url,timestamp" \
  -d "access_token=$INSTAGRAM_ACCESS_TOKEN"
```

### Third-Party Analytics Tools
- Hootsuite
- Sprout Social
- Buffer
- Later
- Creator Studio

### Manual Monitoring
- Instagram mobile app
- Browser bookmarks
- Notification settings
- Instagram's native tools

## Acceptance Tests

**DO NOT RUN THESE TESTS ON ANY ACCOUNT YOU VALUE**

### Test 1: Profile Check (Burner Account Only)
```bash
TARGET_ACCOUNT="public_test_account"
MONITOR_TYPE="posts"
# Expected: Immediate suspension of monitoring account
```

## Token Budget
- Expected turns: 10-20 (before suspension)
- Cost estimate: ~$0.15-0.30 (Sonnet 4)
- One-time cost as account will be suspended

## Final Recommendation

**ABSOLUTELY DO NOT USE THIS PLAYBOOK**

This playbook exists only to:
1. Document the technical impossibility
2. Highlight legal risks
3. Redirect to legitimate alternatives
4. Educate about privacy implications

**Use legitimate alternatives instead**:
1. Instagram Graph API for business needs
2. Manual monitoring for personal use
3. Social media management tools for marketing
4. Native Instagram features for notifications

Any attempt to automate Instagram monitoring will result in account suspension and potential legal consequences.
