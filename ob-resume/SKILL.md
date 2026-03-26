---
name: ob-resume
description: "Loads saved session context from ~/Code/vault/memory/ into the current session. Use this skill whenever the user runs /ob-resume, wants to resume work on a feature, asks to load previous context, says 'pick up where we left off', 'load my session logs', 'what was I working on', 'resume the X feature', or starts a session and wants to restore prior decisions and state. Always ask the user which sessions to load before loading anything."
---

# ob-resume

Load saved context from the vault so this session starts with full awareness of what was decided, what's in progress, and what comes next. The key principle: always show options and get confirmation before loading anything — the user decides what's relevant, not you.

## Step 1: Detect project from working directory

Check the current working directory. Extract the project name as the directory directly under `/Users/ss/Code/` — e.g., `/Users/ss/Code/monorepo` → `monorepo`, `/Users/ss/Code/prompt-injection/pkg/foo` → `prompt-injection`.

Announce the detected project:
```
Project detected: monorepo
```

If the cwd is not under `/Users/ss/Code/` or is ambiguous, use `AskUserQuestion` with an `options` array listing all projects found in `~/Code/vault/memory/` so the user can select with arrow keys.

## Step 2: Pick a feature

Scan `~/Code/vault/memory/{project}/` and list available features with their log counts and last-updated dates.

Use `AskUserQuestion` with an `options` array — do not print a numbered list. Each option should be descriptive, e.g. `"wiz-oauth — 3 logs, last: 2026-03-24"`. Order by most recently updated first so the active feature floats to the top.

Wait for the user's selection before continuing.

## Step 3: Pick sessions to load

List all `.md` files in the chosen feature folder, newest first. Extract the title from each file's `# heading` or filename.

Use `AskUserQuestion` with an `options` array and `multiSelect: true` so the user can check multiple sessions with arrow keys and space bar. Format each option as `"2026-03-24 — OAuth token refresh fix"`. Include a `"Load all"` option at the top.

Do not load anything yet. Wait for the user's selection.

## Step 4: Confirm then load

Use `AskUserQuestion` to confirm the selection before loading:

Show what's about to be loaded:
```
Ready to load:
  ✓ 2026-03-24 — OAuth token refresh fix
  ✓ 2026-03-22 — Client interface refactor
```

Offer two options: `"Yes, load these"` and `"Go back and change selection"`.

Once confirmed, read the selected files and bring their full content into context.

## Step 5: Summarize what's loaded

After loading, give a brief oriented summary so the user knows the context is active and what it contains — don't just say "loaded". Synthesize across sessions if multiple were loaded:

```
Context loaded for monorepo / wiz-oauth

Current state (as of 2026-03-24): OAuth token refresh is working for the standard
flow. The edge case where refresh tokens expire during a long-running scan is still
open.

Last decisions:
- Chose exponential backoff over fixed retry — avoids thundering herd on token expiry
- Kept token storage in-memory only, not persisted to disk

Next steps (from last session):
- Handle the expired refresh token case in pkg/wiz/auth/refresh.go
- Add integration test for token expiry during active scan

Ready to continue.
```

The summary should feel like a senior engineer just briefed you — specific, oriented, actionable.
