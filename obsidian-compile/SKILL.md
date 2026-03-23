---
name: obsidian-compile
description: "Reads all new/unseen monorepo chats from Claude Code and Cursor, distills them into detailed chat notes organized by monorepo package path, routes package-scoped plans alongside chats, and builds hierarchical _index.md indexes. Run daily from any project directory."
---

# Obsidian Compile

Discover new AI chat sessions (Claude Code + Cursor) and Cursor plans since the last compile, distill each into a detailed chat note routed to the correct monorepo package path, and maintain hierarchical `_index.md` indexes at every level. Each chat note captures what was asked, what was implemented, decisions made, and problems solved — no code dumps.

**Core philosophy:**

- **Monorepo only.** Only process transcripts from the monorepo project. Skip all other projects.
- **Package-path routing.** Chat notes live at `chats/monorepo/{monorepo-path}/{title-slug}.md` mirroring the actual monorepo directory hierarchy (e.g., `src/golang/internal.endor.ai/pkg/wiz/`).
- **`_index.md` is the index layer.** Every directory in the hierarchy gets an `_index.md` that serves as a Map of Content (MOC). Higher-level indexes are architectural summaries; deeper indexes have implementation detail.
- **Chat notes are append-only.** Once written, a chat note is never modified. Each captures a point-in-time session.
- **No hardcoded dictionaries.** Discover the existing folder hierarchy at compile time and route new files into it. Create new subfolders as needed.
- **`__misc__` for unresolvable paths.** Chats that cannot be mapped to a monorepo package go under `chats/monorepo/__misc__/`.
- **Package-scoped plans.** Plans related to a specific package live inside that package's directory under a `plans/` subfolder.
- **Skip noise.** Cursor Command sessions for PR reviews and PR creation are skipped entirely.

**Obsidian conventions (follow in ALL generated notes):**

- Tags in frontmatter arrays only — never inline `#tag` in body text
- Use nested slash tags for hierarchy: `monorepo/pkg/wiz`, `monorepo/service/endorctl`
- All `[[wikilinks]]` use lowercase-kebab-case — `[[wiz-exporter]]` not `[[Wiz Exporter]]`
- Every chat note has `up: "[[_index]]"` in frontmatter linking to its parent MOC
- `_index.md` files list child `_index.md` links first, then chat notes in Contents section
- No code blocks anywhere — prose only
- `aliases` in frontmatter for common shorthand names

## Step 1: Load Compile State

Read `~/Code/vault/meta/compile-state.json`. It has this shape:

```json
{
  "last_compiled": "2026-03-12T09:00:00Z",
  "seen_sessions": {
    "claude:SESSION_ID": "2026-03-12T09:00:00Z",
    "cursor:SESSION_ID": "2026-03-12T09:00:00Z"
  },
  "seen_plans": {
    "plan_filename_stem": "2026-03-12T09:00:00Z"
  }
}
```

If `last_compiled` is null, this is the first run — everything is new.

## Step 2: Discover Vault Structure

Before processing sessions, scan the vault to understand the current layout.

1. **Scan `chats/monorepo/`**: list all directories recursively to discover existing package paths. This tells you where existing chats live and what subfolders exist.

2. **Build index**: for each directory found, count the number of `.md` files (excluding `_index.md`). This determines which directories already have chat content.

## Step 3: Discover Sessions

### Claude Code transcripts
- Glob: `~/.claude/projects/-Users-ss-Code-monorepo/*.jsonl`
- **Skip** any path containing `/subagents/`
- Session ID: the JSONL filename stem (e.g., `125a519a-92b8-442b-98ee-8faca5cf8277`)
- State key: `claude:{sessionId}`

### Cursor transcripts
- Glob: `~/.cursor/projects/Users-ss-Code-monorepo/agent-transcripts/*/*.jsonl`
- Session ID: the parent directory name (the UUID)
- State key: `cursor:{sessionId}`

### Cursor plans
- Glob: `~/.cursor/plans/*.plan.md`
- Plan key: filename stem without `.plan.md`, e.g., `add-s3-exporter_076ec446`
- State key in `seen_plans`

### Filtering: monorepo only

- **Claude Code:** Only glob from `-Users-ss-Code-monorepo` directory. Ignore all other project directories.
- **Cursor:** Only glob from `Users-ss-Code-monorepo` project directory. Ignore all others.

