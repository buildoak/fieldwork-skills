# gog Command Reference

Complete command reference for gogcli v0.11.0. Organized by service.
For pipeline examples, see `pipeline-patterns.md`. For auth, see `auth-setup.md`.

---

## Table of Contents

1. [Gmail](#gmail)
2. [Calendar](#calendar)
3. [Drive](#drive)
4. [Docs](#docs)
5. [Slides](#slides)
6. [Sheets](#sheets)
7. [Contacts](#contacts)
8. [Tasks](#tasks)
9. [Chat](#chat)
10. [People](#people)
11. [Forms](#forms)
12. [Groups](#groups)
13. [Classroom](#classroom)
14. [Apps Script](#apps-script)
15. [Keep](#keep)
16. [Utility Commands](#utility-commands)

---

## Gmail

`gog gmail` (aliases: `mail`, `email`)

### Read

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `gmail search <query>` | `find`, `query`, `ls`, `list` | Search threads using Gmail query syntax | `--max=10`, `--all`, `--fail-empty`, `--oldest`, `--timezone` |
| `gmail get <messageId>` | `info`, `show` | Get a message (full/metadata/raw) | `--format=full\|metadata\|raw`, `--headers=FIELDS` |
| `gmail messages <command>` | | Message operations subcommand | |
| `gmail attachment <messageId> <attachmentId>` | | Download a single attachment | |
| `gmail url <threadId>...` | | Print Gmail web URLs for threads | |
| `gmail history` | | Gmail history | |

**Gmail query syntax** (same as Gmail web search):
- `is:unread` -- unread messages
- `from:sender@email.com` -- from specific sender
- `to:recipient@email.com` -- to specific recipient
- `subject:keyword` -- subject contains keyword
- `has:attachment` -- has attachments
- `newer_than:1d` / `older_than:7d` -- relative date
- `after:2026/02/01` / `before:2026/02/17` -- absolute date
- `label:important` -- has label
- `in:inbox` / `in:sent` / `in:trash` -- in specific mailbox
- `filename:pdf` -- attachment filename
- Combine with AND (space), OR, NOT (-)

### Organize

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `gmail thread get <threadId>` | `info`, `show` | Get thread with all messages | `--format`, `--download-attachments`, `--output-dir` |
| `gmail thread modify <threadId>` | `update`, `edit`, `set` | Modify labels on all messages in thread | `--add-labels`, `--remove-labels` |
| `gmail thread attachments <threadId>` | `files` | List all attachments in thread | |
| `gmail labels list` | `ls` | List labels | |
| `gmail labels get <label>` | `info`, `show` | Get label details with counts | |
| `gmail labels create <name>` | `add`, `new` | Create a label | |
| `gmail labels modify <threadId>...` | `update`, `edit` | Modify labels on threads | `--add-labels`, `--remove-labels` |
| `gmail labels delete <label>` | `rm`, `del` | Delete a label | |
| `gmail batch delete <messageId>...` | `rm`, `del` | Permanently delete multiple messages | |
| `gmail batch modify <messageId>...` | `update`, `edit` | Modify labels on multiple messages | `--add-labels`, `--remove-labels` |

### Write

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `gmail send` | (top-level: `gog send`) | Send an email | `--to`, `--cc`, `--bcc`, `--subject`, `--body`, `--body-file`, `--body-html`, `--attach`, `--from`, `--reply-to-message-id`, `--thread-id`, `--reply-all`, `--quote`, `--track` |
| `gmail drafts list` | `ls` | List drafts | |
| `gmail drafts get <draftId>` | `info`, `show` | Get draft details | |
| `gmail drafts create` | `add`, `new` | Create a draft | Same flags as `send` |
| `gmail drafts update <draftId>` | `edit`, `set` | Update a draft | Same flags as `send` |
| `gmail drafts send <draftId>` | `post` | Send a draft | |
| `gmail drafts delete <draftId>` | `rm`, `del` | Delete a draft | |
| `gmail track <command>` | | Email open tracking | |

### Admin

| Command | Description |
|---------|-------------|
| `gmail settings <command>` | Settings and admin |

---

## Calendar

`gog calendar` (alias: `cal`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `cal calendars` | | List calendars | |
| `cal acl <calendarId>` | `permissions`, `perms` | List calendar ACL | |
| `cal events [calendarId]` | `list`, `ls` | List events | `--from`, `--to`, `--today`, `--tomorrow`, `--week`, `--days=N`, `--all` (all calendars), `--query`, `--max=10`, `--all-pages`, `--fail-empty`, `--fields`, `--weekday`, `--week-start` |
| `cal event <calId> <eventId>` | `get`, `info` | Get single event | |
| `cal create <calendarId>` | `add`, `new` | Create an event | `--summary`, `--from` (RFC3339), `--to`, `--description`, `--location`, `--attendees`, `--all-day`, `--rrule`, `--reminder`, `--event-color`, `--visibility`, `--transparency`, `--send-updates`, `--with-meet`, `--source-url`, `--attachment`, `--private-prop`, `--shared-prop`, `--event-type`, `--guests-can-invite/modify/see-others` |
| `cal update <calId> <eventId>` | `edit`, `set` | Update an event | Same flags as create |
| `cal delete <calId> <eventId>` | `rm`, `del` | Delete an event | |
| `cal respond <calId> <eventId>` | `rsvp`, `reply` | RSVP to an invitation | |
| `cal propose-time <calId> <eventId>` | | Generate URL to propose new time | |
| `cal search <query>` | `find`, `query` | Search events | |
| `cal freebusy <calendarIds>` | | Get free/busy | `--from`, `--to` |
| `cal conflicts` | | Find scheduling conflicts | |
| `cal colors` | | Show calendar color IDs | |
| `cal time` | | Show server time | |
| `cal users` | | List workspace users | |
| `cal team <group-email>` | | Events for all group members | |
| `cal focus-time` | `focus` | Create Focus Time block | `--from`, `--to`, `--auto-decline`, `--decline-message`, `--chat-status` |
| `cal out-of-office` | `ooo` | Create Out of Office event | `--from`, `--to`, `--auto-decline`, `--decline-message` |
| `cal working-location` | `wl` | Set working location | `--from`, `--to`, `--type` (home/office/custom) |

**Time format:** RFC3339 with timezone offset, e.g. `2026-02-18T09:00:00+00:00` (replace with your local timezone offset)
**Relative times:** `today`, `tomorrow`, `monday` (for `--from`/`--to` on events list)
**Recurrence:** `--rrule 'RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'`
**Reminders:** `--reminder popup:30m --reminder email:1d` (max 5)

---

## Drive

`gog drive` (alias: `drv`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `drive ls` | (top-level: `gog ls`) | List files in folder | `--parent` (folder ID) |
| `drive search <query>` | `find` (top-level: `gog search`) | Full-text search | `--max=20`, `--raw-query`, `--[no-]all-drives` |
| `drive get <fileId>` | | Get file metadata | |
| `drive download <fileId>` | `dl` (top-level: `gog download`) | Download a file | `--output`, `--format` (for Google Docs types) |
| `drive upload <localPath>` | `up`, `put` (top-level: `gog upload`) | Upload a file | `--name`, `--parent`, `--replace=FILE_ID`, `--mime-type`, `--convert`, `--convert-to=doc\|sheet\|slides`, `--keep-revision-forever` |
| `drive copy <fileId> <name>` | | Copy a file | `--parent` |
| `drive mkdir <name>` | | Create a folder | `--parent` |
| `drive delete <fileId>` | `rm`, `del` | Move to trash | `--permanent` |
| `drive move <fileId>` | | Move to different folder | `--parent` |
| `drive rename <fileId> <newName>` | | Rename a file | |
| `drive share <fileId>` | | Share a file | `--type`, `--email`, `--role`, `--domain`, `--anyone` |
| `drive unshare <fileId> <permissionId>` | | Remove permission | |
| `drive permissions <fileId>` | | List permissions | |
| `drive url <fileId>...` | | Print web URLs | |
| `drive comments <command>` | | Manage file comments | |
| `drive drives` | | List shared drives | |

**Drive search supports Google Drive query language with `--raw-query`:**
- `name contains 'report'`
- `mimeType = 'application/vnd.google-apps.document'`
- `modifiedTime > '2026-02-10'`
- `'FOLDER_ID' in parents`
- `sharedWithMe = true`

---

## Docs

`gog docs` (alias: `doc`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `docs create <title>` | `add`, `new` | Create a Google Doc | `--parent`, `--file` (markdown import) |
| `docs cat <docId>` | `text`, `read` | Print doc as plain text | `--max-bytes=2000000`, `--tab=NAME`, `--all-tabs` |
| `docs write <docId> [content]` | | Write content to doc | `--file`, `--replace`, `--markdown` |
| `docs insert <docId> [content]` | | Insert text at position | `--file`, `--index` |
| `docs delete <docId>` | | Delete text range | `--start=INT`, `--end=INT` |
| `docs find-replace <docId> <find> <replace>` | | Find and replace text | `--match-case`, `--all` |
| `docs update <docId>` | | Update content | |
| `docs info <docId>` | `get`, `show` | Get doc metadata | |
| `docs copy <docId> <title>` | `cp`, `duplicate` | Copy a doc | `--parent` |
| `docs export <docId>` | `download`, `dl` | Export doc | `--format=pdf\|docx\|txt`, `--output` |
| `docs comments <command>` | | Manage doc comments | |
| `docs list-tabs <docId>` | | List all tabs | |

**Key pattern: Markdown to Google Docs**
```bash
# Create new doc from markdown
gog docs create "Title" --file notes.md

# Overwrite existing doc with markdown (preserves formatting)
gog docs write DOC_ID --file notes.md --replace --markdown
```

---

## Slides

`gog slides` (alias: `slide`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `slides create <title>` | `add`, `new` | Create presentation | `--parent` |
| `slides create-from-markdown <title>` | | Create from markdown | `--content`, `--content-file`, `--parent`, `--debug` |
| `slides copy <presentationId> <title>` | `cp`, `duplicate` | Copy presentation | `--parent` |
| `slides info <presentationId>` | `get`, `show` | Get metadata | |
| `slides export <presentationId>` | `download`, `dl` | Export | `--format=pdf\|pptx`, `--output` |
| `slides list-slides <presentationId>` | | List slides with IDs | |
| `slides add-slide <presentationId> <image>` | | Add slide with image | `--notes` (speaker notes) |
| `slides delete-slide <presentationId> <slideId>` | | Delete a slide | |
| `slides read-slide <presentationId> <slideId>` | | Read slide content | (notes, text, images) |
| `slides update-notes <presentationId> <slideId>` | | Update speaker notes | `--notes` |
| `slides replace-slide <presentationId> <slideId> <image>` | | Replace slide image | |

**Markdown slides format:**
- Use `---` to separate slides
- `# Title` for slide titles
- Standard markdown for content

---

## Sheets

`gog sheets` (alias: `sheet`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `sheets get <spreadsheetId> <range>` | `read`, `show` | Get values from range | |
| `sheets update <spreadsheetId> <range> [values...]` | `edit`, `set` | Update values | |
| `sheets append <spreadsheetId> <range> [values...]` | `add` | Append values to range | |
| `sheets clear <spreadsheetId> <range>` | | Clear values | |
| `sheets format <spreadsheetId> <range>` | | Apply cell formatting | |
| `sheets notes <spreadsheetId> <range>` | | Get cell notes | |
| `sheets metadata <spreadsheetId>` | `info` | Get spreadsheet metadata | |
| `sheets create <title>` | `new` | Create spreadsheet | |
| `sheets copy <spreadsheetId> <title>` | `cp`, `duplicate` | Copy spreadsheet | |
| `sheets export <spreadsheetId>` | `download`, `dl` | Export | `--format=pdf\|xlsx\|csv`, `--output` |

**Range notation:** `Sheet1!A1:D10`, `Sheet1!A:D` (full columns), `Sheet1!1:5` (full rows)

---

## Contacts

`gog contacts` (alias: `contact`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `contacts search <query>` | | Search by name/email/phone | |
| `contacts list` | `ls` | List contacts | `--max` |
| `contacts get <resourceName>` | `info`, `show` | Get a contact | |
| `contacts create` | `add`, `new` | Create a contact | `--given-name`, `--family-name`, `--email`, `--phone`, etc. |
| `contacts update <resourceName>` | `edit`, `set` | Update a contact | |
| `contacts delete <resourceName>` | `rm`, `del` | Delete a contact | |
| `contacts directory <command>` | | Directory contacts | |
| `contacts other <command>` | | Other contacts | |

---

## Tasks

`gog tasks` (alias: `task`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `tasks lists <command>` | | Manage task lists | `list`, `create`, `update`, `delete` |
| `tasks list <tasklistId>` | `ls` | List tasks in a list | `--max` |
| `tasks get <tasklistId> <taskId>` | `info`, `show` | Get a task | |
| `tasks add <tasklistId>` | `create` | Add a task | `--title`, `--notes`, `--due`, `--parent` |
| `tasks update <tasklistId> <taskId>` | `edit`, `set` | Update a task | `--title`, `--notes`, `--due`, `--status` |
| `tasks done <tasklistId> <taskId>` | `complete` | Mark completed | |
| `tasks undo <tasklistId> <taskId>` | `uncomplete` | Mark needs action | |
| `tasks delete <tasklistId> <taskId>` | `rm`, `del` | Delete a task | |
| `tasks clear <tasklistId>` | | Clear completed tasks | |

---

## Chat

`gog chat`

| Command | Description | Subcommands |
|---------|-------------|-------------|
| `chat spaces` | Chat spaces | list, get, create, update, delete, members |
| `chat messages` | Chat messages | list, get, create, update, delete |
| `chat threads` | Chat threads | list, get |
| `chat dm` | Direct messages | list, get, create |

---

## People

`gog people` (alias: `person`)

| Command | Aliases | Description |
|---------|---------|-------------|
| `people me` | (top-level: `gog me`, `gog whoami`) | Show your profile |
| `people get <userId>` | `info`, `show` | Get user profile by ID |
| `people search <query>` | `find`, `query` | Search Workspace directory |
| `people relations [userId]` | | Get user relations |

---

## Forms

`gog forms` (alias: `form`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `forms get <formId>` | `info`, `show` | Get a form | |
| `forms create` | `new` | Create a form | `--title` |
| `forms responses <command>` | | Form responses | list, get |

---

## Groups

`gog groups` (alias: `group`)

| Command | Description | Key Flags |
|---------|-------------|-----------|
| `groups list` | List groups you belong to | `--max` |
| `groups members <groupEmail>` | List members of a group | `--max`, `--role` |

---

## Classroom

`gog classroom` (alias: `class`)

| Command | Description |
|---------|-------------|
| `classroom courses` | Courses (list, get, create, update, delete) |
| `classroom students` | Course students (list, get, add, remove) |
| `classroom teachers` | Course teachers (list, get, add, remove) |
| `classroom roster <courseId>` | Full roster (students + teachers) |
| `classroom coursework` | Coursework (list, get, create, update, delete) |
| `classroom materials` | Coursework materials |
| `classroom submissions` | Student submissions (list, get, grade) |
| `classroom announcements` | Announcements |
| `classroom topics` | Topics |
| `classroom invitations` | Invitations |
| `classroom guardians` | Guardians |
| `classroom guardian-invitations` | Guardian invitations |
| `classroom profile` | User profiles |

---

## Apps Script

`gog appscript` (aliases: `script`, `apps-script`)

| Command | Aliases | Description | Key Flags |
|---------|---------|-------------|-----------|
| `appscript get <scriptId>` | `info`, `show` | Get project metadata | |
| `appscript content <scriptId>` | `cat` | Get project source code | |
| `appscript run <scriptId> <function>` | | Run a deployed function | `--parameters` |
| `appscript create` | `new` | Create a project | `--title`, `--parent` |

---

## Keep

`gog keep` (Workspace only -- requires service account)

| Command | Description | Key Flags |
|---------|-------------|-----------|
| `keep list` | List notes | `--max` |
| `keep get <noteId>` | Get a note | |
| `keep search <query>` | Search notes (client-side) | |
| `keep attachment <attachmentName>` | Download attachment | |

---

## Utility Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `gog open <target>` | `browse` | Print web URL for a Google ID (offline) |
| `gog status` | `st` | Show auth/config status |
| `gog me` | `whoami` | Show your profile |
| `gog login <email>` | | Authorize and store token |
| `gog logout <email>` | | Remove stored token |
| `gog config <command>` | | Manage configuration (get/set/list/keys/path) |
| `gog schema [command]` | `help-json` | Machine-readable command schema |
| `gog exit-codes` | | Print stable exit codes |
| `gog agent exit-codes` | | Same as above |
| `gog time <command>` | | Local time utilities |
| `gog version` | | Print version |
| `gog completion <shell>` | | Generate shell completions |
