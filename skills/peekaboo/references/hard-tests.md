# Peekaboo-Ops Hard Tests & Telemetry System

date: 2026-02-22
status: complete

10 hard tests ordered easiest-to-hardest, plus a telemetry measurement system for structured evaluation.

---

## Test Suite

### Test 1: System Settings Toggle

- **Playbook**: `native-app-automation.md`
- **Task**: "Open System Settings, navigate to Desktop & Dock, toggle 'Automatically hide and show the Dock', then toggle it back to its original state."
- **Success criteria**:
  1. System Settings opens and is frontmost
  2. Desktop & Dock pane is navigated to (verified by `see --analyze`)
  3. Dock autohide toggle is flipped (verified by `defaults read com.apple.dock autohide`)
  4. Toggle is restored to original value (verified by same defaults read)
- **Time budget**: 3 minutes
- **Token budget**: 8-12 turns
- **Risk**: System Settings sidebar navigation can require scrolling. AX labels for toggles may differ from visible text ("Automatically hide and show the Dock" vs shorter AX label).
- **Telemetry points**: AX tree discovery latency, toggle element identification method (ID vs label vs coordinate), retry count on toggle interaction, defaults-read verification round-trips.

---

### Test 2: TextEdit Create-Save-Close Cycle

- **Playbook**: `dialog-and-file-picker.md`
- **Task**: "Open TextEdit, create a new document, type 'Peekaboo hard test #2 — timestamp: {ISO8601}', save it as `/tmp/peekaboo/test2-output.txt` using Save As dialog, then close the document."
- **Success criteria**:
  1. File exists at `/tmp/peekaboo/test2-output.txt`
  2. File contents match expected text (verified by `cat`)
  3. TextEdit window is closed (no unsaved document prompt)