### Determine new/updated items
For each discovered file:
- If its state key is NOT in the seen map → **new**, process it
- If its state key IS in the seen map but the file's mtime (check via `stat`) is newer than the stored timestamp → **updated**, re-process it
- Otherwise → skip

Collect all items to process. If there are none, print "Nothing new to compile." and stop.

If there are more than 30 new sessions, process them in batches. For each batch, read and distill the sessions, write notes, then move to the next batch. This avoids context overload.

## Step 4: Read & Distill Each Chat

For each new/updated session, read the JSONL file. Extract:

### Claude Code JSONL format
Each line is a JSON object. Key fields:
- `type`: `"user"` or `"assistant"` (skip `"file-history-snapshot"`, `"progress"`, etc.)
- `message.content`: string or array of content blocks
- `timestamp`: ISO 8601 string
- `sessionId`: session identifier

Read the user and assistant messages to understand the conversation.

### Cursor JSONL format
Each line is a JSON object:
- `role`: `"user"` or `"assistant"`
- `message.content`: array of `{"type":"text","text":"..."}`

No timestamps in the content — use the file's mtime as the date.

### Skip filter — discard these sessions entirely

After reading, check whether the session is a Cursor Command for PR review or PR creation. **Skip the session** (do not write any note, mark it as seen) if:

- The first user message starts with `--- Cursor Command: review ---` or contains `Cursor Command: review`
- The first user message starts with `--- Cursor Command: Create Draft PR ---` or contains `Cursor Command: Create Draft PR`

These sessions are mechanical CI/review operations and bloat the vault with no useful knowledge.

### What to extract from each chat

Distill the conversation into:

1. **Title**: A short descriptive title derived from the main topic (not the first message verbatim). Use lowercase-kebab-case for the filename slug.
2. **What Was Asked**: A concise summary of all user requests across the session. Use bullet points if there were multiple asks. Do NOT copy the raw query verbatim — summarize what the user wanted in clear language.
3. **What Was Done**: A detailed account of what the AI actually implemented or changed. Include:
   - Which files were modified and how
   - Key logic changes, function signatures added or changed
   - Build/test outcomes (did it pass? what broke?)
   - Any iterations or failed approaches before the final solution
   - Config or infrastructure changes made
4. **Decisions**: What was decided and why. Each as a bullet point. Use `[[wikilinks]]` for important concepts.
5. **Problems Solved**: Error → solution pairs. What went wrong, what fixed it.
6. **Concepts/Topics**: Extract 3-8 concept names that could be `[[wikilinks]]`. These should be reusable topic names like `retry-logic`, `s3-upload`, `exporter-framework`, `error-handling`, `graphql`, `protobuf`, etc. — not chat-specific phrases.
7. **Monorepo package path**: Determine which monorepo package this chat is primarily about (see Step 5 routing).

**Rules:**
- NO code blocks in the output. Prose only.
- "What Was Done" should be the most substantial section — this is the core value of the note. Be specific about file names and what changed.
- If a chat is very short (< 5 meaningful exchanges) or trivial, write a minimal note with just "What Was Asked" and "What Was Done".
- If you cannot determine a meaningful title, use the first few words of the first user message as a slug.
- **CRITICAL — wikilink format**: All `[[wikilinks]]` MUST use lowercase-kebab-case. Use `[[wiz-exporter]]` NOT `[[Wiz exporter]]` or `[[Wiz Exporter]]`. Obsidian does NOT convert spaces to hyphens — `[[Wiz exporter]]` looks for `Wiz exporter.md` which doesn't exist. Always use hyphens, never spaces.

## Step 5: Route to Monorepo Package Path

Determine the correct monorepo package path for each chat.

### Extraction strategy

1. **Scan for file paths** in the transcript. Look for patterns:
   - Go import paths: `internal.endor.ai/pkg/wiz`, `internal.endor.ai/service/endorctl/exporter`
   - Relative file paths: `pkg/wiz/client.go`, `service/endorctl/exporter/plugins/ghas/exporter.go`
   - Bazel labels: `//src/golang/internal.endor.ai/pkg/wiz:wiz`

