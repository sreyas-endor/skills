---
name: ob-search
description: "Agentic search over the Obsidian vault memory folder (~/Code/vault/memory/) — past session notes, decisions, hacks, workarounds, technical context from prior Claude sessions. Use this skill whenever the user wants to recall past work, look up what they decided, find a prior session on a bug/feature, or reconstruct context they had before. Trigger on phrases like: 'search memory', 'search my notes', 'find in vault', 'search vault', 'recall', 'what did I note about', 'what did I work on', 'past session on', 'remember when we', 'did I write anything about', 'find notes about', 'look up prior', 'what was that thing we', 'recall the decision on'. Also trigger proactively when the user asks about past work, prior decisions, previous sessions, hacks, workarounds, or any context that might already be in their vault memory."
---

# ob-search

Agentic retrieval over `~/Code/vault/memory/` — session handoff notes written by `ob-compact`. There is no index and no search binary: you find notes by reading the vault directly with `Grep`, `Glob`, and `Read`. You are the retrieval engine — formulate query variants, grep, rank by what actually matched, then read the most promising notes and synthesize.

**Scope:** `~/Code/vault/memory/**/*.md` only. Does not cover `chats/`, `tasks/`, `plans/`, `daily/`, etc.

## Vault layout — use the path as structured metadata

Notes live at:

```
~/Code/vault/memory/{project}/{feature}/{YYYY-MM-DD-short-topic}.md
```

The path itself carries `project`, `feature`, and `date` — so a `Glob` on the path is often the fastest first cut before you grep content. Each note also has frontmatter:

```yaml
---
type: handoff
project: monorepo
feature: bug-1119
date: 2026-03-26
session_id: ...
github_user: ...
tags: [handoff, monorepo, bug-1119, github, provisioning]
---
```

and H2 sections: `Problem`, `Goal`, `State`, `Files Changed`, `Next Steps`, `Decisions`, `Dead Ends`, `Commands`.

## Method

### 1. Extract search terms from the user's request

Pull out two kinds of terms and search for both:

- **Literal identifiers** — ticket IDs (`BUG-1119`), file names, symbol names, error strings, flags. These are exact — grep them verbatim (case-insensitive).
- **Concepts** — the paraphrased idea (`dead URL when provisioning fails`). Expand into several plausible keyword variants and synonyms, because the note may word it differently than the user did.

If the request is sparse (e.g. just a topic word), brainstorm 3–5 concrete terms the note likely contains before grepping.

### 2. Grep the vault

Run a case-insensitive, files-with-matches grep for each term. Start broad, then narrow.

```bash
grep -rliE "bug-1119|dead url|provisioning" ~/Code/vault/memory --include="*.md"
```

- Use alternation (`term1|term2|...`) to cover identifier + concept variants in one pass.
- `-l` lists matching files; `-c` counts matches per file (a cheap relevance signal); drop `-l` to see matching lines in context.
- To weigh a hit, follow up with `grep -c` per candidate, or grep the specific lines to see *how* the term is used.

If a first pass returns nothing, loosen: fewer/shorter terms, stem words (`provision` not `provisioning`), try synonyms.

### 3. Narrow with the path when results are broad

If a content grep spans many projects/features, cut by path first, then grep within:

```bash
# All notes for one project
ls ~/Code/vault/memory/monorepo/

# All features (subdirs) under a project
ls -d ~/Code/vault/memory/*/*/

# Notes for a specific feature
ls ~/Code/vault/memory/monorepo/bug-1119/

# Most recent notes across the vault (date is in the filename)
ls ~/Code/vault/memory/*/*/*.md | sort -t/ -k9 -r | head
```

Combine: restrict the grep to a subtree by pointing it at `~/Code/vault/memory/{project}/` or `.../{project}/{feature}/`.

### 4. Rank the candidates

Order by, roughly: literal-ID match > many concept-term hits > few hits. Prefer more recent notes (date in path/frontmatter) when two notes cover the same topic — later handoffs supersede earlier ones. Filter by `tags:` in frontmatter when the user's ask maps to an obvious tag.

