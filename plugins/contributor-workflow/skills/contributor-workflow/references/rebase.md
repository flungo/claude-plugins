# /rebase

Bring a feature branch up to date with its base, working out what the base's new commits mean for the work in hand and keeping how conflicts were resolved reviewable on its own.

The procedure itself is § Rebasing onto the base branch in `git-conventions`, which applies to every rebase whether or not this command was invoked.
This command adds what an explicit invocation needs on top: which branch and base, who does the review, and how the outcome is reported.
Read that section before starting.

Run it with full autonomy, as with `/ready-to-merge`: rebase, force-push, and report back in chat rather than asking at each step.
Stop only where that section says to — an incoming change that contradicts a decision already made on the branch, or one that leaves unclear what the branch should now do.

## 0. Identify the branch, base, and PR

- If the user named a branch or PR, use it; otherwise use the branch checked out.
- The base is the PR's base branch where a PR is open, and the repo's default branch otherwise — unless the user named another.
- Whether a PR is open decides whether the separated pushes apply, so check rather than assume.

Use whatever GitHub tooling the session has, as in `/ready-to-merge` step 0.

## 1. Review the incoming changes

As `git-conventions` § Review the incoming changes first describes.

**Subagent model:** choose it per the `delegation-conventions` skill.
Judging how another body of work bears on this branch is reasoning rather than following instructions, so it is not the simple, fully specified case.

**Subagent permission:** invoking `/rebase` asks for the review subagent the procedure prescribes, as surely as naming the tool would.
Only an environment that bars subagents outright changes that: there, do the review in the main loop and say so in the report.

## 2. Rebase and push

As `git-conventions` § Rebase with the base's changes and your resolutions in separate pushes describes.

## 3. Report

Report in chat, not as a PR comment, with everything `git-conventions` § Summarise the rebase lists, and:

- **The range rebased over** — the old and new base shas, and how many commits came in.
- **Which path it took** — no conflicts and a single push, the separated pushes, or no PR open.
- **The `git diff --stat "$BASE_WINS" HEAD` check** from the separated pushes, and that it listed only the conflicted files.
- **Anything you stopped on** — the incoming change and the question it leaves for the user.
- **Uncommitted work** — whether any was stashed and reapplied, and whether it reapplied cleanly.
