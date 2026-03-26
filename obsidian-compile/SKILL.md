---
name: obsidian-compile
description: "Reads all new/unseen AI chat sessions (Claude Code + Cursor) from any project under /Users/ss/Code/, distills each into a chat note routed to the correct ticket folder under projects/{project}/{ticket}/, and maintains a living PROBLEM.md per ticket capturing decisions and current approach. Run daily from any directory. Use this skill whenever the user runs /obsidian-compile, asks to compile chats, wants to sync chat history to the vault, or wants to catch up on what was worked on."
---

# Obsidian Compile

Discover new AI chat sessions and Cursor plans, distill each into a structured note routed to the right feature ticket, and keep each ticket's `PROBLEM.md` up to date with decisions made and current approach.

**Core philosophy:**

- **Ticket-centric.** Work is organized by feature/ticket, not by code package. `projects/{project}/{ticket}/` is the unit of organization.
- **PROBLEM.md is the living doc.** Each ticket has one `PROBLEM.md` that accumulates goal, current approach, decisions, and open questions over time. Chat notes underneath it are immutable point-in-time records.
- **Ask when unsure.** If a session can't be matched to a ticket, finish everything else first, then ask the user explicitly.
- **All Code projects.** Compile sessions from any project under `/Users/ss/Code/` — not just the monorepo.

## Vault Structure

```
~/Code/vault/
  projects/
    monorepo/
      PC-415-scan-new-repo/
        PROBLEM.md
        plans/
          add-direct-project-creation.md
        implement-scm-agnostic-helpers.md
        fix-force-flag.md
    vault/
      obsidian-compile-redesign/
        PROBLEM.md
        brainstorm-ticket-centric-structure.md
    prompt-injection/
      prompt-injection-detection/
        some-ticket/
          PROBLEM.md
  meta/
    compile-state.json
```

## Step 1: Load Compile State

Read `~/Code/vault/meta/compile-state.json`:

```json
{
  "last_compiled": "2026-03-20T05:58:28Z",
  "seen_sessions": {
    "claude:SESSION_ID": "2026-03-20T05:58:28Z",
    "cursor:SESSION_ID": "2026-03-20T05:58:28Z"
  },
  "seen_plans": {
    "plan_filename_stem": "2026-03-20T05:58:28Z"
  }
}
```

If the file doesn't exist or `last_compiled` is null, this is the first run — everything is new.

## Step 2: Discover Vault — Build Ticket Registry

Scan `~/Code/vault/projects/` recursively. For each directory at depth 2 (e.g., `projects/monorepo/PC-415-scan-new-repo/`):

1. Extract the folder name (e.g., `PC-415-scan-new-repo`)
2. Parse any Jira-style ticket ID from it using the pattern `[A-Z]+-[0-9]+` (e.g., `PC-415`, `ASE-1330`)
3. Build a registry with both ticket ID and full folder name for matching:
   ```
   {
     "PC-415": { "path": "projects/monorepo/PC-415-scan-new-repo", "folder": "PC-415-scan-new-repo", "project": "monorepo" },
     "ASE-1330": { "path": "projects/ghas/ASE-1330-nil-severity", "folder": "ASE-1330-nil-severity", "project": "ghas" }
   }
   ```
4. Also keep a flat list of all folders (with their paths) for fuzzy matching in Step 5.

## Step 3: Discover Sessions

### Claude Code transcripts
- Glob: `~/.claude/projects/-Users-ss-Code-*/*.jsonl`
- **Exclude** the exact directory `-Users-ss-Code` (no suffix) — that's the Code root itself, not a project
- **Exclude** `-Users-ss-Code-vault` — vault sessions are meta (skill work, note editing) and shouldn't self-compile
- **Exclude** paths containing `/subagents/`
- Session ID: the JSONL filename stem
- State key: `claude:{sessionId}`
- **Derive project name**: strip the `-Users-ss-Code-` prefix from the directory name, then decode the path. The encoded name uses `-` as separator but directory names also contain `-`, so resolve ambiguity by checking against the real filesystem: list `/Users/ss/Code/` and match the longest prefix that corresponds to a real path. For example, `-Users-ss-Code-prompt-injection-prompt-injection-detection` → check if `Code/prompt-injection` exists, then if `Code/prompt-injection/prompt-injection-detection` exists → project name is `prompt-injection/prompt-injection-detection`.

