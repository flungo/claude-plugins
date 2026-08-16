# /session-clean

Confirms whether the current chat session is safe to close or delete without losing context, or surfaces what still needs to happen first.

**Never write, commit, or file anything on your own initiative.**
Always propose the durable-write actions and get the user's go-ahead before touching a `CLAUDE.md`, opening an issue, producing a handoff, or anything else external.

## 0. What "clean" means

A session is clean when every thread it opened is in one of these states:

- **Done** — the work described actually happened (code written and applied, not just planned), not merely discussed.
- **Answered** — a question posed to the user got a real answer, not left hanging.
- **Durably deferred** — anything still open is captured somewhere a future agent could find *without this chat's context*: a `CLAUDE.md`, a code comment, an ADR, a commit message, or a GitHub issue.
  A decision that only lives in this conversation doesn't count, however clearly it was stated at the time.
- **Handed off, confirmed** — the user has said a `/handoff` for that thread landed in a new session.
  It has an owner and that session applies the same hygiene, so whatever must outlive it gets recorded there rather than here.

Not everything from the session needs a durable record.
One-off housekeeping — "which flag do I pass for X", already answered and acted on — doesn't need to survive the session ending.
Only capture what a future agent, or the user in three weeks, would actually need and couldn't otherwise reconstruct.

## 1. Sweep the session

Review the full conversation, start to end — not just the last few turns.
For each distinct thread of work or discussion, check for:

- **Open questions**: anything posed, by either side, that never got resolved.
- **Presented-but-undecided options**: tradeoffs or approaches laid out where no actual choice got made.
- **Soft deferrals**: "we can fix that later", "for now let's just…", "I'll come back to this".
  These are easy to lose because they don't read as open questions — they read as progress.
- **Silent assumptions**: a call made without flagging it, that the user might want to weigh in on, or that's worth recording so it isn't re-litigated later.
- **Useful facts or decisions with nowhere to live**: anything discovered or decided in-session that future work in this repo or area would benefit from knowing, but that currently only exists in this chat.

## 2. Classify each item

For each thread found in step 1:

- **Already durable** — it's in a `CLAUDE.md`, a comment, an issue, a commit message, or similar.
  Nothing to do; don't re-list it in the report just to show it was checked.
- **Finishable now** — small enough to complete before closing the session.
  Flag it as a candidate; don't finish it without saying so first (step 5).
- **Better handed off** — sits between the two either side of it, and needs **all three** of these to be true:
  - it wants doing with some urgency, so parking it in an issue undersells it;
  - it doesn't need this session's context, so it can be picked up cold;
  - it's big enough that finishing it here would drag this session out.

  Offer a `/handoff` for it — grouped in step 3, proposed in step 5.
  If any one of the three fails, it isn't this: work needing the session's context is *finishable now* or *needs durable capture*, and work that isn't urgent is just *needs durable capture*.
- **Needs durable capture** — real, unresolved, and worth recording.
  Needs a destination (step 4).
- **Handed off** — a `/handoff` was produced for this thread during the session.
  Which of two states it is in decides everything:
  - **Confirmed** (the user said it landed in a new session): it has an owner.
    Report it as handed off and nothing more — not as outstanding, not as done.
    Neither is yours to assert.
  - **Unconfirmed** (a document was produced and nothing was said afterwards): **ask whether it was ever handed off.**
    A handoff block that was never pasted leaves no new session, no issue, and no record, so the work has quietly evaporated rather than moved.
    If the answer is no, it drops back to *needs durable capture* and takes a destination like anything else.
- **Fine to drop** — resolved in a way that genuinely doesn't need a record (see step 0).
  Leave it out of the report entirely; don't pad the report with confirmations of things that didn't need doing.

Never fold a handed-off thread into *needs durable capture* without asking first, and never leave an unconfirmed one out of the report on the grounds that a handoff was offered.
Those are the two ways this thread goes missing: counted twice, or not at all.

