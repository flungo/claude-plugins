---
name: handoff
description: Fabrizio's "/handoff" command — produces a session handoff document so a fresh Claude session can pick up exactly where this one left off. Use it whenever he says "handoff", "create a handoff", "session handoff", "new session", "summarise for next session", or anything else suggesting he wants to continue this work in a different conversation, including wanting to share context with a new agent, start fresh, or resume later. If in doubt and the conversation holds meaningful work, lean toward triggering.
---

# /handoff

Produce a concise, structured handoff document that lets a fresh session continue the current work without re-reading the whole conversation.

## Output

Emit the document as a **single fenced markdown block** in the reply, with nothing else inside the fence.
That gives a one-click copy straight into a new session's opening message.

Not an artifact and not a file.
Both reach the same place by a longer route — open it, download it, re-upload it — when the destination is a paste into a text box.

Use a fence long enough to hold whatever is inside it: four backticks if the document itself quotes fenced code, so the block doesn't terminate early and split the document in half.

## Document structure

Use this template, omitting sections that are genuinely empty:

```markdown
# Handoff: [brief topic title]

## What this is about
[1–2 sentences: the project or task, and what the user is trying to accomplish.]

## What happened this session
[Key things accomplished, decided, or discovered. Gist only — not a transcript.]

## Current state
[Where things stand. What's complete, what's in progress, what's blocked.]

## Next steps
[What the user wants to do next, or the most logical continuation.]

## Key decisions & context
[Decisions made, preferences expressed, constraints to carry forward. The most
valuable section — capture anything that would take effort to re-establish.]

## Artifacts & files
[Files, code, documents, or other outputs. Reference by name only — do not
reproduce their contents.]

## Suggested skills for next session
[Optional: skills that would help with the next session's focus, each with a
one-line reason.]
```

## Principles

**Calibrate length to context.**
A short conversation warrants a short document; a long, complex one warrants more.
The goal is the minimum that lets a fresh agent continue without loss — terse enough not to fill a new session's context window immediately, complete enough that nothing crucial is dropped.
Leave out conversation filler, back-and-forth clarification, and anything the fresh agent can infer.
When in doubt, cut it.

**Capture the *why*, not just the *what*.**
An agent that understands the reasoning behind a decision makes better choices downstream.
Include motivation where it matters — "chose X over Y because of Z constraint".

**Reference, don't reproduce.**
Where content already exists in an artifact or a file, name and describe it rather than copying it in.
That artifact is the source of truth; a copy in the handoff is a second one that can drift.

**Tailor to the next focus.**
If the user says what the next session will work on — "handoff, next I'm doing the API layer" — emphasise the state and next steps relevant to that, and suggest skills accordingly.
With no focus given, cover the picture evenly.

**Omit empty sections silently.**
A section with nothing meaningful to say is left out entirely: no placeholder, no explanation of its absence.

## Triggering

The user may just say "handoff" with no further context.
That's fine — build the document from the whole conversation.
A focus given with the request shapes emphasis and the suggested skills; it doesn't narrow what the document covers.

## Relationship to `/session-clean`

These are the two halves of ending a session.
`/handoff` carries unfinished work into a fresh conversation; [`/session-clean`](../session-clean/SKILL.md) checks whether closing this one would lose anything that ought to be recorded durably instead.
Work that should outlive any session — a decision, a constraint, a follow-up task — belongs in a `CLAUDE.md` or an issue via `/session-clean`, not only in a handoff document that one future session reads once.
