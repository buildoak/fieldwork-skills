# Browser Tools Inventory (25 tools)

All tools are prefixed with `browser_`. Args use the ref system: `browser_snapshot` returns refs like `@e1`, `@e2` which are then passed to interaction tools.

Terminology used in this file:
- **a11y tree:** Accessibility tree snapshot generated for assistive technologies and automation.
- **DOM:** Document Object Model, the browser's structured tree of page elements.
- **CSS selector:** A rule for locating DOM elements (for example, `.price` or `#submit`).

---

## Navigation (4 tools)

### browser_navigate
Navigate to a URL.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | yes | URL to navigate to |

```text
browser_navigate(url="https://example.com")
browser_navigate(url="https://saucedemo.com/inventory.html")
```

### browser_back
Navigate back in browser history. No parameters.

```text
browser_back()
```

### browser_forward
Navigate forward in browser history. No parameters.

```text
browser_forward()
```

### browser_reload
Reload the current page. No parameters.

```text
browser_reload()
```

---

## Observation (6 tools)

### browser_snapshot
Get accessibility tree snapshot. Returns element refs (`@e1`, `@e2`...) for use with interaction tools.

| Param | Type | Required | Values | Default | Description |
|-------|------|----------|--------|---------|-------------|
| `mode` | string | no | `interactive`, `compact`, `full` | `interactive` | Snapshot detail level |

**Modes and token costs:**
- `interactive` (~1,400 tokens): Only interactive elements (buttons, links, inputs). **Use this.**
- `compact` (~3,000-5,000 tokens): Condensed output with text content.
- `full` (~15,000 tokens): Complete accessibility tree. Avoid unless needed.

```text
browser_snapshot()                       # interactive (default, cheapest)
browser_snapshot(mode="interactive")     # explicit interactive
browser_snapshot(mode="compact")         # with text content
browser_snapshot(mode="full")            # complete tree (expensive)
```

**Example output (interactive mode):**
```text
@e1: link "Home"
@e2: link "Products"
@e3: textbox "Search..."
@e4: button "Search"
@e5: link "Login"
@e6: link "Sign Up"
```

### browser_screenshot
Take a screenshot of the current page. Returns file path.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | no | File path to save screenshot |
| `fullPage` | boolean | no | Capture full scrollable page (default: false) |

```text
browser_screenshot()                                    # viewport only, auto path
browser_screenshot(path="/tmp/page.png")                # custom path
browser_screenshot(fullPage=true)                       # full scrollable page
browser_screenshot(path="/tmp/full.png", fullPage=true) # both
```

### browser_get_url
Get the current page URL. No parameters. Returns URL string.

```text
browser_get_url()  # => "https://example.com/products?page=2"
```

### browser_get_title
Get the current page title. No parameters. Returns title string.

```text
browser_get_title()  # => "Products | Example Store"
```

### browser_get_text
Get text content of a specific element.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_get_text(ref="@e5")                    # by ref
browser_get_text(ref=".product-price")         # by CSS selector
browser_get_text(ref="#total-amount")           # by ID selector
```

### browser_get_html
Get HTML content of an element.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |
| `outer` | boolean | no | Return outer HTML instead of inner (default: false) |

```text
browser_get_html(ref="@e3")                     # inner HTML
browser_get_html(ref="@e3", outer=true)         # outer HTML (includes the element itself)
browser_get_html(ref=".results-container")       # by CSS selector
```

---

## Interaction (11 tools)

### browser_click
Click an element.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_click(ref="@e4")                  # click by ref
browser_click(ref="#submit-button")       # click by CSS selector
```

### browser_dblclick
Double-click an element.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_dblclick(ref="@e7")               # double-click to edit
```

### browser_fill
Clear and fill an input field. Use for text inputs, textareas, content-editable fields. Preferred over `browser_type` unless keystroke events are specifically needed.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |
| `text` | string | yes | Text to fill |

```text
browser_fill(ref="@e3", text="search query")
browser_fill(ref="#email", text="user@example.com")
browser_fill(ref="@e8", text="John Doe")
```

### browser_type
Type text character by character. Triggers keystroke events (keydown/keypress/keyup). Use when the input relies on keystroke handlers (autocomplete, search-as-you-type, custom widgets).

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |
| `text` | string | yes | Text to type |

```text
browser_type(ref="@e3", text="react hooks")    # triggers search suggestions
browser_type(ref=".autocomplete", text="New Y") # triggers autocomplete dropdown
```

**When to use `fill` vs `type`:**
- `fill`: Fast, replaces entire value. Use for standard form fields.
- `type`: Slow, character by character. Use for inputs that react to keystrokes.

### browser_press
Press a keyboard key or key combination.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | string | yes | Key name or combination |

```text
browser_press(key="Enter")               # submit form
browser_press(key="Tab")                 # next field
browser_press(key="Escape")              # close modal
browser_press(key="Control+a")           # select all
browser_press(key="Control+c")           # copy
browser_press(key="ArrowDown")           # navigate dropdown
```

### browser_select
Select a dropdown option by value. For native `<select>` elements only.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref or CSS selector |
| `value` | string | yes | Option value to select |

```text
browser_select(ref="@e6", value="us")           # select country
browser_select(ref="#language", value="en-US")   # select language
```

**Note:** For custom dropdowns (React Select, MUI), use `click` to open, then `click` on the option.

### browser_hover
Hover over an element. Triggers hover states, tooltips, dropdown menus.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref or CSS selector |

```text
browser_hover(ref="@e2")                 # reveal dropdown menu
browser_hover(ref=".tooltip-trigger")    # show tooltip
```

### browser_focus
Focus an element. Useful for inputs that show suggestions or validation on focus.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_focus(ref="@e3")                 # focus search input
```

