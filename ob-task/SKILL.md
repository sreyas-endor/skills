---
name: ob-task
description: "Create a deeply detailed task note in the Obsidian vault under ~/Code/vault/tasks/{project}/{feature}/. Synthesizes the current conversation into a thorough document covering problem statement, deep context (file paths, call chains, data flows), options considered, implementation plan, decisions, and open questions. Use when the user wants to document a feature, ticket, or engineering task. Trigger on: 'create task', 'document this ticket', 'save this as a task', 'write up this feature', 'document what we discussed', 'create a task note', 'save task to vault', or whenever the user wants a permanent record of a technical discussion."
---

# ob-task

Synthesize the current conversation into a deeply detailed task note. The goal is a document thorough enough that someone reading it cold — with zero prior context — can fully understand the problem, the system, and exactly what to do next.

## Step 1: Detect project from working directory

Check the current working directory. Extract the project name as the directory directly under `/Users/ss/Code/` — e.g. `/Users/ss/Code/monorepo` → `monorepo`, `/Users/ss/Code/prompt-injection/pkg/foo` → `prompt-injection`.

Announce the detected project:
```
Project detected: monorepo
```

If the cwd is not under `/Users/ss/Code/` or is ambiguous, ask the user to confirm.

## Step 2: Pick a feature

List subdirectories under `~/Code/vault/tasks/{project}/`. Use `AskUserQuestion` with an `options` array — do not print a numbered list. Each option should show the feature name and file count, e.g. `"wiz-oauth (3 tasks)"`. Always include a final option: `"+ New feature..."`.

If the user picks "+ New feature...", follow up with another `AskUserQuestion` (free text) asking them to name it.

## Step 2.5: Fetch existing tags

Run the following to get the current vault tag vocabulary:

```bash
/Applications/Obsidian.app/Contents/MacOS/Obsidian tags format=json counts sort=count vault=vault
```

Run in the background with a 5-second timeout. Parse the JSON into a ranked tag list — you'll use this when writing frontmatter tags in Step 5.

## Step 3: Determine filename

Suggest a filename based on what was discussed:

- **With JIRA ticket**: `{JIRA-TICKET}.{feature-slug}.md` — e.g. `PC-415.scan-new-repository-when-its-created.md`
- **Without JIRA ticket**: `{feature-slug}.md` — e.g. `fix-github-enterprise-edit-workflow.md`

**JIRA ticket**: Extract from the conversation if present. If none was mentioned, omit it entirely.
**Feature slug**: Short lowercase-kebab-case description of the main topic.

Confirm with the user via `AskUserQuestion`:
- `"Use {suggested-filename}"`
- `"Enter a different name"`

If they pick a different name, follow up with a free-text question to get it.

Check if the file already exists at `~/Code/vault/tasks/{project}/{feature}/{filename}`. If it does, note it will be overwritten.

## Step 4: Synthesize the content

Read the **entire conversation** carefully. Extract everything that matters. Be exhaustive — this is a permanent record and the detail you capture now is the detail future-you won't have to reconstruct.

### 1. Problem statement
What is being solved? What pain does the user/customer experience? Be concrete: what fails, when, why. 2–4 sentences.

### 2. Deep context
This is the highest-value section. Cover everything that came up:
- System components involved — with **exact file paths** and **function names**
- Key code paths traced: entry point → handler → downstream calls
- Data models, schemas, or API contracts discussed
- State machines or lifecycle flows
- Existing behavior vs desired behavior
- Architectural constraints or invariants to be aware of
- Why the system works the way it does (historical reasons, if mentioned)

Use `###` subsections if multiple components were explored. When in doubt, include it. A future reader will thank you for the extra sentence; they'll never curse you for it.

### 3. Options considered
For each approach discussed:
- What it does (mechanism, not just a name)
- Pros — what exactly does this enable or avoid?
- Cons — what breaks, what's risky, what gets harder to change later?
- Edge cases or concerns raised

Omit this section only if no alternatives were discussed at all.

### 4. Decision & rationale
Which option was chosen, who decided, and the core reasoning. Be direct and specific.

### 5. Implementation plan
Concrete, file-level steps. Group by file. Include:
- Exact file paths that change
- What changes in each (function to add, field to update, interface to implement, test to write)
- Order of changes if it matters (e.g., define interface before implementation)
- Non-code prerequisites: config changes, feature flags, GitHub App settings, infra changes, etc.

### 6. Open questions
Anything unresolved, needing external confirmation, or flagged as a risk. Include confirmations that came back during the conversation (e.g., "✅ Confirmed 2026-03-25: X is true").

### 7. Related
Meaningful `[[wikilinks]]` to related notes, packages, services, or concepts mentioned. Use lowercase-kebab-case always — never spaces or Title Case.

## Step 5: Write the note

### Tag selection rules

1. **Reuse existing tags** — pick from the list fetched in Step 2.5. Prefer higher-count tags (they are the core taxonomy).
2. **Choose 3–6 tags total** — always include `task`, the project name, the jira ticket in lowercase (if present), and 1–3 topic tags from the existing list.
3. **Only propose a new tag** if no existing tag is semantically close enough. If so, ask the user to confirm via `AskUserQuestion`, showing the proposed tag alongside the closest existing alternatives.

Write the file to `~/Code/vault/tasks/{project}/{feature}/{filename}`. Create directories if they don't exist.

### Task note format

```markdown
---
type: task
project: {project}
feature: {feature}
jira: {JIRA-TICKET}
status: {implementing | planning | done | blocked}
date: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tags: [task, {project}, {jira-ticket-lowercase}, {topic-1}, {topic-2}]
aliases: [{jira-ticket-lowercase}, {short-feature-name}]
---

# {JIRA-TICKET}: {Human Readable Title}

## Problem

{2–4 sentences. What fails, when, why. Specific and concrete.}

## Context

{Rich background — file paths, function names, call chains, data flows. Use ### subsections for multiple components. Be exhaustive.}

## Options Considered

### Option 1 — {Name}
{What it does.}

**Pros:**
- {pro}

**Cons:**
- {con}

### Option 2 — {Name}
...

(Omit entirely if no options were discussed)

## Decision

{Which option, who decided, core reasoning. Direct and specific.}

## Implementation Plan

**Prerequisites:**
- {Non-code changes needed first, or "None"}

**Code changes:**

1. `{file-path}` — {what changes}
2. `{file-path}` — {what changes}
...

## Open Questions & Confirmations

- {❓ or ✅} {Question or confirmed fact, with date if confirmed}

(Omit if none)

## Related

- [[{concept-1}]]
- [[{concept-2}]]
```

**Omit the `jira` frontmatter field and ticket prefix from the title/filename if no JIRA ticket was mentioned.**

## Step 6: Confirm

If new:
> Written to `tasks/{project}/{feature}/{filename}`

If overwritten:
> Updated `tasks/{project}/{feature}/{filename}`

## Rules

- **No code blocks in the note body** — prose only. Describe code changes in plain English.
- **Wikilinks must be lowercase-kebab-case** — `[[github-webhook-handler]]` not `[[GitHub Webhook Handler]]`
- **Context is the whole point** — if you're unsure whether to include a file path or function name, include it. This section should be detailed enough that someone cold can navigate to the right place in the codebase.
- **Omit empty sections** — skip "Options Considered" if no alternatives came up, skip "Open Questions" if none remain.
- **Status**: `implementing` if coding starts soon, `planning` if still in design, `done` if complete, `blocked` if waiting on something external.
