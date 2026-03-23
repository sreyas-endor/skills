---
name: obsidian-create-task
description: "Create a structured task note in the Obsidian vault under ~/Code/vault/tasks/. Synthesizes the current conversation into a well-structured document with problem statement, deep context, options considered, implementation plan, decisions, and open questions. File is named <JIRA-TICKET>.<feature-name>.md. Use when the user wants to document a feature, ticket, or engineering task they've been discussing."
---

# Obsidian Create Task

Synthesize the current conversation into a structured task note and write it to `~/Code/vault/tasks/`.

## Step 1: Determine the filename

The filename format is always: `<JIRA-TICKET>.<feature-slug>.md`

- **JIRA ticket**: Extract from the conversation (e.g., `PC-415`, `UI-1234`). If no ticket was mentioned, use the arguments passed to this skill.
- **Feature slug**: A short lowercase-kebab-case description of the feature derived from the ticket title or the main topic of the conversation (e.g., `scan-new-repository-when-its-created`, `fix-github-enterprise-edit-workflow`).

Example: `PC-415.scan-new-repository-when-its-created.md`

Check if the file already exists at `~/Code/vault/tasks/{filename}`. If it does, overwrite it with the latest synthesized content.

## Step 2: Synthesize the content

Read the **entire conversation** carefully. Extract:

1. **Problem statement** — What is the user trying to solve? What pain does the customer/user experience? Be concrete and specific.

2. **Deep context** — Background needed to understand the problem. This should include:
   - Relevant system components and how they work (with specific file paths and function names from the conversation)
   - Any code paths traced during the discussion
   - Key data flows or state machines explored
   - Be thorough — this section should be detailed enough that someone reading it cold can understand the system

3. **Options considered** — If multiple approaches were discussed, list each one with:
   - What it does
   - Pros
   - Cons
   - Any concerns or edge cases raised

4. **Decision & rationale** — Which option was chosen and why. Include who made the decision (if mentioned) and the reasoning.

5. **Implementation plan** — Concrete, file-level steps to implement. Include:
   - Exact file paths that need to change
   - What changes in each file (function to add, field to update, etc.)
   - Any prerequisites (non-code changes like config, feature flags, GitHub App settings, etc.)

6. **Open questions** — Anything not yet resolved, confirmed externally, or needing follow-up. Include confirmations that came back during the conversation (e.g., "Confirmed 2026-03-16: X is true").

7. **Backlinks** — Extract meaningful `[[wikilinks]]` from the conversation. These should be:
   - Monorepo package names (e.g., `[[github-webhook-handler]]`, `[[scheduler-ingest]]`, `[[githubapp-reconciler]]`)
   - Key concepts discussed (e.g., `[[scan-states]]`, `[[reconcile-installation-projects]]`, `[[sync-org]]`)
   - File/service names that came up frequently
   - Use lowercase-kebab-case always — NEVER use spaces or Title Case in wikilinks

## Step 3: Write the note

Write the note to `~/Code/vault/tasks/{filename}.md` using this template:

```markdown
---
type: task
project: monorepo
jira: {JIRA-TICKET}
status: {implementing | planning | done | blocked}
date: {YYYY-MM-DD today}
updated: {YYYY-MM-DD today}
tags: [task, monorepo, {topic-slug-1}, {topic-slug-2}, {jira-ticket-lowercase}]
aliases: [{jira-ticket-lowercase}, {short-feature-name}]
---

# {JIRA-TICKET}: {Human Readable Feature Title}

## Problem

{2-4 sentences describing the user pain point and root cause. Be specific — mention what fails, when, and why.}

## Context

{Rich background section. Cover the relevant system components with file paths and function names.
Trace the key code paths discussed. Explain the data flow or state machine if relevant.
This section should be detailed enough that someone who wasn't in the conversation can understand
the system. Use subsections (###) if multiple components were explored.}

## Options Considered

### Option 1 — {Name}
{What it does.}

**Pros:**
- {pro}

**Cons:**
- {con}

### Option 2 — {Name}
...

(Omit this section entirely if no options were discussed — e.g. for straightforward bug fixes)

## Decision

{Which option was chosen, who decided, and the core reasoning. Be direct.}

## Implementation Plan

{Ordered list of concrete changes. Group by file. Include non-code prerequisites.}

**Prerequisites:**
- {Any non-code changes needed first}

**Code changes:**

1. `{file-path}` — {what changes}
2. `{file-path}` — {what changes}
...

## Open Questions & Confirmations

- {❓ or ✅} {Question or confirmed fact, with date if confirmed}

## Related

- [[{concept-1}]]
- [[{concept-2}]]
- [[{concept-3}]]
```

## Step 4: Confirm

After writing, tell the user:
> "Written to `~/Code/vault/tasks/{filename}.md`"

If the file already existed and was overwritten, say:
> "Updated `~/Code/vault/tasks/{filename}.md`"

## Rules

- **No code blocks in the note body** — prose only. Describe code changes in plain English.
- **Wikilinks must be lowercase-kebab-case** — `[[github-webhook-handler]]` not `[[GitHub Webhook Handler]]`
- **Be thorough in Context** — this is the highest-value section. Capture file paths, function names, state machines, and data flows that came up. Future-you will thank present-you.
- **Omit empty sections** — if no options were discussed, skip "Options Considered". If no open questions remain, skip that section.
- **Status field**: use `implementing` if coding is about to start, `planning` if still in design, `done` if complete, `blocked` if waiting on something.
- **Tags**: always include `task`, `monorepo`, the jira ticket in lowercase (e.g., `pc-415`), and 2-4 topic slugs derived from the main concepts discussed.
