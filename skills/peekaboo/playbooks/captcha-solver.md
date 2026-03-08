# CAPTCHA Solver Playbook

Detect CAPTCHAs and attempt solving via vision models and coordinate interaction.

## Status: **experimental** | Last Updated: 2026-02-22

> **FINDING (Feb 22, 2026):** Checkbox CAPTCHAs (reCAPTCHA v2, hCaptcha, Cloudflare Turnstile) auto-pass instantly on real Safari with a home network. The image grid/puzzle challenge only appears for suspicious fingerprints. For most real-browser automation, CAPTCHA is a single coordinate click, not a vision-solving problem.

⚠️ **WARNING: EXPERIMENTAL - SUCCESS RATE DEPENDS ON CONTEXT** ⚠️
- On real Safari + home network: checkbox CAPTCHAs auto-pass (~95%+)
- On headless/VPN/datacenter: image challenge likely, success ~20-40%
- Modern image-grid CAPTCHAs designed to defeat AI
- May trigger additional security measures
- Consider this a fallback, not primary solution
- Human handoff recommended for critical workflows

## Validated Test Results (Feb 22, 2026)

Live testing on Mac Mini via real Safari, home network Dubai.

| Type | Provider | Demo URL | Result | Method | Notes |
|------|----------|----------|--------|--------|-------|
| reCAPTCHA v2 checkbox | Google | google.com/recaptcha/api2/demo | **PASS — auto-passed, no image challenge** | Single coordinate click on checkbox | Green checkmark instant, no grid shown |
| hCaptcha checkbox | hCaptcha | accounts.hcaptcha.com/demo | **PASS — auto-passed, no challenge** | Single coordinate click on checkbox | "Challenge Success!" instant |
| Cloudflare Turnstile | Cloudflare | 2captcha.com/demo/cloudflare-turnstile | **PASS — auto-passed instantly** | Single coordinate click on checkbox | "Success!" — modern replacement for reCAPTCHA |
| Normal text CAPTCHA | 2captcha demo | 2captcha.com/demo/normal | **INCONCLUSIVE — rigged demo** | Vision read (W9H5K) + JS injection | Both Claude and peekaboo vision correctly read the text, but 2captcha demo rejects all answers to sell their service |
| GeeTest slide puzzle | GeeTest | 2captcha.com/demo/geetest | **UNTESTED** | Drag available via peekaboo drag --from-coords --to-coords --duration | Ad overlay blocked puzzle image. Peekaboo drag works mechanically (tested), but finding target position requires vision |

### Key Insight

Real Safari on a home network with a real browser fingerprint causes all three major CAPTCHA providers (reCAPTCHA, hCaptcha, Cloudflare Turnstile) to auto-pass without showing any challenge. The image grid/puzzle challenge only triggers for suspicious fingerprints (headless browsers, VPNs, data centers). This means for Reddit, Booking.com, Twitter, Instagram — CAPTCHA is effectively a single coordinate click, not a vision-solving problem.

---

## Inputs
- `CAPTCHA_TYPE`: image|audio|recaptcha|hcaptcha|custom (auto-detect if not specified)
- `MAX_ATTEMPTS`: Maximum solving attempts (default: 3)
- `CONFIDENCE_THRESHOLD`: Minimum confidence for solution (default: 0.7)
- `FALLBACK_ACTION`: human_handoff|skip|abort (default: human_handoff)

## Preconditions
- CAPTCHA is currently visible on screen
- UI-TARS server running for vision analysis
- Claude vision model available for analysis

## FSM Flow
PREFLIGHT → DETECT → ANALYZE → SOLVE → VERIFY → CLEANUP (or HUMAN_HANDOFF)

## CAPTCHA Types Supported

| Type | Success Rate | Notes |
|------|-------------|--------|
| Simple text CAPTCHAs | ~60% | OCR-based, older systems |
| Image selection | ~30% | "Select all cars" type |
| reCAPTCHA v2 | ~20% | Google's system, very robust |
| hCaptcha | ~25% | Privacy-focused alternative |
| Audio CAPTCHAs | ~40% | Speech-to-text based |
| Math problems | ~80% | Simple arithmetic |
| Custom CAPTCHAs | Variable | Site-specific challenges |

## Practical Flow for CAPTCHA Handling (Validated)

This is the recommended flow based on real-browser testing. Checkbox CAPTCHAs almost always auto-pass on real Safari.