## 3. Group the handoffs before proposing them

Classification is per-thread; a handoff is not.
Work out the *set* of new sessions in one pass over everything marked *better handed off*, and default to one.
A second session is a claim that two bodies of work genuinely don't want the same context, and it costs the user a whole conversation to re-establish what the first one already had.

Bundle into a single handoff when threads:

- **Depend on one another.**
  Never propose two sessions for dependent work.
  Splitting it doesn't resolve the dependency — it turns it into a wait, with the blocked half sitting in a session that has no idea when it clears.
  One session takes the whole chain: it carries the context through the first task and, once the second is unblocked, decides for itself whether to do it or hand it on.
- **Share a repo, a subsystem, or the same background.**
  Two threads needing the same files read and the same decisions understood are one handoff, however different their subjects.
- **Are small side tasks hanging off a main stream of work** — a stray TODO noticed in passing, a doc line to fix in a repo already being touched.
  These ride along with the stream they came from rather than justifying a session of their own.

Split only where the receiving sessions would share almost nothing: different repos, different context, and no ordering between them.
When it's marginal, bundle — a session that finds a thread doesn't belong can hand it off again, whereas context never carried can't be recovered.

## 4. Pick a destination for anything needing durable capture

- **A fact or decision future work in this area should know** — why something was built a certain way, a constraint discovered, a choice between approaches and why it was made: the nearest relevant `CLAUDE.md`.
  Check for a subdirectory-specific one before defaulting to the repo root.
  Read the existing file first and match its structure; don't append to the bottom if it already has organised sections.
- **Something that still needs to be *done*, not just known** — a bug, a follow-up task, unfinished work: a GitHub issue in the relevant repo.
- If a thread spans multiple repos or projects, route each part to its own destination rather than picking one repo for everything.
- If it's genuinely unclear which of the two fits — or whether it needs both, such as a decision recorded in a `CLAUDE.md` *and* a tracked follow-up task — ask rather than guessing.

## 5. Propose — don't write yet

Before touching anything, present the user a list:

- **Verdict up front**: clean and safe to delete, or not yet.
- **Finishable now**: what it is, and that you'd finish it now if they want.
- **Better handed off**: one entry per proposed session, as grouped in step 3 — not one per thread.
  For each: what it covers, why each thread in it meets all three tests, and what holds them together.
  Say plainly that they can decline and have any of it finished in-session or captured durably instead — a handoff is a proposal about how to move work, not a verdict on it.
- **Needs durable capture**: the fact, decision, or task; the proposed destination (which `CLAUDE.md`, or which repo's issue tracker); and a draft of what you'd actually write — not just "I'll note this somewhere".

Nothing gets written, committed, or filed until the user confirms.
A general go-ahead on the whole list is enough — don't demand a separate confirmation per item unless their response leaves it unclear which items they meant.

## 6. Execute confirmed items

- **`CLAUDE.md` edits**: read the current file, edit in place matching its existing structure and tone.
  Don't restate history the file already implies, and don't paste in raw chat quotes — write it the way the rest of the file is written.
- **GitHub issues**: check for an existing near-duplicate first — the GitHub MCP's search, or `gh issue list --search …` — before filing a new one.
- **Anything the user chose to finish now** instead of deferring: do that work, then re-check it against step 0 before including it in the verdict.
- **A handoff they accepted**: produce it in scoped mode — the threads it groups and nothing else, not the session — and then treat it as *handed off, unconfirmed* for the rest of this session.
  It becomes confirmed only when they say it landed.

## 7. Final report

- **Verdict**: clean and safe to delete, or what's still open and why.
- What was actually written and where — `CLAUDE.md` file and section, or issue number and link — for anything the user confirmed.
- Anything handed off during the session, named as handed off and left at that.
  Don't describe it as complete or incomplete; this session no longer knows.
- Anything left open because the user didn't confirm it or wanted to handle it themselves.
