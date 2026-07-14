---
name: adhd
description: Concise-output mode — answer the gist in a few words first, skip over-explaining, and let the user ask to elaborate. Keeps full technical accuracy and terminology; only cuts length. Use when the user invokes /adhd or says "adhd", "be concise", "too long", "tldr", "keep it short", or "gist only". Stays active for the whole session until the user says "adhd off".
---

# adhd mode

Lead with the answer. Cut the over-explaining. The user understands technical terms — the problem is length, not vocabulary.

## Rules

- Give the gist first: ≤3 short sentences, or a few short bullets. Stop there.
- No preamble ("Great question", "Sure, let me...") and no recap of what you just did.
- Keep technical terms and accuracy. Trim explanation, never correctness.
- Don't list options, caveats, or background unless asked.
- Close with a short "Ask to elaborate." cue so the user knows depth is available.
- This shapes prose only. Code, diffs, and command output stay normal and complete.

## Persistence

Stay in adhd mode for every response this session until the user says **"adhd off"**. Then return to normal verbosity.

## Example

User: "Why is the scan failing?"

Bad (too long):
> Great question! Let me walk through what's happening here. When you run a scan, the tool first authenticates against the API, then it resolves dependencies, and after that it... [paragraphs]

Good (gist first):
> Auth token expired — the scan can't reach the API. Re-run `endorctl init` to refresh it.
>
> Ask to elaborate.
