---
name: session-clean
description: Fabrizio's "/session-clean" command (aliases "Session Clean?", "Safe to delete?") — a check on whether the current chat session can be closed or deleted without losing anything. Use it whenever he asks if a session is safe to close, safe to delete, done with, or finished, or invokes the command by name. It sweeps the whole conversation for work left undone, questions left unanswered, options left undecided, and facts or decisions that exist only in the chat, then proposes where each should be recorded. It never writes, commits, or files anything without his confirmation first.
---

# /session-clean

A check on whether the current chat session can be closed without losing context.
It sweeps the whole session for anything left undone, unanswered, or decided only in chat rather than recorded somewhere durable, and reports either that it is safe to delete or what still needs attention.

Full procedure: `references/session-clean.md`.
Read it before starting — classifying each thread, grouping whatever is better handed off, and picking a destination for the rest are what make the verdict trustworthy.

## Never write anything unprompted

This command **proposes and waits**.
It puts up the `CLAUDE.md` edits, GitHub issues, or handoffs it thinks are worth making — with a draft of the actual content — and touches nothing until the user confirms.

That is not caution for its own sake.
The command operates on the user's judgement about what mattered in a conversation, and that judgement is theirs: what looks like an unresolved thread from the transcript may be something they decided against, already know, or don't want recorded.
Acting on the sweep's own reading would quietly convert that judgement into commits and issues.

## Scope

The whole current chat session, not one repo.
If the session touched several repos or projects, findings are routed to each one's own `CLAUDE.md` or issue tracker rather than lumped together.

## Relationship to `/handoff`

These are the two halves of ending a session.
`/session-clean` asks whether anything durable would be lost by closing this one; [`/handoff`](../handoff/SKILL.md) carries unfinished work into a fresh one.
A session that comes back clean can simply be closed.
A session that doesn't, and whose remaining work is better continued than recorded, wants `/handoff` instead — or as well.
Where several threads want continuing, they usually want *one* new session between them rather than one each; the procedure's grouping step is where that gets decided.

**A handoff is not durable capture.**
It exists only in a chat reply until someone pastes it, so a thread that was handed off but never carried has evaporated rather than moved.
That is why the sweep treats a confirmed handoff and an unconfirmed one differently, and asks about the second rather than assuming either way.

## Tooling

Use whichever GitHub tooling the session has for issue search and creation — some environments offer only the MCP, others a `gh` CLI alongside it.

Where you are working through the MCP, **`connector-conventions:github`** (a declared dependency of this plugin) covers what its reads mangle and omit.
That matters for the near-duplicate check before filing an issue — an existing issue whose body reads as truncated has not been read, and dismissing it on that basis files the duplicate this command exists to avoid.
