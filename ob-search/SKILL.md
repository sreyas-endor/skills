---
name: ob-search
description: "Semantic hybrid search over the Obsidian vault memory folder (~/Code/vault/memory/) — past session notes, decisions, hacks, workarounds, technical context from prior Claude sessions. Use this skill whenever the user wants to recall past work, look up what they decided, find a prior session on a bug/feature, or reconstruct context they had before. Trigger on phrases like: 'search memory', 'search my notes', 'find in vault', 'search vault', 'recall', 'what did I note about', 'what did I work on', 'past session on', 'remember when we', 'did I write anything about', 'find notes about', 'look up prior', 'what was that thing we', 'recall the decision on'. Also trigger proactively when the user asks about past work, prior decisions, previous sessions, hacks, workarounds, or any context that might already be in their vault memory."
---

# ob-search

Semantic hybrid retrieval over `~/Code/vault/memory/` — session logs written by `ob-compact`. Combines vector search (nomic-embed) + BM25 (FTS5) via Reciprocal Rank Fusion, with tiered confidence labels.

**Scope:** semantic-only over `~/Code/vault/memory/**/*.md`. Does not cover `chats/`, `tasks/`, `plans/`, `daily/`, etc.

## Command

Always call via the pinned venv Python. Use `--json` so output is machine-readable:

```bash
/Users/ss/Code/vault-indexer/venv/bin/python /Users/ss/Code/vault-indexer/search.py "<query>" --json [options]
```

## Return structure — every result has these fields

| Field | Type | Purpose |
|---|---|---|
| `note_path` | absolute path | Feed to `Read` tool to get the full note |
| `project` | string | Frontmatter `project` (e.g. `monorepo`) |
| `feature` | string | Frontmatter `feature` (e.g. `bug-1119`) |
| `date` | string | YYYY-MM-DD from frontmatter |
| `granularity` | `"section"` \| `"whole"` | Chunk scope — one H2 section, or the entire note body |
| `section` | string \| null | H2 heading for section chunks; null for whole chunks |
| `content` | string | The actual chunk text, prefixed with `[project/feature § section]` |
| `tags` | string[] | Tags from the note's frontmatter |
| `score` | float | Ranking score (mode-dependent) |
| `score_label` | `"rrf"` \| `"dist"` \| `"bm25"` | How to interpret `score` |
| `vector_dist` | float \| null | Raw vector distance (null if not in vector candidate pool) |
| `bm25_rank` | float \| null | Raw BM25 rank (null if not in BM25 candidate pool) |
| `confidence` | `"high"` \| `"medium"` \| `"low"` | Tiered confidence label |
| `id` | int | Internal; ignore |

## When to `Read` the full note vs. use `content` as-is

Do **not** call `Read` reflexively — it burns tokens. Rules:

- `granularity: "whole"` → `content` already contains the entire note body. **Do not Read.**
- `granularity: "section"` + `confidence: "high"` + the chunk answers the question → use `content` as-is.
- `granularity: "section"` + the answer likely spans multiple sections → `Read note_path` once.
- User wants the raw markdown / frontmatter / file state → `Read note_path`.
- Answering across multiple notes → `Read` only the top-1–3 most relevant `note_path`s.

## Query formulation — the single most important rule

The search is **hybrid**: vectors catch paraphrased meaning, BM25 catches literal keywords. The best queries **combine both**:

- **Short identifier alone** (e.g. `BUG-1119`) — works, but lands in LOW confidence because evidence is thin
- **Pure concept** (e.g. `dead URL provisioning`) — works for paraphrase but may miss ticket numbers
- **Combined** (e.g. `BUG-1119 dead URL in GitHub check run when provisioning fails`) — **both systems score it high, you get HIGH confidence**

When the user's phrasing is sparse, enrich it with plausible conceptual context before searching. Don't wrap the query in quotes — FTS5 treats quotes as phrase literals.

## Filters

| Flag | Example | Effect |
|---|---|---|
| `--top-k N` | `--top-k 10` | Number of results returned (default 5) |
| `--project X` | `--project monorepo` | Only chunks from this project |
| `--feature Y` | `--feature bug-1119` | Only chunks from this feature |
| `--tag A` (repeatable) | `--tag go --tag sarif` | AND semantics — chunk must have all listed tags |
| `--granularity G` | `--granularity whole` | `section` or `whole` only |
| `--mode M` | `--mode vector` | `hybrid` (default), `vector`, or `bm25` |
| `--min-confidence C` | `--min-confidence medium` | Drops results below this tier |
| `--all-chunks` | `--all-chunks` | Turn off dedup-by-note (see all chunks) |

Use `--mode vector --min-confidence medium` when doing **conceptual paraphrase queries** where you want strong filtering — best precision/recall balance per eval.

## Vocabulary discovery — only when narrowing

If the first broad query returns too many weak results or spans multiple projects, list the available vocabulary and filter down. **Don't run this by default — only when a broad search didn't converge.**

