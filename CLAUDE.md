# CLAUDE.md — claude-plugins

Fabrizio's personal Claude Code / claude.ai plugin marketplace, `flungo-plugins`.
One repo of plugins usable from both Claude Code and claude.ai, kept in sync by pulling from this repo rather than by re-uploading files by hand.

> **Status: build-out under way.** The marketplace holds the seed plugin plus
> the plugins split out from it; the remaining plugins are authored one PR at a
> time. The structure and sequencing are scoped in
> [`docs/plans/marketplace-buildout.md`](docs/plans/marketplace-buildout.md).
> Keep this file, the README, the ADR index, and the plan current as plugins
> land.

## What this is

A marketplace named for the owner (`flungo-plugins`), not for any one plugin, so it can grow to cover many topics without a rename.
Its scope is **Fabrizio's personal conventions, packaged so they load automatically** — always-on for his account (user scope) or adopted by a repository (project scope) — rather than being restated per session.
See [ADR-001](docs/decisions/001-marketplace-structure.md).

## Structure

Plugins are split by **enablement boundary, not by topic** (ADR-001): a plugin is the unit enabled/disabled at a scope; a skill is the topic unit within it.

| Scope | Enabled how | Plugins |
|---|---|---|
| **Personal (user)** | Installed + enabled in the claude.ai account; always on | `git-conventions`, `contributor-workflow`, `claude-code-web`, `upstream-research`, `scaffolding` |
| **Repo-adopted (project)** | Declared in a repo's `.claude/settings.json` | `docs-standards`, `markdown-standards`, `terraform-standards`, `terraform-provider-standards` |

Reusable CI (markdownlint, lychee, `terraform` plan/apply) is **not** a plugin — it lives in `flungo/github-workflows` and is referenced by `scaffolding`.

All the plugins above have landed; the plan tracks the remaining build-out (this repo's own CI) before it retires.

> **🤖 Agent** — `terraform-provider-standards` is deliberately scoped to conventions common to *any* provider; single-provider specifics (the coverage ratchet, container-based acceptance tests, and env-fallback provider config) stay in each provider's own `CLAUDE.md`. When a **second** Terraform provider exists, revisit extracting whatever the two genuinely share into the plugin.

## Plugin authoring conventions

- **One plugin per `plugins/<name>/`**, with `.claude-plugin/plugin.json`, and
  skills under `skills/<skill-name>/SKILL.md` (+ `references/` for detail).
  Register each in `.claude-plugin/marketplace.json`.
- **Compose via first-party dependencies.** Where a plugin builds on another,
  list it in the plugin's `dependencies` array (bare string = latest in this
  marketplace). Installing the dependent auto-installs the dependency. Do not
  depend on third-party marketplaces ([ADR-001](docs/decisions/001-marketplace-structure.md),
  [ADR-002](docs/decisions/002-documentation-and-adr-model.md)).
- **Never reference a user-scope-only plugin from a project-scope one.**
  `scaffolding`, `claude-code-web`, and `upstream-research` are user-scope only and never repo-adopted ([ADR-003](docs/decisions/003-owned-vs-third-party-adoption.md)), so a repo-adopted plugin cannot declare one as a dependency — and pointing at it anyway leaves a reference that dangles wherever the plugin is enabled at project scope.
  Where both need the same rule, cite the **ADR** that records it (by full URL, since an installed plugin has no `docs/` tree beside it), or state the rule locally.
- **`SKILL.md` frontmatter is YAML** — keep `name` and `description` on single
  lines and **avoid a colon followed by a space (`:` + space) inside an unquoted value** (it parses
  as a mapping and silently drops the frontmatter). The `description` is what
  drives skill triggering; write it for that.
- **Validate before committing:** `claude plugin validate .` (marketplace) and
  `claude plugin validate plugins/<name>` (each plugin). Test-install from the
  local path and confirm the skill loads and any dependency resolves.
- **Name for the domain, not the initial slice** — plugin names are install
  identifiers, so a rename is breaking.
- **Evals** live under a plugin's `evals/` (dev-time fixtures, not loaded at
  runtime).

## Sensitive information

This repo is **public** and its plugin/skill/reference content is world-readable.
Never commit tokens, keys, or secret values; skills that mention a secret use its **name** and a placeholder, never its value.

## Working with this repo in Claude Code