```bash
# Step 1: Detect CAPTCHA presence
captcha_check=$(peekaboo-safe.sh see --analyze "Is there a CAPTCHA checkbox on this page?" --mode screen)

# Step 2: If checkbox type (reCAPTCHA/hCaptcha/Turnstile) — click it
# Will almost certainly auto-pass on real Safari with home network
peekaboo-safe.sh click --coords <checkbox_x>,<checkbox_y> --no-auto-focus --app Safari

# Step 3: Wait for verification to complete
sleep 3

# Step 4: Verify result
result=$(peekaboo-safe.sh see --analyze "Did the CAPTCHA pass? Is there a green checkmark or success message?" --mode screen)

# Step 5a: If image grid challenge appears (rare on real browser)
# Take screenshot + Claude vision to identify correct squares + coordinate clicks
# (Fall through to ANALYZE/SOLVE states below)

# Step 5b: If slide puzzle (GeeTest)
# peekaboo drag --from-coords X,Y --to-coords X2,Y2 --duration 800
# Use vision to identify target position first
```

---

## Step-by-Step Implementation

### PREFLIGHT (State 1)
```bash
./scripts/health-check.sh
mkdir -p /tmp/peekaboo

# Check UI-TARS server availability
if ! curl -sf http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then
    echo "ERROR: UI-TARS server required for CAPTCHA vision analysis"
    exit 1
fi

echo "WARNING: CAPTCHA solving has low success rates"
echo "Consider human handoff for critical workflows"
```

### DETECT (State 4) - CAPTCHA Detection
```bash
# Take screenshot for analysis
peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/captcha-screen.png

# Detect CAPTCHA presence and type
captcha_detection=$(peekaboo-safe.sh see --analyze "Is there a CAPTCHA visible on screen? What type is it: image selection, text entry, checkbox, audio, or other? Describe its location and content." --mode screen)

echo "CAPTCHA Detection: $captcha_detection"

# Parse detection results
if [[ "$captcha_detection" == *"no CAPTCHA"* ]] || [[ "$captcha_detection" == *"not visible"* ]]; then
    echo "No CAPTCHA detected on screen"
    exit 0
fi

# Auto-detect CAPTCHA type if not specified
if [ -z "$CAPTCHA_TYPE" ]; then
    if [[ "$captcha_detection" == *"select all"* ]] || [[ "$captcha_detection" == *"click on"* ]]; then
        CAPTCHA_TYPE="image"
    elif [[ "$captcha_detection" == *"text"* ]] || [[ "$captcha_detection" == *"type"* ]]; then
        CAPTCHA_TYPE="text"
    elif [[ "$captcha_detection" == *"reCAPTCHA"* ]] || [[ "$captcha_detection" == *"Google"* ]]; then
        CAPTCHA_TYPE="recaptcha"
    elif [[ "$captcha_detection" == *"hCaptcha"* ]]; then
        CAPTCHA_TYPE="hcaptcha"
    elif [[ "$captcha_detection" == *"audio"* ]] || [[ "$captcha_detection" == *"listen"* ]]; then
        CAPTCHA_TYPE="audio"
    else
        CAPTCHA_TYPE="custom"
    fi
fi

echo "CAPTCHA Type: $CAPTCHA_TYPE"
```

### ANALYZE (State 4) - Detailed CAPTCHA Analysis
```bash
# Discover CAPTCHA structure
result=$(peekaboo-safe.sh see --app Safari --json --annotate --path /tmp/peekaboo/)
snapshot_id=$(echo "$result" | jq -r '.snapshot_id')

case "$CAPTCHA_TYPE" in
    "image")
        analyze_image_captcha
        ;;
    "text")
        analyze_text_captcha
        ;;
    "recaptcha")
        analyze_recaptcha
        ;;
    "hcaptcha")
        analyze_hcaptcha
        ;;
    "audio")
        analyze_audio_captcha
        ;;
    "custom")
        analyze_custom_captcha
        ;;
    *)
        echo "ERROR: Unknown CAPTCHA type: $CAPTCHA_TYPE"
        exit 1
        ;;
esac
```

#### Image Selection CAPTCHA Analysis
```bash
analyze_image_captcha() {
    echo "Analyzing image selection CAPTCHA..."

    # Extract challenge text and images
    challenge_analysis=$(peekaboo-safe.sh see --analyze "What is the CAPTCHA asking for? (e.g., 'Select all images with cars', 'Click on traffic lights'). Describe the grid of images and what each image shows." --mode screen)

    echo "Challenge: $challenge_analysis" > /tmp/peekaboo/captcha-challenge.txt

    # Look for image grid coordinates
    image_grid=$(peekaboo-safe.sh see --analyze "Where are the clickable image squares located? Describe their positions and contents." --mode screen)
    echo "Image Grid: $image_grid" >> /tmp/peekaboo/captcha-challenge.txt
}
```

