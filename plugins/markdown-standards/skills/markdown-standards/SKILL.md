---
name: markdown-standards
description: Fabrizio's Markdown authoring conventions. Consult this whenever writing or editing Markdown in one of his repos — adding or changing a link, cross-reference, or heading; fixing a markdownlint finding; fixing a failed link/anchor check (lychee) or a markdown-links external-sweep issue; deciding how to reference an ADR, file, or another repo; or onboarding a repo to the Markdown validation CI via /adopt-markdown-ci. Covers unambiguous cross-reference and link-text rules, semantic line breaks, unique cross-referenced headings, adjacent-blockquote handling, padded table delimiter rows, and fix-the-target-never-suppress remediation. Complements the repo's own CLAUDE.md rather than overriding it.
---

# Markdown Standards

Fabrizio's standing conventions for authoring Markdown — the **semantic** half of the Markdown validation standard.
The **mechanical** half is CI: his repos adopt the reusable `markdown-lint.yml` (markdownlint-cli2) and `markdown-links.yml` (lychee internal link/anchor check + scheduled external-URL sweep) workflows from [`flungo/github-workflows`](https://github.com/flungo/github-workflows) — see its [`docs/reference/markdown-validation.md`](https://github.com/flungo/github-workflows/blob/main/docs/reference/markdown-validation.md).
The tools verify that links resolve and style rules hold; this skill covers what they cannot — that references are unambiguous and correctly qualified, that prose follows the conventions the lint rules are configured around, and how to fix the failures the tools raise.

Apply these in any repo of Fabrizio's whenever you touch Markdown, whether or not that repo has adopted the CI.
**These conventions complement repo/context rules, they never supersede them** — where a repo's `CLAUDE.md`/`CONTRIBUTING.md` specifies something different, follow the repo.

## The reference files

Read the relevant reference before doing the work:

- **`references/cross-references.md`** — the cross-reference rules: unambiguous link text (never a bare identifier, never "here"), prefix labels, same-repo-implied vs cross-repo-explicit qualification, anchor disambiguation, relative-vs-full links, updating references on rename, and how to fix internal link/anchor failures and external-sweep findings (always fix the link or its target, never suppress the check).
  Read it before adding or fixing any link or cross-reference.
- **`references/prose-conventions.md`** — the prose conventions paired with the markdownlint rule defaults: semantic line breaks (`MD013` disabled), unique names for cross-referenced headings (`MD024` `siblings_only` and the anchor-ambiguity gap it leaves), adjacent-blockquote handling (`MD028`), and padded table delimiter rows (`MD060`).
  Read it before writing prose, structuring headings, or fixing a finding from one of those rules.
- **`references/adopt-markdown-ci.md`** — the `/adopt-markdown-ci` command procedure, including the parts of adoption that are *opinion* rather than mechanism: the markdownlint rule defaults, the check-then-fix commit discipline, and the reflow pass.

This plugin also ships **`scripts/reflow.py`** (`${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py`) — the render-gated one-time pass that migrates a repo's existing Markdown to semantic line breaks, covering top-level paragraphs, list items and blockquotes.
See `references/prose-conventions.md` for when and how to run it.

## Commands

### `/adopt-markdown-ci` (aliases: "adopt markdown CI", "add markdown validation")

Onboards a repo to the Markdown validation CI: adds the two caller workflows pinned to the current major, the per-repo config (`.markdownlint-cli2.jsonc`, `.lycheeignore`, `LYCHEE_GITHUB_TOKEN`), works through the checks in check-then-fix commit order, runs the render-gated semantic-line-break reflow, and adopts this plugin at project scope so the conventions travel with the repo.
Enabling this plugin in a repo *is* the opt-in, so the command has no further gate: run it wherever the plugin is enabled.

Full procedure: `references/adopt-markdown-ci.md`.

The workflows and these conventions are **separable** — a repo can adopt the CI and want none of this.
So the two sources divide cleanly: [`docs/runbooks/adopting-markdown-workflows.md`](https://github.com/flungo/github-workflows/blob/main/docs/runbooks/adopting-markdown-workflows.md) in `flungo/github-workflows` is authoritative for the **mechanical contract** any adopter needs (callers, `permissions:`, token provisioning, pitfalls) and should be opened rather than recalled; this plugin owns the **opinions** layered on top.