### Cursor transcripts
- Glob: `~/.cursor/projects/Users-ss-Code-*/agent-transcripts/*/*.jsonl`
- **Exclude** exact directory `Users-ss-Code`
- **Exclude** `Users-ss-Code-vault`
- Session ID: the parent directory UUID
- State key: `cursor:{sessionId}`
- Derive project name the same way (strip `Users-ss-Code-` prefix, resolve against filesystem)

### Cursor plans
- Glob: `~/.cursor/plans/*.plan.md`
- Plan key: filename stem without `.plan.md`
- State key in `seen_plans`

### Determine new/updated items

For each discovered file:
- If state key NOT in seen map → **new**, process it
- If state key IS in seen map but file mtime (via `stat`) is newer than stored timestamp → **updated**, re-process it
- Otherwise → skip

If nothing is new, print "Nothing new to compile." and stop.

If more than 30 new sessions, process in batches of ~10 to avoid context overload.

## Step 4: Read & Distill Each Session

For each new/updated session, read the file. Extract:

### Claude Code JSONL format
- Each line is a JSON object with `type`, `message.content`, `timestamp`, `sessionId`
- Process only `type: "user"` and `type: "assistant"` messages
- For large files (>500 lines): read first 200 and last 50 lines

### Cursor JSONL format
- Each line: `{ "role": "user"|"assistant", "message": { "content": [{"type":"text","text":"..."}] } }`
- No timestamps — use file mtime as the date

### Skip filter

Discard the session entirely (but still mark as seen) if the first user message contains:
- `Cursor Command: review`
- `Cursor Command: Create Draft PR`

These are mechanical operations with no knowledge value.

### What to extract

Distill into:

1. **Title**: short descriptive slug in `lowercase-kebab-case` derived from the main topic
2. **What Was Asked**: concise summary of all user requests — bullet points if multiple. Summarize intent, don't copy verbatim.
3. **What Was Done**: the most important section. Include: files modified and how, key logic changes, build/test outcomes, any failed approaches before the final solution, config/infra changes.
4. **Decisions**: what was decided and why, each as a bullet with `[[wikilinks]]` for related concepts
5. **Problems Solved**: error → solution pairs
6. **Ticket ID**: scan the full transcript for Jira-style IDs (`[A-Z]+-[0-9]+`). Collect all found. The primary ticket is the one most frequently mentioned, or the one the user was actively fixing/building (not just referencing).
7. **Topics**: 3-6 concept slugs for tags (e.g., `oauth`, `rate-limiting`, `exporter-framework`)

**Rules:**
- No code blocks in notes — prose only
- "What Was Done" should be the most substantial section
- Short chats (<5 meaningful exchanges): minimal note with just What Was Asked + What Was Done
- All `[[wikilinks]]` must be `lowercase-kebab-case` — never spaces or Title Case

## Step 5: Route Each Session

For each distilled session, run through these steps in order — stop at the first match:

1. **Exact ticket ID match**: look up the primary ticket ID in the registry from Step 2.
   - Found → route there. Done.

2. **Child/related ticket match**: if the exact ticket isn't in the registry, check whether any *other* ticket IDs found in the transcript *are* in the registry. A session mentioning `PC-416` alongside `PC-415` (which has a folder) likely belongs in the `PC-415` folder — child tickets and related work often live together.
   - Found a registry match among the secondary ticket IDs → route there. Done.

3. **Fuzzy folder name match**: if no ticket ID matched at all, look at all existing folder names under `projects/` and judge whether any is semantically related to this session's topic. Consider words in the folder name, the project context, and the session's subject matter. This is intentionally judgment-based — a session about "wiz oauth token refresh" is a strong match for `PC-300-wiz-oauth-client`, not a new folder.
   - Confident match → route there. Done.
   - Not confident → route to `projects/__misc__/`. Done.

4. **No match at all** → route to `projects/__misc__/`.

**Key principle**: prefer routing to an existing folder over creating a new one. When in doubt, `__misc__` — never block or ask mid-run.

## Step 6: Write Chat Notes

For each resolved session, write to `~/Code/vault/projects/{project}/{ticket}/{title-slug}.md`.

Create the directory if it doesn't exist.

**Dedup check**: before writing, glob `projects/**/{title-slug}.md`. If the slug exists at the same path (re-processing), overwrite. If it exists at a different path, append `-2`, `-3`, etc.

Chat notes are **append-only** — never modify an existing note (except when re-processing an updated session).

### Chat note template

