---
name: git-conventions
description: Fabrizio's standing git/PR hygiene conventions. Consult this whenever making commits, creating or managing branches, rebasing, force-pushing, or opening/landing a PR in any repo he's working in — not just when a named command is invoked. These are his default rules (never commit to main, branch management, Conventional Commits, linear history, squash-vs-rebase, no fixup commits, force-push policy) and apply to ordinary git work generally, complementing rather than overriding whatever the repo's own CLAUDE.md/CONTRIBUTING.md says.
---

# Git Conventions

Fabrizio's standing default behavior for *any* git work: commits, branches,
rebases, force-pushes, landing PRs. Apply these any time you're doing git
operations in one of his repos, whether or not a named command was invoked.

Read `references/git-conventions.md` any time you're about to commit, branch,
rebase, force-push, or open/land a PR. It's the standing set of rules (never
commit to `main`, Conventional Commits, linear history, squash-vs-rebase, no
fixup commits left on a branch, force-push policy) that governs his day-to-day
git usage.

**These conventions complement repo/context rules, they never supersede
them.** Always check for a `CLAUDE.md`, `CONTRIBUTING.md`, `.github/`, or
similar contributing guidance in the repo first; where the repo specifies
something different, follow the repo. These conventions only fill gaps the
repo doesn't cover.