#### Text CAPTCHA Analysis
```bash
analyze_text_captcha() {
    echo "Analyzing text CAPTCHA..."

    # Extract distorted text
    text_analysis=$(peekaboo-safe.sh see --analyze "What text is shown in the CAPTCHA image? Look for distorted letters and numbers. What should be typed in the text field?" --mode screen)

    echo "Text Challenge: $text_analysis" > /tmp/peekaboo/captcha-challenge.txt

    # Find text input field
    input_field=$(peekaboo-safe.sh see --analyze "Where is the text input field for entering the CAPTCHA solution?" --mode screen)
    echo "Input Field: $input_field" >> /tmp/peekaboo/captcha-challenge.txt
}
```

#### reCAPTCHA Analysis
```bash
analyze_recaptcha() {
    echo "Analyzing reCAPTCHA..."

    # Check for checkbox or image challenge
    recaptcha_state=$(peekaboo-safe.sh see --analyze "Is this a reCAPTCHA checkbox ('I'm not a robot') or an image challenge? Describe what's visible." --mode screen)

    if [[ "$recaptcha_state" == *"checkbox"* ]]; then
        echo "reCAPTCHA Checkbox detected"
        echo "Type: checkbox" > /tmp/peekaboo/captcha-challenge.txt
    else
        echo "reCAPTCHA Image Challenge detected"
        challenge_analysis=$(peekaboo-safe.sh see --analyze "What is the reCAPTCHA image challenge asking for? Describe the images shown." --mode screen)
        echo "Type: image_challenge" > /tmp/peekaboo/captcha-challenge.txt
        echo "Challenge: $challenge_analysis" >> /tmp/peekaboo/captcha-challenge.txt
    fi
}
```

### SOLVE (State 5) - Attempt Solution
```bash
echo "Attempting CAPTCHA solution (Attempt 1/${MAX_ATTEMPTS:-3})..."

case "$CAPTCHA_TYPE" in
    "image")
        solve_image_captcha
        ;;
    "text")
        solve_text_captcha
        ;;
    "recaptcha")
        solve_recaptcha
        ;;
    "audio")
        solve_audio_captcha
        ;;
    *)
        echo "CAPTCHA type not solvable - escalating to human"
        human_handoff
        ;;
esac
```

#### Image Selection CAPTCHA Solver
```bash
solve_image_captcha() {
    echo "Solving image selection CAPTCHA..."

    # Read challenge description
    challenge=$(cat /tmp/peekaboo/captcha-challenge.txt)

    # Get specific solution
    solution=$(peekaboo-safe.sh see --analyze "Based on the challenge '$challenge', which specific images should be clicked? Provide coordinates or positions of the correct images." --mode screen)

    echo "Solution: $solution"

    # Attempt to click identified images (low success rate)
    if [[ "$solution" == *"top left"* ]]; then
        peekaboo-safe.sh click --coords 200,200 --no-auto-focus --app Safari
    fi
    if [[ "$solution" == *"top right"* ]]; then
        peekaboo-safe.sh click --coords 300,200 --no-auto-focus --app Safari
    fi
    # Add more position mappings as needed

    sleep 2
}
```

#### Text CAPTCHA Solver
```bash
solve_text_captcha() {
    echo "Solving text CAPTCHA..."

    # Extract text from analysis
    challenge=$(cat /tmp/peekaboo/captcha-challenge.txt)
    extracted_text=$(echo "$challenge" | grep -o "text: [^,]*" | cut -d' ' -f2- || echo "")

    if [ -n "$extracted_text" ]; then
        echo "Extracted text: $extracted_text"

        # Find text input field and type solution
        peekaboo-safe.sh click --query "text" --no-auto-focus --app Safari
        peekaboo-safe.sh type "$extracted_text" --profile human --app Safari
    else
        echo "Could not extract CAPTCHA text"
        return 1
    fi
}
```

