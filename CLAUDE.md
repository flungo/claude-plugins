# CLAUDE.md — claude-plugins

Fabrizio's personal Claude Code / claude.ai plugin marketplace, `flungo-plugins`.
One repo of plugins usable from both Claude Code and claude.ai, kept in sync by pulling from this repo rather than by re-uploading files by hand.

> **Status: build-out complete.**
> The marketplace holds the full planned plugin set, and this repo's own CI validates its Markdown and its plugin manifests.
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
| **Personal (user)** | Installed + enabled in the claude.ai account; always on | `personal-defaults` (bundle) → `git-conventions`, `contributor-workflow`, `session-workflow`, `upstream-research`, `scaffolding`, `connector-conventions`; plus `personal-cloud-environment` → `claude-code-web` |
| **Repo-adopted (project)** | Declared in a repo's `.claude/settings.json` | `docs-standards`, `markdown-standards`, `writing-styles`, `claude-plugin-standards`, `terraform-standards`, `terraform-provider-standards` |

Reusable CI (markdownlint, lychee, `terraform` plan/apply) is **not** a plugin — it lives in `flungo/github-workflows` and is referenced by `scaffolding`.

This repo adopts those Markdown workflows and `flungo-workflows` itself (see § Markdown validation CI), plus a repo-specific plugin-validate workflow.

> **🤖 Agent** — `terraform-provider-standards` is deliberately scoped to conventions common to *any* provider; single-provider specifics (the coverage ratchet, container-based acceptance tests, and env-fallback provider config) stay in each provider's own `CLAUDE.md`.
> When a **second** Terraform provider exists, revisit extracting whatever the two genuinely share into the plugin.

## Plugin authoring conventions

The authoritative conventions are two plugins this repo dogfoods at project scope via [`.claude/settings.json`](.claude/settings.json) ([ADR-009](docs/decisions/009-plugin-authoring-standards.md)):

- **Structure** — `claude-plugin-standards` (`plugins/claude-plugin-standards/skills/plugin-authoring/SKILL.md`): the directory and manifest layout, declaring every dependency you reference, citing a dependency's skill or reference by name rather than by path, whether a plugin is ambient or on-demand and what may therefore depend on it, filing a fact by what it is a property of, skill naming in single- and multi-skill plugins, keeping cross-references current by basename, the reserved word that makes a skill silently fail to load on claude.ai, `SKILL.md` frontmatter hazards, validating and test-installing before committing, and the minor-versus-patch test.
- **Prose** — the instructional-writing style in `writing-styles` (`plugins/writing-styles/skills/writing-styles/references/instructional-writing.md`): state the current truth rather than the document's own history, converge on plain fact over time, fix wrong guidance at its source instead of annotating it, and never direct an agent to do what only the user can do.

Only what is specific to *this marketplace* stays here:

- **A new user-scope plugin must be reachable from a bundle.**
  `personal-defaults` carries the surface-independent set and `personal-cloud-environment` carries what a cloud session needs; between them they are the only things anything installs by name.
  A plugin in neither is one nobody installs, and nothing fails to say so.
- **The user-scope-only plugins are `scaffolding`, `claude-code-web`, and `upstream-research`** ([ADR-003](docs/decisions/003-owned-vs-third-party-adoption.md)), so no repo-adopted plugin here may declare one as a dependency or point at it.
- **Where each kind of fact goes here** ([ADR-008](docs/decisions/008-connector-behaviour-belongs-to-the-connector.md)): a connector's behaviour to its skill in `connector-conventions`, which tools exist at all to the surface plugin (`claude-code-web`), and platform behaviour an agent reasons about away from any tool to the domain plugin that owns the subject (`git-conventions`).
- **Two skills here are not named after their plugin** — `claude-code-web` ships `cloud-sessions`, and `claude-plugin-standards` ships `plugin-authoring` — both because the plugin name carries the reserved word.
  Deliberate, and not an inconsistency to tidy away.

## Sensitive information

This repo is **public** and its plugin/skill/reference content is world-readable.
Never commit tokens, keys, or secret values; skills that mention a secret use its **name** and a placeholder, never its value.

## Working with this repo in Claude Code

- GitHub interaction is via the **GitHub MCP** (`mcp__github__*`) — there is no `gh` CLI in web sessions.
- Use the `claude plugin` CLI (`validate`, `install`, `list`, `details`, `marketplace add`) to exercise changes; prefer a **local-path marketplace** when testing an in-flight branch.

## Branch management

The authoritative git conventions are the `git-conventions` plugin (`plugins/git-conventions/skills/git-conventions/references/git-conventions.md`) — this repo dogfoods them, enabling it at project scope via [`.claude/settings.json`](.claude/settings.json).
In brief:

- **Never commit to `main`.**
  Work on a feature branch; land via PR and let the user merge; delete the remote branch after merge.
- **Conventional Commits** — imperative subject, no trailing period; body for the *why*.
- **Linear history** — squash or rebase, never `git merge`.
  Squash a single logical change; rebase to preserve several distinct ones.
  When in doubt, squash.
- **No fixup commits** left on a branch; amend/fixup so history reads as though always correct.
  Force-push feature branches only, never `main`.

## Documentation standards

The authoritative documentation conventions are the `docs-standards` plugin (`plugins/docs-standards/skills/docs-standards/SKILL.md` and its `references/`) — this repo dogfoods them, enabling it at project scope via [`.claude/settings.json`](.claude/settings.json), and its own `docs/` is the plugin's reference implementation (ADR-002).
In brief:

- **Diátaxis split** — `docs/decisions/` (ADRs), `docs/plans/` (one-time, retired when done), and — when there is content — `docs/runbooks/` (repeatable) and `docs/reference/` (lookup).
  Each directory has a `README.md` index kept current **in the same commit** as any change to its documents.
- **ADRs** use the Nygard format (template in [`docs/decisions/README.md`](docs/decisions/README.md)); numbered sequentially, never deleted or renumbered.
- **Plans** are ephemeral — never referenced from permanent docs — and retired in a second PR once complete.
  Only § Active work below may link a live plan.
- **Two callouts, kept distinct** — `> **🤖 Agent** — …` for an instruction to an agent (one action per callout), and `> **Verify:** …` for uncertainty that can't be checked without live access.
- A session-end **doc-maintenance checklist** ships as the plugin's `Stop` hook.

## Markdown standards

The authoritative Markdown authoring conventions are the `markdown-standards` plugin (`plugins/markdown-standards/skills/markdown-standards/SKILL.md` and its `references/`) — this repo dogfoods them at project scope, and `docs-standards` declares it as a dependency (ADR-004).
They govern every Markdown file here, not only the ones under `docs/`.
In brief:

- **Semantic line breaks** — top-level prose is written one sentence per line; there is no line-length limit (`MD013` is off).
- **Cross-references** — never a bare identifier or "here" as link text; same-repo context is implied, cross-repo is qualified and linked in full.
- **Unique headings for link targets** — give any heading you cross-reference a unique name, so an anchor can't silently redirect.
- **Fix the link or its target, never suppress the check** — for markdownlint findings, link/anchor failures, and the external-URL sweep alike.

## Markdown validation CI

The checks those conventions pair with, adopted from [flungo/github-workflows](https://github.com/flungo/github-workflows) and pinned `@v2`: markdownlint (`.markdownlint-cli2.jsonc`), a blocking offline check of relative links and heading anchors on every PR, and a daily external-URL sweep that reports through a single auto-updated issue, and `markdown-sembr` — blocking on every PR — for the one semantic-line-break MUST rule, two sentences never sharing a source line.
A repo-specific `plugin-validate` workflow runs `claude plugin validate` on the marketplace and every plugin, so a broken manifest can't merge.
The conventions themselves stay in `markdown-standards` (above); only repo-specific facts belong here:

- **Tool version — read it from a CI run, don't trust this note.**
  The shared workflow tracks the action's major tag, so the linter version *floats*: it moved from `markdownlint-cli2-action@v19` (markdownlint-cli2 0.17.2 / markdownlint 0.37.4) to `@v24` (0.23.1 / 0.41.1) without any change here, and the new major added `MD060` — which failed CI on tables that had been clean for months (PR #31).
  Take the version from the first line of the markdownlint job's log and match it locally (`npx markdownlint-cli2@<version> "**/*.md" "!node_modules/**"`) before chasing findings; matching a *stale* pin gives a false pass, which is the failure mode this note exists to prevent.
  Last seen: **0.23.2** (markdownlint 0.41.1), 2026-08-30.
- **`.lycheeignore`** is populated only from this repo's own token-enabled `workflow_dispatch` runs, per the rules in its header.

## Active work

No plans are currently active.

## Key decisions

See [`docs/decisions/README.md`](docs/decisions/README.md).
In short:

- Split plugins by enablement scope (personal user-scope vs repo-adopted project-scope); compose via first-party dependencies; reusable CI lives in `github-workflows`, not the marketplace ([ADR-001](docs/decisions/001-marketplace-structure.md)).
- Diátaxis docs, Nygard ADRs, self-encoded rather than depending on a third-party ADR plugin ([ADR-002](docs/decisions/002-documentation-and-adr-model.md)).
- Markdown authoring conventions ship as the `markdown-standards` plugin here, referenced from the `github-workflows` docs instead of being inlined there or copied into consumer `CLAUDE.md`s ([ADR-004](docs/decisions/004-markdown-standards-plugin.md)).
- Generalisable guidance and Fabrizio's own applied configuration ship as separate plugins — `claude-code-web` holds for any user in any environment, `personal-cloud-environment` records his, and depends on it ([ADR-005](docs/decisions/005-generic-plugins-and-personal-configuration.md)).
- Plugin delivery differs per surface — a cloud-environment setup script carries the user-scope plugins into every cloud session, chat installs from the marketplace as its own enablement decision, and repo-adopted plugins are left at project scope even though they don't load in cloud sessions ([ADR-006](docs/decisions/006-plugin-delivery-per-surface.md)).
- Conventions for working through connectors ship as one plugin — `connector-conventions` — with a skill per connector plus cross-cutting skills, aspects within a connector split by reference file rather than by skill; its Drive skill finds a folder's `CONVENTIONS` document by walking the parent chain and applies the deepest one last, and the owner's actual rules stay in Drive rather than in a companion plugin ([ADR-007](docs/decisions/007-connector-carried-conventions.md)).
- A fact is sorted by what it is a property of, not by where it was discovered — connector behaviour to `connector-conventions`, which tools exist at all to the surface plugin, platform behaviour reasoned about away from any tool to the domain plugin that owns the subject ([ADR-008](docs/decisions/008-connector-behaviour-belongs-to-the-connector.md)).
- Prose styles ship as an on-demand `writing-styles` plugin that `claude-plugin-standards` and `docs-standards` both depend on, so the instructional-writing rules are stated once and cited by name; applying nothing until named is what makes it safe to depend on from either scope, and plugin *structure* conventions live in `claude-plugin-standards` ([ADR-009](docs/decisions/009-plugin-authoring-standards.md)).
