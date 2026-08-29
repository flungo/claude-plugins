# claude-plugins

Personal Claude Code / Claude.ai plugin marketplace.
One repo, plugins kept in sync by pulling from this repo rather than by re-uploading files by hand.
All three surfaces are covered — the local Claude Code CLI, cloud sessions, and claude.ai chat — but each pulls through a different mechanism ([ADR-006](docs/decisions/006-plugin-delivery-per-surface.md)).

## Plugins

- **[personal-defaults](plugins/personal-defaults)** — the always-on personal set as a single install (user scope).
  A dependency-only bundle carrying `git-conventions`, `contributor-workflow`, `session-workflow`, `upstream-research`, `scaffolding`, and `connector-conventions`; it contributes no skills of its own and costs no context.
  The Claude Code Web plugins stay outside it, being useful only there — `personal-cloud-environment` picks them up instead.
- **[git-conventions](plugins/git-conventions)** — standing git/PR hygiene conventions (branch management, Conventional Commits, linear history, squash-vs-rebase, no fixup commits, force-push policy, and which commit signature warnings to ignore).
  Applies to all git work, not just a named command.
- **[contributor-workflow](plugins/contributor-workflow)** — personal contributor/review workflow commands.
  Currently one command, `/ready-to-merge` (aliases "Ready to Merge?", "RTM?"); more expected over time.
  Depends on `git-conventions`.
- **[docs-standards](plugins/docs-standards)** — repo-adopted documentation conventions (project scope): the Diátaxis `docs/` split, Nygard ADRs, the ephemeral-plan lifecycle, README-index and staleness discipline, the agent and verify callouts, and a session-end doc-maintenance checklist hook.
  Depends on `markdown-standards`.
- **[claude-code-web](plugins/claude-code-web)** — always-on working preferences for Claude Code Web (user scope): the egress proxy and CA bundle, GitHub-via-MCP, containers replaced across idle periods, repo scoping and `add_repo`'s cross-owner rule, project config in a multi-repo session, why repo-adopted plugins never load and how the user-scope ones arrive, and delegating unrunnable steps to CI.
  Written to hold for any Claude Code Web user, in any environment.
- **[personal-cloud-environment](plugins/personal-cloud-environment)** — the record of Fabrizio's own Claude Code Web environment (user scope): the domains, environment variables, and setup he has applied on top of the platform defaults, and the round-trip rule that keeps that record and the live environment in step.
  The owner-specific counterpart to `claude-code-web`, which it depends on — and, because what that environment carries is part of describing it, `personal-defaults` too.
  Installing this one plugin is therefore the whole cloud-session setup.
- **[connector-conventions](plugins/connector-conventions)** — conventions for working through connectors (user scope): both the rules a connected store carries in its own content and the rules an agent should follow when using it.
  `google-drive` covers Drive, where a `CONVENTIONS` document governs its own folder and everything beneath it, discovered by walking a file's parent chain, cached for the session, and applied deepest-first — plus the connector's verified behaviours and how to write such a document.
  `data-boundaries` is cross-cutting, for information crossing between sources — a connector, another connector, and the local repo.
  The mechanism ships here; the rules themselves stay in the store, beside the content they describe.
