# Incident Report Template

Incident reports live in `docs/incidents/` and record an unplanned failure: what happened, what it affected, why, and how it was resolved.
They exist so that a failure is investigated once, and so that permanent docs have something lasting to cite when they need to point at what happened.
This is the canonical shape; use it verbatim.

## When to write one

Write a report for an unplanned failure or degradation that took investigation to understand, or that someone would otherwise investigate again: lost or damaged data, a service down or wrong, a security event, a change that broke something.
A routine alert that cleared by itself, or a fault fixed in minutes with nothing learned, needs none.

`docs/incidents/` is optional: a repository has one only where tracking incidents makes sense, and it is created with the first report, not in advance.

Open the report while the incident is live, not after it ends.
It is where the timeline accumulates, and it is what the follow-up work points back to.

## Canonical shape

```markdown
# YYYY-MM-DD: Title

- **Date:** YYYY-MM-DD
- **Status:** Open | Mitigated | Resolved
- **Affected:** A short list of the hosts, services or data affected

## Summary

Two to four sentences: what failed, what it affected, the cause in a phrase, and where it stands.

## Impact

What failed or was at risk, for whom, and for how long; what was lost, if anything, and what was not.

## Timeline

Times in UTC.

- **YYYY-MM-DD HH:MM** — **Onset:** What first went wrong.
- **YYYY-MM-DD HH:MM** — **Detected:** How it was noticed.
- **YYYY-MM-DD HH:MM** — Each finding or action that changed the course, one per bullet.
- **YYYY-MM-DD HH:MM** — **Mitigated:** What contained the impact.
- **YYYY-MM-DD HH:MM** — **Resolved:** What fixed it for good.

## Cause

What caused the failure, as far as it is established, with each claim's provenance.
Where the trigger differs from the underlying cause, name both; where several factors combined, list each.

## Resolution

What stopped the impact, what restored normal operation, and any workaround used meanwhile.

## Follow-ups

- [ ] Each action still owed, with where it is tracked.
```

Every timeline entry carries its full date as well as its time, so that entries either side of midnight cannot be misread.
Every time is UTC; convert a local time when writing it down, rather than marking it as local.
Mark the onset, detection, mitigation and resolution in bold, as they happen; an entry the incident has not reached yet is left out, not left blank.

The filename is `YYYY-MM-DD-short-slug.md`, dated by the incident's **onset** — the first evidence of the failure, which may precede its detection — so that alphabetical order is chronological.
The `# YYYY-MM-DD: Title` heading, the three metadata lines and all six sections are required.
The title names what failed, not who or what is to blame.

## Optional sections

Three more sections are allowed, but **not required** — `## Detection` and `## Lessons` between `## Resolution` and `## Follow-ups`, and `## References` last:

```markdown
## Detection

How the failure was noticed, and how long after onset; what would have caught it sooner.

## Lessons

What went well, what went badly, and where luck helped — what the incident showed that is worth carrying forward and is not already a follow-up.

## References

Log excerpts, screenshots, commits and pull requests the report draws on, too long for the sections above.
```

Include one only when there is something real to put in it — `## Detection` earns its place when the gap between onset and detection is itself part of the story, and "where luck helped" is often the most useful lesson.

## Status

Status is a lifecycle:

| Status | Means |
| --- | --- |
| `Open` | The failure is ongoing, or its impact is not yet contained |
| `Mitigated` | The impact is contained — by a workaround, a stopped service, a held change — but the permanent fix is not in place |
| `Resolved` | The permanent fix is in place, and every follow-up left open links to where it is tracked |

Change the status, its index row, and the timeline in the same commit.
A report is not `Resolved` while a follow-up exists only in the report: give it a home first — a plan, an issue, or the repo's follow-ups list — so it cannot be forgotten once the report stops being read.

## A record, not a reference

A report records what happened and what was known at the time, as an ADR records a decision.
While the incident is `Open` or `Mitigated`, edit the report freely as the picture changes: it should read as the current understanding, not a log of revised guesses.
Once it is `Resolved`, treat it like an accepted ADR: fix what was wrong when written in place, and add anything learned later with a dated `> **Amended YYYY-MM-DD:** …` beneath the statement it overtakes, per `adr-template.md`.

Write it blamelessly: name systems, decisions and conditions, not people at fault.
Give every finding its provenance, as a reference doc does — observed and when, inferred, or from a named source — and mark what is still unknown as unknown rather than leaving a guess standing as fact.

## Moving durable knowledge out

The report is not the only home for what the incident taught.
Each kind of fact goes to its permanent home, and the report links to it:

| What was learned | Goes to |
| --- | --- |
| How a system behaves | The reference doc for that system |
| A decision taken because of the incident | An ADR |
| A procedure that will be run again | A runbook |
| One-time recovery work | A plan |

A permanent doc may link the report, because the report is permanent; that is how a reference doc or ADR cites an incident without carrying its detail.

**A report may link its recovery plan only while the plan is in progress**, the same exception the plan lifecycle gives `CLAUDE.md`'s "Active work".
When the plan is retired, replace the link with its outcome, in the timeline and the resolution.

## One incident per report

A failure with its own cause gets its own report, even when it surfaced during another incident; cross-link the two.
Symptoms of one cause, however many systems show them, stay in one report.

## Index maintenance

`docs/incidents/README.md` is the incident index.
It carries one row per report — date, title, status, and a one-line summary — in chronological order, and the template above.

> **🤖 Agent** — every time you add a report or change its status, update its row in `docs/incidents/README.md` in the **same commit**.
