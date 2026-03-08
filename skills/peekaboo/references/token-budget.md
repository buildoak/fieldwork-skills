# Token Budget Reference

Token costs, optimization strategies, and budget management for peekaboo-ops automation.

## Cost Per Operation (Claude Sonnet 4)

### Vision Operations
- **see --analyze "question"**: ~100 tokens (text response only)
- **see --json**: ~600 tokens (full AX tree structure)
- **see --annotate**: ~800 tokens (AX tree + annotated screenshot)
- **image --mode screen**: ~1400 tokens (1024x768 screenshot)
- **image --mode screen (cropped)**: ~400-800 tokens (depending on crop size)

### Interaction Operations
- **click/type/hotkey commands**: ~50-100 tokens (command + confirmation)
- **Agent conversation turn**: ~200 tokens (natural language + tool calls)
- **Complex workflow step**: ~300-500 tokens (see + interact + verify)

### Analysis Operations
- **Simple state check**: ~100-200 tokens (see --analyze with yes/no question)
- **Content extraction**: ~200-400 tokens (see --analyze with data extraction)
- **Error diagnosis**: ~150-300 tokens (failure analysis and recovery suggestions)

## Context Window Math

### Turn Calculations
- **200k context**: ~265 turns @ 700 tokens/turn average
- **1M context**: ~1,300 turns @ 700 tokens/turn average
- **AX-first hybrid approach**: 3-7x more efficient than screenshot-only automation

### Workflow Estimates
- **Simple task (login)**: 5-8 turns = ~$0.03-0.06
- **Medium workflow (form fill + submit)**: 15-25 turns = ~$0.12-0.20
- **Complex automation (multi-app transfer)**: 30-60 turns = ~$0.25-0.50
- **Extended session**: 100+ turns = checkpoint recommended

## Budget Gates and Governance

### Soft Warning (50 turns)
```bash
if [ $TURN_COUNT -ge 50 ]; then
    echo "⚠️  TOKEN BUDGET WARNING: $TURN_COUNT turns used"
    echo "Estimated cost so far: ~$$(( TURN_COUNT * 8 / 100 )).$(( (TURN_COUNT * 8) % 100 ))"
    echo "Consider checkpointing if this is a long workflow"
fi
```

### Hard Pause (100 turns)
```bash
if [ $TURN_COUNT -ge 100 ]; then
    echo "🛑 TOKEN BUDGET LIMIT REACHED: $TURN_COUNT turns"
    echo "Estimated cost: ~$$(( TURN_COUNT * 8 / 100 )).$(( (TURN_COUNT * 8) % 100 ))"
    echo "Checkpoint required before continuing"
    echo "Type 'CONTINUE' to resume or 'STOP' to end:"
    read -p "> " user_choice
    if [ "$user_choice" != "CONTINUE" ]; then
        exit 0
    fi
fi
```

### Over-Budget (150+ turns)
```bash
if [ $TURN_COUNT -ge 150 ]; then
    echo "🚨 OVER-BUDGET: $TURN_COUNT turns used"
    echo "This session is consuming significant resources"
    echo "Consider breaking into smaller workflows"
    echo "Explicit resume required - type 'EXPENSIVE CONTINUE':"
    read -p "> " expensive_confirm
    if [ "$expensive_confirm" != "EXPENSIVE CONTINUE" ]; then
        exit 1
    fi
fi
```

## Optimization Strategies

### 1. AX-First Hierarchy
```bash
# BEST: AX analysis (100 tokens)
result=$(peekaboo-safe.sh see --analyze "Is the login form visible?" --app Safari)

# GOOD: Targeted AX tree (600 tokens)
result=$(peekaboo-safe.sh see --app Safari --json)

# EXPENSIVE: Full screenshot (1400 tokens)
result=$(peekaboo-safe.sh image --mode screen --path /tmp/screenshot.png)
```

### 2. Question Specificity
```bash
# EFFICIENT: Specific question
peekaboo-safe.sh see --analyze "Is there a red error message visible?" --app Safari

# INEFFICIENT: Broad question
peekaboo-safe.sh see --analyze "What's happening on the screen right now?" --app Safari
```

### 3. Batch Compatible Operations
```bash
# Safe batching (non-GUI operations)
mkdir -p /tmp/peekaboo
./scripts/health-check.sh
peekaboo-safe.sh clean --older-than 24

# NEVER batch GUI operations (race conditions)
# peekaboo-safe.sh click --on B1 & peekaboo-safe.sh type "text" &  # WRONG
```

### 4. Smart Verification
```bash
# EFFICIENT: Targeted verification
success=$(peekaboo-safe.sh see --analyze "Did the form submit successfully?" --app Safari)

# EXPENSIVE: Screenshot verification
peekaboo-safe.sh image --mode screen --path /tmp/verify.png
# Then analyze the screenshot
```

### 5. Crop Screenshots When Possible
```bash
# Full screen: ~1400 tokens
peekaboo-safe.sh image --mode screen --path /tmp/full.png

# Cropped region: ~400-800 tokens (if cropping is available)
# Note: peekaboo doesn't currently support cropping, but future enhancement
```

## Token Telemetry Schema

Track token usage with this logging format:

