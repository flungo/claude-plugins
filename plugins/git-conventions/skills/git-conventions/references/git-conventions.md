# Git & PR Conventions

**Precedence: these are Fabrizio's personal defaults, and they complement
repo/context rules — they never supersede them.** Before applying anything
below, check the repo for its own instructions — `CLAUDE.md`,
`CONTRIBUTING.md`, `.github/`, or any other contributing guidance. Where the
repo specifies a different approach (branch naming, commit message format,
merge vs squash vs rebase, force-push policy, etc.), follow the repo's
rules instead. These conventions only fill the gaps the repo doesn't cover.
If a repo's instructions are ambiguous about whether they override a
specific point here, treat that as the "requires a decision" case in
`ready-to-merge.md` step 4 — ask, don't assume.

This applies to *all* git work in one of his repos — every-day commits,
branching, and rebasing, not only during a named command like
`/ready-to-merge`.

Shared standards used across commands in this skill. Apply whatever is relevant
to the command you're running — not every command touches every section.

## Branch management

- Never commit directly to `main`. All work happens on a feature branch.
- If `main` is checked out at the start of a session: pull to update, then
  create a new feature branch before making changes.
- If a non-`main` branch is already checked out: confirm with the user
  whether to continue on it or start fresh, before proceeding.
- Before finishing a task, fetch `origin main`. If it has moved, rebase the
  feature branch onto it:

  ```sh
  git fetch origin main
  git rebase origin/main   # only if fetch produced new commits
  ```

  Review what changed upstream (diff, updated docs/decision records) before
  continuing. If upstream changes affect work already on the branch, fold in
  the adjustment via amend/fixup (see "Rebase hygiene" below) rather than a
  new corrective commit. If anything is ambiguous or conflicts with a
  decision already made on the branch, stop and ask the user — don't
  silently resolve it.

## Commit message convention

[Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `chore:`, `refactor:`, etc. Imperative mood subject line, no
trailing period. Body explains *why*, not a restatement of the diff.

## Linear history — no merge commits

Assume repos maintain a strictly linear history, unless told otherwise.
Never create merge commits. Branches land on `main` via squash or rebase
(fast-forward) — never `git merge`. This is the default stylistic choice
Fabrizio would make contributing by hand, so it's harmless to apply on his
own branches even where the repo hasn't stated a preference either way —
it only yields when the repo explicitly asks for something different.

**Squash vs rebase when landing:**

- **Squash** when the branch is a single logical change, however many
  working commits it took (one DNS record, one doc fix, one ADR). The
  squashed message describes the change, not the journey.
- **Rebase** (no squash) when the branch holds multiple distinct logical
  changes worth preserving individually (e.g. separate commits for DNS, a
  doc update, and a new runbook).
- When in doubt, squash — a single clean commit is easier to revert and
  easier to read in `git log`.

## Rebase hygiene — no fix-up commits left on a branch

When a branch contains a minor inaccuracy (typo, wrong value, incorrect
claim), amend or fixup the relevant existing commit rather than appending a
corrective commit. The branch should read as though it was always correct —
not as a record of corrections made after the fact. Applies both to
self-correction during a session and to folding in upstream changes from
`main`.

A branch is **not** clean if it contains commits like `fix typo`,
`address review comment`, `wip`, `oops` — these should be squashed/fixed
into the commit they correct via `git rebase -i` (`fixup`/`squash`), not
left as standalone entries.

## Force-push policy

Force-pushing is allowed on feature branches (expected after `--amend` or
interactive rebase). Never force-push `main`.

## Landing — always via PR

Never push directly to `main`. When a branch is ready, open a PR and let the
user merge it. After a PR merges, delete the remote branch.

## PR monitoring

When watching a PR via activity subscriptions, don't use `send_later` to
schedule self check-ins — either review comments arrive as events that wake
the session, or the user returns to proceed, and either way the session can
re-check PR state when next awoken. Only propose `send_later` for polling a
CI job's outcome when that outcome is blocking *and* might complete without
emitting an event.