2. **Normalize to full monorepo path**: strip any `//src/golang/` prefix from bazel labels, strip filename suffixes, and resolve to a directory. The target path is always relative to the monorepo root (e.g., `src/golang/internal.endor.ai/pkg/wiz`).

3. **Choose the dominant package**: the package directory most frequently referenced in the conversation. If multiple packages are referenced equally, pick the one the user was primarily working on (the one being modified, not just imported).

4. **Fallback — `__misc__`**: If no file paths are found in the transcript and the topic cannot be confidently mapped to a package, place the note under `chats/monorepo/__misc__/`. Do NOT place notes at the bare `chats/monorepo/` root.

5. **Write path**: `~/Code/vault/chats/monorepo/{resolved-path}/{title-slug}.md`

If the directory does not exist, create it.

### Dedup check

Before writing, check if the slug already exists anywhere under `chats/monorepo/` using a recursive glob: `chats/monorepo/**/{title-slug}.md`. If it exists at the same path (re-process), overwrite. If it exists at a different path, append `-2`, `-3`, etc. to the slug.

## Step 6: Write Chat Notes

Chat notes are **append-only** — once created, they are never modified.

### Chat note template

```markdown
---
type: chat
source: {claude-code or cursor}
project: monorepo
package: {full-monorepo-path}
up: "[[_index]]"
date: {YYYY-MM-DD}
tags: [chat, monorepo/{slash-separated-package-path}, {topic-slug-1}, {topic-slug-2}]
aliases: []
session_id: {session-id}
---
# {Title}

## What Was Asked
{Concise summary of all user requests in this session. Use bullet points for multiple asks.
NOT the raw query — summarize what the user wanted.}

## What Was Done
{Detailed implementation account:
- Files modified and how
- Key logic/function changes
- Build and test results
- Iterations or failed approaches before final solution}

## Decisions
- {Decision with [[wikilinks]] to related packages}

## Problems Solved
- {Error or problem encountered → how it was fixed}

## Related
- [[{concept1}]]
- [[{concept2}]]
```

**Field details:**
- `package`: the resolved monorepo path, e.g., `src/golang/internal.endor.ai/pkg/wiz`
- `up`: always `"[[_index]]"` — links to the parent directory's `_index.md` for tree navigation
- `tags`: include `chat`, the nested package tag (e.g., `monorepo/pkg/wiz`), and 2-5 topic slugs
- `aliases`: optional shorthand names for the note

If a section would be empty (e.g., no problems were solved), omit that section entirely. "What Was Asked" and "What Was Done" should always be present.

## Step 7: Write Plan Notes

For each new/updated plan, read the `.plan.md` file.

### Plan routing

- **ALL plans go to `~/Code/vault/plans/`**: Cursor plans and any plan notes imported from transcripts must always be written under the top-level `plans/` folder (never under `chats/monorepo/**/plans/`).
- **Human-friendly naming**: The note filename slug and `# {Plan Name}` should be derived from the plan content (goal/overview/todos) and should NOT just mirror the raw `.plan.md` filename. Prefer short, descriptive slugs (e.g., `wiz-client-refactor.md`, `centralize-log-redaction.md`), and append `-2`, `-3`, etc. on collision.

### Plan note template

```markdown
---
type: plan
source: cursor
project: {monorepo or other}
date: {YYYY-MM-DD from file mtime}
tags: [plan, {project-tag}, {monorepo-derived-tags}, {topic-tags}]
---
# {Plan Name}

## Overview
{From plan's overview field}

## Status
- [x] {Completed todo}
- [ ] {Pending todo}

## Related
- [[{concept1}]]
- [[{concept2}]]
```

**Tagging rules (plans):**

- **project-tag**:
  - Use `monorepo` if the plan references monorepo paths/targets/packages
  - Otherwise use `other`
- **monorepo-derived-tags**:
  - If the plan references one or more monorepo package paths (file paths, Go imports, Bazel targets), add one or more nested tags like `monorepo/pkg/wiz`, `monorepo/service/endorctl/exporter/plugins/wiz`
  - If multiple packages are referenced, include up to 3 package tags (pick the most prominent)
- **topic-tags**:
  - Add 2-5 additional tag slugs based on the plan themes (e.g., `auth`, `refactor`, `observability`, `sarif`, `rate-limit`, `bazel`, `gomock`)

Do not include `up` or `package` fields for plan notes; plans live in `~/Code/vault/plans/` and are navigated via search/tags.

