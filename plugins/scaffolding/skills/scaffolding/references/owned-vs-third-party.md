# Owned vs third-party — the gate

**Determining whether Fabrizio owns the repo is the first thing this plugin does** — everything else depends on it.

## Verify ownership — namespace is not enough

A repo is *owned* only if it is Fabrizio's **and not a fork**.
Being in his namespace is necessary but not sufficient: **to contribute to a third-party project he forks it into his own namespace**, so a fork sits there too.

> **🤖 Agent** — verify ownership before treating a repo as owned: check its **fork status** on GitHub (the `fork` flag / `parent`, via the GitHub MCP), and/or use the **contributor list** as a heuristic (sole/primary author → his; active upstream and other maintainers → third-party). Pre-existing adoption of his plugins or shared workflows in the repo is itself strong precedent that it's owned. When unsure, treat it as third-party.

## Owned repo — adopt what's relevant, at repo level

A repo he owns adopts the conventions **relevant to it** at repo level, so every contributor and session inherits them.

**Standards plugins** — enable, in the repo's `.claude/settings.json` (`extraKnownMarketplaces` → `flungo/claude-plugins`, `enabledPlugins` listing them), the ones relevant to the repo type:

| Repo kind | Enable |
|---|---|
| Any repo | `git-conventions`, `markdown-standards`, `docs-standards` |
| Terraform config repo | + `terraform-standards` |
| Terraform provider repo | + `terraform-provider-standards` |

Relevance is the rule — a Terraform *config* repo takes `terraform-standards`, not `terraform-provider-standards`.
`docs-standards` depends on `markdown-standards`, so it arrives either way; list it explicitly all the same, and take it **alone** in a repo that has Markdown but no `docs/` tree to govern.
`git-conventions` is personal (user-scope) but is applied at repo level too, so every contributor follows it.
The **purely personal** plugins — `scaffolding`, `claude-code-web`, `upstream-research` — are **user-scope only and never adopted at repo level**; `scaffolding` in particular assumes full autonomy over an owned repo, which only Fabrizio has.

**Shared CI** — adopt the `flungo/github-workflows` family relevant to the repo type, plus the version check (see `helper-repos.md`).

An owned repo adopts much of the standard and **extends it with bespoke additions** where its needs genuinely differ — e.g. a repo with a bespoke pipeline still takes the Markdown workflows and the version check.

## Third-party repo — do nothing without explicit consent

In a fork or a repo he doesn't own, this plugin does **nothing proactive**:

- Adopt **nothing** into the repo — no committed `.claude/settings.json`, no CI, no docs restructure.
- His user-scope plugins are still active for his own session (they travel with his account), but propose **no** repo-level adoption; adopt his plugins or CI **only if he explicitly asks**.
- Work **within the repo's own conventions** — its `CONTRIBUTING`/`CLAUDE.md`, CI, and commit/PR style.
