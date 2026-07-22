# Documentation Model

The organising model for a repository's `docs/` tree, and the maintenance discipline that keeps it trustworthy.
Documentation is a first-class deliverable — treat stale docs as a defect, not a cosmetic issue, because a future session reads them as truth.

## The Diátaxis split — four kinds of doc

Docs are either **task-oriented** (how-to) or **information-oriented** (reference), following the [Divio/Diátaxis](https://diataxis.fr/) split; ADRs add a third, **decision-oriented**, kind.
That yields four directories under `docs/`, each with a `README.md` index:

| Directory | Kind | Holds | Lifecycle |
|---|---|---|---|
| `docs/decisions/` | Decision | ADRs — the *why* behind a structural choice | Permanent; numbered, never deleted or renumbered |
| `docs/plans/` | Task (one-time) | A single build/onboarding procedure tracked to completion | Ephemeral — retired (deleted) once done |
| `docs/runbooks/` | Task (repeatable) | A how-to run indefinitely (rotation, onboarding, importing) | Permanent; no completion checkboxes |
| `docs/reference/` | Information | Descriptive lookup docs (settings catalogues, name registries, coverage maps) | Permanent; no steps, exists to be looked up |

The distinction that most often trips people:

- A doc with **steps to follow that will be run more than once** is a
  **runbook**, not a reference.
- A doc with **no steps, that exists to be looked up**, is a **reference**, not
  a runbook.
- A doc with **steps that are followed exactly once and then done** is a
  **plan**, not a runbook.

Only create a directory when it has content — an empty `runbooks/` or `reference/` is noise until the first doc lands.

## README index per directory — kept current in the same commit

Every one of the four directories has a `README.md` that indexes its contents.
The index is the single-glance truth for that directory; a stale row is actively misleading.

Keep the index current in the same commit as any doc you add, change, or remove — never a follow-up.
This is a best practice for humans and agents alike, not an agent-only chore.

Each index does two jobs: it lists the directory's contents, and it documents that doc type's expected structure — the template or required sections a new doc of that kind should follow.
The decisions index carries the ADR template (see `references/adr-template.md`) and one summary row per ADR; the plans index describes a plan's shape (a status row plus numbered checkbox steps) and carries one status row per plan; a runbooks or reference index likewise states what a runbook or reference doc should contain.
Don't update a doc without also updating its parent README row.

**Ordering.** Unless a doc type has a clear chronology, order pages — and their index rows — alphabetically.
ADRs look like the exception, but they use zero-padded monotonic numbers (`001`, `002`, …) precisely so that alphabetical order *is* chronological order — so ADRs sort alphabetically too.

## Callouts — two distinct devices, kept separate

These docs are read by both humans and AI agents.
Two callout devices mark two different things; they are complementary, not substitutes for each other.

**Agent-directed instruction** — an instruction to an *agent* following the doc, telling it what to *do* (as opposed to a fact everyone needs):

> **🤖 Agent** — \<the single action the agent should take\>

Reserve it for agent behaviour, and keep it to **one action per callout**.
Shared facts and ordinary steps stay as normal prose — don't dress a fact up as an agent callout.

**Uncertainty flag** — something that is probably stale or unverified and *can't be checked without live access* (a running server, a private dashboard, a value only the owner holds):

> **Verify:** \<what is uncertain and why it couldn't be confirmed\>

Use it instead of silently leaving a doubtful statement, or silently dropping it.
A `> **Verify:**` says "a human with access should confirm this"; a `> **🤖 Agent**` says "an agent reading this should act".
Never collapse one into the other.

## Plan lifecycle — ephemeral, retired in two PRs

Plans are short-lived working documents.
A plan has numbered checkbox steps (`- [ ]` / `- [x]`) and a status row in `docs/plans/README.md`; its permanent output lives in ADRs, runbooks, and the code/config it produced — **not** in the plan.

1. **Planning** — the plan is being written, or is written but not yet being executed; its README row reads "Planning".
   This is the review window for the plan's shape, before any work runs against it.
2. **In progress** — execution has started; the README row reads "In progress".
   Mark steps `[x]` as they complete.
   The PR that completes a tracked step is the one that ticks it and flips its status — not a later follow-up.
3. **Complete** — when every step is done, set the README row to
   `Complete (YYYY-MM-DD)`, update the "Active work" section of `CLAUDE.md`, and
   open a PR.
4. **Retired** — once the completion PR is merged **and the user confirms**,
   open a *second* PR that deletes the plan file and removes its README row.
   Git history preserves it; nothing is lost.

The two-PR split exists to give the user a review gate before anything is deleted.
Before retiring, an **independent verification** — a pass distinct from whoever executed the plan, e.g. a subagent or a second reviewer — confirms that every load-bearing fact the plan produced has been persisted to its permanent home: decisions to ADRs, information to reference docs, repeatable procedures to runbooks, and final architecture to the README or architecture doc.
A plan is safe to delete only once nothing load-bearing lives in it alone.

> **🤖 Agent** — never delete a plan in the same PR that marks it complete;
> retirement is always a separate, user-confirmed PR.

**Plans are ephemeral — never reference them from permanent docs or code.** Architecture, decisions, and repeatable procedures belong in their permanent home (README, ADRs, runbooks, code comments), expressed as *outcomes* — what the thing is, what was decided, when — not as a link to the plan that produced it.
The one exception is the "Active work" section of `CLAUDE.md`, which may link a plan **while it is in progress**; remove the link when the plan is retired.

## Staleness discipline

Stale docs mislead, so maintenance is not optional — it happens after every change and again at session end.

**After a change:**

- Recording or revising a decision → write or update the ADR and its index row
  (`references/adr-template.md`).
- Introducing a new resource, feature, or component → update the repo `README`
  ("what this manages" / equivalent) and any affected reference doc.
- Advancing a plan → tick its steps and update both the plans README and
  "Active work".
- Touching anything under `docs/` → refresh that directory's README index in
  the same commit.

**End-of-session staleness scan** — before finishing, search for anything that may have drifted:

- Values that change over time — versions, hostnames, IPs, owner/workspace/
  provider/module/secret names — and correct any that moved.
- Open decisions (marked `[ ]` or "OPEN DECISION") that were resolved this
  session — close them in the docs.
- Whether `CLAUDE.md` "Active work" (and any "current blocker") still reflects
  reality.
- Every README row whose underlying document was touched — audit the whole row,
  description and status, against the document's current state.

> **🤖 Agent** — if something is probably stale but you can't verify it without
> live access, add a `> **Verify:** …` callout rather than leaving silent
> uncertainty or guessing.

The session-end doc-maintenance checklist (`references/stop-hook.md`) is a backstop for this scan, not a replacement — and it fires *after* the turn, too late to land a tracker update in the PR that earned it, so do the tracker updates as you go.

## Semantic line breaks

Write top-level prose **one sentence per line** (semantic line breaks / [sembr](https://sembr.org/)).
Source diffs then show which *sentence* changed instead of reflowing a whole paragraph, and review comments land on the right line.

This also means **no maximum line length**: a sentence lives on a single line however long it runs, so any line-length lint (markdownlint's `MD013`) is disabled rather than left to fight the convention.
A hard wrap column and one-sentence-per-line are mutually exclusive, and the sentence is the meaningful unit — so the wrap limit goes.
This is the same intent behind the reflow tooling and the Markdown-validation workflows in the sibling `stalwart.flungo.net` repo (`reflow.py` and its `markdown-validation` plan).

Scope and exceptions:

- Applies to **top-level prose paragraphs**. Leave lists, tables, headings,
  code blocks, and metadata lines (e.g. a `**Date:**` line) alone — they are
  not reflowed.
- It changes only **source whitespace**, never rendered output — a sentence per
  line renders identically to a hard-wrapped paragraph.
- Preserve hard-break blocks (lines ending in two spaces or a backslash);
  reflowing them would change the render.

Because it is render-neutral, a migration can be **gated on render-equivalence**: reflow the source, render both versions to normalised HTML, and keep the change only where the HTML is byte-identical, leaving any file that would render differently untouched.
A reference implementation of exactly this render-gated approach — paragraph-level reflow with a CommonMark render gate and abbreviation-aware sentence splitting — lives in the sibling `stalwart.flungo.net` repo at `docs/plans/markdown-validation/reflow.py`; it is a one-time best-effort migration tool, not repo CI.

> **🤖 Agent** — write new prose one sentence per line from the start; don't
> hard-wrap a paragraph and rely on a later reflow pass.
