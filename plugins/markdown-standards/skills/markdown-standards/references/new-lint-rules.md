# When a lint rule fires that nobody chose

The reusable `markdown-lint.yml` in [`flungo/github-workflows`](https://github.com/flungo/github-workflows/blob/main/.github/workflows/markdown-lint.yml) tracks `markdownlint-cli2-action` by **major tag**, so a routine Dependabot bump can pull in a markdownlint release that adds rules.
A new rule is enabled by default, applies to every adopting repo at once, and turns long-standing prose into errors without anyone having decided anything.

That is the failure this procedure exists for: **a linter default is not a decision until it is written down.**

## When this applies — and when it does not

**Only when a rule fires on content that was already there and previously passed.**
That is the signature of a rule nobody chose: the prose did not change, the linter did.

A finding on something you just wrote is **not** this.
Fix the prose — that is the ordinary remediation in [`cross-references.md`](cross-references.md), and most of markdownlint's default rules never need an entry anywhere.

[`prose-conventions.md`](prose-conventions.md) is the register, but it is **not** a list of every enabled rule.
It holds the rules the fleet has had to take a *position* on — because the rule needed a human convention beside it, or because adopting it was a choice rather than a default nobody minded.
So "no entry" does not mean "undecided"; it means "no position was ever needed".
The trigger is the rule firing on unchanged content, not the mere absence of an entry.

## First: it is not the pull request that surfaced it

The rule fires on whichever pull request happens to run next, and on files that pull request never touched.
Establish that before anything else:

- Compare the failing paths against the pull request's own diff.
- Check when the base branch last ran.
  Green on `main` usually means *not run since the bump*, not *unaffected*.

Say so **once** on the surfacing pull request, then leave it alone.
Never fold the fix into it — a reformat across dozens of unrelated files buries whatever that pull request was actually for.

## Then: has the fleet taken a position?

### Already accepted — an entry exists saying to follow it

The convention exists; this repo simply has not been brought into line.

Open a **dedicated pull request** that adopts it — `markdownlint-cli2 --fix` where the rule is auto-fixable, by hand where it is not.
No approval needed; the decision was already made.

### Already rejected — an entry exists saying the fleet declined it

Open a **dedicated pull request** adding it to the repo's `.markdownlint-cli2.jsonc` alongside the existing overrides, **with the inline justification** that file's header requires.

### No position yet

Stop.
**Ask which it is** — accept the rule and adopt it, or reject and disable it.
This is a fleet-wide style decision and not one to infer from whichever answer is less work.

Give the user what they need to decide in one pass: what the rule wants, how many files and lines it touches, whether `--fix` handles it, whether rendering changes, and which other repos are affected.

Once decided, the change lands in this order:

1. **Against `claude-plugins`** — add the entry to [`prose-conventions.md`](prose-conventions.md).
   This is what makes it decided for every repo, so it comes first.
   Bump the plugin version and the matching `.claude-plugin/marketplace.json` entry **in the same commit**: a convention change that alters what an agent does is a minor bump, and this repo's `CLAUDE.md` requires both files to move together.
2. **Against the affected repo** — adopt or disable, as above.
   Skip this when the affected repo *is* `claude-plugins`; the two collapse into one.
3. **Against `flungo/github-workflows`** — only for a rejection that should become the fleet default, since the standard `.markdownlint-cli2.jsonc` shape is documented there rather than repeated per consumer.

A rejection does not *have* to be fleet-wide.
[`cross-references.md`](cross-references.md) keeps overrides "per-repo decisions, kept to a justified minimum", and that still holds: the fleet sets the default, and a repo may still deviate with its own justification.
What changed is only that a rule nobody has ever considered is not a repo's call to make silently.

## Before opening any of these: check for an existing pull request

The rule fires everywhere simultaneously, so another session — or an earlier you — may already have opened the fix.
Search the repo's open pull requests for the rule ID before creating one.

## Never suppress to go green

Disabling a rule the fleet has never considered, to unblock a pull request, is the one forbidden move — and the tempting one, because it works instantly.
It converts a decision the user should make into a silent default, in the file that is supposed to record decisions.
Same principle as link failures in [`cross-references.md`](cross-references.md): fix the target, never weaken the check.
Rejecting a rule is legitimate; rejecting it *without being asked*, to make a red tick go away, is not.

## Writing the entry

Keep it to the convention: what to do, and anything a reader would otherwise get wrong.
The reason it was adopted belongs in the commit message and the pull request that adopted it — the doc inherits that justification rather than restating it.

An entry that spends more lines on how the rule arrived than on what to write is one that every future reader pays for.
If the history is genuinely worth keeping, it is worth an ADR in the affected repo, not a paragraph here.