- GitHub interaction is via the **GitHub MCP** (`mcp__github__*`) — there is no
  `gh` CLI in web sessions.
- Use the `claude plugin` CLI (`validate`, `install`, `list`, `details`,
  `marketplace add`) to exercise changes; prefer a **local-path marketplace**
  when testing an in-flight branch.

## Branch management

The authoritative git conventions are the `git-conventions` plugin (`plugins/git-conventions/skills/git-conventions/references/git-conventions.md`) — this repo dogfoods them, enabling it at project scope via [`.claude/settings.json`](.claude/settings.json).
In brief:

- **Never commit to `main`.** Work on a feature branch; land via PR and let the
  user merge; delete the remote branch after merge.
- **Conventional Commits** — imperative subject, no trailing period; body for
  the *why*.
- **Linear history** — squash or rebase, never `git merge`. Squash a single
  logical change; rebase to preserve several distinct ones. When in doubt,
  squash.
- **No fixup commits** left on a branch; amend/fixup so history reads as though
  always correct. Force-push feature branches only, never `main`.

## Documentation standards

The authoritative documentation conventions are the `docs-standards` plugin (`plugins/docs-standards/skills/docs-standards/SKILL.md` and its `references/`) — this repo dogfoods them, enabling it at project scope via [`.claude/settings.json`](.claude/settings.json), and its own `docs/` is the plugin's reference implementation (ADR-002).
In brief:

- **Diátaxis split** — `docs/decisions/` (ADRs), `docs/plans/` (one-time,
  retired when done), and — when there is content — `docs/runbooks/`
  (repeatable) and `docs/reference/` (lookup). Each directory has a `README.md`
  index kept current **in the same commit** as any change to its documents.
- **ADRs** use the Nygard format (template in
  [`docs/decisions/README.md`](docs/decisions/README.md)); numbered
  sequentially, never deleted or renumbered.
- **Plans** are ephemeral — never referenced from permanent docs — and retired
  in a second PR once complete. Only § Active work below may link a live plan.
- **Two callouts, kept distinct** — `> **🤖 Agent** — …` for an instruction to
  an agent (one action per callout), and `> **Verify:** …` for uncertainty that
  can't be checked without live access.
- A session-end **doc-maintenance checklist** ships as the plugin's `Stop` hook.

## Markdown standards

The authoritative Markdown authoring conventions are the `markdown-standards` plugin (`plugins/markdown-standards/skills/markdown-standards/SKILL.md` and its `references/`) — this repo dogfoods them at project scope, and `docs-standards` declares it as a dependency (ADR-004).
They govern every Markdown file here, not only the ones under `docs/`.
In brief:

- **Semantic line breaks** — top-level prose is written one sentence per line;
  there is no line-length limit (`MD013` is off).
- **Cross-references** — never a bare identifier or "here" as link text;
  same-repo context is implied, cross-repo is qualified and linked in full.
- **Unique headings for link targets** — give any heading you cross-reference a
  unique name, so an anchor can't silently redirect.
- **Fix the link or its target, never suppress the check** — for markdownlint
  findings, link/anchor failures, and the external-URL sweep alike.

## Active work

| Plan | Status |
|---|---|
| [Marketplace build-out](docs/plans/marketplace-buildout.md) | In progress — structure decided; split (#1), bootstrap + git-conventions dogfood (#2), `docs-standards` plugin (#4), `claude-code-web` (#5), `upstream-research` (#6), `terraform-standards` (#7), `terraform-provider-standards` (#8), `scaffolding` (#10), and `markdown-standards` (#14) merged; only this repo's own CI remains |

## Key decisions

See [`docs/decisions/README.md`](docs/decisions/README.md).
In short:

- Split plugins by enablement scope (personal user-scope vs repo-adopted
  project-scope); compose via first-party dependencies; reusable CI lives in
  `github-workflows`, not the marketplace ([ADR-001](docs/decisions/001-marketplace-structure.md)).
- Diátaxis docs, Nygard ADRs, self-encoded rather than depending on a
  third-party ADR plugin ([ADR-002](docs/decisions/002-documentation-and-adr-model.md)).
- Markdown authoring conventions ship as the `markdown-standards` plugin here,
  referenced from the `github-workflows` docs instead of being inlined there or
  copied into consumer `CLAUDE.md`s ([ADR-004](docs/decisions/004-markdown-standards-plugin.md)).