### browser_clear
Clear the value of an input field.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_clear(ref="@e3")                 # clear before re-typing
```

### browser_check
Check a checkbox. Idempotent -- no-op if already checked.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_check(ref="@e9")                 # accept terms checkbox
browser_check(ref="#remember-me")
```

### browser_uncheck
Uncheck a checkbox. Idempotent -- no-op if already unchecked.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ref` | string | yes | Element ref (`@e1`) or CSS selector |

```text
browser_uncheck(ref="@e9")              # uncheck newsletter opt-in
```

---

## Page (3 tools)

### browser_scroll
Scroll the page in a direction.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `direction` | string | yes | `up`, `down`, `left`, `right` |
| `pixels` | number | no | Pixels to scroll (default: viewport height) |

```text
browser_scroll(direction="down")                 # one viewport down
browser_scroll(direction="down", pixels=500)     # 500px down
browser_scroll(direction="up")                   # back to top area
```

### browser_wait
Wait for an element to appear or a fixed duration.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `target` | string | yes | CSS selector to wait for, or milliseconds as string |

```text
browser_wait(target=".results-loaded")           # wait for element
browser_wait(target="#success-message")           # wait for confirmation
browser_wait(target="2000")                      # wait 2 seconds
browser_wait(target="500")                       # wait 500ms
```

### browser_evaluate
Execute JavaScript in the browser context. Returns the result.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `script` | string | yes | JavaScript code to execute |

```text
# Extract specific text (Tier 3 approach)
browser_evaluate(script="document.querySelector('.price').textContent")

# Get page metadata
browser_evaluate(script="document.title")

# Count elements
browser_evaluate(script="document.querySelectorAll('.product-card').length")

# Extract structured data
browser_evaluate(script="JSON.stringify(Array.from(document.querySelectorAll('.item')).map(e => ({name: e.querySelector('.name').textContent, price: e.querySelector('.price').textContent})))")

# Check for JSON-LD (structured data workaround)
browser_evaluate(script="document.querySelector('script[type=\"application/ld+json\"]')?.textContent")

# Scroll to bottom (for lazy-loaded content)
browser_evaluate(script="window.scrollTo(0, document.body.scrollHeight)")
```

---

## Session (1 tool)

### browser_close
Close the browser. **Always call at the end of a browser task.**

No parameters.

```text
browser_close()
```

Releases the browser session. Forgetting to close leaves an orphaned Chromium process and blocks subsequent workers.

---

## Common Patterns

### Login flow
```text
browser_navigate(url="https://example.com/login")
browser_snapshot()                              # find form refs
browser_fill(ref="@e3", text="username")
browser_fill(ref="@e5", text="password")
browser_click(ref="@e7")                        # submit
browser_wait(target=".dashboard")               # wait for redirect
browser_snapshot()                              # verify logged in
```

### Form filling with validation
```text
browser_navigate(url="https://example.com/register")
browser_snapshot()
browser_fill(ref="@e2", text="John")            # first name
browser_fill(ref="@e3", text="Doe")             # last name
browser_fill(ref="@e4", text="john@example.com")
browser_fill(ref="@e5", text="Password123!")
browser_check(ref="@e6")                        # terms checkbox
browser_click(ref="@e7")                        # submit
browser_snapshot()                              # check for errors
```

### Paginated scraping
```text
browser_navigate(url="https://quotes.toscrape.com")
# Loop:
browser_snapshot(mode="compact")                # need text content
# ... extract data from snapshot ...
browser_click(ref="@eN")                        # "Next" button
# Repeat until no more pages
browser_close()
```

### Targeted extraction (Tier 3)
```text
browser_navigate(url="https://known-site.com/product")
browser_evaluate(script="document.querySelector('.price-display').textContent")
browser_close()
```
