# GitHub connector — verified behaviours

How the GitHub MCP actually behaves, and how GitHub behaves where you meet it through that connector, in the places where knowing it changes what you do.
Not only surprises — some entries are simply the mechanism, recorded so it is not re-derived.
Each entry states the behaviour, how it was established, and a `**Do:**` line.

GitHub behaviour you reason about away from any particular tool — how a merge method rewrites commits, why merged commits report as unverified — is **not** here.
That belongs to the `git-conventions` skill, which owns the domain whatever tool reaches it.

> **Verify:** these are properties of the GitHub MCP server and of GitHub's API as that server surfaces them, not of any one environment, and both can change without notice.
> An undated or stale entry is a hint to re-probe, not a fact to rely on.

## Issue and pull request text is sanitised on the way out

Text fields come back altered, with no error and no indication that anything was changed.

- A **tag-shaped token is deleted outright** — `<n>`, `<branch>` and `<sha>` all vanish.
- A **lone or unmatched bracket** returns as `&lt;`/`&gt;`, and **quotes and apostrophes** likewise as `&#34;`/`&#39;`.
  Both render correctly on the page, so this half is cosmetic in the read rather than lossy — but it will not compare equal to what you posted, so never diff a read-back body against your source to decide whether an edit landed.
- An **allow-listed HTML tag** such as `<b>` survives intact.
- A token naming an **HTML raw-text element** — `<title>` and `<style>` both do it — **truncates the whole remainder of the body**, silently.
  One incidental mention in a preamble is enough to discard everything after it.

Markdown offers no protection.
Inline code, fenced and indented code blocks, and table cells are all mangled alike, so the pass runs over raw text before anything parses it.

*Verified 2026-08-22 against a description and comments posted from a session, plus a control comment typed by hand in the browser — all read back mangled, all rendered correctly on the page.*
*Entity-escaping of quotes and apostrophes re-confirmed 2026-08-31, reading back a pull request description posted minutes earlier from the same session.*

**Do:** treat a mangled or truncated read as a fact about the read path, never about the text.

## The text on GitHub itself is intact

The same content renders correctly on the page, arrives whole in a webhook payload, and comes back unaltered through `get_file_contents`.
Only this one read path loses it.

The loss extends to code quoted in a comment, so generics (`Vec<T>`, `List<String>`) can disappear from something you are reviewing.

The one real exception is not the connector's doing — a tag-shaped token written as **bare prose**, outside backticks, is stored but does not render, because GitHub drops unknown tags at display time.
That is the ordinary reason to put a placeholder in backticks.

**Do:** never rewrite a description or comment because an MCP read looks wrong, and never reword what you post to survive it.
Check the rendered page with `WebFetch`, and treat an apparently truncated body as unread rather than incomplete.

## The sanitising is deliberate upstream, and known to be lossy

It is applied on purpose to untrusted response fields — issue comments, pull request bodies, reviews, releases, commit messages — with a stated goal of preserving "source-code and file-content fidelity" ([github/github-mcp-server#3106](https://github.com/github/github-mcp-server/issues/3106)), which for body text it does not achieve.

The symptom is reported in [github/github-mcp-server#2202](https://github.com/github/github-mcp-server/issues/2202), open since March 2026 and scoped narrower than what is described above — `issue_read` and fenced code blocks alone.

**Do:** expect it to persist, and don't re-derive it as a local quirk of the session you are in.

## `pull_request_read` does not return `reviewDecision`

`reviewDecision` is the field that says whether a pull request is approved, and the connector does not surface it.

**Do:** read it another way rather than concluding it is unset — `gh pr view --json reviewDecision` where the session has a `gh` CLI, or infer it from `mergeable_state` being `clean` while unapproved, together with the reviews list showing no `APPROVED`.

Its only values are `APPROVED`, `CHANGES_REQUESTED`, and `REVIEW_REQUIRED`; **null means the repository doesn't require approval**, which is the usual case on a solo repo.

## `workflow_dispatch` accepts a ref the workflow is not yet on

A run can be triggered through `actions_run_trigger` with an explicit `ref`, and that works on a feature branch **before** the workflow file exists on the default branch.

This is GitHub's own behaviour rather than the connector's, recorded here because the connector is where you meet it — and because the common assumption is the opposite, that a workflow must land on the default branch before it can be dispatched at all.

**Do:** dispatch against the feature branch to test a new workflow, instead of merging it first to find out whether it works.
