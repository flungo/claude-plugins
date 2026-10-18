# ADR Template — Nygard Format

Architecture Decision Records live in `docs/decisions/` and use Michael Nygard's original lightweight format — the industry-default form that records just enough to make a decision durable: its Status, the Context that forced it, the Decision itself, and the Consequences.
This is the canonical shape; use it verbatim.

## Canonical shape

```markdown
# ADR-NNN: Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated

## Context

The forces and problem motivating the decision — what made a choice necessary.

## Decision

What we will do, in active voice ("Adopt X", "Split Y") — the choice itself, not
a discussion of options.

## Consequences

What becomes easier or harder as a result.
```

`NNN` is the zero-padded sequential number (`001`, `002`, …); the filename is `NNN-short-slug.md` (e.g. `002-documentation-and-adr-model.md`).
The `# ADR-NNN: Title` heading and the two `**Date:**` / `**Status:**` metadata lines are required; so are the three `## Context` / `## Decision` / `## Consequences` sections.

## Optional Consequences subsections

Under `## Consequences`, two subsections are allowed but **not required**:

```markdown
## Consequences

### Positive

- What this makes easier or better.

### Negative — trade-offs

- What this costs, or the judgement calls it leaves open.
```

Include a subsection only when there is something real to put in it — don't pad a record with empty `### Positive` / `### Negative` headings.
A short flat `## Consequences` paragraph or list is perfectly correct when the consequences don't split cleanly into wins and costs.

## Numbering, status, and supersession

- **Sequential numbering, never reused.**
  The next ADR takes the next number.
  ADRs are **never deleted or renumbered** — the number is a stable reference.
- **Parallel branches collide on ADR numbers — by design.**
  Because index rows are ordered and numbers are sequential, two branches that each grab "the next" number pick the *same* one; whoever merges second hits a merge conflict and must renumber.
  Always take the next *available* number, and if your ADR depends on one being introduced on another branch, **stack your branch on that one rather than working in parallel** — don't write dependent ADRs as sibling branches.
- **Status is a lifecycle**, not a quality bar: `Proposed` → `Accepted`, and later possibly `Superseded by ADR-MMM` or `Deprecated`.
- **Supersession keeps both files.**
  When a new ADR replaces an old one, the old ADR stays in place with its `**Status:**` changed to `Superseded by ADR-MMM`, and the new ADR notes what it supersedes.
  Never edit the superseded decision away — the chain is the audit trail, and the superseded ADR is [frozen](#superseded-and-deprecated-adrs-are-frozen) from then on.

## Amending an accepted ADR

An ADR records a decision at a point in time, so what it says stays true *of that moment* even once the world has moved past it.
Four different things can happen to an accepted record, and each takes its own mechanism:

| What changed | Mechanism |
| --- | --- |
| The text was wrong when written — a typo, a link that never resolved, a mis-stated number | Edit in place, unmarked: it was never true, so there is nothing to date. |
| A link's target has since moved or been renamed | Edit in place, unmarked: the link is upkeep, not part of what was recorded. |
| The text was true when written, and something since has overtaken it | **Amend** — add, never rewrite (below). |
| The decision, or the reasoning it rests on, no longer holds | **Supersede** — a new ADR, and a status change on the old one (above); [reconsidering an amended ADR](#reconsidering-an-amended-adr) says when. |

**An amendment adds; it does not edit the original away.**
Leave the sentence or bullet as written and put the new fact immediately beneath it, dated:

> **Amended YYYY-MM-DD:** \<what has changed, and what changed it\>

Immediately beneath, rather than at the top of the file or in a trailing section, because a reader meets the overtaken statement at one particular place and that is where the correction has to be.
A log at the end leaves it reading as current everywhere but the last screen, which is the failure of an errata page.

The `**Date:**` line stays the date of the *decision* — never bump it for an amendment, which carries its own.

### Reconsidering an amended ADR

Amendments keep a record true point by point, but they cannot say whether the decision as a whole still stands.
**Reconsider the ADR when an amendment contradicts its Context or one of its Consequences** — a premise the decision was argued from, not a detail it happened to mention.
An amendment that only follows a rename or a moved file is not a reason, however many of them accumulate.

A reconsideration ends one of three ways:

- **The decision no longer holds** → supersede it with an ADR recording the new decision.
- **The decision holds, but the reasoning it rests on has moved** → supersede it with an ADR restating the decision on current facts, so a reader meets one argument rather than an original and its corrections.
- **The record still explains the decision** → keep amending.

**Restate only once the subject has settled.**
A restating ADR is worth writing when the change behind its amendments is complete and nothing still in progress — an active plan, a platform behaviour still being probed — is expected to amend it again.
Until then, keep amending: an amendment is cheap and local, while each restatement adds a link to the supersession chain and has to be written again if the facts move once more.
A decision that no longer holds is superseded without waiting for anything else in flight, since leaving it `Accepted` tells a reader to follow it.

**The amendment lands with the change that prompted it; the superseding ADR is a change of its own.**
The amendment goes in the same commit as the work that overtook the record, so the ADR is never wrong on `main`.
The superseding ADR, whether a new decision or a restatement, follows as its own commit and usually its own PR, so it is reviewed as a decision rather than carried along inside the work that prompted it.

> **🤖 Agent** — when an amendment you are adding contradicts an ADR's Context or a Consequence, raise the reconsideration with the user alongside it, saying which of the three outcomes you think applies and whether its subject has settled.

### Superseded and deprecated ADRs are frozen

Once its Status reads `Superseded by ADR-MMM` or `Deprecated`, an ADR records history and takes no further amendments.
A fact that overtakes a superseded ADR belongs in the ADR that replaced it; one that overtakes a deprecated ADR belongs nowhere, since nothing rests on it any more.
Three edits still apply, because the file has to keep reading correctly and passing link checks: its Status line, and the two unmarked in-place fixes in the table above.

## Index maintenance

`docs/decisions/README.md` is the ADR index.
It carries a one-row-per-ADR table (number, title, status) and the template above.

> **🤖 Agent** — every time you add an ADR or change an ADR's status (including marking one superseded), update its row in `docs/decisions/README.md` in the **same commit** — and, on supersession, add both the new row and the status change to the old row.

## Format notes

- **One decision per ADR.**
  If a PR settles two independent structural questions, that is two ADRs, not one with two Decisions.
- ADRs record **structural / architectural** decisions — the ones a future contributor would otherwise re-litigate.
  A routine implementation choice does not need an ADR.
- Write the Context so it still makes sense years later, without the PR discussion that produced it.
