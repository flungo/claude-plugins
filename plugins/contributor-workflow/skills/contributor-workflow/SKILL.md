---
name: contributor-workflow
description: Fabrizio's personal, named git/PR workflow commands — structured workflows he invokes by name for a particular task. Currently "/ready-to-merge" (aliases "Ready to Merge?", "RTM?"), a final pre-merge sweep of a PR covering title/description accuracy, review-thread triage, resolving fixable ambiguity, cleaning up commit history, and marking it ready. More commands expected over time. Relies on the git-conventions skill for the underlying git hygiene rules.
---

# Contributor Workflow

Fabrizio's repeatable, named workflow commands — the specific, structured
workflows he invokes by name for a particular task. Each has its own
reference file under `references/`. Currently one; more will be added over
time — check `references/` for the full list before assuming a command isn't
covered here.

These commands build on the standing git hygiene rules in the
**`git-conventions`** skill (a declared dependency of this plugin) — read
those for any commit, branch, rebase, force-push, or PR-landing behavior the
commands rely on.

## Commands

### `/ready-to-merge` (aliases: "Ready to Merge?", "RTM?")

A final sweep on a PR that's believed to be essentially done, to confirm
it's actually in a clean, mergeable state — or to make it so. Covers: PR
title/description accuracy, unresolved review thread triage, resolving any
fixable ambiguity in code/docs, cleaning up commit history, and marking the
PR ready. Runs with full autonomy (including rebase + force-push); reports
results in chat rather than asking for confirmation at each step.

Full procedure: `references/ready-to-merge.md`.

**PR identification**: an explicitly named PR (number/URL/branch) always
takes precedence; otherwise use the PR for the currently checked-out
branch. If neither is available, ask.

**Tooling**: try MCP GitHub tools first (thread listing, resolving,
editing); fall back to the `gh` CLI where MCP doesn't cover something
(e.g. GraphQL calls for review thread state).

**Tests**: `evals/` holds regression fixtures for the commit-history and
thread-triage logic in this command — see `evals/README.md`.
