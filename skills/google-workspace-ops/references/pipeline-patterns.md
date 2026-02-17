# Pipeline Patterns

Composable patterns for combining `gog` with `jq`, shell scripts, and multi-service workflows.
These are the 10x patterns -- copy, adapt, ship.

---

## Pattern 1: Email Triage Pipeline

Read, filter, and process unread emails in a single pipeline.

```bash
# Get unread emails, extract key fields
gog gmail search "is:unread" --max 10 --json | \
  jq '.[] | {
    thread_id: .threadId,
    subject: .subject,
    from: .from,
    date: .date,
    snippet: .snippet
  }'

# Unread from specific sender
gog gmail search "is:unread from:boss@company.com" --max 5 --json

# Unread with attachments
gog gmail search "is:unread has:attachment" --max 10 --json

# Read full thread content for the most recent unread
THREAD_ID=$(gog gmail search "is:unread" --max 1 --json | jq -r '.[0].threadId')
gog gmail thread get "$THREAD_ID" --json

# Get message count by label
gog gmail labels list --json | jq '.[] | {name: .name, unread: .messagesUnread, total: .messagesTotal}'
```

## Pattern 2: Calendar Intelligence

Query and analyze calendar data.

```bash
# Today's schedule as a clean summary
gog cal events --today --all --json | \
  jq '.[] | "\(.start.dateTime // .start.date) - \(.summary) [\(.status)]"'

# This week's meetings with attendees
gog cal events --week --json | \
  jq '.[] | {
    when: .start.dateTime,
    title: .summary,
    attendees: [.attendees[]?.email] | join(", "),
    location: .location
  }'

# Find schedule conflicts
gog cal conflicts --json

# Free/busy check for scheduling
# Replace with your local timezone offset in the next two timestamps
gog cal freebusy "primary,colleague@company.com" \
  --from "2026-02-18T08:00:00+00:00" \
  --to "2026-02-18T18:00:00+00:00" --json

# Next 3 days with day-of-week labels
gog cal events --days 3 --weekday --json
```

## Pattern 3: Drive Search & Extract

Find files and extract content.

```bash
# Search and get web links
gog search "project proposal" --max 5 --json | \
  jq '.[] | {name: .name, type: .mimeType, link: .webViewLink, modified: .modifiedTime}'

# Find Google Docs specifically
gog search "budget" --json | \
  jq '.[] | select(.mimeType == "application/vnd.google-apps.document") | {name, id: .id, link: .webViewLink}'

# Find files modified in the last week
gog search "modifiedTime > '2026-02-10'" --raw-query --json

# Download a file by search
FILE_ID=$(gog search "meeting notes february" --max 1 --json | jq -r '.[0].id')
gog download "$FILE_ID" --output ./meeting-notes.pdf

# List files in a specific folder
gog ls --parent FOLDER_ID --json | jq '.[] | {name: .name, type: .mimeType, size: .size}'
```

## Pattern 4: Document Pipeline (Markdown -> Google Docs)

Create and edit Google Docs from local markdown.

```bash
# Create a new doc from markdown file
gog docs create "Sprint Review 2026-W07" --file sprint-review.md --json

# Read a doc as plain text (for agent consumption)
gog docs cat DOC_ID

# Write markdown to existing doc (replaces all content)
gog docs write DOC_ID --file updated-content.md --replace --markdown

# Insert text at a specific position
gog docs insert DOC_ID "New paragraph here" --index 1

# Find and replace across a doc
gog docs find-replace DOC_ID "old text" "new text"

# Read specific tab
gog docs cat DOC_ID --tab "Meeting Notes"

# Export doc as PDF
gog docs export DOC_ID --format pdf --output ./doc.pdf
```

## Pattern 5: Slides from Markdown

Create presentations from markdown content.

```bash
# Create slides from a markdown file
gog slides create-from-markdown "Q1 Review" --content-file presentation.md --json

# Create slides from inline markdown
gog slides create-from-markdown "Quick Deck" --content "# Slide 1\nContent here\n\n---\n\n# Slide 2\nMore content"

# Add a slide with an image
gog slides add-slide PRESENTATION_ID /path/to/image.png --notes "Speaker notes here"

# Read slide content
gog slides list-slides PRESENTATION_ID --json
gog slides read-slide PRESENTATION_ID SLIDE_ID --json

# Export as PDF
gog slides export PRESENTATION_ID --format pdf --output deck.pdf
```

## Pattern 6: Spreadsheet Data Pipeline

Read, write, and process spreadsheet data.

```bash
# Read a range as JSON
gog sheets get SHEET_ID "Sheet1!A1:E10" --json

# Read and pipe to jq for processing
gog sheets get SHEET_ID "Sheet1!A:E" --json | \
  jq '.values[] | {name: .[0], email: .[1], status: .[2]}'

# Append a row
gog sheets append SHEET_ID "Sheet1!A:D" "2026-02-17" "Task completed" "John" "Done"

# Update specific cell
gog sheets update SHEET_ID "Sheet1!B5" "Updated value"

# Clear a range
gog sheets clear SHEET_ID "Sheet1!A10:D20"

# Get spreadsheet metadata (sheet names, row counts)
gog sheets metadata SHEET_ID --json

# Create new spreadsheet
gog sheets create "Monthly Report" --json
```

