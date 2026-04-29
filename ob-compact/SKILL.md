---
name: ob-compact
description: "Saves high-signal session context into the Obsidian vault under ~/Code/vault/memory/{project}/{feature}/. Use this skill whenever the user runs /ob-compact, wants to save the current session, capture decisions before context resets, checkpoint progress mid-feature, or says things like 'save this session', 'capture what we did', 'log this to the vault', or 'compact this session'. Trigger proactively when the user seems to be wrapping up a chunk of work."
---

# ob-compact

Save the meaningful parts of this session — decisions, current state, next steps — into the vault so the next session can pick up exactly where this one left off. The goal is a compact, high-signal record, not a transcript. Someone (or a future you) should be able to read this in 60 seconds and know exactly what happened and what to do next.

> This skill handles **manual** `/ob-compact` invocations (mid-session checkpoints). Automatic end-of-session compaction is wired via `SessionEnd` hook at `~/.claude/hooks/ob-compact-session-end.sh`, which runs a stripped-down Haiku variant of this logic. Both paths write to the same vault layout and share the session_id matching rule below.

## Step 1: Load session metadata

Read `~/.claude/state/current` (a symlink to the active session's state file). Parse JSON fields:

- `session_id` — required for the frontmatter + existing-note lookup
- `github_user` — required for frontmatter

If the state file is missing (e.g., the SessionStart hook didn't run), fall back to `session_id: "unknown-<timestamp>"` and `github_user: "unknown"`, and warn the user: "Session state not found; this note won't merge with prior ones from the same session."

## Step 2: Detect project from working directory

Extract the project name as the directory name directly under `/Users/ss/Code/` — e.g., `/Users/ss/Code/monorepo` → `monorepo`, `/Users/ss/Code/prompt-injection/some-subdir` → `prompt-injection`.

Inform the user:
```
Project detected: monorepo
```

If cwd is not under `/Users/ss/Code/` or is ambiguous, ask the user to confirm.

## Step 3: Look up existing notes for this session

Run:
```bash
grep -rlF "session_id: <session_id>" ~/Code/vault/memory --include="*.md" 2>/dev/null
```

For each match, read its frontmatter to learn its `(project, feature)`. These are the candidates for **update** vs **new**.

## Step 4: Pick a feature — match or fresh

**If** any existing-session note's feature cleanly fits the current work (same ticket ID, same topic) → select **update**, reuse its exact filename, preserve its original `date:` frontmatter.

**Else** → select **new**:
1. List subdirectories under `~/Code/vault/memory/{project}/`.
2. Use `AskUserQuestion` with arrow-key options — each option shows feature name and log count, plus a final `"+ New feature..."`. If the user picks new, follow up with a free-text `AskUserQuestion` for the name.
3. Filename: `YYYY-MM-DD-short-topic.md` (today's date).

## Step 5: Fetch existing tags

```bash
/Users/ss/Code/vault-indexer/venv/bin/python /Users/ss/Code/vault-indexer/search.py --list tags
```

Parse output; use as the tag vocabulary for Step 7.

## Step 6: Synthesize the session

Review the conversation and extract only what matters. Think like someone writing a handoff note — what does the next person (or next session) absolutely need to know?

Pull out:
- **Where things stand** — what's working, what's broken, overall progress toward the feature goal
- **Decisions made** — choices and why (especially non-obvious ones)
- **What was done** — key changes, not a blow-by-blow; focus on what shifted
- **Problems hit and how they were solved** — errors, dead ends, the fix that worked
- **What's next** — the clearest possible handoff
- **Key files touched** — just the most important ones

**If this is an update:** read the existing note first and produce a full superset (prior + current), not an append. Keep "Decisions Made" coherent when later decisions override earlier ones; merge "What Was Done" into a single flowing account; preserve `date:` frontmatter.

## Step 7: Tag selection rules

1. **Always reuse existing tags** — pick from Step 5. Prefer higher-count tags.
2. **Choose 3–6 tags total** — include `session-log`, the project name, the feature name, and 1–3 topic tags from the existing list.
3. **Only propose a new tag if** the session topic is genuinely novel and no existing tag is within reasonable semantic distance.
4. **If a new tag is needed**, confirm via `AskUserQuestion` with closest existing tags as options plus `"Use {proposed-tag}"`.

## Step 8: Write the file

Path: `~/Code/vault/memory/{project}/{feature}/{filename}.md`. Create directories if they don't exist.

### Session log format

```markdown
---
type: session-log
project: {project}
feature: {feature}
date: {YYYY-MM-DD}
session_id: {session_id}
github_user: {github_user}
tags: [session-log, {project}, {feature}, {topic-1}, {topic-2}]
---
# {Short descriptive title}

## Current State
{Where things stand — what's working, what's not, overall progress toward the goal}

## Decisions Made
- {Decision}: {why this choice was made}

## What Was Done
{Key changes made this session — what actually shifted}

## Problems & Solutions
- {Problem} → {what fixed it}

## Next Steps
{Concrete handoff — what should happen at the start of the next session}

## Files Touched
{Key files modified or created, one per line}
```

Omit any section that has nothing real to say. `Current State` and `Next Steps` should always be present.

## Step 9: Reindex

After writing, trigger the semantic indexer so the new/updated note is immediately searchable via `ob-search`:

```bash
/Users/ss/Code/vault-indexer/venv/bin/python /Users/ss/Code/vault-indexer/index.py --file <path>
```

The indexer is idempotent — it deletes+reinserts by file hash, so update and new paths are handled identically.

## Step 10: Confirm

Tell the user what was saved:

```
Saved to: memory/monorepo/wiz-oauth/2026-03-25-oauth-token-refresh.md
Action: new (or: updated existing note for this session)
Indexed.

Captured: current state, 2 decisions, next steps, 4 files touched.
```
