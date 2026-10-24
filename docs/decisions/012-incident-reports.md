# ADR-012: Incident reports are a fifth kind of doc, in a fixed lightweight format

- **Date:** 2026-10-24
- **Status:** Proposed

## Context

ADR-002 gave every repo four kinds of doc: decisions, plans, runbooks and reference.
None of them records an unplanned failure.
A plan holds the recovery but is deleted when done; a reference states current truth and should not tell the story of how it was learned.
So a permanent doc that needs to point at what happened has nothing lasting to cite.

Some repos already keep incident write-ups in `docs/incidents/` (`stalwart.flungo.net`), each in its own shape, with recovery steps, upgrade records and investigation notes mixed in.

Published postmortem templates — Google SRE's example, PagerDuty's, GitLab's incident review, Kubernetes test-infra's, and the `dastergon/postmortem-templates` collection — share a core of Summary, Impact, Timeline, Cause, Resolution and follow-up actions.
Most of the rest serves a team: severity levels, roles, review meetings, approval workflows, customer messaging.

## Decision

**Add `docs/incidents/` as a fifth kind of doc in `docs-standards`**, a permanent record of an unplanned failure, with its template in `references/incident-template.md`.

- **The shared core is required:** a dated `# YYYY-MM-DD: Title` heading, `Date` (onset), `Status` and `Affected` metadata, and `Summary`, `Impact`, `Timeline`, `Cause`, `Resolution` and `Follow-ups` sections.
  `Detection`, `Lessons` and `References` are optional.
- **No team machinery**: no severity, roles or review workflow.
- **Status is `Open`, `Mitigated` or `Resolved`**, and a report is not `Resolved` while a follow-up lives only in it.
- **A report is a record, like an ADR**: edited freely while open, amended rather than rewritten once resolved.
- **What an incident teaches moves to its permanent home** — reference, ADR, runbook or plan — and the report links to it; permanent docs may link the report.
  A report may link its recovery plan only while the plan is in progress.

## Consequences

### Positive

- Reference docs and ADRs can cite an incident without describing it, or linking a plan that will be deleted.
- A failure is investigated once, and the next occurrence starts from the record.

### Negative — trade-offs

- Existing write-ups, such as `stalwart.flungo.net`'s, do not match the template until migrated.
- A report that stays `Open` or `Mitigated` needs its status kept current, one more tracker to maintain.
