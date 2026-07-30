# ADR-004: Markdown conventions ship as a marketplace plugin, referenced from `github-workflows`

- **Date:** 2026-07-29
- **Status:** Accepted

## Context

The Markdown validation standard has two halves.
The **mechanical** half is reusable CI in [`flungo/github-workflows`](https://github.com/flungo/github-workflows) — `markdown-lint.yml` (markdownlint-cli2) and `markdown-links.yml` (lychee internal check + external sweep) — which per [ADR-001](001-marketplace-structure.md) is not a plugin.
The **semantic** half is Claude-facing prose: the `## Cross-references` rules, the conventions paired with the lint defaults (semantic line breaks / `MD013`, unique cross-referenced headings / `MD024`, adjacent blockquotes / `MD028`), and remediation guidance.

That semantic half was **inlined** in the `github-workflows` docs (`docs/runbooks/adopting-markdown-workflows.md`, `docs/reference/markdown-validation.md`), and each adopting repo **copied** the generic `## Cross-references` block into its own `CLAUDE.md`.
Copies drift: a fix to the rules would have to be re-pasted into every consumer.
[`github-workflows` issue #3](https://github.com/flungo/github-workflows/issues/3) captured the follow-up: extract the reusable, Claude-facing content into an installable plugin, and decide repo-exposed vs marketplace, skill vs command, and what the docs keep inline.

## Decision

**Ship the conventions as a `markdown-standards` plugin in this marketplace — not exposed from the `github-workflows` repo.**
ADR-001 already draws the line: reusable CI lives in `github-workflows`; Fabrizio's conventions, packaged to load automatically, live here.
Exposing a plugin from `github-workflows` would give the fleet a second plugin source to install, update, and validate.

**Shape:** one skill plus one named command.

- The **skill** carries the conventions and remediation guidance — `references/cross-references.md` (the former generic `CLAUDE.md` block, plus fix-the-target-never-suppress remediation) and `references/prose-conventions.md` (the three lint-paired conventions).
- The adoption starter prompt becomes the **`/adopt-markdown-ci` command** (a named command in the skill, following the `contributor-workflow` pattern), gated on verified ownership per [ADR-003](003-owned-vs-third-party-adoption.md) and deferring to the `github-workflows` adoption runbook as the source of truth.

**Scope:** repo-adopted (project scope), like the other `*-standards` plugins — and, like `git-conventions`, also useful at user scope: Fabrizio enables it personally so the conventions and `/adopt-markdown-ci` are available in a repo *before* it adopts anything.

**A separate plugin from `docs-standards`, which depends on it.**
The two overlap — `docs-standards` covered semantic line breaks — so the alternative was to fold the Markdown conventions into it.
[ADR-001](001-marketplace-structure.md)'s test settles it: plugins split by **enablement boundary**, and these have different ones.
`markdown-standards` is enablable at **user scope**, because Markdown authoring applies to every `.md` file Fabrizio touches — including in third-party repos where [ADR-003](003-owned-vs-third-party-adoption.md) forbids adopting anything *into* the repo.
`docs-standards` is project-scope only: it governs a `docs/` tree a repo has agreed to structure, and it ships a `Stop` hook that would be pure noise if it fired in every unrelated repo.
Folding them together would force that whole apparatus to travel wherever the Markdown rules are wanted.
The applicability is asymmetric in the same direction: every repo has Markdown (a `README.md` at minimum), only some have a governed `docs/` tree.

So the dependency runs **`docs-standards` → `markdown-standards`** (bare-string, first-party, per ADR-001): every docs adopter necessarily writes Markdown, but not vice versa.
`markdown-standards` becomes the single home of semantic line breaks — including the scope/exceptions and the render-gated migration *guidance* — and `docs-standards` keeps only the docs-specific *why* and points at it.

**`reflow.py` and the opinionated adoption steps move here too.**
The dividing line between the two repos is not knowledge-versus-executable but **mechanism versus opinion**, because `github-workflows` is *public reusable CI*: its workflows can be adopted in full by a repo that wants none of these conventions, so its runbook must not present them as part of the deal.
[ADR-001](001-marketplace-structure.md)'s "reusable CI is not a plugin" does not settle where `reflow.py` goes — it is not CI and never runs in CI.
What settles it is that `reflow.py` implements semantic line breaks, a preference the lint and link checks neither require nor invoke, and its change driver is this plugin's convention: its docstring flags list and blockquote inner paragraphs as a deliberate first-pass omission, and extending that is a decision made here.
So it ships here, as `docs-standards` already ships `scripts/doc-checklist.sh`.

By the same test, the runbook's opinionated adoption steps move into `/adopt-markdown-ci`: the markdownlint rule defaults (`MD013` off, `MD024` `siblings_only`), the check-then-fix commit discipline, and the reflow pass.
What stays in `github-workflows` is what any adopter needs regardless of house style — caller snippets, the required `permissions:` block, the purpose of each per-repo config file, `LYCHEE_GITHUB_TOKEN` provisioning and the `token:`-not-`env:` trap, and the tool-version and sandbox pitfalls — plus a thin pointer offering this plugin as an **optional** opinionated path.

**The `github-workflows` docs reference the plugin instead of inlining.**
The runbook's `## CLAUDE.md additions` section (the fenced `## Cross-references` block and the paired-conventions instruction) is replaced by "adopt `markdown-standards@flungo-plugins` at project scope"; the reference doc keeps the *rule rationale* (why `MD013` off, why `siblings_only`) and points at the plugin for the paired human conventions.
Thin one-line summaries remain for humans reading the docs directly; the normative text lives only in the plugin.

**The fleet's duplicated `CLAUDE.md` blocks migrate to the plugin.**
Consumer repos that inlined `## Cross-references` (or the semantic-line-break / `MD028` sections) switch to enabling the plugin and delete the copies — opportunistically, as each repo is next touched (`/adopt-markdown-ci` step), not as a big-bang sweep.
Repo-specific content (e.g. pinned local tool versions) stays in each repo's `CLAUDE.md`.

## Consequences

### Positive

- One source of truth: a rule fix lands here once and reaches every consumer via a marketplace update, instead of N `CLAUDE.md` re-pastes.
- The semantic-line-breaks rule stops being stated in two plugins.
  Consolidating it also retired a stale pointer in `docs-standards`, which still sent readers to a `reflow.py` inside a *plan* directory in `stalwart.flungo.net` — a path that disappears when that plan is retired.
  The tool now ships with this plugin, alongside the convention it implements.
- The conventions load automatically at the right scope (always-on for Fabrizio, contributor-wide in adopting repos) rather than depending on each repo's `CLAUDE.md` being current.
- `github-workflows` docs shrink to what that repo owns — the CI contract and adoption mechanics.

### Negative — trade-offs

- The Markdown standard now spans two repos: CI and adoption mechanics in `github-workflows`, conventions and the opinionated adoption path here.
  The cross-links must be kept accurate (the plugin's own rules apply).
- Adopting the CI and adopting the conventions are now two reads instead of one.
  Two-repo changes are rarer than that split suggests, though, because the move put the rule choices *and* the script on the same side of the line: a convention change that touches both stays here.
  Only a change spanning the **pipeline** and the conventions — a new check that needs a matching authoring rule, say — crosses repos, and that is the unlikely case.
  Accepted deliberately either way: it is the price of the workflows being genuinely reusable by a repo that does not want these opinions.
- Adopting `docs-standards` now pulls in a second plugin.
  That is the intended composition (as `contributor-workflow` → `git-conventions`), but a repo wanting *only* the docs structure can no longer get it alone — judged the right trade, since a `docs/` tree without Markdown conventions is not a case that arises.
- Until each consumer repo is touched, its inlined copy lingers and can drift from the plugin — the migration is opportunistic by design.
- Contributors without the marketplace configured (or humans reading on GitHub) see a pointer, not the rules; the plugin files remain world-readable as plain Markdown, so the cost is a click, not lost access.
