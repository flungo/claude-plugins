# Evals for code-review-workflow

Four scenarios, each a real (buildable) git repo plus a mock PR context, targeting specific rules in `references/ready-to-merge.md`:

| eval_name | fixture | what it checks |
|---|---|---|
| `messy-history-needs-splitting` | `fixtures/messy-history-orbital-cafe` | Under-splitting: bundled features, a deferred docs-index update, a stray fixup commit. This is the general shape of the original bug. |
| `clean-history-no-unnecessary-rewrite` | `fixtures/clean-history-starlight-planner` | Over-eagerness: an already-clean history shouldn't get rewritten for its own sake. |
| `review-thread-triage` | `fixtures/thread-triage-tidepool-notes` | The three-way thread split (already addressed / trivial fix now / requires a decision), including the framing-research rule for decision-required threads. |
| `regression-bundled-commits-sanitized` | `fixtures/regression-owner-onboarding` | A sanitized reproduction of the actual PR that surfaced the original bug — see that fixture's `notes.md` for provenance. |

## Building a fixture

Each fixture directory has a `build_repo.sh`.
Run it to materialize the repo:

```sh
cd fixtures/messy-history-orbital-cafe
./build_repo.sh /tmp/orbital-cafe
cd /tmp/orbital-cafe
git log --oneline
```

All four have been run once already to confirm they build cleanly.

## `pr-context.json` stands in for GitHub

These fixtures don't hit real GitHub.
`pr-context.json` in each fixture directory is the full mock of what `gh pr view` plus a review-thread query would return — title, description, draft state, check status, review decision, and (where relevant) unresolved review threads.
When running an eval, tell the agent under test to treat this file as that data rather than attempting real `gh`/MCP calls.
This isolates the fixture from network access and from needing an actual PR to exist anywhere.

## Running the actual evals

This directory has the prompts, fixtures, and assertions (`evals.json`) — the input side of the skill-creator eval loop.
Running them (dispatching with-skill/without-skill subagent runs, grading against the assertions, viewing results) needs an environment with subagent tooling, e.g. Claude Code — this chat surface doesn't have a way to spawn subagent runs, so that step has to happen there, following the "Running and evaluating test cases" section of the skill-creator skill.

A lighter-weight option that doesn't need the full harness: build a fixture, invoke `/ready-to-merge` on it directly in a real session, and check the assertions by hand.
That's how these four were designed — each assertion is something a human can check by reading the agent's own report and diffing the resulting `git log`.

## Sanitization note

`fixtures/regression-owner-onboarding` is a fictionalized reconstruction of a real PR that triggered the original bug report — see that fixture's `notes.md`.
Names, domains, and org identifiers are invented; the commit pattern and failure modes are preserved because that's what's being tested.