```bash
# List all tags with note counts
python search.py --list tags

# List all projects
python search.py --list projects

# List all features (grouped by project)
python search.py --list features
```

## Confidence tiers

- **HIGH** — both vector distance and BM25 rank are strong → top result is reliable, use directly.
- **MEDIUM** — one signal is strong → top result is likely right, worth verifying by reading or running a tighter query.
- **LOW** — neither signal is strong. Three cases:
  - Very short query (1–2 tokens) that's still correct — common for exact-ID searches like `BUG-1119`. Read the note to confirm.
  - Paraphrased query with no literal overlap — rephrase by adding identifiers or concrete terms.
  - No good match exists in the corpus — answer the user from general knowledge and note that vault has no coverage.

## Worked examples

### 1. Exact ticket ID (short query, LOW confidence is normal)

```bash
python search.py "BUG-1119" --json --top-k 3
```

Expect top-1 to be the `bug-1119` note with `confidence: "low"` (short queries always land LOW — evidence is thin, but the answer is still correct). `granularity: "whole"` means the full note is in `content` — no `Read` needed.

### 2. Combined identifier + concept (preferred form)

```bash
python search.py "BUG-1119 dead URL in GitHub check run when provisioning fails" --json --top-k 3
```

Should return HIGH confidence because both BM25 (`BUG-1119`) and vector (conceptual phrasing) agree. Use `content` directly.

### 3. Pure paraphrase — rely on vectors

```bash
python search.py "understanding how MCP pipes auth and JSON-RPC work" --json --top-k 3
```

No ticket ID, pure concept. Returns the mcp architecture note at HIGH confidence. `granularity: "whole"` → `content` is the full note.

### 4. Section-level lookup (need just the "Decisions Made" part)

```bash
python search.py "decisions about PR comment formatting" --json --top-k 3
```

Likely returns a `granularity: "section"` hit for `Decisions Made` in `bug-1296-pr-comment-formatting`. If the user only wants decisions, `content` is enough. If they want surrounding context, `Read note_path` once.

### 5. Filter by project — scope to one codebase

```bash
python search.py "integration test broken" --json --project monorepo --top-k 5
```

Narrows to the monorepo project. Useful when the user's query could match multiple projects and you want to disambiguate.

### 6. Filter by feature — zoom into a specific bug/feature

```bash
python search.py "migration script" --json --feature bug-1415 --top-k 5
```

Returns only chunks from the bug-1415 feature directory.

### 7. Vocabulary discovery → then filter

```bash
# User asks: "what do we have on authentication?"
python search.py --list tags
# output includes: 3  authentication, 2  mcp, ...

python search.py "authentication flow" --json --tag authentication --top-k 5
```

Two-step: fetch the tag vocabulary, pick the right tag, run a filtered search.

### 8. Multi-tag AND filter

```bash
python search.py "fork PR review issues" --json --tag go --tag integration-test --top-k 5
```

AND semantics: chunk must have **both** tags.

### 9. Low-confidence → rephrase

First attempt:
```bash
python search.py "that migration thing" --json --top-k 3
```

If top result is LOW with weak distance — rephrase with more concrete terms:
```bash
python search.py "migration script platform source Azure DevOps" --json --top-k 3
```

Expect HIGH confidence on the second try.

### 10. Multi-note synthesis

User asks: "summarize everything we've done on the AGENTS.md work."

```bash
python search.py "AGENTS.md skill loader subagent layout cost experiments" --json --feature agentic-monorepo --top-k 5
```

Returns ~4 notes. `Read` the top 3 `note_path`s for full context, then synthesize. Use the `tags`, `date`, and `section` fields to group/order the results in the response.

### 11. Mode comparison when one mode underperforms

Paraphrase query with strong semantic but weak keyword overlap:
```bash
python search.py "clickable file paths in terminal output" --json --mode vector --min-confidence medium --top-k 5
```

Pure vector mode avoids BM25 noise. `--min-confidence medium` filters weak matches.

### 12. BM25-only for exact-text recall

User wants "the note that has exactly this error message":
```bash
python search.py "context.id == prRunUuid" --json --mode bm25 --top-k 5
```

BM25 finds literal string matches. Useful when the user quotes something from code.

### 13. Strict narrowing — "only the Decisions sections across the vault"

```bash
python search.py "decision on X" --json --granularity section --top-k 10
```

Combined with natural-language search, this surfaces only section chunks, which is useful when hunting for specific decision points.

### 14. Filter-first flow — "tell me every note about the MCP server"

```bash
python search.py "MCP server" --json --feature mcpserver --top-k 10 --granularity whole
```

Limits to whole-note chunks of one feature. Each result's `content` is a full note — iterate and synthesize without any `Read` calls.

## How to answer the user

After searching, cite the source note in your response using the full relative path with no line number (these are markdown, not code):

> Based on [memory/monorepo/bug-1119/2026-03-26-dead-url-brainstorm.md]: the fix is to check `p.sc == nil` in `OnFinish`...

Prefer quoting or paraphrasing from `content` over generating new prose — the note captured what was decided, don't override it.