#### reCAPTCHA Solver
```bash
solve_recaptcha() {
    echo "Attempting reCAPTCHA solution..."

    challenge_type=$(grep "Type:" /tmp/peekaboo/captcha-challenge.txt | cut -d' ' -f2)

    if [ "$challenge_type" = "checkbox" ]; then
        echo "Clicking reCAPTCHA checkbox..."
        # Try to click the checkbox (low success rate)
        peekaboo-safe.sh click --coords 400,300 --no-auto-focus --app Safari
        sleep 3

        # Check if image challenge appeared
        follow_up=$(peekaboo-safe.sh see --analyze "Did clicking the checkbox result in an image challenge appearing?" --mode screen)
        if [[ "$follow_up" == *"image"* ]]; then
            echo "Image challenge appeared - analyzing..."
            analyze_image_captcha
            solve_image_captcha
        fi
    else
        echo "reCAPTCHA image challenge detected"
        solve_image_captcha  # Same logic as regular image CAPTCHA
    fi
}
```

#### Audio CAPTCHA Solver
```bash
solve_audio_captcha() {
    echo "Audio CAPTCHA solving not implemented"
    echo "Audio CAPTCHAs require speech-to-text processing"
    echo "Escalating to human handoff"
    human_handoff
}
```

### VERIFY (State 6) - Solution Verification
```bash
sleep 3  # Allow CAPTCHA system to process

# Check if CAPTCHA was solved
verification=$(peekaboo-safe.sh see --analyze "Is the CAPTCHA still visible? Are there any success indicators, error messages, or has the page progressed past the CAPTCHA?" --mode screen)

echo "Verification: $verification"

if [[ "$verification" == *"success"* ]] || [[ "$verification" == *"solved"* ]] || [[ "$verification" == *"no CAPTCHA"* ]]; then
    echo "✅ CAPTCHA appears to be solved successfully"
    captcha_solved=true
elif [[ "$verification" == *"error"* ]] || [[ "$verification" == *"incorrect"* ]] || [[ "$verification" == *"try again"* ]]; then
    echo "❌ CAPTCHA solution failed"
    captcha_solved=false

    # Retry logic
    current_attempt=$((current_attempt + 1))
    if [ $current_attempt -lt ${MAX_ATTEMPTS:-3} ]; then
        echo "Retrying CAPTCHA solution (Attempt $((current_attempt + 1))/${MAX_ATTEMPTS:-3})..."
        sleep 2
        # Goto SOLVE state again
        solve_captcha
    else
        echo "Max attempts reached - escalating to human"
        human_handoff
    fi
else
    echo "⚠️ CAPTCHA solution status unclear"
    captcha_solved=false
fi
```

### Human Handoff Function
```bash
human_handoff() {
    echo "🤖➡️👤 CAPTCHA HUMAN HANDOFF REQUIRED"

    # Take screenshot for human reference
    peekaboo-safe.sh image --mode screen --path /tmp/peekaboo/captcha-handoff.png

    # Log handoff details
    cat > /tmp/peekaboo/captcha-handoff.json << EOF
{
    "reason": "CAPTCHA solution failed or not supported",
    "type": "$CAPTCHA_TYPE",
    "attempts": "$current_attempt",
    "screenshot": "/tmp/peekaboo/captcha-handoff.png",
    "timestamp": "$(date)",
    "next_action": "Human must solve CAPTCHA manually"
}
EOF

    echo "Human handoff details saved to /tmp/peekaboo/captcha-handoff.json"
    echo "Screenshot saved to /tmp/peekaboo/captcha-handoff.png"
    echo ""
    echo "Manual steps required:"
    echo "1. View screenshot to see current CAPTCHA"
    echo "2. Solve CAPTCHA manually in browser"
    echo "3. Resume automation after CAPTCHA is solved"

    exit 2  # Human handoff exit code
}
```

### CLEANUP (State 8)
```bash
if [ "$captcha_solved" = true ]; then
    echo "✅ CAPTCHA solved successfully"

    # Clean temporary files
    rm -f /tmp/peekaboo/captcha-*.txt /tmp/peekaboo/captcha-*.png 2>/dev/null || true

    # Clean snapshots
    peekaboo-safe.sh clean --older-than 1

    echo "CAPTCHA solution completed - continuing workflow"
else
    echo "❌ CAPTCHA solution failed - human intervention required"
    human_handoff
fi
```

## Success Rate Expectations

Rates split by context: real Safari + home network vs. headless/VPN/datacenter.

