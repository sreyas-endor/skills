---
name: ob-compact
description: "Saves high-signal session context into the Obsidian vault under ~/Code/vault/memory/{project}/{feature}/. Use this skill whenever the user runs /ob-compact, wants to save the current session, capture decisions before context resets, checkpoint progress mid-feature, or says things like 'save this session', 'capture what we did', 'log this to the vault', or 'compact this session'. Trigger proactively when the user seems to be wrapping up a chunk of work."
---

# ob-compact

Save the meaningful parts of this session — decisions, current state, next steps — into the vault so the next session can pick up exactly where this one left off. The goal is a compact, high-signal record, not a transcript. Someone (or a future you) should be able to read this in 60 seconds and know exactly what happened and what to do next.

## Step 1: Detect project from working directory

Check the current working directory. Extract the project name as the directory name directly under `/Users/ss/Code/` — for example, `/Users/ss/Code/monorepo` → `monorepo`, `/Users/ss/Code/prompt-injection/some-subdir` → `prompt-injection`.

Inform the user which project was detected:
```
Project detected from working directory: monorepo
```

If the cwd is not under `/Users/ss/Code/` or is ambiguous, ask the user to confirm.

## Step 2: Pick a feature

List the subdirectories under `~/Code/vault/memory/{project}/`. Include an option to create a new feature.

Use `AskUserQuestion` with an `options` array so the user can navigate with arrow keys — do not print a numbered list and ask them to type. Each option should show the feature name and log count, e.g. `"wiz-oauth (3 logs)"`. Always include a final option: `"+ New feature..."`.

If the user picks "New feature", follow up with another `AskUserQuestion` (free text) asking them to name it.

## Step 2.5: Fetch existing tags

Before synthesizing, run the following command to get the current tag vocabulary from the vault:

```bash
/Applications/Obsidian.app/Contents/MacOS/Obsidian tags format=json counts sort=count vault=vault
```

Run it in the background with a 5-second timeout (the app is interactive — kill it after output arrives). Parse the JSON and build a ranked list of existing tags. You will use this in Step 4 when writing the frontmatter.

## Step 3: Synthesize the session

Review the conversation and extract only what matters. Think like someone writing a handoff note — what does the next person (or next session) absolutely need to know?

Pull out:
- **Where things stand** — what's working, what's broken, overall progress toward the feature goal
- **Decisions made** — choices that were made and why (especially non-obvious ones)
- **What was done** — key changes, not a blow-by-blow; focus on what shifted
- **Problems hit and how they were solved** — errors, dead ends, the fix that worked
- **What's next** — the clearest possible handoff: what should happen at the start of the next session
- **Key files touched** — just the most important ones

## Step 4: Confirm filename and write

Suggest a filename based on the main topic: `YYYY-MM-DD-short-topic.md` (e.g., `2026-03-25-oauth-token-refresh.md`).

Use `AskUserQuestion` to confirm — show the suggested filename and offer:
- `"Use this filename"` (the suggestion)
- `"Enter a different name"`

If they pick a different name, follow up with a free-text `AskUserQuestion` to get it.

Then write the file to `~/Code/vault/memory/{project}/{feature}/{filename}.md`. Create directories if they don't exist.

### Tag selection rules

When choosing tags for the frontmatter:

1. **Always reuse existing tags** — pick from the list fetched in Step 2.5. Prefer higher-count tags (they are the core taxonomy).
2. **Choose 3–6 tags total** — include `session-log`, the project name, the feature name, and 1–3 topic tags from the existing list that best match the session content.
3. **Only propose a new tag if** the session topic is genuinely novel and no existing tag is within reasonable semantic distance (e.g., don't invent `#oauth-token-refresh` if `#oauth` already exists).
4. **If a new tag is needed**, ask the user to confirm before using it:
   > "No existing tag fits `{proposed-tag}` well. Closest existing: `{tag-a}` (N), `{tag-b}` (N). Use new tag `{proposed-tag}`, or pick one of these?"
   Use `AskUserQuestion` with the closest existing tags as options plus `"Use {proposed-tag}"`.

### Session log format

```markdown
---
type: session-log
project: {project}
feature: {feature}
date: {YYYY-MM-DD}
tags: [session-log, {project}, {feature}, {topic-1}, {topic-2}]
---
# {Short descriptive title}

## Current State
{Where things stand — what's working, what's not, overall progress toward the goal}

## Decisions Made
- {Decision}: {why this choice was made}

## What Was Done
{Key changes made this session — what actually shifted, not every step}

## Problems & Solutions
- {Problem encountered} → {what fixed it}

## Next Steps
{Concrete handoff — what should happen at the start of the next session}

## Files Touched
{Key files modified or created, one per line}
```

Omit any section that genuinely has nothing to say. Current State and Next Steps should always be present.

## Step 5: Confirm

Tell the user what was saved:

```
Saved to: memory/monorepo/wiz-oauth/2026-03-25-oauth-token-refresh.md

Captured: current state, 2 decisions, next steps, 4 files touched.
```