The parent package's `_index.md` Contents section should list plan notes under a `### Plans` sub-heading, separate from chat notes.

## Step 8: Generate `_index.md` Files

`_index.md` files are **living knowledge bases** tied to the monorepo directory hierarchy. They are the **most valuable artifact** of the compile process — far more than just a list of links.

**CRITICAL: An `_index.md` is NOT a plain list of links.** It is a rich, synthesized document that tells a developer everything they need to know about a package by reading the chats. A bare link list is a failure. Every `_index.md` MUST have substantive prose in Overview, and where applicable, Architecture, Key Changes, Patterns, and Decisions sections — all synthesized from the chat notes in that directory.

### When to create or update

After writing all chat notes for this batch:

1. **Collect affected directories**: determine which directories received new chat notes or plan notes.

2. **Walk up to root**: for each affected directory, collect all ancestor directories up to `chats/monorepo/`. Every directory in the ancestry chain needs an `_index.md`.

3. **For each directory (leaf to root)**:
   - If `_index.md` does not exist → **create** it
   - If `_index.md` exists → **enrich** it (read existing, merge new info, update Contents)

### Creating a new `_index.md`

**Read ALL chat notes in the directory.** This is non-negotiable — you must read every chat note to synthesize an accurate, rich `_index.md`. Then write the `_index.md` following the template below.

For leaf-level packages (directories with actual chat notes), search the web for additional architecture context about the technology to enrich the Overview and Architecture sections.

For intermediate directories (like `src/`, `src/golang/`, `internal.endor.ai/`), write an architectural summary of what's below based on the chat notes in child directories.

### Enriching an existing `_index.md`

- Read the current content
- Read the NEW chat note(s) that were just written to this directory
- Merge new information:
  - Add new key points not already captured
  - Add new decisions with their dates
  - Add new patterns or gotchas
  - Summarize new changes made in the Key Changes section
  - If the new chat **contradicts** something, **update** the `_index.md` to reflect the latest understanding
  - **Rebuild the Contents section** to include all current child `_index.md` links, chat notes, and plan notes
- Do NOT repeat information already present
- Preserve existing content that is still valid
- Update the `updated` field in frontmatter to today's date

### `_index.md` template

```markdown
---
type: index
package: {full-monorepo-path}
updated: {YYYY-MM-DD}
tags: [index, monorepo/{slash-separated-path}]
aliases: [{short-name}]
---
# {Package/Directory Name}

## Overview
{What this package/directory is, its purpose, how it fits in the system.
This should be a rich paragraph (3-8 sentences) explaining what this package does,
why it exists, what problem it solves, and how it fits into the broader system.
Higher-level directories = broad architectural summary of all sub-packages.
Deeper directories = specific implementation detail about this package.
Synthesize this from all the chat notes — what was the user building/fixing here?}

## Architecture
{Internal structure, key components, interfaces, dependencies.
Describe the main types/interfaces, how they interact, what the data flow looks like.
Mention key files and their roles. Describe the dependency graph.
Only include for directories that represent actual code packages.
For intermediate directories like src/ or internal.endor.ai/, omit this section.}

## Key Changes
{A chronological or thematic summary of what was built, modified, or fixed in this package.
Synthesize from all chat notes — each chat represents work done. Summarize:
- What features were added or changed
- What bugs were fixed and how
- What refactors were performed
- What integrations were built
Group related changes together. This section tells the story of the package's evolution.}

## Patterns
{Conventions, best practices, gotchas specific to this area.
Synthesized from all chats — what patterns emerged? What mistakes were made and corrected?
What conventions does the codebase follow in this area?
Include auth patterns, error handling approaches, testing strategies, etc.}

## Decisions
- {YYYY-MM-DD}: {Decision and rationale, with [[wikilinks]] to related concepts}

## Contents
- [[child-folder/_index|Child Package Name]]
- [[chat-note-slug]]

### Plans
- [[plans/plan-note-slug]]
```

### Rules for `_index.md` generation

