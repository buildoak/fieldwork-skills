# Stripe Iframe Playbook

**Target:** Stripe payment forms (cross-origin iframes)
**Tested:** Feb 2026
**Result:** PASS
**Stealth:** None needed (Stripe demo has no anti-bot)

Terminology:
- **iframe:** An embedded webpage loaded inside another page.
- **Cross-origin:** Loaded from a different domain, which triggers browser security restrictions.
- **a11y tree:** Accessibility tree used by snapshot tools.

## What Works

### The iframe bypass pattern

Stripe payment forms live inside cross-origin iframes. Standard `browser_fill` and `browser_type` cannot interact with elements inside cross-origin iframes due to browser security restrictions. The workaround: extract the iframe's `src` URL and navigate directly to it.

```text
# Step 1: Navigate to the page containing the Stripe payment form
browser_navigate(url="https://checkout.stripe.dev/preview")
browser_wait(target="2000")
browser_snapshot()                             # see the page with embedded Stripe iframe

# Step 2: Extract the iframe src URL
browser_evaluate(script="document.querySelector('iframe').src")
# Returns something like: https://js.stripe.com/v3/elements-inner-card-...

# Step 3: Navigate directly to the iframe URL
browser_navigate(url="<iframe_src_url>")
browser_wait(target="2000")
browser_snapshot()                             # iframe content now renders as a regular page

# Step 4: Fill payment fields normally
browser_fill(ref="@card_number", text="4242424242424242")
browser_fill(ref="@expiry", text="12/30")
browser_fill(ref="@cvc", text="123")
browser_fill(ref="@zip", text="10001")         # if ZIP/postal required

# Step 5: Submit payment
# Note: You are now on the iframe page, not the parent page.
# The submit button may be on the parent page.
# You may need to navigate back to the parent page to click Submit.
browser_navigate(url="https://checkout.stripe.dev/preview")
browser_wait(target="2000")
browser_snapshot()
browser_click(ref="@pay_button")               # Pay / Submit button
browser_wait(target="3000")                    # wait for payment processing
browser_snapshot()                             # verify success

# Step 6: Check for visual confirmation
# Stripe demos show success as a visual indicator (green checkmark on Pay button)
# Not all Stripe integrations render a separate confirmation page
browser_screenshot(path="/tmp/stripe-payment-result.png")

browser_close()
```

### Performance

- 59 tool calls, 168 seconds
- The iframe discovery + navigation adds significant call overhead

## What Doesn't Work

1. **`browser_fill` / `browser_type` directly on iframe elements.** Cross-origin iframes enforce the same-origin policy. The browser tools cannot access elements inside a cross-origin iframe through the parent page's context.

2. **Clicking into the iframe via `browser_click`.** While you can click an iframe element in the a11y tree, this gives you a nested context that is unreliable for form filling. Direct navigation is more reliable.

3. **Expecting a text confirmation page.** Some Stripe demo implementations show success as a visual indicator only (green checkmark on the Pay button) rather than a redirect to a confirmation page. Workers should check for both.

## Key Patterns

- **iframe src extraction via `browser_evaluate`.** `document.querySelector('iframe').src` is the key. If there are multiple iframes, use a more specific selector: `document.querySelector('iframe[name="__stripe_hosted_stripe_element"]').src` or similar.
- **Direct navigation renders iframe as regular page.** Once you navigate to the iframe URL, all its form fields become regular page elements that respond to standard `browser_fill` and `browser_type`.
- **Visual-only confirmation.** Not all payment flows render a confirmation page. A green checkmark, a "Payment successful" toast, or a button state change may be the only success signal. Screenshot to capture it.
- **Pattern applies beyond Stripe.** Any cross-origin iframe (payment forms, embedded widgets, third-party content) can potentially be bypassed with this technique. Extract `src`, navigate, interact.

## Anti-Bot Notes

- **No anti-bot on Stripe demo pages.** The Stripe Elements demo/preview pages do not have anti-bot detection.
- **Production Stripe integrations may differ.** Real merchant checkout pages (not Stripe demos) may have their own anti-bot measures. The iframe bypass technique still works, but the parent page may require stealth.
- **Stripe test card numbers.** For testing, use `4242 4242 4242 4242` (Visa), any future expiry date, any 3-digit CVC. These are Stripe's official test card numbers.

## Sample Worker Prompt

```text
Complete a Stripe payment form on a demo checkout page.

The payment form is inside a cross-origin iframe. Standard browser_fill will NOT work on iframe elements.

Workaround:
1. Navigate to the checkout page
2. Use browser_evaluate to extract the iframe src: document.querySelector('iframe').src
3. Navigate directly to that iframe URL -- this renders the form as a regular page
4. Fill the payment fields:
   - Card number: 4242424242424242
   - Expiry: 12/30
   - CVC: 123
   - ZIP: 10001 (if required)
5. Navigate back to the parent page
6. Click the Pay/Submit button
7. Wait for confirmation (may be a visual indicator like a green checkmark, not a separate page)
8. Screenshot the result

Report: payment submitted successfully or not, screenshot of final state.
```
