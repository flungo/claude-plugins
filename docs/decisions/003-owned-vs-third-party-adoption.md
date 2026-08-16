# ADR-003: Owned-vs-third-party — adoption depends on who owns the repo

- **Date:** 2026-07-28
- **Status:** Accepted

## Context

Fabrizio's conventions are packaged as plugins at two enablement scopes ([ADR-001](001-marketplace-structure.md)): **user scope** (personal, always-on — they travel with his account) and **project scope** (repo-adopted, enabled in a repo's `.claude/settings.json` so every contributor and session inherits them).
Separately, shared reusable CI lives in [`flungo/github-workflows`](https://github.com/flungo/github-workflows), which his repos adopt by calling and pinning the workflows.

When a session works in a repo, it needs a rule for *how much* of this to apply.
In a repo Fabrizio owns, repo-level adoption is what he wants — every contributor should follow the house style.
In a repo he does **not** own, adopting anything into it imposes his conventions on someone else's project — wrong by default.

The naive test — "is the repo in his namespace?"
— does not work, because **to contribute to a third-party project he forks it into his own namespace**.
A fork sits in his namespace but is not his to standardise.
So ownership has to be *verified*, not inferred from the namespace.

## Decision

**Key the adoption decision on ownership, verified — not on namespace alone.**

**Determining ownership.**

A repo is *owned* only if it is his **and not a fork**.
Being in his namespace is necessary but not sufficient — a fork he made to contribute upstream also sits there.
Verify before treating a repo as owned:

- Check the repo's **fork status** on GitHub (its `fork` flag / `parent` — the authoritative signal).
- And/or use the **contributor list** as a heuristic — sole or primary author points to his own repo; an active upstream and other maintainers point to a fork/third-party.
- **Pre-existing adoption** of his plugins or shared workflows in the repo is strong precedent that it's owned (and that adopting further is expected).
- **When unsure, treat it as third-party** — the safe default, because third-party adopts nothing.

**Owned repo** (his, verified not a fork):

- Adopt at **repo level** — enable, in the repo's `.claude/settings.json`, `git-conventions` plus the project-scope standards *relevant to the repo type* (`docs-standards`, and `terraform-standards` or `terraform-provider-standards`).
  The purely-personal plugins (`scaffolding`, `claude-code-web`, `upstream-research`) are user-scope only and never adopted at repo level.
- Adopt the `flungo/github-workflows` reusable CI for the repo's type, and the version check.
- Repo-level adoption means every contributor and session inherits the conventions, not only Fabrizio's own sessions.

**Third-party repo** (someone else's project — including a fork of it in his namespace):

- Adopt **nothing** into the repo — no committed `.claude/settings.json`, no CI, no docs restructure.
- His user-scope plugins stay active for his own session (they travel with his account), but the plugin proposes **no** repo-level adoption and adopts his plugins or CI **only with his explicit consent**.
- Otherwise work **within the repo's own conventions** (its `CONTRIBUTING`/`CLAUDE.md`, CI, and commit/PR style).

**Owned means adopting what's relevant, and extending where needed.**

Adopt the plugins and workflows relevant to the repo's type — a Terraform *config* repo takes `terraform-standards`, not the provider standards.
An owned repo adopts much of the standard and **extends it with bespoke additions** where its needs genuinely differ (e.g. a repo with a bespoke pipeline still takes the Markdown workflows and the version check).

## Consequences

### Positive

- The verified test prevents the real failure mode — imposing house style on a repo Fabrizio doesn't own, including a fork of it he made to contribute upstream.
- Owned repos get consistent, contributor-wide conventions from a single `.claude/settings.json` plus the shared CI.
- The rule mirrors the user-vs-project plugin scopes already established in ADR-001, so there's one mental model, not two.

### Negative — trade-offs

- Ownership needs a verification step (a fork check / contributor heuristic) rather than a glance at the namespace, and a judgement call at the edges (an org he co-administers, a repo transferred in).
- Which families and standards plugins an owned repo adopts is per-repo judgement, not a mechanical rule — the plugin gives the default and the exceptions, not an algorithm.