```json
{
  "operation": "see_analyze",
  "app": "Safari",
  "prompt_tokens": 150,
  "completion_tokens": 50,
  "total_tokens": 200,
  "elapsed_ms": 1200,
  "timestamp": "2026-02-22T10:30:00Z",
  "success": true,
  "workflow_id": "login_flow_001"
}
```

### Implementation Example
```bash
log_token_usage() {
    local operation="$1"
    local tokens="$2"
    local success="$3"

    cat >> /tmp/peekaboo/token-log.jsonl << EOF
{"operation":"$operation","tokens":$tokens,"success":$success,"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF
}

# Usage
log_token_usage "see_analyze" 180 true
```

## Cost Tiers and Planning

### Low Cost Operations (<100 tokens)
- Simple state checks
- Basic element discovery
- Command execution confirmations
- Yes/no questions

### Medium Cost Operations (100-500 tokens)
- AX tree analysis
- Content extraction
- Multi-step verifications
- Complex state analysis

### High Cost Operations (500+ tokens)
- Full screenshot analysis
- Complex scene understanding
- Multi-element interaction planning
- Error diagnosis and recovery

## Model-Specific Optimizations

### Claude Sonnet 4
- Excellent at AX tree interpretation
- Strong visual understanding
- Efficient with targeted questions
- Good at error diagnosis

```bash
# Optimized for Sonnet 4
peekaboo-safe.sh see --analyze "What are the clickable elements in this Safari tab?" --app Safari
```

### Token-Efficient Patterns
```bash
# Pattern: Progressive Discovery
# Start with cheap analysis, escalate if needed

# Step 1: Cheap state check (100 tokens)
state=$(peekaboo-safe.sh see --analyze "Is this a login page?" --app Safari)

if [[ "$state" == *"login"* ]]; then
    # Step 2: Structure discovery only if needed (600 tokens)
    structure=$(peekaboo-safe.sh see --app Safari --json)

    # Step 3: Visual confirmation only if AX fails (1400 tokens)
    if [[ "$structure" == *"error"* ]]; then
        peekaboo-safe.sh image --mode screen --path /tmp/fallback.png
    fi
fi
```

## Workflow-Specific Budgets

### Native App Automation
- **Budget**: 20-40 turns
- **Typical cost**: $0.15-0.30
- **Efficiency**: High (AX trees work perfectly)

### Safari Web Automation
- **Budget**: 30-60 turns
- **Typical cost**: $0.25-0.50
- **Efficiency**: Medium (requires JS injection + coordinate clicks)

### Cross-App Workflows
- **Budget**: 40-80 turns
- **Typical cost**: $0.35-0.65
- **Efficiency**: Medium (multiple app context switches)

### Agent Mode Sessions
- **Budget**: 50-200 turns (depending on complexity)
- **Typical cost**: $0.40-1.60
- **Efficiency**: Variable (depends on task complexity)

## Budget Monitoring Commands

### Check Current Usage
```bash
# Count turns in current session (approximate)
turn_count=$(grep -c "peekaboo-safe.sh" /tmp/peekaboo/*.log 2>/dev/null || echo "0")
echo "Approximate turn count: $turn_count"
```

### Estimate Remaining Budget
```bash
estimate_remaining_budget() {
    local used_turns="$1"
    local context_limit="$2"  # 200000 or 1000000

    local max_turns=$((context_limit / 700))
    local remaining=$((max_turns - used_turns))

    echo "Used: $used_turns turns"
    echo "Remaining: $remaining turns"
    echo "Estimated cost so far: \$$(echo "scale=2; $used_turns * 0.008" | bc)"
}
```

## Integration with Playbooks

Add budget awareness to playbooks:

```bash
# At start of playbook
TURN_COUNT=0

# Increment after each major operation
increment_turn_count() {
    TURN_COUNT=$((TURN_COUNT + 1))

    # Check budget gates
    if [ $TURN_COUNT -eq 50 ]; then
        echo "⚠️  Budget warning: $TURN_COUNT turns used"
    elif [ $TURN_COUNT -eq 100 ]; then
        echo "🛑 Budget limit: checkpoint recommended"
        read -p "Continue? (y/n): " continue_choice
        if [ "$continue_choice" != "y" ]; then
            exit 0
        fi
    fi
}

# Usage in playbooks
peekaboo-safe.sh see --analyze "Is login form visible?" --app Safari
increment_turn_count
```

## Optimization Checklist

Before running expensive automation:

- [ ] Can this use `see --analyze` instead of screenshots?
- [ ] Are questions specific rather than broad?
- [ ] Can operations be batched safely?
- [ ] Is this the most efficient interaction tier?
- [ ] Can we checkpoint and resume if needed?
- [ ] Are we using the right model for the task?
- [ ] Have we set budget limits appropriately?

## Future Enhancements

Potential optimizations for future versions:

1. **Screenshot Cropping**: Crop images to relevant regions
2. **AX Tree Caching**: Cache and reuse AX structures
3. **Smart Batching**: Batch compatible operations automatically
4. **Model Selection**: Auto-select cheaper models for simple tasks
5. **Compression**: Compress screenshot data for transmission
6. **Delta Analysis**: Only analyze changed regions