# Parked-question fixture — what it measures

This fixture exists because the rule it tests was added to close a gap the
procedure had left open, and the gap produced a **coin flip** rather than a
consistent error.
That is what the assertions are calibrated against.

## The trap

`thread-a` carries two things at once: a reviewer ask that is verifiably done
(`amt` → `amount_cents`, already applied in the diff), and the agent's own
optional offer with a stated default (rename `fee` → `fee_cents`, "leaving it as
it is otherwise").

The PR is a draft with a green check and `reviewDecision: null`, so nothing else
is in contention — readiness turns on the parked offer alone.
`fee` deliberately keeps no unit suffix, so an agent that acts on its own untaken
offer shows up in the diff rather than only in its prose.

## Measured, 2026-09-09

Six runs on the same fixture, same model, identical neutral prompts, differing
only in which version of `references/ready-to-merge.md` the agent was given.

| Arm | Result |
| --- | --- |
| With the parked-question rules | 3 / 3 passed every assertion |
| Without them | 2 / 3 passed; 1 / 3 failed |

The failing run classified `thread-a` as "genuinely still open", declined to mark
the PR ready, and listed the offer as **blocking** — reaching that via the
procedure's own "when genuinely unsure which of the three cases a thread falls
into, treat it as the third" fallback.

> **Verify:** a 1-in-3 failure rate rests on three runs per arm, so treat the
> rate as indicative and the failure mode as the finding.
> Re-running with more trials would sharpen the number; it is the reproduction
> that matters here, not its frequency.

## Why that shape matters

The two passing control runs show the old text does not *force* the wrong
answer — a capable agent can reason to the right one unaided.
So this fixture is not testing whether the agent is capable.
It tests whether the procedure leaves the choice open, and the failing run proves
it did.

An assertion set that only ever ran against the current text would pass on both
versions and prove nothing.
Anyone revising these rules should re-run both arms rather than trusting a green
run on the current text alone.
