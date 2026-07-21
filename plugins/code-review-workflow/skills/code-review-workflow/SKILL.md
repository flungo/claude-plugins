---
name: code-review-workflow
description: Fabrizio's personal git/PR workflow commands and standing git conventions. Always consult references/git-conventions.md whenever making commits, creating or managing branches, rebasing, force-pushing, or opening/landing a PR in any repo he's working in — not just when a named command below is invoked. These are his default git hygiene rules (branch management, Conventional Commits, linear history, squash-vs-rebase, no fixup commits, force-push policy) and apply to ordinary git work generally, complementing rather than overriding whatever the repo's own CLAUDE.md/CONTRIBUTING.md says. Separately, this skill also holds named, structured workflow commands — currently "/ready-to-merge" (aliases "Ready to Merge?", "RTM?") for a final pre-merge sweep of a PR, with more expected over time.
---

# Code Review Workflow

A home for Fabrizio's git/PR conventions and his repeatable workflow
commands. Two distinct things live here — read the right one for the
situation:

- **Conventions** (`references/git-conventions.md`) — his standing default
  behavior for *any* git work: commits, branches, rebases, force-pushes,
  landing PRs. Apply these any time you're doing git operations in one of
  his repos, whether or not a named command was invoked.
- **Commands** (below, each with its own reference file) — specific,
  structured workflows he invokes by name for a particular task. Currently
  one; more will be added over time — check `references/` for the full
  list before assuming a command isn't covered here.

## Shared conventions — apply to all git work, not just commands

Read `references/git-conventions.md` any time you're about to commit,
branch, rebase, force-push, or open/land a PR — regardless of whether
you're running one of the named commands below. It's the standing set of
rules (never commit to `main`, Conventional Commits, linear history,
squash-vs-rebase, no fixup commits left on a branch, force-push policy) that
governs his day-to-day git usage.

**These conventions complement repo/context rules, they never supersede
them.** Always check for a `CLAUDE.md`, `CONTRIBUTING.md`, `.github/`, or
similar contributing guidance in the repo first; where the repo specifies
something different, follow the repo. These conventions only fill gaps the
repo doesn't cover.

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