- **Time budget**: 4 minutes
- **Token budget**: 10-15 turns
- **Risk**: TextEdit maps Cmd+Shift+S to "Duplicate" not "Save As" -- must use `menu click --path "File > Save As..."`. Compact file dialog may hide Save button from AX tree. Path entry in file dialog requires Go To Folder (Cmd+Shift+G) or manual navigation.
- **Telemetry points**: Dialog type detected (compact vs expanded), path entry method used (Go To Folder vs sidebar nav), AX label mismatch count (Don't Save = "Delete"), file verification latency.

---

### Test 3: Notes App Cross-App Transfer

- **Playbook**: `cross-app-data-transfer.md`
- **Task**: "Open Notes app, read the content of the most recent note, then open TextEdit and paste that content into a new document. Verify the transferred text matches."
- **Success criteria**:
  1. Notes app content is captured (clipboard or AX extraction)
  2. TextEdit receives the identical text
  3. Content diff between source and target is zero (ignoring trailing whitespace)
- **Time budget**: 5 minutes
- **Token budget**: 12-18 turns
- **Risk**: Notes app AX tree is complex (rich text, embedded objects). Clipboard may contain RTF data instead of plain text. App switching between Notes and TextEdit must maintain clipboard contents. Notes content selection may require Cmd+A which could fail if focus is wrong.
- **Telemetry points**: Clipboard format captured (RTF vs plain), app switch count, content extraction method (AX read vs clipboard), character-level diff result, total inter-app round-trips.

---

### Test 4: Safari Login to httpbin.org

- **Playbook**: `safari-login.md`
- **Task**: "Open Safari, navigate to `https://httpbin.org/forms/post`, fill the form: Customer='PeekabooTest', Size='Medium', Topping='Bacon', and submit. Extract the response JSON from the result page."
- **Success criteria**:
  1. Safari navigates to httpbin form (URL verified)
  2. All form fields filled correctly (JS injection verification)
  3. Form submitted successfully
  4. Response JSON extracted and contains `"custname": "PeekabooTest"` and `"size": "medium"`
- **Time budget**: 5 minutes
- **Token budget**: 12-18 turns
- **Risk**: Safari AX click misfires to Start Page (known bug). Form fields require JS injection, not AX type. Radio button and checkbox selection via JS needs precise selectors. Response page may have different DOM structure than expected.
- **Telemetry points**: Navigation method (open vs URL bar), form fill method (JS injection vs AX type), selector accuracy per field, submission method (JS click vs coordinate click), response extraction method, total JS injection commands.

---

### Test 5: Reddit Subreddit Reader

- **Playbook**: `reddit-organic.md`
- **Task**: "Open Safari, navigate to `https://old.reddit.com/r/MachineLearning/`, scroll down twice, and extract the titles and scores of the top 5 visible posts. Return as structured JSON."
- **Success criteria**:
  1. Safari navigates to the subreddit (URL verified)
  2. Page loads fully (not login wall or CAPTCHA)
  3. At least 5 post titles extracted with numeric scores
  4. Output is valid JSON array with `{title, score, url}` objects
- **Time budget**: 6 minutes
- **Token budget**: 15-20 turns
- **Risk**: Reddit may show login prompt blocking content (old.reddit mitigates this). Dynamic content loading after scroll may not be captured by AX tree. Post scores may be hidden ("vote" instead of number). Anti-bot detection could redirect to CAPTCHA. JS injection depth required for DOM traversal of post list.
- **Telemetry points**: Login wall encountered (boolean), scroll commands issued, JS injection depth (number of nested queries), posts successfully extracted vs target, CAPTCHA detection event, total page load wait time.

---

### Test 6: Twitter/X Trending Topics Extraction

- **Playbook**: `twitter-feed-reader.md`
- **Task**: "Open Safari, navigate to `https://x.com/explore/tabs/trending`, wait for content to load, and extract the top 10 trending topics. Return as structured JSON with rank and topic name."
- **Success criteria**:
  1. Safari navigates to X explore page
  2. No login wall blocks trending content (trending is partially public)
  3. At least 8 of 10 trending topics extracted with rank numbers
  4. Output is valid JSON
- **Time budget**: 7 minutes
- **Token budget**: 15-25 turns
- **Risk**: X.com requires login for most content -- trending may be gated. Page is React SPA with complex DOM that changes frequently. Anti-bot detection is aggressive. Content may be behind interstitial ("Log in to see what's happening"). Fallback to `see --analyze` screenshot interpretation may be necessary.
- **Telemetry points**: Login wall encountered (boolean), fallback to screenshot analysis (boolean), topics extracted count, DOM extraction vs vision extraction ratio, anti-bot event count, page load retry count.

---

### Test 7: Booking.com Hotel Search

- **Playbook**: `booking-search.md`
- **Task**: "Open Safari, navigate to Booking.com, search for hotels in 'Siargao, Philippines' for dates March 15-22 2026, 2 guests. Extract the names and prices of the first 3 results."
- **Success criteria**:
  1. Booking.com loads without CAPTCHA block
  2. Search form filled: destination, dates, guests
  3. Results page shows Siargao properties
  4. At least 3 hotel names with prices extracted
- **Time budget**: 10 minutes
- **Token budget**: 20-35 turns
- **Risk**: Booking.com has sophisticated anti-bot (Cloudflare + custom). Date picker is complex interactive widget requiring coordinate clicks. Autocomplete dropdown for destination needs timing. CAPTCHA is highly likely. Price extraction requires handling currency formatting and dynamic loading. Search form is a multi-step widget, not a simple form.
- **Telemetry points**: CAPTCHA encountered (boolean + type), date picker interaction method, autocomplete handling turns, search form completion steps, results page load time, price extraction accuracy, total coordinate clicks vs AX clicks.

---

### Test 8: Multi-App Workflow Chain

- **Playbook**: Novel combination -- `native-app-automation.md` + `cross-app-data-transfer.md` + `dialog-and-file-picker.md`
- **Task**: "Open Safari and extract the current Bitcoin price from `https://coinmarketcap.com/currencies/bitcoin/`. Then open Numbers, create a new spreadsheet, enter 'BTC Price' in cell A1 and the extracted price in cell B1. Save the spreadsheet as `/tmp/peekaboo/btc-tracker.numbers`."
- **Success criteria**:
  1. Bitcoin price extracted from CoinMarketCap (numeric value, not 'N/A')
  2. Numbers app opens with new spreadsheet
  3. Cell A1 contains 'BTC Price', B1 contains the numeric price
  4. File saved successfully at specified path
  5. File is a valid Numbers document (openable)
- **Time budget**: 10 minutes
- **Token budget**: 25-35 turns
- **Risk**: CoinMarketCap is JS-heavy SPA that may not expose price via simple DOM query. Numbers cell navigation differs from Excel (click vs tab). Save dialog in Numbers may default to iCloud, requiring path override. Three-app chain means any failure cascades. Clipboard format from Safari JS extraction to Numbers paste may lose formatting.
- **Telemetry points**: Web data extraction method, cross-app clipboard transfers, Numbers cell targeting method (click vs keyboard nav), save dialog path override method, total app switches, cascade failure point (if any), end-to-end wall clock.

---

### Test 9: CAPTCHA Detection and Handoff

- **Playbook**: `captcha-solver.md`
- **Task**: "Open Safari, navigate to `https://www.google.com/recaptcha/api2/demo`, detect the reCAPTCHA challenge, attempt to classify its type, take an evidence screenshot, and escalate to HUMAN_HANDOFF with a structured report including CAPTCHA type, screenshot path, and recommended human action."
- **Success criteria**:
  1. reCAPTCHA demo page loads
  2. CAPTCHA iframe/element detected (by AX or screenshot analysis)
  3. CAPTCHA type correctly classified as 'reCAPTCHA v2'
  4. Evidence screenshot saved to `/tmp/peekaboo/captcha-evidence.png`
  5. Structured HUMAN_HANDOFF JSON produced with all required fields
  6. Agent does NOT attempt to solve the CAPTCHA (respects experimental status)
- **Time budget**: 5 minutes
- **Token budget**: 10-15 turns
- **Risk**: reCAPTCHA lives in an iframe which may not be visible to AX tree. Screenshot analysis must correctly identify the challenge type. The agent might incorrectly attempt to solve rather than escalate. The demo page structure may change.
- **Telemetry points**: CAPTCHA detection method (AX vs screenshot vs JS), classification accuracy, time-to-detection, screenshot capture success, handoff JSON completeness score (fields present / fields required), attempted-solve violation (boolean).

---

### Test 10: Safari Cookie Extraction Pipeline

- **Playbook**: `cookie-extractor.md`
- **Task**: "Open Safari, navigate to `https://httpbin.org/cookies/set?peekaboo_test=hard_test_10&session_id=abc123`, then extract all cookies for the httpbin.org domain using Safari JavaScript. Output as JSON with cookie name, value, and domain fields. Verify by navigating to `https://httpbin.org/cookies` and comparing the extracted cookies against the server-reported cookies."
- **Success criteria**:
  1. Cookie-setting URL loads successfully (httpbin returns cookies)
  2. Cookies extracted via JS: `document.cookie` returns `peekaboo_test` and `session_id`
  3. Extracted cookie JSON is valid and contains both cookies
  4. Verification page (`/cookies`) confirms server sees the same cookies
  5. Extracted values match server-reported values exactly
- **Time budget**: 6 minutes
- **Token budget**: 12-18 turns
- **Risk**: `document.cookie` does not return HttpOnly cookies (httpbin may set HttpOnly). Safari may block third-party cookie access via ITP. The set-cookies redirect may not persist cookies as expected. AppleScript JS injection security restrictions may limit cookie access. Verification comparison requires JSON parsing on both sides.
- **Telemetry points**: Cookie set confirmation, cookies visible to JS count vs server-reported count, HttpOnly gap (cookies server sees but JS cannot), ITP interference detected (boolean), extraction-to-verification match ratio, total JS injection commands.

---

## Telemetry System

### Event Schema

Every telemetry event is a single JSONL line written to `/tmp/peekaboo/telemetry/YYYY-MM-DD-test-N.jsonl`:

```json
{
  "ts": "2026-02-22T14:30:00.000Z",
  "test_id": "test-1",
  "event": "state_enter|command_run|command_result|error|retry|state_exit|test_result",
  "state": "PREFLIGHT|ACQUIRE_WINDOW|DISCOVER|INTERACT|VERIFY|EXTRACT|CLEANUP|RECOVER|HUMAN_HANDOFF|ABORT|DONE",
  "data": {
    "command": "peekaboo-safe.sh see --app Safari --json",
    "duration_ms": 1200,
    "tokens_in": 450,
    "tokens_out": 120,
    "result": "success|failure|timeout|retry",
    "error_type": "stale_snapshot|element_not_found|ax_timeout|captcha|login_wall",
    "detail": "free text for context"
  },
  "turn": 5,
  "wall_clock_elapsed_s": 45.2
}
```

### Event Types

| Event | When | Required `data` fields |
|-------|------|----------------------|
| `test_start` | Test begins | `test_name`, `playbook`, `timestamp` |
| `state_enter` | FSM transitions to new state | `state`, `from_state` |
| `command_run` | Peekaboo or osascript command executed | `command`, `turn` |
| `command_result` | Command returns | `command`, `duration_ms`, `result`, `tokens_in`, `tokens_out` |
| `error` | Error encountered | `error_type`, `detail`, `command` |
| `retry` | Retry triggered | `state`, `retry_count`, `max_retries` |
| `state_exit` | Leaving a state | `state`, `next_state`, `duration_ms` |
| `checkpoint` | Budget gate hit | `turn`, `tokens_total`, `gate_level` |
| `test_result` | Test ends | `pass`, `duration_s`, `total_turns`, `total_tokens`, `errors`, `detail` |

### Telemetry File Location

```
/tmp/peekaboo/telemetry/
  2026-02-22-test-1.jsonl
  2026-02-22-test-2.jsonl
  ...
  2026-02-22-test-10.jsonl
  2026-02-22-summary.json
```

---

## Telemetry Preamble (Copy-Paste into Subagent Prompt)

Prepend this to any test execution prompt:

```markdown
## Telemetry Instrumentation (MANDATORY)

You MUST log structured telemetry throughout this task. Before ANY other action:

1. Create telemetry directory:
   ```bash
   mkdir -p /tmp/peekaboo/telemetry
   ```

2. Set telemetry file path:
   ```bash
   TELEM_FILE="/tmp/peekaboo/telemetry/$(date +%Y-%m-%d)-test-{N}.jsonl"
   ```

3. Log `test_start` event immediately:
   ```bash
   echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'","test_id":"test-{N}","event":"test_start","data":{"test_name":"{TEST_NAME}","playbook":"{PLAYBOOK}","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'"}}' >> "$TELEM_FILE"
   ```

4. Before each peekaboo or osascript command, log `command_run`:
   ```bash
   TURN=$((${TURN:-0} + 1))
   START_MS=$(python3 -c "import time; print(int(time.time()*1000))")
   echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'","test_id":"test-{N}","event":"command_run","state":"'$CURRENT_STATE'","data":{"command":"COMMAND_HERE","turn":'$TURN'}}' >> "$TELEM_FILE"
   ```

5. After each command returns, log `command_result`:
   ```bash
   END_MS=$(python3 -c "import time; print(int(time.time()*1000))")
   DURATION=$((END_MS - START_MS))
   echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'","test_id":"test-{N}","event":"command_result","state":"'$CURRENT_STATE'","data":{"command":"COMMAND_HERE","duration_ms":'$DURATION',"result":"success"}}' >> "$TELEM_FILE"
   ```

6. On FSM state transitions, log `state_enter` and `state_exit`.

7. On errors, log `error` event with `error_type` and `detail`.

8. At test completion (pass OR fail), log `test_result`:
   ```bash
   echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'","test_id":"test-{N}","event":"test_result","data":{"pass":true,"duration_s":TOTAL_S,"total_turns":'$TURN',"total_tokens":0,"errors":0,"detail":"SUMMARY"}}' >> "$TELEM_FILE"
   ```

Token counts: If you cannot measure tokens precisely, estimate based on command type:
- `see --analyze`: ~100 tokens out
- `see --json`: ~600 tokens out
- `image --mode screen`: ~1400 tokens out
- Each turn overhead: ~200 tokens

State tracking: Maintain a `CURRENT_STATE` variable. Update it at every FSM transition.

IMPORTANT: Telemetry logging must NOT interfere with task execution. If a telemetry write fails, continue the task. Telemetry is observational, not blocking.
```

---

## Aggregation Script Outline

```python
#!/usr/bin/env python3
"""
peekaboo-telemetry-aggregate.py
Reads JSONL telemetry files, produces summary table.

Usage: python3 peekaboo-telemetry-aggregate.py /tmp/peekaboo/telemetry/
"""

import json
import sys
import os
from pathlib import Path
from collections import defaultdict

def load_events(telemetry_dir: str) -> dict[str, list[dict]]:
    """Load all JSONL files, grouped by test_id."""
    tests = defaultdict(list)
    for f in sorted(Path(telemetry_dir).glob("*.jsonl")):
        for line in f.read_text().strip().split("\n"):
            if not line.strip():
                continue
            event = json.loads(line)
            tests[event.get("test_id", f.stem)].append(event)
    return dict(tests)

def summarize_test(test_id: str, events: list[dict]) -> dict:
    """Extract summary metrics from a test's event stream."""
    result_event = next((e for e in events if e["event"] == "test_result"), None)
    command_events = [e for e in events if e["event"] == "command_result"]
    error_events = [e for e in events if e["event"] == "error"]
    retry_events = [e for e in events if e["event"] == "retry"]
    state_events = [e for e in events if e["event"] == "state_enter"]

    total_cmd_time = sum(e["data"].get("duration_ms", 0) for e in command_events)
    states_visited = [e["data"].get("state", e.get("state", "?")) for e in state_events]

    return {
        "test_id": test_id,
        "pass": result_event["data"]["pass"] if result_event else None,
        "duration_s": result_event["data"].get("duration_s") if result_event else None,
        "total_turns": result_event["data"].get("total_turns") if result_event else len(command_events),
        "peekaboo_commands": len(command_events),
        "avg_command_ms": int(total_cmd_time / max(len(command_events), 1)),
        "errors": len(error_events),
        "retries": len(retry_events),
        "states_visited": states_visited,
        "unique_states": len(set(states_visited)),
        "detail": result_event["data"].get("detail", "") if result_event else "incomplete",
    }

def print_summary(summaries: list[dict]):
    """Print a formatted summary table."""
    header = f"{'Test':<12} {'Pass':<6} {'Time(s)':<8} {'Turns':<6} {'Cmds':<5} {'Errs':<5} {'Retries':<8} {'States':<7}"
    print("=" * len(header))
    print("PEEKABOO-OPS HARD TEST RESULTS")
    print("=" * len(header))
    print(header)
    print("-" * len(header))

    pass_count = 0
    total_time = 0
    total_turns = 0

    for s in summaries:
        p = "PASS" if s["pass"] else ("FAIL" if s["pass"] is not None else "N/A")
        t = f"{s['duration_s']:.1f}" if s["duration_s"] else "?"
        print(f"{s['test_id']:<12} {p:<6} {t:<8} {s['total_turns']:<6} {s['peekaboo_commands']:<5} {s['errors']:<5} {s['retries']:<8} {s['unique_states']:<7}")

        if s["pass"]:
            pass_count += 1
        if s["duration_s"]:
            total_time += s["duration_s"]
        total_turns += s["total_turns"] or 0

    print("-" * len(header))
    total = len(summaries)
    print(f"Success rate: {pass_count}/{total} ({100*pass_count/max(total,1):.0f}%)")
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"Total turns: {total_turns}")
    print(f"Avg turns/test: {total_turns/max(total,1):.1f}")

def write_summary_json(summaries: list[dict], output_path: str):
    """Write machine-readable summary."""
    agg = {
        "total_tests": len(summaries),
        "passed": sum(1 for s in summaries if s["pass"]),
        "failed": sum(1 for s in summaries if s["pass"] is False),
        "incomplete": sum(1 for s in summaries if s["pass"] is None),
        "total_duration_s": sum(s["duration_s"] or 0 for s in summaries),
        "total_turns": sum(s["total_turns"] or 0 for s in summaries),
        "total_errors": sum(s["errors"] for s in summaries),
        "total_retries": sum(s["retries"] for s in summaries),
        "tests": summaries,
    }
    Path(output_path).write_text(json.dumps(agg, indent=2))
    print(f"\nSummary JSON written to: {output_path}")

if __name__ == "__main__":
    telemetry_dir = sys.argv[1] if len(sys.argv) > 1 else "/tmp/peekaboo/telemetry/"
    if not os.path.isdir(telemetry_dir):
        print(f"Telemetry directory not found: {telemetry_dir}")
        sys.exit(1)

    tests = load_events(telemetry_dir)
    summaries = [summarize_test(tid, events) for tid, events in sorted(tests.items())]
    print_summary(summaries)
    write_summary_json(summaries, os.path.join(telemetry_dir, "summary.json"))
```

---

## Execution Strategy

### Recommended Order

Run sequentially. No parallelization -- peekaboo requires sequential GUI access (hard rule from SKILL.md). Each test uses the display, so only one can run at a time.

```
Phase 1 (Validated - expect all pass):     ~17 min
  Test 1: System Settings Toggle            3 min
  Test 2: TextEdit Create-Save-Close        4 min
  Test 3: Notes Cross-App Transfer          5 min
  Test 4: Safari httpbin Form               5 min

Phase 2 (Web automation - expect 1-2 pass): ~23 min
  Test 5: Reddit Subreddit Reader           6 min
  Test 6: Twitter/X Trending Extraction     7 min
  Test 7: Booking.com Hotel Search         10 min

Phase 3 (Edge cases - expect 0-1 pass):    ~21 min
  Test 8: Multi-App Workflow Chain         10 min
  Test 9: CAPTCHA Detection & Handoff       5 min
  Test 10: Cookie Extraction Pipeline       6 min

Total estimated: ~61 minutes
```

### Go/No-Go Gates

- **After Phase 1**: If <3/4 pass, STOP. Fix validated playbooks before proceeding.
- **After Phase 2**: If 0/3 pass, mark web automation as "needs UI-TARS + more work" and proceed to Phase 3 edge cases anyway (they test different capabilities).
- **After Phase 3**: Any passes here are bonus signal.

### Expected Outcomes

| Tier | Tests | Expected Pass Rate | What It Proves |
|------|-------|-------------------|----------------|
| Validated | 1-4 | 75-100% | Core AX automation is production-ready |
| Web | 5-7 | 25-50% | Safari JS injection works for real sites |
| Edge | 8-10 | 0-33% | Envelope of current capability |

### Pre-Run Checklist

```bash
# 1. Health check
cd /path/to/user/thinking/project-root/workspace/skills/peekaboo-ops
./scripts/health-check.sh

# 2. Create telemetry directory
mkdir -p /tmp/peekaboo/telemetry

# 3. Verify Safari is available and logged out of test sites
# 4. Close unnecessary apps to reduce AX tree noise
# 5. Ensure display is active (not locked, not sleeping)
```
