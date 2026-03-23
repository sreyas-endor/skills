---
name: obsidian-reminders
description: "Manage reminders in the Obsidian vault. Supports adding, completing, updating, listing, and removing reminders with checkbox status tracking."
---

# Obsidian Reminders

Manage a single reminders file in the Obsidian vault at `~/Code/vault/reminders.md`. Each reminder has a checkbox status (`[ ]` for active, `[x]` for completed), descriptive text, a due date, and tracking dates.

## Reminders File

The file lives at `~/Code/vault/reminders.md`. If it does not exist, create it with the template below.

### File template

```markdown
---
type: reminders
updated: {YYYY-MM-DD}
---
# Reminders

## Active
{active reminders go here, newest at the bottom}

## Completed
{completed reminders go here, newest at the bottom}
```

### Reminder format

Each reminder is a single line:

- Active: `- [ ] {reminder text} — due: {YYYY-MM-DD} | added: {YYYY-MM-DD}`
- Completed: `- [x] {reminder text} — due: {YYYY-MM-DD} | added: {YYYY-MM-DD} | completed: {YYYY-MM-DD}`

## Operations

Always read `~/Code/vault/reminders.md` first before any operation. If the file does not exist, create it using the template above.

### Add

Add a new reminder to the **Active** section.

1. Read the reminders file
2. Append a new line under `## Active`: `- [ ] {reminder text} — due: {YYYY-MM-DD} | added: {today's date}`
3. If the user does not specify a due date, ask for one or use "no due date" as: `- [ ] {reminder text} | added: {YYYY-MM-DD}`
4. Update the `updated` date in frontmatter to today
5. Write the file

### Complete

Mark an active reminder as done and move it to the Completed section.

1. Read the reminders file
2. Find the reminder in the `## Active` section by matching the reminder text (partial match is fine — match the most specific one)
3. Remove it from the `## Active` section
4. Change `[ ]` to `[x]` and append `| completed: {today's date}`
5. Add the line to the bottom of the `## Completed` section
6. Update the `updated` date in frontmatter to today
7. Write the file

If no match is found, list all active reminders and ask the user which one to complete.

### List

Display all active reminders without modifying the file.

1. Read the reminders file
2. Print all lines under `## Active` that start with `- [ ]`
3. If there are completed reminders, mention how many are completed but don't list them unless asked

### Update

Modify the text or due date of an existing active reminder.

1. Read the reminders file
2. Find the reminder in the `## Active` section by matching the reminder text
3. Replace the old line with the updated text/date, keeping the `added` date unchanged
4. Update the `updated` date in frontmatter to today
5. Write the file

If no match is found, list all active reminders and ask the user which one to update.

### Remove

Delete a reminder entirely (not mark as complete — permanently remove).

1. Read the reminders file
2. Find the reminder by matching text (search both Active and Completed sections)
3. Remove the line entirely
4. Update the `updated` date in frontmatter to today
5. Write the file

If no match is found, list all reminders and ask the user which one to remove.

## Trigger Phrases

Use this skill when the user says any of:
- "add a reminder", "remind me to", "set a reminder"
- "complete reminder", "mark reminder done", "finish reminder"
- "list reminders", "show reminders", "what are my reminders"
- "update reminder", "change reminder", "edit reminder"
- "remove reminder", "delete reminder"