### 5. Read the winners — but don't over-read

Reading burns tokens; be selective.

- **Answer is in one note** → `Read` just that note.
- **Answering across notes** (synthesis / "everything we did on X") → `Read` the top 1–3 only.
- **You already saw the answer in a grep context line** and it fully answers the question → skip `Read`, cite the note directly.
- Never `Read` every candidate reflexively — read top-ranked first and stop once the question is answered.

## Vocabulary discovery — only when a broad search didn't converge

If you can't guess the right project/feature/tag, enumerate the vocabulary, then re-search filtered. Don't do this by default.

```bash
# Tags with frequency
grep -rhF "tags:" ~/Code/vault/memory --include="*.md" | sort | uniq -c | sort -rn

# Projects
ls -d ~/Code/vault/memory/*/

# Features grouped by project
ls -d ~/Code/vault/memory/*/*/
```

## Worked examples

### 1. Exact ticket ID

```bash
grep -rliE "bug-1119" ~/Code/vault/memory --include="*.md"
```

Usually a single hit — `Read` it (or, if there are several, prefer the most recent by filename date).

### 2. Identifier + concept together (preferred)

```bash
grep -rliE "bug-1119|dead url|github check run|provisioning" ~/Code/vault/memory --include="*.md"
```

The note that hits the most terms is almost certainly the answer. Confirm with `grep -c` if several tie, then `Read` the top one.

### 3. Pure paraphrase — expand into keyword variants

User: "understanding how MCP pipes auth and JSON-RPC work."

```bash
grep -rliE "mcp|json-?rpc|auth token|stdio|jsonrpc" ~/Code/vault/memory --include="*.md"
```

No ID, so lean on synonym coverage. `Read` the strongest hit.

### 4. Section-level lookup — just the decisions

```bash
grep -rl "pr comment formatting" ~/Code/vault/memory --include="*.md"
# then, in the candidate, jump to the Decisions section:
grep -nA10 "## Decisions" ~/Code/vault/memory/monorepo/bug-1296-.../<note>.md
```

### 5. Scope to one project

```bash
grep -rliE "integration test|broken" ~/Code/vault/memory/monorepo --include="*.md"
```

### 6. Scope to one feature

```bash
grep -rliE "migration script" ~/Code/vault/memory/monorepo/bug-1415 --include="*.md"
```

### 7. Vocabulary discovery → then filter

```bash
grep -rhF "tags:" ~/Code/vault/memory --include="*.md" | sort | uniq -c | sort -rn
# see: authentication appears in a few notes, then:
grep -rliE "authentication|oauth|login flow" ~/Code/vault/memory --include="*.md"
```

### 8. Exact-text / error-string recall

The user quotes something from code or a log:

```bash
grep -rlF "context.id == prRunUuid" ~/Code/vault/memory --include="*.md"
```

Use `-F` (fixed string) for literal code/error text so regex metacharacters aren't interpreted.

### 9. No hit → loosen and retry

```bash
grep -rliE "that migration thing" ~/Code/vault/memory --include="*.md"   # nothing
# stem + concrete terms:
grep -rliE "migrat|azure devops|platform source" ~/Code/vault/memory --include="*.md"
```

### 10. Multi-note synthesis

User: "summarize everything we've done on the AGENTS.md work."

```bash
ls ~/Code/vault/memory/monorepo/agentic-monorepo/
grep -rliE "agents\.md|skill loader|subagent" ~/Code/vault/memory/monorepo/agentic-monorepo --include="*.md"
```

`Read` the top 1–3, order by date, synthesize; use each note's `tags`/`date` to group the answer.

## How to answer the user

Cite the source note using its full relative path with no line number (these are markdown, not code):

> Based on [memory/monorepo/bug-1119/2026-03-26-dead-url-brainstorm.md]: the fix is to check `p.sc == nil` in `OnFinish`...

Prefer quoting or paraphrasing what the note actually says over generating new prose — the note captured what was decided; don't override it. If nothing in the vault matches after loosening the search, say so plainly and answer from general knowledge instead of implying coverage that isn't there.
