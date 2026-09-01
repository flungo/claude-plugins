---
name: github
description: Working rules for GitHub through the MCP connector — what its read path silently mangles, and which fields it does not hand back. Consult this whenever reading or writing issue, pull request, review, or release text through the GitHub MCP tools, before acting on a body that looks truncated or malformed, before rewriting a description or comment because a read looked wrong, and before concluding that a field is absent from a pull request. Covers the sanitising that deletes tag-shaped tokens and silently truncates bodies, how to read the real text instead, and the verified behaviours behind each rule.
---

# GitHub

Rules for working with GitHub **through the MCP connector** — the tools named `mcp__github__*`.

Whether the connector is the right tool for a given session is not this skill's business.
Some environments offer nothing else, others offer a `gh` CLI alongside it; that choice belongs to whatever describes the environment you are in.
Everything here applies once you are already using the connector.

## Never rewrite text because the read looked wrong

**What the connector hands back for issue and pull request *text* is sanitised, and lossy.**
Tag-shaped tokens are deleted outright — `<n>`, `<branch>` and `<sha>` all vanish — and a token naming an HTML raw-text element, such as `<title>` or `<style>`, **silently truncates the whole remainder of the body**.
Backticks are no protection; the pass runs over raw text before anything parses it.

The text on GitHub itself is intact.
It renders correctly on the page, arrives whole in a webhook payload, and comes back unaltered through `get_file_contents`.

So a description or comment that reads as mangled, malformed, or cut short is **evidence about the read path, not about the text** — never edit one to "fix" it, and never reword what you are about to post to survive a path that is not the problem.

## Treat a truncated body as unread, not as incomplete

A body that stops mid-sentence has not told you it is short; it has told you nothing about what follows.
Acting on it is acting on a fragment you cannot see the end of.

When the content matters — reviewing a description, triaging a comment, checking whether something was already said — read the rendered page with `WebFetch` before relying on it.

The same loss applies to code quoted in a comment, so generics (`Vec<T>`, `List<String>`) can disappear from the very thing you were asked to review.

## A field you cannot find may be one the connector omits

The connector does not surface everything the API has.
`pull_request_read` returns no `reviewDecision`, which is the field that says whether a pull request is approved.

So absence in a connector response is not absence on GitHub.
Before concluding that a repository doesn't set something, or that a state can't be read, check whether the field is one the connector simply doesn't return — `references/behaviours.md` records the ones met so far, and another source (a `gh` CLI where the session has one, the rendered page, or a related field) will usually have it.

## References

| Read | When |
| --- | --- |
| [`references/behaviours.md`](references/behaviours.md) | The connector behaves unexpectedly, or before relying on any tool's result — each behaviour with how it was established and its last-verified date |
