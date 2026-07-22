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
| **Repo-adopted (project)** | Declared in a repo's `.claude/settings.json` | `docs-standards`, `terraform-standards`, `terraform-provider-standards` |

Reusable CI (markdownlint, lychee, `terraform` plan/apply) is **not** a plugin — it lives in `flungo/github-workflows` and is referenced by `scaffolding`.

Most of these do not exist yet; the plan tracks which have landed.

## Plugin authoring conventions

- **One plugin per `plugins/<name>/`**, with `.claude-plugin/plugin.json`, and
  skills under `skills/<skill-name>/SKILL.md` (+ `references/` for detail).
  Register each in `.claude-plugin/marketplace.json`.
- **Compose via first-party dependencies.** Where a plugin builds on another,
  list it in the plugin's `dependencies` array (bare string = latest in this
  marketplace). Installing the dependent auto-installs the dependency. Do not
  depend on third-party marketplaces (ADR-001, ADR-002).
- **`SKILL.md` frontmatter is YAML** — keep `name` and `description` on single
  lines and **avoid a colon-space (`: `) inside an unquoted value** (it parses
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
- **Semantic line breaks** — top-level prose is written one sentence per line.
- A session-end **doc-maintenance checklist** ships as the plugin's `Stop` hook.

## Active work

| Plan | Status |
|---|---|
| [Marketplace build-out](docs/plans/marketplace-buildout.md) | In progress — structure decided; split (#1), bootstrap + git-conventions dogfood (#2), and `docs-standards` plugin (#4) merged |

## Key decisions

See [`docs/decisions/README.md`](docs/decisions/README.md).
In short:

- Split plugins by enablement scope (personal user-scope vs repo-adopted
  project-scope); compose via first-party dependencies; reusable CI lives in
  `github-workflows`, not the marketplace ([ADR-001](docs/decisions/001-marketplace-structure.md)).
- Diátaxis docs, Nygard ADRs, self-encoded rather than depending on a
  third-party ADR plugin ([ADR-002](docs/decisions/002-documentation-and-adr-model.md)).
