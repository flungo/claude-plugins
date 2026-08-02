# claude-plugins

Personal Claude Code / Claude.ai plugin marketplace.
One repo, plugins usable from both Claude Code and claude.ai, kept in sync by pulling from this repo rather than by re-uploading files by hand.

## Plugins

- **[git-conventions](plugins/git-conventions)** — standing git/PR hygiene
  conventions (branch management, Conventional Commits, linear history,
  squash-vs-rebase, no fixup commits, force-push policy, and which commit
  signature warnings to ignore). Applies to all git work, not just a named
  command.
- **[contributor-workflow](plugins/contributor-workflow)** — personal
  contributor/review workflow commands. Currently one command,
  `/ready-to-merge` (aliases "Ready to Merge?", "RTM?"); more expected over
  time. Depends on `git-conventions`.
- **[docs-standards](plugins/docs-standards)** — repo-adopted documentation
  conventions (project scope): the Diátaxis `docs/` split, Nygard ADRs, the
  ephemeral-plan lifecycle, README-index and staleness discipline, the agent
  and verify callouts, and a session-end doc-maintenance checklist hook.
  Depends on `markdown-standards`.
- **[claude-code-web](plugins/claude-code-web)** — always-on working
  preferences for Claude Code Web (user scope): the egress proxy and CA bundle,
  GitHub-via-MCP, containers replaced across idle periods, repo scoping and
  `add_repo`'s cross-owner rule, project config in a multi-repo session, and
  delegating unrunnable steps to CI. Written to hold for any Claude Code Web
  user, in any environment.
- **[personal-cloud-environment](plugins/personal-cloud-environment)** — the
  record of Fabrizio's own Claude Code Web environment (user scope): the
  domains, environment variables, and setup he has applied on top of the
  platform defaults, and the round-trip rule that keeps that record and the
  live environment in step. The owner-specific counterpart to
  `claude-code-web`, which it depends on.
- **[upstream-research](plugins/upstream-research)** — personal, always-on
  method (user scope) for verifying facts about third-party/upstream
  components: go to the authoritative source (the project's own repo and docs),
  distrust training data, web-search summaries, and generated docs, and record
  provenance.
- **[terraform-standards](plugins/terraform-standards)** — repo-adopted
  conventions (project scope) for a Terraform/HCL config repo: one `.tf` per
  concern, resource names that mirror the real object, sensitive values as
  variables, durations as arithmetic, pinned providers with a committed lock,
  and adopting existing resources via `import {}` blocks.
- **[terraform-provider-standards](plugins/terraform-provider-standards)** —
  repo-adopted conventions (project scope) for building a Terraform provider in
  Go: the terraform-plugin-framework layout, `tfplugindocs`-generated docs,
  MPL-2.0 per-file headers, and adopting the shared `flungo/github-workflows`
  provider CI (golangci-lint v2, GoReleaser dual-registry release).
- **[markdown-standards](plugins/markdown-standards)** — repo-adopted Markdown
  authoring conventions (project scope): unambiguous cross-references and link
  hygiene, semantic line breaks, unique cross-referenced headings,
  adjacent-blockquote handling, compact tables (delimiter rows included),
  handling lint rules a linter bump introduces, fixing markdownlint and
  link/anchor CI failures (fix the target, never suppress), and
  `/adopt-markdown-ci` for onboarding a repo to the reusable Markdown CI from
  `flungo/github-workflows`.
- **[scaffolding](plugins/scaffolding)** — personal, always-on guide (user
  scope) for setting up, building out, and extending repos across the fleet:
  gated on verified ownership (an owned repo adopts the conventions and standards
  plugins; a fork or third-party repo gets nothing without explicit consent),
  routing to the shared CI and the helper repos (`github-workflows`,
  `claude-plugins`, `terraform-github`) added as needed.

## Install in Claude Code

```text
/plugin marketplace add flungo/claude-plugins
/plugin install contributor-workflow@flungo-plugins
```

Installing `contributor-workflow` pulls in its `git-conventions` dependency automatically.
To install just the standing conventions on their own:

```text
/plugin install git-conventions@flungo-plugins
```

To pull in updates later:

```text
/plugin marketplace update flungo-plugins
```

(Claude Code also refreshes marketplaces in the background periodically; `update` forces it immediately.)

## Install in claude.ai (web, desktop, Cowork)

1. Open **Customize** in the left sidebar → **Plugins** tab.
2. Under **Personal plugins**, click "+" → **Add marketplace**.
3. Choose **Add from a repository** and paste this repo's URL:
   `https://github.com/flungo/claude-plugins`
4. Claude parses `.claude-plugin/marketplace.json` and lists the plugins —
   install `contributor-workflow` (which brings in `git-conventions`), or
   `git-conventions` on its own.

To pick up updates after pushing changes here, use the marketplace's "Update" action in the Plugins tab to pull the latest commit.

## Repo layout

```text
.claude-plugin/marketplace.json     — marketplace catalog
plugins/<plugin-name>/
  .claude-plugin/plugin.json        — plugin manifest
  skills/<skill-name>/SKILL.md      — the skill Claude loads
  skills/<skill-name>/references/   — supporting reference docs
  evals/                            — dev-time test fixtures (not loaded at runtime)
```

Adding a new plugin later: create `plugins/<new-plugin>/` following the same shape, then add an entry to `.claude-plugin/marketplace.json`'s `plugins` array.

## Conventions

Commits in this repo follow the same git conventions documented in `plugins/git-conventions/skills/git-conventions/references/git-conventions.md` — Conventional Commits, linear history, one logical change per commit.
