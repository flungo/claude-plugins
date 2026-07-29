# /ready-to-merge

Final sweep before the user hits merge.
Assume the PR is basically done — this is cleanup and verification, not a first-pass review.
Operate with full autonomy: make the fixes, resolve threads, rewrite history, push, and mark ready — then report back in chat.
Don't ask permission for routine steps in this procedure; do ask if you hit a genuine ambiguity (see steps 3-4).

Read `references/git-conventions.md` before starting — commit history cleanup in step 5 depends on it.

## 0. Identify the target PR

- If the user gave an explicit PR (number, URL, or branch name), use that —
  it always takes precedence.
- Otherwise, use the PR associated with the currently checked-out branch.
- If there's no PR for the current branch and none was specified, stop and
  ask the user which PR they mean.

**Getting PR data:** try MCP GitHub tools first if available in this session.
Fall back to the `gh` CLI otherwise:

```sh
gh pr view <number> --json title,body,state,isDraft,headRefName,baseRefName,reviewDecision,statusCheckRollup
gh pr diff <number>
```

Unresolved review threads aren't exposed by `gh pr view`; use the GraphQL API (via MCP if it supports thread queries, otherwise `gh api graphql`):

```graphql
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first: 100) {
        nodes { id isResolved comments(first: 50) { nodes { body author { login } } } }
      }
    }
  }
}
```

Resolving a thread is the `resolveReviewThread(threadId: ...)` mutation.

## 1. Sync with base branch

Fetch the base branch (usually `main`) and rebase if it has moved, per git-conventions.
Review what changed upstream before continuing — if it affects work on this branch, fold the adjustment in now (fixup/amend, not a new commit).

## 2. Accuracy — PR description and in-repo status trackers

Compare the PR title and description against the actual diff.
If either is stale, inaccurate, or missing something the PR now does, update it (`gh pr edit --title ... --body ...`).
The description should reflect what the PR *actually does*, not what it originally set out to do.

