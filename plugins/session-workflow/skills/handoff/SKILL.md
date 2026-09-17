---
name: handoff
description: Fabrizio's "/handoff" command — produces a session handoff document so a fresh Claude session can pick up exactly where this one left off, and where the session can start another session, offers to open the receiving one from it directly. Use it whenever he says "handoff", "create a handoff", "session handoff", "new session", "summarise for next session", or anything else suggesting he wants to continue this work in a different conversation, including wanting to share context with a new agent, start fresh, or resume later. If in doubt and the conversation holds meaningful work, lean toward triggering.
---

# /handoff

Produce a concise, structured handoff document that lets a fresh session continue the current work without re-reading the whole conversation.

## Two modes

**Whole-session** is the default: this session is ending, and everything in it carries forward.

**Scoped** applies when the request names a subset — "hand off the API layer work", "handoff for the follow-up task that just came up".
That subset leaves; this session continues without it.
The rest of the conversation is not summarised, mentioned, or carried.

A scope is not necessarily a single task.
Work that another scoped thread depends on, or that shares its repo and background, belongs in the same document rather than a second one: one session that carries the whole chain beats two that each hold half of it, and the receiving session can hand a piece on later if it turns out not to belong.
Where the scope is several threads, say so in the document — what it covers and in what order — so the next session isn't left inferring the shape of its own work.

The two differ in more than emphasis, so decide which one you're in before writing anything.

## Output

Emit the document as a **single fenced markdown block** in the reply, with nothing else inside the fence.
That gives a one-click copy straight into a new session's opening message, and it is the one form that works on every surface.

Not an artifact and not a file.
Both reach the same place by a longer route — open it, download it, re-upload it — when the destination is a paste into a text box.

Use a fence long enough to hold whatever is inside it: four backticks if the document itself quotes fenced code, so the block doesn't terminate early and split the document in half.

## Offer to open the receiving session

Where the session has a **`create_session`** tool, the receiving session can be started from here, with the document as its opening message, and the fenced block is then a review copy rather than something to paste.

The tool is the surface's, not this command's: Claude Code Web carries it on the harness's own MCP server, and a session elsewhere has it only if something configured that server for it.
So check the tools you actually have rather than assuming either way, and treat a server missing on this turn as not yet connected rather than absent.

**Offer it; never call it unasked.**
Put the fenced document in the reply as above, and beneath it one line offering to start the session from it.
The document is what the user reviews before it goes anywhere, and a session is theirs to start: it runs on their account like one they open themselves, and they may want the work continued in chat or on the local CLI instead.

On a yes, call the tool with:

- **`prompt`** — the document, verbatim.
  Exactly what they reviewed, with no wrapper around it; the document is already written to be a session's opening message.
- **`title`** — the handoff's title.
- **`source_url`** and **`source_revision`** — the repository the work is in, and the branch it is on.
  A spawned session inherits the calling session's environment, not its repositories, so with no source it starts with no repository at all; and the revision has to exist on the remote, since a branch that was never pushed fails the session's start.
  Push first.
  The tool takes one source, so where the work spans several repositories, pass the one the next steps are in and say in the document which others to add.
- **`outcome_branch`** — the branch the work continues on, normally the same one.
  It is what the receiving session's system prompt names as the branch to develop on and push to; without it the session is told only of an unnamed "designated branch" and picks its own.
- **`model`** — chosen for the work the document describes, per the **`delegation-conventions`** skill, a declared dependency.
  Omitted, it inherits this session's, which makes the receiving session's model an accident of where the work started.

Leave `environment_id` and `permission_mode` alone: inherited, they give the receiving session the same allowlist, plugins, and permissions as this one.

The tool returns the new session's id; report it as a link, `https://claude.ai/code/<id>`, so the user can open it.
Then confirm the session started: `get_session` on the id shows a `last_init_error` when the checkout failed, and a session that failed there never sees its prompt.
Fix the cause — usually the unpushed branch — archive the failed session, and create it again.

A session created this way is a **confirmed** handoff; see § After a scoped handoff.

In scoped mode the two sessions run at the same time.
Where both will push to the same repository, say in the document which branch is the receiving session's, so that neither session works on the other's.

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
In whole-session mode, a stated focus shifts emphasis without narrowing what the document covers — "handoff, next I'm doing the API layer" foregrounds that work but still carries the session.
With no focus given, cover the picture evenly.

**In scoped mode, filter by relevance — not by provenance.**
Include only what the receiving session needs to do its work, and leave every other thread out entirely rather than summarising it briefly.
But relevant does not mean "arose while discussing this thread": a constraint discovered elsewhere that *bounds* the scoped work belongs in the document, while a finished thread that merely happened nearby does not.
Judge each item by whether the receiving session would make a worse decision without it.

**Omit empty sections silently.**
A section with nothing meaningful to say is left out entirely: no placeholder, no explanation of its absence.

## Triggering

The user may just say "handoff" with no further context.
That's fine — build the document from the whole conversation.
A focus given with the request shapes emphasis and the suggested skills; it doesn't narrow what the document covers.

## After a scoped handoff

The thread is no longer this session's to carry, and the way you talk about it changes accordingly.

**Say it was handed off.
Never say more than that in either direction.**
Not "still outstanding", not "done" — neither is yours to assert, and both are wrong in a way the user can't easily catch.
This binds every later turn, not just the one that produced the document: end-of-session summaries, wrap-ups, PR descriptions, and `/session-clean` reports all inherit it.

**Until it lands, the handoff is only *offered*.**
A fenced block that is never pasted leaves nothing behind — no new session, no issue, no record.
So treat the work as transferred once it has landed, and as still in the air until then.
It lands in one of two ways: the user says they pasted it into a new session, or this session created that session with `create_session` and saw it start.
The second is confirmation in itself — the session exists, with the document as its first message — so there is nothing to ask.
The first is worth asking for explicitly, in one line, when the handoff covers something that matters: it is the difference between a thread that has an owner and a thread that has quietly evaporated.

**A confirmed handoff needs no further capture from you.**
The receiving session follows the same hygiene, so whatever must outlive it will be recorded there.

## Relationship to `/session-clean`

These are the two halves of ending a session.
`/handoff` carries unfinished work into a fresh conversation; [`/session-clean`](../session-clean/SKILL.md) checks whether closing this one would lose anything that ought to be recorded durably instead.

The division that matters: **a handoff transfers work to a session that is about to start, while durable capture makes work survive whether that session ever happens.**
A handoff document is not durable capture — it exists only in a chat reply until someone pastes it or a session is created from it.
So work that must not be lost wants both: a handoff to carry it now, and an issue or a `CLAUDE.md` entry so it still exists if the handoff is never used.
Neither command is sufficient alone for that case.
