# CLAUDE.md — claude-plugins

Fabrizio's personal Claude Code / claude.ai plugin marketplace, `flungo-plugins`.
One repo of plugins usable from both Claude Code and claude.ai, kept in sync by pulling from this repo rather than by re-uploading files by hand.

> **Status: build-out complete.** The marketplace holds the full planned plugin
> set, and this repo's own CI validates its Markdown and its plugin manifests.
> Keep this file, the README, and the ADR index current as plugins evolve.

## What this is

A marketplace named for the owner (`flungo-plugins`), not for any one plugin, so it can grow to cover many topics without a rename.
Its scope is **Fabrizio's personal conventions, packaged so they load automatically** — always-on for his account (user scope) or adopted by a repository (project scope) — rather than being restated per session.
See [ADR-001](docs/decisions/001-marketplace-structure.md).

**Delivery differs per surface** ([ADR-006](docs/decisions/006-plugin-delivery-per-surface.md)): the local CLI installs from the marketplace directly, cloud sessions get the user-scope plugins from the cloud environment's setup script (recorded in the README), and claude.ai chat installs from the marketplace directly, which now works — the crash that blocked it was a duplicate-marketplace-name bug, since resolved.
Chat is its own enablement decision, not a smaller copy of the user-scope set: install there only what belongs in a chat window.
Repo-adopted plugins do not load in cloud sessions at all, which is why a repo's own `CLAUDE.md` still has to summarise the rules it adopts.

## Structure

Plugins are split by **enablement boundary, not by topic** (ADR-001): a plugin is the unit enabled/disabled at a scope; a skill is the topic unit within it.

| Scope | Enabled how | Plugins |
| --- | --- | --- |
| **Personal (user)** | Installed + enabled in the claude.ai account; always on | `personal-defaults` (bundle) → `git-conventions`, `contributor-workflow`, `upstream-research`, `scaffolding`; plus `personal-cloud-environment` → `claude-code-web` |
| **Repo-adopted (project)** | Declared in a repo's `.claude/settings.json` | `docs-standards`, `markdown-standards`, `terraform-standards`, `terraform-provider-standards` |

Reusable CI (markdownlint, lychee, `terraform` plan/apply) is **not** a plugin — it lives in `flungo/github-workflows` and is referenced by `scaffolding`.

This repo adopts those Markdown workflows and `flungo-workflows` itself (see § Markdown validation CI), plus a repo-specific plugin-validate workflow.

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
- **A new user-scope plugin must be reachable from a bundle.** `personal-defaults`
  carries the surface-independent set and `personal-cloud-environment` carries
  what a cloud session needs; between them they are the only things anything
  installs by name. A plugin in neither is one nobody installs, and nothing
  fails to say so.
- **Never reference a user-scope-only plugin from a project-scope one.**
  `scaffolding`, `claude-code-web`, and `upstream-research` are user-scope only and never repo-adopted ([ADR-003](docs/decisions/003-owned-vs-third-party-adoption.md)), so a repo-adopted plugin cannot declare one as a dependency — and pointing at it anyway leaves a reference that dangles wherever the plugin is enabled at project scope.
  Where both need the same rule, cite the **ADR** that records it (by full URL, since an installed plugin has no `docs/` tree beside it), or state the rule locally.
- **Keep generalisable guidance separate from the owner's own configuration.**
  A plugin whose content would hold for any reader stays that way; the concrete
  settings *Fabrizio* has applied — an environment's allowlist, its variables,
  its setup — live in a companion plugin that depends on it, so neither is
  diluted by the other. `claude-code-web` (generic) and
  `personal-cloud-environment` (his applied environment) are the worked example
  ([ADR-005](docs/decisions/005-generic-plugins-and-personal-configuration.md)).
- **A skill's `name` must not contain `claude`.** claude.ai's marketplace
  ingestion rejects it outright — `plugin_upload_skill_upload_name_reserved_words`,
  *"Skill name in SKILL.md cannot contain the reserved word 'claude'"* — so the
  skill silently never loads on that surface. Nothing local catches this:
  `claude plugin validate` passes, and Claude Code loads the skill normally, so
  the only signal is the marketplace's `sync_errors` after a sync.
  The restriction appears to bind **skills only** — the `claude-code-web`
  *plugin* synced under that name while its skill was rejected — which is why
  that skill is `cloud-sessions` while the plugin keeps its name. Prefer a
  skill name that describes the domain without naming the product.
  Every other plugin here names its skill after itself, so `claude-code-web` is
  the one mismatch — deliberate, and not an inconsistency to tidy away.
- **`SKILL.md` frontmatter is YAML** — keep `name` and `description` on single
  lines and **avoid a colon followed by a space (`:` + space) inside an unquoted value** (it parses
  as a mapping and silently drops the frontmatter). The `description` is what
  drives skill triggering; write it for that.
- **Validate before committing:** `claude plugin validate .` (marketplace) and
  `claude plugin validate plugins/<name>` (each plugin). Test-install from the
  local path and confirm the skill loads and any dependency resolves.
- **Bump the version when a plugin's behaviour or footprint changes.** These are content plugins pulled from this repo, not immutable releases, so the version is a human signal rather than a resolver input — keep it cheap.
  **Minor** for anything a consumer would notice: a skill or command added or removed, a new dependency or hook, a shipped script, or a convention change that alters what an agent does.
  **Patch** for wording that clarifies without changing a rule.
  **Major** for a break — a rename, a removed command, or a reversal that invalidates a repo's existing `.claude/settings.json`.
  Update the matching `marketplace.json` entry in the same commit.
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

## Markdown validation CI

The checks those conventions pair with, adopted from [flungo/github-workflows](https://github.com/flungo/github-workflows) and pinned `@v2`: markdownlint (`.markdownlint-cli2.jsonc`), a blocking offline check of relative links and heading anchors on every PR, and a daily external-URL sweep that reports through a single auto-updated issue.
A repo-specific `plugin-validate` workflow runs `claude plugin validate` on the marketplace and every plugin, so a broken manifest can't merge.
The conventions themselves stay in `markdown-standards` (above); only repo-specific facts belong here:

- **Tool version — read it from a CI run, don't trust this note.** The shared
  workflow tracks the action's major tag, so the linter version *floats*: it
  moved from `markdownlint-cli2-action@v19` (markdownlint-cli2 0.17.2 /
  markdownlint 0.37.4) to `@v24` (0.23.1 / 0.41.1) without any change here, and
  the new major added `MD060` — which failed CI on tables that had been clean
  for months (PR #31). Take the version from the first line of the
  markdownlint job's log and match it locally
  (`npx markdownlint-cli2@<version> "**/*.md" "!node_modules/**"`) before
  chasing findings; matching a *stale* pin gives a false pass, which is the
  failure mode this note exists to prevent. Last seen: **0.23.1**
  (markdownlint 0.41.1), 2026-08-01.
- **`.lycheeignore`** is populated only from this repo's own token-enabled
  `workflow_dispatch` runs, per the rules in its header.

## Active work

No plans are currently active.

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
- Generalisable guidance and Fabrizio's own applied configuration ship as
  separate plugins — `claude-code-web` holds for any user in any environment,
  `personal-cloud-environment` records his, and depends on it
  ([ADR-005](docs/decisions/005-generic-plugins-and-personal-configuration.md)).
- Plugin delivery differs per surface — a cloud-environment setup script carries
  the user-scope plugins into every cloud session, chat installs from the
  marketplace as its own enablement decision, and repo-adopted plugins are left
  at project scope even though they don't load in cloud sessions
  ([ADR-006](docs/decisions/006-plugin-delivery-per-surface.md)).