- **NEVER create a bare link list.** Every `_index.md` MUST have a substantive Overview section (minimum 3 sentences) synthesized from the chat notes. If a directory has chat notes, it MUST also have a Key Changes section summarizing what was done.
- **Hierarchy of detail**: `chats/monorepo/_index.md` is a 5-8 sentence project overview covering the monorepo's purpose, key subsystems, and what kinds of work has been done. `src/golang/_index.md` describes the Go backend architecture and all packages below it. `pkg/wiz/_index.md` has detailed component-level architecture, auth flows, API patterns, every decision made, and a thorough summary of all changes.
- **Read before writing**: Always read existing content before writing — enrich, never blindly overwrite
- **Contents section**: list child `_index.md` links first (sub-packages), then chat note links, then plan note links under a `### Plans` sub-heading — keeps the MOC scannable
- Omit empty sections (e.g., no Architecture for intermediate dirs, no Decisions if none recorded)
- Use `[[wikilinks]]` in lowercase-kebab-case to cross-reference other packages
- No code blocks — prose only
- `up` link is NOT needed in `_index.md` (the parent relationship is implicit from the folder hierarchy)

### What NOT to create

- Do NOT create `_index.md` for empty directories (directories with zero chat notes and zero child directories that have chat notes)
- Do NOT create trivial indexes for throw-away chats like `lorem-ipsum-test`

## Step 9: Update Compile State

Write the updated `compile-state.json` at `~/Code/vault/meta/compile-state.json`:
- Set `last_compiled` to the current ISO 8601 timestamp
- Add/update entries in `seen_sessions` with the current timestamp for each processed session (including skipped PR review/creation sessions — mark them seen so they aren't re-processed)
- Add/update entries in `seen_plans` with the current timestamp for each processed plan
- Keep all previously seen entries (don't remove them)

## Step 10: Print Summary

Print a report like:

```
Obsidian compile complete.
- 12 new chats processed (8 cursor, 4 claude-code)
- 3 sessions skipped (PR review/creation)
- 1 plan imported (2 package-scoped, 1 general)
- 6 _index.md files created, 2 enriched
- Packages: pkg/wiz, service/endorctl/exporter/plugins/wiz, service/endorctl/exporter/plugins/ghas

New/updated notes:
  chats/monorepo/src/golang/internal.endor.ai/pkg/wiz/wiz-auth-import-cycle-resolution.md
  chats/monorepo/src/golang/internal.endor.ai/pkg/wiz/_index.md (new)
  chats/monorepo/src/golang/internal.endor.ai/pkg/wiz/plans/wiz-client-refactor.md
  chats/monorepo/__misc__/cursor-lsp-troubleshooting.md
  plans/vault-restructure.md
```

## Important Guidelines

- **Monorepo only**: Skip any transcript not from the monorepo project. This is non-negotiable.
- **Skip PR reviews and PR creation**: Sessions that are Cursor Command review or Create Draft PR operations must be skipped (but still marked as seen in compile state).
- **Batch processing**: If there are many sessions (>30), process in batches to avoid context limits. Read ~10 sessions at a time, distill and write, then continue.
- **Large files**: Some JSONL files may be very large. Read the first 200 lines and last 50 lines to get the gist. If the file is under 500 lines, read it all.
- **Idempotency**: Running twice without new chats should produce "Nothing new to compile."
- **Chat notes are append-only**: Never modify an existing chat note (except when re-processing an updated session, which overwrites it).
- **`_index.md` files are living**: Always read before writing. Enrich, correct, and evolve — never blindly overwrite.
- **Wikilink format**: All `[[wikilinks]]` MUST be lowercase-kebab-case. NEVER use spaces or Title Case. `[[wiz]]` works, `[[Wiz]]` also works (case insensitive), but `[[Wiz exporter]]` does NOT (space ≠ hyphen).
- **Vault path**: Always use `~/Code/vault` as the vault root.
- **File checks**: Use stat/glob to check file existence and mtime, not assumptions.
- **Internet enrichment**: When creating leaf-level `_index.md` files for packages with chat notes, search the web for relevant documentation about the technology or API to enrich the Overview and Architecture sections. This provides context beyond what the chats contain.
- **`__misc__` routing**: Any chat that cannot be resolved to a monorepo package path goes under `chats/monorepo/__misc__/`. Never place notes at the bare `chats/monorepo/` root (only `_index.md` lives there).
- **Package-scoped plans**: Plans that reference specific monorepo packages are written to `chats/monorepo/{package-path}/plans/` not to the top-level `plans/` folder.
