---
name: obsidian-search
description: "Search the Obsidian vault at ~/Code/vault for notes, chats, tasks, plans, ideas, and daily entries. Use this skill whenever the user wants to find something in their vault, recall past work, look up notes, search for chat sessions, find tasks, check plans, or ask 'what did I note about X'. Trigger on: 'search obsidian', 'find in vault', 'search my notes', 'look up in obsidian', 'find notes about', 'search vault for', 'what did I note about', 'search chats for', 'find my tasks about', 'find my plans about', 'look in my vault', 'did I write anything about', 'what do I have on X'. Also trigger when the user asks about past work, coding sessions, or decisions and the vault might have relevant context."
---

# Obsidian Search

Search the Obsidian vault at `~/Code/vault` and return rich, detailed results. The vault is plain markdown on disk — no Obsidian app needed.

## Vault layout

```
~/Code/vault/
├── chats/          # AI coding session notes (cursor + claude code)
│   └── monorepo/   # sessions organized by monorepo package path
│       └── monorepo-session-summary.json  ← session index
├── tasks/          # task notes
├── plans/          # engineering plans
├── daily/          # daily notes
├── projects/       # project notes
├── ideas/          # idea notes
└── reminders.md
```

## Search strategy

### Step 1: Check for obsidian CLI

```bash
which obsidian 2>/dev/null
```

If found, use `obsidian search query="<term>"` for full-text search. Otherwise (most likely), proceed with direct file search below.

### Step 2: Search using ripgrep

Run these in parallel to cover content + frontmatter:

```bash
# Full-text content matches (with 2 lines context)
rg -n -i "<query>" ~/Code/vault --type md -C 2 -l

# Tag/frontmatter matches
rg -n "tags:.*<keyword>" ~/Code/vault --type md

# Title matches
rg -n "^# .*<keyword>" ~/Code/vault --type md -i
```

For broad searches, also scan `_index.md` files which serve as Maps of Content and summarize directories.

### Step 3: Read matching files

For every matched file, read it fully with the Read tool. Don't summarize snippets — return the actual content. Group results by folder.

## Special handling: chats/ folder

Chat notes are the most information-dense content in the vault. When results land in `chats/`, do all of the following:

**A. Read the full note.** Chat notes have this structure:

```yaml
---
type: chat
source: cursor | claude       # which AI tool
session_id: <uuid>
package: src/golang/...       # monorepo package path
date: YYYY-MM-DD
tags: [chat, monorepo/pkg/..., ...]
project: monorepo
---
```

Body sections to read and return fully:
- **What Was Asked** — the original request
- **What Was Done** — implementation summary
- **Decisions** — key choices made (with `[[wikilinks]]`)
- **Problems Solved** — bugs and blockers resolved
- **Related** — linked concepts

**B. Cross-reference session-summary.json.** For any chat result, also read:

```
~/Code/vault/chats/monorepo-session-summary.json
```

Find the entry matching `session_id` to get: `source`, `status`, `title`, `slug`, `package_path`, `vault_path`, `date`.

**C. Return everything:** source tool (cursor/claude), session_id, package path, date, full note sections. Don't abbreviate chat notes.

## Output format

Group results by folder. For each result:

```
### [note title] — chats/monorepo/src/.../slug.md
- **Source:** cursor | claude  (chats only)
- **Session:** <session_id>    (chats only)
- **Package:** src/golang/...  (chats only)
- **Date:** YYYY-MM-DD
- **Tags:** tag1, tag2

[full note content]
```

After all results, show: `Found N matches across K files in [folders]`

## What to return

- **Chat notes:** full content of all sections — never truncate
- **Tasks / plans:** full content
- **Daily notes:** full content
- **Regular notes:** full content up to ~100 lines; summarize if longer
- If there are more than 10 matches, prioritize: chats > tasks/plans > daily > other; mention remaining count

## Tips

- If the query is broad (e.g., "wiz"), also check `_index.md` files for that topic — they're great summaries
- If the user asks about a specific date, search `daily/` for that date's note
- If the user asks about a specific package path, search `chats/monorepo/<path>/` directly
- The `monorepo-session-summary.json` is a fast index — for queries about session count or recent sessions, read it first before scanning individual notes