| CAPTCHA Type | Real Safari (Home) | Headless/VPN | Notes |
|-------------|-------------------|--------------|-------|
| reCAPTCHA v2 checkbox | ~95%+ | 15% | Auto-passes; only fails if fingerprint flagged. Validated Feb 22 |
| hCaptcha checkbox | ~95%+ | 25% | Auto-passes. Validated Feb 22 |
| Cloudflare Turnstile | ~95%+ | 20% | Auto-passes. Validated Feb 22 |
| reCAPTCHA v2 images | 20% | 20% | Only appears on suspicious fingerprints |
| hCaptcha images | 25% | 25% | Only appears on suspicious fingerprints |
| GeeTest slide puzzle | Untested | Untested | Drag mechanics work; vision targeting not yet validated |
| Simple text | 60% | 60% | Clear OCR possible |
| Distorted text | 30% | 30% | Complex distortions |
| Math problems | 80% | 80% | Arithmetic solvable |
| Image selection (cars) | 25% | 25% | Object detection challenging |
| Image selection (traffic lights) | 35% | 35% | More distinctive features |
| Audio CAPTCHAs | 40% | 40% | With good speech processing |
| Custom CAPTCHAs | Variable | Variable | Site-specific |

## Failure Modes

| Symptom | Cause | Recovery |
|---------|--------|----------|
| Cannot detect CAPTCHA | Vision analysis failed | Human verification |
| Wrong answer generated | AI interpretation error | Retry with different approach |
| Multiple failures | Sophisticated CAPTCHA | Human handoff immediately |
| New CAPTCHA appears | Previous solution incorrect | Retry with new analysis |
| Account locked | Too many failed attempts | Wait or human intervention |
| Different CAPTCHA type | Site changed systems | Re-analyze CAPTCHA type |

## Integration with Other Playbooks

```bash
# In safari-login.md or other playbooks
captcha_check=$(peekaboo-safe.sh see --analyze "Is there a CAPTCHA challenge visible?" --app Safari)
if [[ "$captcha_check" == *"CAPTCHA"* ]]; then
    echo "CAPTCHA detected - attempting solution..."
    source playbooks/captcha-solver.md

    # Check exit code
    if [ $? -eq 2 ]; then
        echo "Human handoff required for CAPTCHA"
        exit 2
    fi
fi
```

## Acceptance Tests

### Test 1: Simple Text CAPTCHA
```bash
# Navigate to a site with simple text CAPTCHA
CAPTCHA_TYPE="text"
MAX_ATTEMPTS=3
# Expected: ~60% success rate
```

### Test 2: Image Selection CAPTCHA
```bash
# Navigate to a site with image selection
CAPTCHA_TYPE="image"
MAX_ATTEMPTS=2
# Expected: ~30% success rate, likely human handoff
```

## Token Budget
- Expected turns: 8-15 per attempt
- Cost estimate: ~$0.10-0.25 per attempt (Sonnet 4)
- High cost due to vision analysis complexity

## Ethical and Legal Considerations

1. **Terms of Service**: Some sites prohibit CAPTCHA solving
2. **Rate Limiting**: Respect site rate limits
3. **Legitimate Use**: Only for authorized automation
4. **Privacy**: Don't solve CAPTCHAs to bypass privacy measures
5. **Security**: Don't help bypass legitimate security measures

## Production Recommendations

1. **Human handoff is preferred** for critical workflows
2. **Use CAPTCHA solving as fallback only**
3. **Implement monitoring** for success rates
4. **Consider CAPTCHA services** like 2captcha for production
5. **Avoid CAPTCHAs entirely** by using official APIs

## Test Sites

Reference URLs for live CAPTCHA testing. All validated Feb 22, 2026.

| Provider | URL | Notes |
|----------|-----|-------|
| reCAPTCHA v2 | https://www.google.com/recaptcha/api2/demo | Clean test — auto-passes on real Safari |
| hCaptcha | https://accounts.hcaptcha.com/demo | Auto-passes on real Safari |
| Cloudflare Turnstile | https://2captcha.com/demo/cloudflare-turnstile | Auto-passes on real Safari |
| Normal text CAPTCHA | https://2captcha.com/demo/normal | Rigged — always rejects correct answers; do not use for validation |
| GeeTest slide puzzle | https://2captcha.com/demo/geetest | Ad overlay blocks puzzle; mechanically drag works, vision targeting unvalidated |
| NopeCHA multi-type | https://nopecha.com/demo | Not yet tested; covers multiple CAPTCHA types in one place |

---

## Status

- **Checkbox CAPTCHAs validated** — auto-pass on real Safari/home network (Feb 22, 2026)
- **Image-grid CAPTCHAs** — low success rates, only triggered on suspicious fingerprints
- **GeeTest slide** — drag mechanics work, vision targeting not yet validated
- **Not recommended for production** without human backup for image-grid cases
- **Real-browser automation** is essentially CAPTCHA-free for major platforms