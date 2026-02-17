# Google Flights Playbook

**Target:** https://www.google.com/travel/flights
**Tested:** Feb 2026
**Result:** PASS
**Stealth:** None needed (Google does not block search functionality)

Terminology:
- **SPA:** Single-page application; content updates dynamically without full page reloads.
- **Autocomplete widget:** Input that requires keystrokes to trigger suggestions.
- **a11y tree:** Accessibility tree used by snapshot tools.

## What Works

### Primary approach: URL pre-population (recommended)

Bypass the form entirely by navigating to a URL with a natural language query parameter:

```text
browser_navigate(url="https://www.google.com/travel/flights?q=Flights+from+SFO+to+NRT+on+2026-04-17+return+2026-05-01")
browser_wait(target="2000")                    # wait for results to load
browser_snapshot()                             # verify flights are displayed
```

Google parses the natural language query and populates all form fields automatically -- departure, destination, dates, trip type. This bypasses all autocomplete widget complexity.

### Applying filters after URL load

```text
# After results load from URL pre-population:
browser_snapshot(mode="interactive")           # get refs for filter controls

# Example: Apply "1 stop or fewer" filter
browser_click(ref="@stops_dropdown")           # open stops filter
browser_snapshot()
browser_click(ref="@one_stop_option")          # select "1 stop or fewer"
browser_wait(target="1000")                    # wait for results to update

# Extract flight data
browser_snapshot(mode="compact")               # need text content for prices
```

### Fallback: Manual form filling

If URL pre-population doesn't work for a specific query:

```text
browser_navigate(url="https://www.google.com/travel/flights")
browser_snapshot()

# Change trip type (if needed)
browser_click(ref="@trip_type_dropdown")
browser_snapshot()
browser_click(ref="@one_way_option")

# Set departure
browser_click(ref="@from_field")
browser_type(ref="@from_field", text="LAX")    # MUST use browser_type, not browser_fill
browser_wait(target="1000")                    # wait for autocomplete suggestions
browser_snapshot()
browser_click(ref="@first_suggestion")

# Set destination (same pattern)
browser_click(ref="@to_field")
browser_type(ref="@to_field", text="JFK")
browser_wait(target="1000")
browser_snapshot()
browser_click(ref="@first_suggestion")

# Set date via calendar widget
browser_click(ref="@date_field")
browser_snapshot()                             # calendar widget
browser_click(ref="@target_date")              # click date cell
browser_click(ref="@done_button")

# Search
browser_click(ref="@search_button")
browser_wait(target="2000")
browser_snapshot(mode="compact")               # extract results
```

## What Doesn't Work

1. **`browser_fill` on autocomplete fields.** Google Flights uses custom React/Material autocomplete widgets. `browser_fill` sets the value without triggering keystrokes, so the suggestion dropdown never appears. Always use `browser_type` for these fields.

2. **Encoded URL parameters.** Attempting to construct URLs with encoded search parameters (e.g., `/flights/SFO-NRT/...`) is unreliable -- the URL format is geo/session-dependent and changes frequently. The `?q=` natural language format is the reliable approach.

3. **Fighting autocomplete that reverts to geo-defaults.** The autocomplete widgets may revert to geo-default airports after typing. The URL pre-population approach was discovered specifically to bypass this issue.

## Key Patterns

- **`?q=` natural language URL format.** `?q=Flights+from+SFO+to+NRT+on+2026-04-17+return+2026-05-01`. Google parses this correctly every time. This is the primary approach.
- **`browser_type` not `browser_fill` for autocomplete.** The SPA autocomplete widgets require character-by-character keystroke events to trigger suggestions.
- **Wait after each interaction.** Google Flights is a heavy SPA. Add `browser_wait(target="1000")` between interactions to allow dynamic content to load.
- **`compact` mode for extraction.** Interactive mode shows only buttons/inputs. You need compact mode to see flight prices, times, and airline names in the a11y tree.
- **Sort/filter follow click-snapshot-click pattern.** Open dropdown, snapshot to see options, click desired option. Standard SPA widget interaction.

## Anti-Bot Notes

- **No anti-bot detection for search.** Google does not block or challenge headless browsers on the Flights search page.
- **No stealth configuration needed.** Layer 0 (no stealth) works fine.
- **Rate limiting may apply at scale.** Not tested at high volume, but Google is known to rate-limit automated access. For one-off searches, not a concern.

## Sample Worker Prompt

```text
Search Google Flights for round-trip flights from SFO to NRT (Tokyo Narita), departing April 17, 2026, returning May 1, 2026.

Use URL pre-population to bypass the form:
Navigate to: https://www.google.com/travel/flights?q=Flights+from+SFO+to+NRT+on+2026-04-17+return+2026-05-01

After results load:
1. Apply "1 stop or fewer" filter
2. Extract the top 3 cheapest flights: airline, departure time, arrival time, duration, stops, price
3. Screenshot the results page

If URL pre-population fails, fall back to manual form filling using browser_type (NOT browser_fill) for the airport autocomplete fields.

Report: top 3 flights with full details.
```
