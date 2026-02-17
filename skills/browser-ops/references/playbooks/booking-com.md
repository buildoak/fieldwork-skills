# Booking.com Playbook

**Target:** https://www.booking.com
**Tested:** Feb 2026
**Result:** PASS (with workaround)
**Stealth:** Layer 1 sufficient (no CAPTCHA, no block -- issue is UX redirect behavior)

## What Works

The working approach discovered after multiple iterations:

1. **Search by landmark, not city name.** Navigate to booking.com homepage, enter a landmark name (e.g., "Sepilok Orangutan Rehabilitation Centre") instead of a city name (e.g., "Sandakan"). Landmark searches return lat/long-based results (204 properties in the tested case) and bypass the city template redirect entirely.

2. **Use ArrowDown + Enter for autocomplete.** Booking.com's React autocomplete ignores click events on dropdown options. After typing the landmark name, use `browser_press(key="ArrowDown")` to highlight the first suggestion, then `browser_press(key="Enter")` to select it.

3. **Select dates via calendar widget clicks.** Click the date input field to open the calendar. Navigate month-by-month using arrow buttons. Click specific date cells by their accessible names (e.g., "Sa 14 March 2026"). Always snapshot after selection to verify the date display updated.

4. **Watch for the "I'm flexible" tab trap.** After selecting dates, the calendar may reopen on the "I'm flexible" tab instead of the "Calendar" tab. Explicitly click the "Calendar" tab before selecting dates.

5. **Get per-night pricing from individual hotel page calendars.** The search results page never shows date-locked prices -- it shows generic "from $X" pricing. Navigate into an individual hotel page and check its availability calendar for actual per-night rates (e.g., "14 $133").

### Step-by-step

```
browser_navigate(url="https://www.booking.com")
browser_snapshot()

# Enter landmark (NOT city name)
browser_click(ref="@destination_field")
browser_type(ref="@destination_field", text="Sepilok Orangutan Rehabilitation Centre")
browser_wait(target="1000")                    # wait for autocomplete
browser_press(key="ArrowDown")                 # highlight first suggestion
browser_press(key="Enter")                     # select it

# Open calendar and select check-in date
browser_click(ref="@date_field")
browser_snapshot()                             # verify on "Calendar" tab, not "I'm flexible"
# If on wrong tab: browser_click(ref="@calendar_tab")
# Navigate to target month with arrow buttons
browser_click(ref="@target_date")              # click check-in date cell
browser_snapshot()                             # calendar auto-advances to checkout selection
browser_click(ref="@checkout_date")            # click checkout date cell

# Search
browser_click(ref="@search_button")
browser_wait(target="2000")
browser_snapshot()                             # verify results (not city template)

# For date-locked pricing: navigate into a specific hotel
browser_click(ref="@hotel_link")
browser_wait(target="2000")
browser_snapshot()                             # check hotel calendar for per-night rates

browser_close()
```

## What Doesn't Work

1. **URL pre-population is completely blocked.** All `searchresults.html` URLs with query parameters (`checkin`, `checkout`, `dest_id`, etc.) are redirected server-side to static city pages. Date, destination, and guest params are stripped.

2. **City name search redirects to city template.** Searching for a city name (e.g., "Sandakan") triggers a redirect to a city landing page (`/city/my/sandakan.html`). This is a static marketing page that resets the date picker to blank and shows generic "from $X" pricing.

3. **Re-entering dates on the city page also fails.** The city page has its own search bar, but re-entering dates and searching again from the city page still does not produce date-locked pricing on the results page.

4. **Clicking autocomplete suggestions with `browser_click`.** The React autocomplete dropdown ignores click events on option elements. Only keyboard navigation (ArrowDown + Enter) works.

## Key Patterns

- **Landmark search bypasses city redirect.** This is the core discovery. City searches trigger a marketing redirect; landmark/POI searches return proper search results with lat/long coordinates.
- **ArrowDown + Enter for autocomplete.** Booking.com's custom React autocomplete does not respond to standard click events on dropdown options. Use keyboard navigation exclusively.
- **Calendar widget protocol.** Never type dates into date fields -- they are read-only triggers for the calendar widget. Click to open, navigate months with arrows, click specific date cells by accessible name.
- **"I'm flexible" tab trap.** The calendar widget has two tabs. It may open on the wrong one. Always verify via snapshot before clicking dates.
- **Per-night pricing requires hotel page entry.** Search results show generic pricing. Individual hotel pages show actual date-locked rates in their availability calendars.

## Anti-Bot Notes

- **No CAPTCHA, no block.** Booking.com does not trigger Cloudflare or any visible anti-bot mechanism against Layer 1 stealth.
- **The redirect behavior is UX/SEO, not anti-bot.** City template pages exist for SEO purposes. The parameter stripping is a design choice, not a detection response.
- **Layer 1 stealth is sufficient.** No escalation needed.

## Sample Worker Prompt

```
Navigate to Booking.com and find hotel prices near Sepilok Orangutan Rehabilitation Centre in Sandakan, Malaysia for March 14-17, 2026.

CRITICAL: Search by the LANDMARK NAME "Sepilok Orangutan Rehabilitation Centre", NOT the city name "Sandakan". City name searches redirect to a static page that strips date parameters.

Steps:
1. Go to booking.com
2. In the destination field, type "Sepilok Orangutan Rehabilitation Centre"
3. Use ArrowDown + Enter to select from autocomplete (click events do not work on Booking.com's autocomplete)
4. Click the date field, navigate to March 2026 in the calendar, click March 14 for check-in, click March 17 for checkout
5. WATCH OUT: If the calendar opens on the "I'm flexible" tab, click "Calendar" tab first
6. Click Search
7. Verify results show properties (not a city template page). If you see generic "from $X" prices, the search failed
8. Click into 2-3 hotels and check their availability calendars for actual per-night pricing
9. Screenshot results

Report: hotel names, per-night prices, and total for 3-night stay.
```
