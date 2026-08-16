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
  Never edit the superseded decision away — the chain is the audit trail.

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
