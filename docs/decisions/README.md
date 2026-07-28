# Architecture Decision Records

Decision-oriented records for `flungo-plugins`.
ADRs are numbered sequentially and **never deleted or renumbered** — a superseded decision keeps its file with its Status updated to point at the newer ADR.

| # | Title | Status |
|---|---|---|
| [001](001-marketplace-structure.md) | Marketplace structure — split by enablement scope, compose via dependencies | Accepted |
| [002](002-documentation-and-adr-model.md) | Documentation model — Diátaxis docs, Nygard ADRs, self-encoded | Accepted |
| [003](003-owned-vs-third-party-adoption.md) | Owned-vs-third-party — adoption depends on who owns the repo | Accepted |

## Template

New ADRs use the Nygard format (see ADR-002):

```markdown
# ADR-NNN: Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated

## Context

The forces and problem motivating the decision.

## Decision

What we will do, in active voice.

## Consequences

What becomes easier or harder as a result. Optional `### Positive` /
`### Negative — trade-offs` subsections; include only what's real.
```