Then do the same for anything the repo tracks **in-doc** that this PR advances — plan step checkboxes and status rows, a `CLAUDE.md` "Active work" table, ADR statuses, a CHANGELOG.
Update them to the state the repo will be in *once this PR merges*: the PR that completes a tracked step is the one that ticks it (`[ ]` → `[x]`) and flips its status, not a later follow-up.
Fold each edit into the commit that does the corresponding work (per step 5's tracking-content rule and git-conventions "Rebase hygiene").
Don't lean on a session-end doc-checklist hook for this — that fires after merge, too late to land the update in the PR that earned it.

## 3. Unresolved review threads

For each unresolved thread, work out which of three cases it is:

- **Already addressed** — the requested change is verifiably already in the
  current diff. Resolve the thread. Report: which thread, and how you
  confirmed it was already done.
- **Not yet addressed, but trivial to fix now** — the ask is mechanical and
  unambiguous (e.g. a rename, a missing null check, a typo, applying a
  pattern already used elsewhere in the file) — the same class of thing
  step 4 calls "discoverable," just prompted by a review comment instead of
  something you noticed yourself. Make the fix, fold it into the relevant
  existing commit (see git-conventions "Rebase hygiene"), then resolve the
  thread. Report: which thread, and what change you made.
- **Genuinely still open** — the right resolution is ambiguous, contested,
  requires a decision, or the comment raises a real design question rather
  than a mechanical ask. Don't touch it and don't resolve it — this is the
  same "requires a decision" case as step 4, including its rule on when
  research is worth doing to frame the options. Leave it unresolved and
  report it as a question that needs the user's input before it can be
  resolved.

Never resolve a thread you haven't either verified as already-fixed or fixed yourself this pass.
When genuinely unsure which of the three cases a thread falls into, treat it as the third.

## 4. Resolve fixable ambiguity elsewhere in the diff

Beyond review threads, reviewing the diff on your own may surface ambiguity in code or docs that nobody's flagged in a comment.
Triage it the same way:

- **Discoverable** (the answer exists somewhere — current library behavior,
  what another part of the codebase already does, what a linked issue/doc
  says, correct terminology, etc.): dispatch a research subagent to find the
  answer rather than guessing or leaving it. Apply the fix once resolved.
  Report: what was ambiguous, what the research found, and the fix applied.
- **Requires a decision** (a genuine judgment call, a design tradeoff, or
  something only the user can decide — no amount of research resolves it):
  don't guess, and don't let research make the call for you. Research only
  if and only if it will help frame the options for the user — e.g.
  surfacing tradeoffs, prior art in the codebase, or constraints that bound
  the decision. Skip research if it wouldn't change how the question is
  presented. Stop and ask the user directly either way. If the framing is
  more than a couple of lines, put it in a linked markdown artifact instead
  of inlining it in chat; otherwise summarize it inline when you ask.

Either way, fold the eventual fix into the relevant existing commit rather than adding a new one (see git-conventions "Rebase hygiene").

## 5. Clean commit history

Before applying any of the defaults below, check whether the repo's own `CLAUDE.md`/`CONTRIBUTING.md`/etc. specifies a different history or merge policy — if so, follow that instead (see git-conventions precedence note).

**Judge cleanliness by content, never by titles.** `git log --oneline` looking tidy (good Conventional Commits messages, no obvious "wip"/"fix typo" entries) is not evidence the history is clean — a well-titled commit can still bundle several unrelated changes, or a title can promise one thing while the diff does another.
The only way to know is to read the actual hunks in each commit against the PR description and any other context of what was done.

**What "one logical change" means in practice:** default to one commit per distinct thing described in the PR (its description, or your own understanding of the disparate work if the description doesn't break it down) — not one commit per file, and not one commit for the whole PR.
A new standalone document is normally its own commit; a doc that specifically explains a change introduced in this PR is normally bundled with that change, not split out.
Convention/config changes (e.g. a `CLAUDE.md` update) are normally bundled with the change that made the convention relevant, not left as a separate catch-all.
When you're not sure whether two things are "the same change" or two changes that happen to touch the same file, default to splitting them — over-splitting is far easier for the user to squash back together than an under-split history is to untangle.

**Delegate the analysis to a subagent.** Don't do this triage yourself from memory of the diff — dispatch a subagent whose only job is to work out the target commit structure.
Don't read the full diff into your own context first and paste it into the subagent's prompt; instead, point the subagent at the branch/commit range (`origin/<base>..HEAD`) and have it pull the diff itself, so the full diff only ever lives in the subagent's context, not yours.
Give the subagent:

- The branch and base to diff (it fetches the diff itself, per above).
- The PR title and description.
- Any additional context you have on side work bundled into the PR that
  isn't obvious from the description alone (e.g. things the user mentioned
  in chat, or that came up during steps 2-4).

Have it report back a proposed list of target commits — each with the files and specific hunks that belong in it, and a Conventional Commits message — along with reasoning for any grouping or split that isn't obvious.
Use that to drive the interactive rebase; don't take its list uncritically if something in it looks off given the context you have that it might not.

**Splitting hunks within a file.** A single file changing for two different reasons in the same PR is not a signal to keep it as one commit — different hunks of the same file can and should land in different commits when they serve different logical changes.
Use `git add -p` (or equivalent) rather than `git add <file>` when the target commit structure calls for it.
If a hunk is too entangled to split cleanly that way (e.g. one line edited twice for two different reasons, or a diff tool can't isolate the pieces), reconstruct the target file content for that commit by hand instead of forcing an imprecise `git add -p` split.

**Self-consistency across commits.** Ideally, each resulting commit stands on its own — the repo is coherent if you check it out at that commit, including content that gets refined or overwritten by a later commit in the same PR (e.g. a runbook drafted in one commit, then revised per review feedback in a later one, rather than only appearing complete at the final commit).
This is the ideal, not a hard requirement for every hunk — where splitting a genuinely blurred/entangled hunk cleanly isn't worth the effort, it's acceptable to defer it to the latest commit that touches that area, as a shortcut.

**Exception: don't take that shortcut on tracking/index content.** Files that track a growing list (a docs index, a CHANGELOG, a table of contents, a secrets catalogue) must be updated incrementally, in the same commit that adds the thing being tracked — each commit adds only the rows/lines for what it introduces.
Deferring the whole index update to a later or final commit breaks self-consistency in exactly the case where it's cheap not to (it's rarely ambiguous which row belongs with which commit), and leaves intermediate commits looking like they added something the index doesn't yet reflect.

Use `git rebase -i` (with `git add -p` for hunk-level splits) to reorder, squash, fixup, or split as needed.

**Verify the rewrite changed only history, not content.** Before force-pushing, confirm the resulting tree at the new HEAD is byte-identical to the tree at the old HEAD — e.g. `git diff <old-head-sha> HEAD` is empty — even though intermediate commits along the way may differ from the original commits (that's expected; it's the final state that must match, not the journey).
If the diff isn't empty, something was lost or altered during the reconstruction and needs fixing before you push, not after.
Report this check in step 8 either way.

Force-push the feature branch when done (never `main`).

## 6. Checks and approvals

Confirm CI status (`statusCheckRollup`) and review decision (`reviewDecision`).
This skill doesn't wait on or retrigger CI — it checks current state once, at the end, after everything else above is done.

## 7. Mark ready — only if everything is actually green

Marking the PR ready is gated on **all** of the following:

- All CI checks passing (no pending, no failing).
- Required approvals satisfied (`reviewDecision` is approved, not just
  "review required").
- No unresolved review threads remain (including ones explicitly flagged
  in step 3 as genuinely open — those block readiness too, they're not an
  exception).
- In-repo status trackers reflect what this PR completes (step 2).
- Commit history is clean (step 5 complete).

If **all** of these hold and the PR is currently a draft, mark it ready (`gh pr ready <number>`).
If any of them don't hold, do **not** mark it ready — report what's blocking instead, even if it's something outside this skill's control (e.g. waiting on a specific reviewer, a flaky CI job).
Never mark ready "provisionally" or because the remaining item seems minor.

## 8. Report

Report back in chat (not as a PR comment) with:

- **Verdict**: ready to merge (and marked as such), or not yet — and
  exactly what's blocking.
- Description edits made, if any.
- Per unresolved thread you touched: which case it was (already addressed /
  fixed now) and what you found or changed. Don't just say "resolved
  threads" — list them.
- Per ambiguity you resolved outside of threads: what was ambiguous, what
  research found, what you changed.
- Threads and ambiguities left open: the specific question blocking each
  one. Where you did framing research, summarize it inline (or link the
  artifact if it went there) so the user can decide without doing that
  legwork themselves.
- History rewritten: the resulting commit list, and the reasoning behind
  any grouping or split that isn't obvious (don't just say "cleaned up").
  Confirm the byte-identical tree check (see step 5) passed.
- CI/approval status.
