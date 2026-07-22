# ADR-001: Marketplace structure — split by enablement scope, compose via dependencies

- **Date:** 2026-07-22
- **Status:** Accepted

## Context

`flungo-plugins` packages Fabrizio's personal conventions as Claude Code /
claude.ai plugins so they load automatically — always-on for his account, or
adopted by a repository — rather than being restated per session or per repo.

Two questions needed a durable answer before authoring more than the first
plugin:

1. **Where do plugin boundaries fall?** A plugin is the unit Claude Code
   enables/disables at a scope; a skill is the topic unit *within* a plugin.
   Splitting the wrong way produces either monoliths that can't be enabled
   independently, or a scatter of overlapping fragments.
2. **How do plugins that build on each other relate?** Some plugins depend on
   the behaviour of another (a review command relies on the git hygiene
   rules).

A third fact constrains scope: some standards are **not Claude-facing skills**
at all (reusable CI — markdownlint, lychee, `terraform` plan/apply). They have
a different distribution channel and should not be forced into the marketplace.

## Decision

**Split plugins by enablement boundary, not by topic.** Two things always
enabled together at the same scope can be one plugin (as separate skills); two
things enabled at different scopes must be different plugins. Enablement maps
onto Claude Code's two scopes:

- **Personal — user scope** (installed + enabled in the claude.ai account,
  always on): `git-conventions`, `contributor-workflow`, `claude-code-web`,
  `upstream-research`, `scaffolding`.
- **Repo-adopted — project scope** (declared in a repo's
  `.claude/settings.json`, so every session on that repo inherits it):
  `docs-standards`, `terraform-standards`, `terraform-provider-standards`.

**Compose plugins via first-party marketplace dependencies.** Where a plugin
builds on another, it declares the dependency in its `.claude-plugin/plugin.json`
`dependencies` array (bare string = latest in this marketplace). Installing the
dependent auto-installs the dependency; `claude plugin prune` removes orphans.
The first instance is `contributor-workflow` → `git-conventions`.

**Reusable CI is not a plugin.** markdownlint, lychee link-checking, and
`terraform` plan/apply live in `flungo/github-workflows` as reusable workflows.
The `scaffolding` plugin *points* Claude to them when creating a repo or adopting
a toolchain; the workflows themselves are never marketplace entries.

## Consequences

**Positive**

- Each plugin is enabled at exactly the scope it belongs to; a repo can adopt
  `git-conventions` without pulling in personal review commands.
- Dependencies keep cross-plugin composition first-party — no coupling to
  third-party marketplaces or their release cadence.
- The marketplace stays a catalogue of Claude-facing capability; CI machinery
  is kept in its own channel.

**Negative — trade-offs**

- More plugins to author and version than a single bundle.
- Plugin names are install identifiers, so renames are breaking; names must be
  chosen for the domain, not the initial slice (cf. the repo-naming philosophy
  in the sibling Terraform repos).
- The split between "capability → plugin" and "CI → `github-workflows`" is a
  judgement call that must be applied consistently as new standards land.
