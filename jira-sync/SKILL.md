---
name: jira-sync
description: "Syncs Jira ticket statuses with GitHub PR states for ASE and BUG boards."
disable-model-invocation: true
---

# jira-sync

Sync Jira ticket statuses (ASE and BUG boards) with GitHub PR states in `endorlabs/monorepo`. The GitHub PR is the source of truth — open PRs mean "In Review", merged PRs mean "Done" (ASE) or "Fixed" (BUG). Also assigns the current sprint to ASE tickets that have no sprint set, but only for tickets being transitioned. The BUG board does not use sprints — never attempt sprint assignment on BUG tickets.

This skill works for any team member — it dynamically resolves both the Jira and GitHub identities at runtime.

## Core Rules

- **Never update anything without explicit user confirmation.** Always present proposed changes and wait for approval.
- **Only touch ASE and BUG projects.** Ignore all other Jira projects.
- **Only look at endorlabs/monorepo PRs.** No other repos.
- **Skip tickets already in a terminal state** (Done, Fixed, Won't Do, Duplicate, Not a Bug). Even if a PR exists for them, do not propose changes.
- **Merged PR wins over open PR.** If a ticket has both an open and a merged PR, treat it as merged.
- **Scope:** Current sprint + previous sprint + tickets with no sprint set. At most 2 sprints of data.

## Step 1: Resolve Identities

### Jira Identity
Use the `atlassianUserInfo` MCP tool (no parameters needed) to get the current user's Jira `account_id` and display name.

### GitHub Identity
Run `gh api user --jq '.login'` via Bash to get the GitHub username. If `gh` is not authenticated or the command fails, ask the user for their GitHub username using AskUserQuestion.

Announce both:
```
Jira: Sreyas S
GitHub: sreyas-endor
```

## Step 2: Fetch Jira Tickets

Query for non-terminal tickets across ASE and BUG where the user is assignee OR reporter, scoped to the last 2 sprints plus unset sprints.

Use the `searchJiraIssuesUsingJql` MCP tool with:
- **cloudId:** `endorlabs.atlassian.net`
- **jql:** `project in (ASE, BUG) AND (assignee = currentUser() OR reporter = currentUser()) AND status NOT IN (Done, Fixed, "Won't Do", Duplicate, "Not a Bug") AND (sprint in openSprints() OR sprint in closedSprints() OR sprint is EMPTY) ORDER BY project ASC, key ASC`
- **fields:** `["summary", "status", "sprint", "customfield_10020", "assignee", "reporter", "issuetype"]`
- **maxResults:** `100`
- **responseContentFormat:** `markdown`

The `closedSprints()` function returns recently closed sprints. Combined with `openSprints()` and `EMPTY`, this covers the current sprint, previous sprint, and unset tickets.

If the results include tickets from sprints older than the previous sprint, filter them out client-side by checking the sprint name/dates. Keep only current sprint, immediately previous sprint, and no-sprint tickets.

Save the list of ticket keys (e.g., `ASE-900`, `BUG-1415`) for the next step.

## Step 3: Fetch GitHub PRs

Use `gh` CLI to fetch PRs authored by the resolved GitHub username from endorlabs/monorepo. Fetch both open and merged PRs from roughly the last 4 weeks (covers 2 sprint window).

Run both commands in parallel:
```bash
gh pr list --repo endorlabs/monorepo --author <github-username> --state open --limit 100 --json number,title,state,body,url
```
```bash
gh pr list --repo endorlabs/monorepo --author <github-username> --state merged --limit 100 --json number,title,state,body,url --search "merged:>=$(date -v-30d +%Y-%m-%d)"
```

## Step 4: Match Tickets to PRs

For each PR, scan the `body` (description) field for ticket key patterns: `ASE-\d+` and `BUG-\d+`. Use simple string matching.

Build a mapping of `ticket_key -> PR info`:
- If a ticket matches multiple PRs, prefer the merged one. If multiple merged PRs exist, use the most recent.
- Track: PR number, PR state (open/merged), PR URL, PR title.

Only keep matches for tickets found in Step 2 (your Jira query results).

## Step 5: Determine Current Sprint

To assign sprint to tickets with no sprint, you need the current active sprint ID. Look at the tickets from Step 2 that DO have a sprint set — extract the sprint ID and name from `customfield_10020`. The active/current sprint is the one with `state: "active"`.

If no tickets have a sprint set (unlikely), use the Jira board API to find the active sprint.

## Step 6: Build the Action Plan

For each ticket from Step 2 that has a matching PR:

### Determine status transition
| PR State | Current Jira Status | Action |
|----------|-------------------|--------|
| Open | Not "In Review" | Transition to **In Review** |
| Open | Already "In Review" | No change |
| Merged | Not terminal | Transition to **Done** (ASE) or **Fixed** (BUG) |
| Merged | Already terminal | No change (shouldn't happen due to Step 2 filter) |

### Determine sprint action (ASE only)
Sprint assignment applies only to ASE tickets. Never set sprint on BUG tickets.
- If ASE ticket has `customfield_10020` null/empty AND is being transitioned -> set sprint to current active sprint
- If sprint is already set -> no change
- If BUG ticket -> skip sprint assignment entirely

### Transition IDs reference
These are the Jira transition IDs (global transitions, valid from any state):

**ASE board:**
- In Review: transition ID `101`
- Done: transition ID `31`

**BUG board:**
- In Review: transition ID `31`
- Fixed: transition ID `71`

## Step 7: Present Changes and Get Confirmation

Display a clear table of ALL proposed changes. For each ticket show the key info so the user can make an informed decision:

```
### Proposed Updates

| Ticket | Summary | Current Status | -> New Status | PR | Sprint Action |
|--------|---------|---------------|--------------|-----|---------------|
| ASE-900 | Add export support | In Progress | -> In Review | #1234 (open) | Set -> Sprint 47 |
| BUG-1415 | SARIF Azure error | To Do | -> Fixed | #1201 (merged) | — (BUG board) |

### No Changes Needed
| Ticket | Summary | Status | Reason |
|--------|---------|--------|--------|
| ASE-831 | Refactor auth | In Review | Already correct |
| ASE-845 | Add tests | To Do | No PR found |
```

After displaying the table, ask for confirmation using AskUserQuestion:
```
Proceed with these updates? (You can also say "skip ASE-900" to exclude specific tickets)
```

If the user wants to skip specific tickets, remove them and re-confirm the remaining list.

## Step 8: Execute Updates

Only after explicit user confirmation, apply the changes one ticket at a time.

### For status transitions
Use the `transitionJiraIssue` MCP tool:
- **cloudId:** `endorlabs.atlassian.net`
- **issueIdOrKey:** the ticket key (e.g., `ASE-900`)
- **transition:** `{"id": "<transition_id>"}` using the appropriate ID from the reference table

### For sprint assignment
Use the `editJiraIssue` MCP tool:
- **cloudId:** `endorlabs.atlassian.net`
- **issueIdOrKey:** the ticket key
- **fields:** `{"customfield_10020": {"id": <sprint_id>}}`

Report success/failure for each ticket as it completes:
```
ASE-900: In Progress -> In Review, Sprint set to Sprint 47
BUG-1415: To Do -> Fixed, Sprint set to Sprint 47
```

## Error Handling

- If a transition fails, report the error and continue with the next ticket. Don't abort the whole batch.
- If sprint assignment fails, still attempt the status transition.
- If both Jira and GitHub identity resolution fail, stop and explain what went wrong.