## Pattern 7: Contact & People Lookup

Search directory and manage contacts.

```bash
# Search contacts by name
gog contacts search "John Smith" --json

# List all contacts
gog contacts list --max 50 --json

# Workspace directory search
gog people search "engineering team" --json

# Get your own profile
gog me --json

# Create a contact
gog contacts create --given-name "Jane" --family-name "Doe" --email "jane@example.com" --phone "+1234567890"
```

## Pattern 8: Task Management

Manage Google Tasks lists and items.

```bash
# List all task lists
gog tasks lists list --json

# List tasks in a specific list
gog tasks list TASKLIST_ID --json

# Add a task
gog tasks add TASKLIST_ID --title "Review PR #42" --due "2026-02-18" --notes "Check edge cases"

# Pipeline: list uncompleted tasks across all lists
for LIST_ID in $(gog tasks lists list --json | jq -r '.[].id'); do
  gog tasks list "$LIST_ID" --json | jq '.[] | select(.status == "needsAction") | {title, due}'
done
```

## Pattern 9: Multi-Service Orchestration

Chain operations across services.

```bash
# Email -> Calendar: Create event from email content
MSG=$(gog gmail get MSG_ID --json)
SUBJECT=$(echo "$MSG" | jq -r '.subject')
# Replace with your local timezone offset in the next two timestamps
gog cal create primary --summary "$SUBJECT follow-up" \
  --from "2026-02-18T14:00:00+00:00" \
  --to "2026-02-18T14:30:00+00:00" --json \
  --description "Follow up on: $SUBJECT"

# Drive -> Docs -> Email: Find doc, read it, email summary
DOC_ID=$(gog search "weekly status" --max 1 --json | jq -r '.[0].id')
CONTENT=$(gog docs cat "$DOC_ID" | head -50)
gog send --to "manager@company.com" --subject "Weekly Status Summary" \
  --body "$CONTENT" --no-input

# Calendar -> Email: Send today's schedule to someone
SCHEDULE=$(gog cal events --today --plain)
gog send --to "assistant@company.com" --subject "Today's Schedule" \
  --body "$SCHEDULE" --no-input

# Sheets -> Email: Read data, format, send
DATA=$(gog sheets get SHEET_ID "Summary!A1:C10" --json | jq -r '.values[] | join(" | ")')
gog send --to "team@company.com" --subject "Data Update" --body "$DATA" --no-input
```

## Pattern 10: Batch Operations

Process multiple items efficiently.

```bash
# Archive all emails from a sender
THREAD_IDS=$(gog gmail search "from:newsletter@spam.com" --all --json | jq -r '.[].threadId')
for TID in $THREAD_IDS; do
  gog gmail thread modify "$TID" --add-labels "TRASH" --no-input
done

# Share a folder with multiple people
EMAILS="alice@co.com bob@co.com carol@co.com"
for EMAIL in $EMAILS; do
  gog drive share FOLDER_ID --type user --email "$EMAIL" --role writer --no-input
done

# Export all Google Docs in a folder as PDFs
gog ls --parent FOLDER_ID --json | \
  jq -r '.[] | select(.mimeType == "application/vnd.google-apps.document") | .id' | \
  while read DOC_ID; do
    gog docs export "$DOC_ID" --format pdf --output "./exports/${DOC_ID}.pdf"
  done

# Bulk create calendar events from a file
# events.jsonl: {"summary":"...", "from":"...", "to":"..."}
while IFS= read -r line; do
  SUMMARY=$(echo "$line" | jq -r '.summary')
  FROM=$(echo "$line" | jq -r '.from')
  TO=$(echo "$line" | jq -r '.to')
  gog cal create primary --summary "$SUMMARY" --from "$FROM" --to "$TO" --no-input
done < events.jsonl
```

---

## jq Recipes

Common jq patterns for `gog` JSON output.

```bash
# Extract specific fields
gog gmail search "query" --json | jq '.[].subject'

# Filter by condition
gog cal events --week --json | jq '.[] | select(.attendees | length > 3)'

# Count results
gog gmail search "is:unread" --json | jq 'length'

# Sort by date
gog cal events --week --json | jq 'sort_by(.start.dateTime)'

# Group by label/category
gog gmail search "label:work" --json | jq 'group_by(.labelIds[0]) | .[] | {label: .[0].labelIds[0], count: length}'

# Flatten nested arrays
gog gmail thread get THREAD_ID --json | jq '.messages[] | {from, subject, date}'

# Create TSV output for spreadsheet import
gog contacts list --json | jq -r '.[] | [.names[0]?.displayName, .emailAddresses[0]?.value, .phoneNumbers[0]?.value] | @tsv'
```

---

## Error Recovery Patterns

```bash
# Retry on transient errors
retry_gog() {
  local max_retries=3
  local count=0
  while [ $count -lt $max_retries ]; do
    gog "$@" && return 0
    local exit_code=$?
    if [ $exit_code -eq 8 ]; then  # retryable
      count=$((count + 1))
      sleep $((count * 2))
    elif [ $exit_code -eq 7 ]; then  # rate limited
      sleep 60
      count=$((count + 1))
    else
      return $exit_code  # non-retryable
    fi
  done
  return 1
}

# Usage
retry_gog gmail search "is:unread" --json
```
