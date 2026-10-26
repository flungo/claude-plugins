---
name: contributor-workflow
description: Fabrizio's personal, named git/PR workflow commands — structured workflows he invokes by name for a particular task. Currently "/ready-to-merge" (aliases "Ready to Merge?", "RTM?"), a final pre-merge sweep of a PR covering title/description accuracy, review-thread triage, resolving fixable ambiguity, cleaning up commit history, and marking it ready; and "/rebase" (alias "Rebase onto main"), which reviews what the base brought in, rebases with the base's changes and the conflict resolutions in separate force-pushes, and reports both with compare links. Relies on the git-conventions skill for the underlying git hygiene rules.
---

# Contributor Workflow

Fabrizio's repeatable, named workflow commands — the specific, structured workflows he invokes by name for a particular task.
Each has its own reference file under `references/`.
Check `references/` for the full list before assuming a command isn't covered here.

These commands build on the standing git hygiene rules in the **`git-conventions`** skill (a declared dependency of this plugin) — read those for any commit, branch, rebase, force-push, or PR-landing behavior the commands rely on.

## Commands

### `/ready-to-merge` (aliases: "Ready to Merge?", "RTM?")

A final sweep on a PR that's believed to be essentially done, to confirm it's actually in a clean, mergeable state — or to make it so.
Covers: PR title/description accuracy, unresolved review thread triage, resolving any fixable ambiguity in code/docs, cleaning up commit history, and marking the PR ready.
Runs with full autonomy (including rebase + force-push); reports results in chat rather than asking for confirmation at each step.

Full procedure: `references/ready-to-merge.md`.

**PR identification**: an explicitly named PR (number/URL/branch) always takes precedence; otherwise use the PR for the currently checked-out branch.
If neither is available, ask.

**Tooling**: use whichever GitHub tooling the session actually has — some environments offer only the MCP, others a `gh` CLI alongside it, and which to reach for is the environment's business rather than this command's.
Review thread state comes from the MCP's thread read, or from a GraphQL call where `gh` is all there is.
Where you are working through the MCP, **`connector-conventions:github`** (a declared dependency of this plugin) covers what its reads mangle and omit — both of which bite a command that reads PR descriptions and review threads and then rewrites them.

**Tests**: `evals/` holds regression fixtures for the commit-history and thread-triage logic in this command — see `evals/README.md`.

### `/rebase` (alias: "Rebase onto main")

Brings a branch up to date with its base.
Reviews what the base's new commits mean for the work in hand — through a subagent when they are large — then rebases.
While a PR is open, the base's changes and the conflict resolutions go up as separate force-pushes, so each shows on its own in GitHub's compare view.
Reports what was relevant, how each conflict was resolved, and a compare link per push.
Runs with full autonomy, like `/ready-to-merge`.

Full procedure: `references/rebase.md`, which carries out § Rebasing onto the base branch in `git-conventions`.
Its review subagent's model follows the **`delegation-conventions`** skill, a declared dependency of this plugin.