- **[upstream-research](plugins/upstream-research)** — personal, always-on method (user scope) for verifying facts about third-party/upstream components: go to the authoritative source (the project's own repo and docs), distrust training data, web-search summaries, and generated docs, and record provenance.
- **[terraform-standards](plugins/terraform-standards)** — repo-adopted conventions (project scope) for a Terraform/HCL config repo: one `.tf` per concern, resource names that mirror the real object, sensitive values as variables, durations as arithmetic, pinned providers with a committed lock, and adopting existing resources via `import {}` blocks.
- **[terraform-provider-standards](plugins/terraform-provider-standards)** — repo-adopted conventions (project scope) for building a Terraform provider in Go: the terraform-plugin-framework layout, `tfplugindocs`-generated docs, MPL-2.0 per-file headers, and adopting the shared `flungo/github-workflows` provider CI (golangci-lint v2, GoReleaser dual-registry release).
- **[markdown-standards](plugins/markdown-standards)** — repo-adopted Markdown authoring conventions (project scope): unambiguous cross-references and link hygiene, semantic line breaks, unique cross-referenced headings, adjacent-blockquote handling, compact tables (delimiter rows included), handling lint rules a linter bump introduces, fixing markdownlint and link/anchor CI failures (fix the target, never suppress), and `/adopt-markdown-ci` for onboarding a repo to the reusable Markdown CI from `flungo/github-workflows`.
- **[session-workflow](plugins/session-workflow)** — personal, always-on commands (user scope) for ending a Claude session well: `/session-clean` (aliases "Session Clean?", "Safe to delete?")
  checks whether closing the session would lose anything and proposes where each loose end should be recorded, and `/handoff` produces a document that carries unfinished work into a fresh session.
  The two halves of the same moment — record it, or carry it.
- **[scaffolding](plugins/scaffolding)** — personal, always-on guide (user scope) for setting up, building out, and extending repos across the fleet: gated on verified ownership (an owned repo adopts the conventions and standards plugins; a fork or third-party repo gets nothing without explicit consent), routing to the shared CI and the helper repos (`github-workflows`, `claude-plugins`, `terraform-github`) added as needed.

## Install in Claude Code (local CLI)

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

## Install in Claude Code Web and other cloud sessions

Cloud sessions install no plugins of their own, and a repo's `.claude/settings.json` declaration has no effect in one — see [ADR-006](docs/decisions/006-plugin-delivery-per-surface.md).
The working channel is the **setup script** on the cloud environment, which runs before Claude Code launches.

Set it at [claude.ai/code](https://claude.ai/code) → the environment selector above the message box → the environment's settings icon → **Setup script**:

```bash
#!/bin/bash
# Resolve the CLI without assuming it is on PATH. /opt/node*/bin/claude is only a
# symlink to a self-contained binary, and that directory is added to PATH by
# /etc/profile.d/nodejs.sh — so a non-login shell doesn't have it.
CLAUDE="$(command -v claude 2>/dev/null || true)"
if [ -z "$CLAUDE" ]; then
  for candidate in /opt/claude-code/bin/claude /opt/node*/bin/claude; do
    if [ -x "$candidate" ]; then CLAUDE="$candidate"; break; fi
  done
fi
if [ -z "$CLAUDE" ]; then
  echo "setup: claude CLI not found — skipping plugin install" >&2
  exit 0
fi

"$CLAUDE" plugin marketplace add flungo/claude-plugins || echo "setup: FAILED to add marketplace" >&2

# personal-cloud-environment carries claude-code-web and the personal-defaults
# bundle through its dependencies, so this one install is the whole setup.
"$CLAUDE" plugin install personal-cloud-environment@flungo-plugins --scope user \
  || echo "setup: FAILED to install personal-cloud-environment" >&2
exit 0
```

This is the authoritative copy of that script — the environment holds the only live one, and nothing here can detect drift between the two.

Every step is deliberately non-fatal, because a setup script that exits non-zero stops the session from starting at all.
But a bare `|| true` hides a failed install behind a session that starts perfectly and is simply missing a plugin, so each step announces its own failure instead.
A named plugin that isn't on this repo's default branch yet fails exactly that way — the install returns non-zero, the session starts, and nothing else says so.

One environment serves every cloud surface, so this covers Claude Code Web, `claude --cloud`, the mobile and Desktop apps, routines, and Claude Tag, in every repository rather than only in repos that adopt this marketplace.

Installed versions are frozen into the environment's filesystem snapshot, which rebuilds when the script changes or after roughly seven days.
To pull newer plugin versions immediately, edit the script — changing a comment is enough — which forces a rebuild on the next session.
The same applies after a plugin is *added* to this marketplace: the snapshot has no idea the catalogue changed, so a newly published plugin only arrives once the script is edited or the cache expires.

`SKIP_PLUGIN_MARKETPLACE=true` is set in every cloud session and **cannot be overridden** from the environment's variables — the platform sets it after copying yours, verified with a canary variable.
Nothing in this flow depends on changing it; it is noted so nobody spends an afternoon trying.

## Install in claude.ai chat (web, Desktop Chat tab, Cowork)

**Add the marketplace** — **Settings** → **Plugins** → **Add** → **Add marketplace** → **Add from a repository**, paste `https://github.com/flungo/claude-plugins`, then **Sync**.

**Install from it** — **Settings** → **Plugins** → **Browse** → **Personal**, which lists every plugin in the marketplace: a **+** to install, a cog once it is installed.

**Check its sync state** — same screen.
Above the plugin list the marketplace appears under its repository name (`claude-plugins`), with a **…** menu carrying the short **Synced commit** sha, a **Sync automatically** toggle (on by default), **Check for updates**, and **Remove**.

Installed plugins' skills load into every conversation, namespaced as `<plugin>:<skill>`, with their `references/` readable.

Install only what belongs in a chat window.
The plugins here are written for repo work, so a plugin that is always-on in Claude Code is not automatically one you want in chat — that is a separate enablement decision, not a smaller version of the same one, and it is the one surface where the set can be narrowed to what a chat can actually use.

This crashed for months, and the cause is worth knowing because it can recur.
Two marketplace records for this repo were created 88 ms apart by a double-submit, and the Personal tab appears to key its list on `name` rather than `id` — so two records sharing a name send it into a React update-depth loop that unmounts the whole app, with no way to reach the UI that would let you delete either.
Deleting one record resolved it: the tab renders, all plugins list, and **Add marketplace** works again.
Filed upstream with captures and an instrumented trace as [anthropics/claude-code#83139](https://github.com/anthropics/claude-code/issues/83139); tracked here in [issue #21](https://github.com/flungo/claude-plugins/issues/21).

**If the Plugins tab ever unmounts the app again, suspect a duplicate marketplace name first.**
Two repos with the same name under different owners — `alice/plugins` and `bob/plugins` — would do it, since `name` is derived from the repo name.

Note separately that claude.ai's ingestion rejects any skill whose name contains the reserved word `claude` — unrelated to the crash, and a rule for authoring skills here rather than a property of this delivery path.

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