```markdown
---
type: chat
source: {claude-code or cursor}
project: {project-name}
ticket: {TICKET-ID}
date: {YYYY-MM-DD}
tags: [chat, {project}, {ticket-lowercase}, {topic-slug-1}, {topic-slug-2}]
session_id: {session-id}
---
# {Title}

## What Was Asked
{Concise summary of user requests. Bullet points for multiple asks.}

## What Was Done
{Detailed implementation account: files modified, key logic changes, build/test results, failed approaches.}

## Decisions
- {Decision with [[wikilinks]] to related concepts}

## Problems Solved
- {Error or problem → how it was fixed}

## Related
- [[{concept1}]]
- [[{concept2}]]
```

Omit empty sections. "What Was Asked" and "What Was Done" are always present.

## Step 7: Write Plan Notes

For each new/updated Cursor plan, read the `.plan.md` file and determine which ticket it belongs to (scan for Jira IDs in the plan content). Route to `~/Code/vault/projects/{project}/{ticket}/plans/{slug}.md`.

If no ticket match, add to the unresolved list.

### Plan note template

```markdown
---
type: plan
source: cursor
project: {project}
ticket: {TICKET-ID}
date: {YYYY-MM-DD from file mtime}
tags: [plan, {project}, {ticket-lowercase}, {topic-tags}]
---
# {Plan Name}

## Overview
{From plan's goal/overview}

## Status
- [x] {Completed todo}
- [ ] {Pending todo}

## Related
- [[{concept}]]
```

## Step 8: Create or Enrich PROBLEM.md

For each ticket folder that received new chat notes or plans, update its `PROBLEM.md`.

`PROBLEM.md` is a **living document** — read the current version, then merge in new information from the sessions just processed. Never blindly overwrite.

### Creating a new PROBLEM.md

When writing a note to a ticket folder that has no `PROBLEM.md` yet, create one by synthesizing what you know from the chat note(s):

```markdown
---
type: problem
ticket: {JIRA-ID}
project: {project-name}
status: in-progress
updated: {YYYY-MM-DD}
tags: [problem, {project}, {ticket-lowercase}]
---
# {Ticket Title — derived from chat content}

## Goal
{What this ticket is trying to achieve, synthesized from the chat sessions.}

## Current Approach
{How the problem is being solved — the approach in use as of the latest session.}

## Decisions
- {YYYY-MM-DD}: {Key decision and rationale}

## Open Questions
- {Anything unresolved or worth revisiting}
```

### Enriching an existing PROBLEM.md

Read current content, read the new chat note(s), then:
- Update **Current Approach** if the approach has changed or evolved
- Append new bullets to **Decisions** — never remove existing ones
- Add or resolve items in **Open Questions**
- Update the `updated` field to today's date
- Do NOT repeat information already present

## Step 9: Update Compile State


Write the updated `~/Code/vault/meta/compile-state.json`:
- Set `last_compiled` to current ISO 8601 timestamp
- Add/update entries in `seen_sessions` for every processed session (including skipped PR sessions)
- Add/update entries in `seen_plans` for every processed plan
- Keep all previously seen entries

## Step 11: Print Summary

```
Obsidian compile complete.
- 8 sessions processed (5 cursor, 3 claude-code)
- 2 sessions skipped (PR review/creation)
- 3 plans imported
- 4 PROBLEM.md files updated, 1 created
- 2 sessions routed to __misc__ (no ticket match)

New/updated notes:
  projects/monorepo/PC-415-scan-new-repo/implement-scm-agnostic-helpers.md
  projects/monorepo/PC-415-scan-new-repo/PROBLEM.md (enriched)
  projects/ghas/ASE-1330-nil-severity/fix-cvss-scientific-notation.md
  projects/ghas/ASE-1330-nil-severity/PROBLEM.md (created)
  projects/__misc__/cursor-lsp-troubleshooting.md
  projects/__misc__/vault-brainstorm-session.md
```

## Important Guidelines

- **All Code projects**: compile sessions from any `/Users/ss/Code/` subdirectory — not just monorepo. Exclude the bare `Code` root itself.
- **Finish before asking**: always process all resolvable sessions before prompting the user about unresolved ones. Don't block mid-run.
- **Chat notes are append-only**: never modify an existing chat note (except re-processing an updated session)
- **PROBLEM.md is living**: always read before writing, enrich and correct, never blindly overwrite
- **Wikilinks**: all `[[wikilinks]]` must be `lowercase-kebab-case` — spaces break Obsidian links
- **No code blocks**: prose only in all generated notes
- **Batching**: if >30 new sessions, process in batches of ~10 to avoid context limits
- **Large JSONL files**: read first 200 + last 50 lines for files over 500 lines
- **Idempotency**: running twice with no new sessions should produce "Nothing new to compile."
- **Vault path**: always use `~/Code/vault` as the vault root
