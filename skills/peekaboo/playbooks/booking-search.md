---
status: validated
validated: 2026-02-22
domain: browser-automation
---
# Booking.com Hotel Search

## When to Use
Search and filter hotels on Booking.com, extract pricing and details. URL-first strategy bypasses all form widgets.

## Prerequisites
- Safari browser, peekaboo health check passing
- Home network (Cloudflare Turnstile did NOT appear on real Safari + home IP)
- VLM available for `see --analyze` (popup identification, price interpretation)

## Flow

1. Construct URL with all search parameters encoded — bypass form widgets entirely:
   ```bash
   # Key URL params:
   # ss=DESTINATION  checkin=YYYY-MM-DD  checkout=YYYY-MM-DD
   # group_adults=N  group_children=N
   # selected_currency=USD
   # hotelfacility=11 (gym)  hotelfacility=2 (pool)
   # nflt=price%3DUSD-min-MAX-1 (price cap per night)
   # nflt=class%3D4 (4-star)  nflt=class%3D5 (5-star)
   URL="https://www.booking.com/searchresults.html?ss=Siargao&checkin=2026-03-01&checkout=2026-03-05&group_adults=1&selected_currency=USD&hotelfacility=11&nflt=price%3DUSD-min-70-1"
   peekaboo-safe.sh open "$URL" --app Safari --wait-until-ready
   sleep 5
   ```

2. Dismiss popups (cookie banner, Google sign-in, genius offers):
   ```bash
   peekaboo-safe.sh see --analyze "Are there any popups, cookie banners, or sign-in prompts covering the results?" --app Safari
   # Google sign-in popup (Arabic) is outside DOM — requires visual dismissal
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari  # click X on popup
   ```

3. Verify filters applied correctly:
   ```bash
   peekaboo-safe.sh see --analyze "Are the filters applied? What currency are prices shown in? Is gym filter active? What is the price range?" --app Safari
   ```

4. Extract hotel results via VLM:
   ```bash
   peekaboo-safe.sh see --analyze "List the top 5 hotels visible: name, price per night in USD, star rating, location, and review score." --app Safari
   ```

5. Deep-dive into specific hotels (click hotel name, extract details):
   ```bash
   peekaboo-safe.sh click --coords X,Y --no-auto-focus --app Safari
   sleep 3
   peekaboo-safe.sh see --analyze "What are the room types, amenities, cancellation policy, and exact price breakdown?" --app Safari
   ```

6. Navigate back and continue extraction:
   ```bash
   peekaboo-safe.sh hotkey --keys "cmd,left" --app Safari  # browser back
   sleep 3
   ```

## Key Patterns

- **URL-first, always.** Booking.com encodes everything in URL params. Never touch date pickers, guest selectors, or filter checkboxes. Construct the URL and go straight to results.
- **VLM as decision engine.** Use `see --analyze` for judgment calls: "Is this price per night or per stay?", "Is the gym filter actually applied?", "What's the location quality from the breadcrumb?"
- **Browser popups are outside DOM.** Google sign-in prompt (renders in Arabic based on IP locale) is a browser-level overlay. JS querySelector returns nothing. Dismiss visually with coordinate click.
- **Cloudflare Turnstile invisible.** On real Safari + home IP, no Cloudflare challenge appeared despite Booking.com using heavy Cloudflare protection. Do not preemptively script CAPTCHA handling.
- **Price format ambiguity.** Booking shows "US$280" which could be per-night or per-stay. Always ask VLM to clarify and cross-reference with the number of nights.

## Known Issues

- Currency filter via URL (`selected_currency=USD`) sometimes reverts to local currency after popup dismissal. Re-verify after any interaction.
- Booking.com A/B tests layout variants. Hotel card structure may differ between sessions.
- Deep-dive (clicking into hotel) opens new tab in some layouts. Check for new tabs and switch.
- Scrolling loads more results dynamically. First page typically shows 25 properties.

## Evidence
- Validated Feb 22, 2026, desktop Safari environment, home network
- 978 properties filtered, 5 hotels extracted, 3 deep-dived
- No Cloudflare Turnstile challenge encountered
- URL params: destination, dates, guests, currency, gym filter, price cap all worked
