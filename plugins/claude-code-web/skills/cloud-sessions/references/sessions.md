# Sessions — ephemeral containers and repo scoping

A web session is a fresh, isolated, throwaway container scoped to a fixed set of repositories.
Two consequences bite if you forget them: nothing on disk survives, and project config only loads under the right conditions.

## The container is ephemeral

Repositories are cloned fresh when the container starts, and the container is reclaimed after inactivity or when the session ends.
Anything worth keeping must be **committed and pushed** — a local commit that is never pushed is lost with the container.

"After inactivity" includes inactivity *within* a session: resuming an idle session runs it in a **new container**, so a single conversation can span several.
*Observed 2026-08-02: a container reporting 20 seconds of uptime, hours into an ongoing session.*
Nothing outside the repo survives that boundary — background jobs, installed tools, and started daemons are gone — and it is also why an environment change can appear mid-session: it most likely arrives with the next container rather than being pushed into a running one.
Writable disk is a fixed per-session allowance, so a "no space left on device" is the allowance being spent, not a broken machine; delete build artifacts, caches, or stale clones to free space (deletes still succeed while writes fail).

## Shared environments

The *container* is per-session and ephemeral, but the *environment* it runs in — the network allowlist, environment variables and secrets, and any setup script — is defined once and reused, so a session's sibling sessions share it regardless of repo or context.
Anything added to it persists into **every future session** that uses it, not just this one.

> **🤖 Agent** — treat environment changes as global and lasting: only propose adding something (an allowlist entry, an environment variable, a tool) that's appropriate to share across every session using that environment, and confirm with the user before it's added.

## Repo scoping and `add_repo`

The session is scoped to a specific set of repositories, **listed individually** in the system prompt — there is no owner-level wildcard, and an owner is rendered lower-case there however GitHub cases it.

*Last verified 2026-08-02 across four sessions — one repo, one repo from a second owner, two repos under one owner, and two repos under two owners.*

- **Add another repo from an owner the session already has with `add_repo`**, then clone it.
  Re-adding an attached repo reports it as already attached rather than failing.
- **The restriction is at add time, not at session creation.**
  A session may be *created* with repositories from two different owners and reaches both normally; what `add_repo` refuses is introducing an owner the session doesn't already have:

  ```text
  add_repo: cross-tier adds are not supported in v1: requested "<owner>/<repo>" but session
  already has repos from owner(s) [<owner> ...]. Start a new session with the requested repo
  as the initial source, or add a repo from the same owner as the existing sources
  ```

  So the test is **"an owner already in this session"**, not "an owner the GitHub integration is installed in" — an installed owner, visible in `list_repos`, is refused just the same.
- **A cross-tier refusal says nothing about authorisation.**
  The check runs before any access check, so a third-party repo fails with exactly this error rather than an auth error — and a session that already holds repositories, which is every session, therefore can't discover what a genuine no-access failure looks like. Don't report a cross-tier message as "no access".
- **One identity spans the owners.** In a two-owner session, `git` reached both and the GitHub MCP resolved to a single account — it behaves as one credential, not one per owner.
- **When you can't attach a repo you only need to read**, use `WebFetch` against `github.com` / `raw.githubusercontent.com` (see `egress-and-tooling.md`); otherwise the fix is a new session with it as an initial source, which is the user's to make.
- **Treat `list_repos` totals as indicative.** Repeat runs returned different totals and different `has_more` values, and a repository listed there may not appear in the session-creation picker.
- **`/add-dir` is not available in web sessions**, so you can't attach a local directory after start that way.

## Project config in a multi-repo session

A multi-repo session **does** load project-scoped configuration from `.claude/settings.json`, including `enabledPlugins`.

*Verified 2026-08-02 in two sessions started with two repositories each — one with both under a single owner, one spanning two owners.
Both loaded the project plugins of the repository that declared them; the repositories that loaded nothing had no `.claude/settings.json` at all.*

This **contradicts** the older report that such a session loads project config from no repository ([anthropics/claude-code#4938](https://github.com/anthropics/claude-code/issues/4938)), which this plugin previously carried second-hand and unverified.
Either it has been fixed or it was always narrower than described; the issue, not this file, is where to check its status.

Two related behaviours are **still untested** — don't assume either way:

- whether `.mcp.json` loads on the same terms as `.claude/settings.json` (only `enabledPlugins` was observed);
- whether a repository attached mid-session with `add_repo` gets its project config loaded, since the ones attached during that test carried none.

> **🤖 Agent** — when a repo's plugins aren't loading, check that the repo actually declares them before blaming the session's shape. If a fresh session does turn out to be the fix, say so — the starting repositories are the user's choice at creation and can't be changed from inside (`/add-dir` isn't available).

## MCP servers can be unavailable at first

A session can come up with its MCP servers reported as disconnected, and have them connect on a later turn — observed 2026-08-02 on a fresh session whose servers were all missing on the first turn and present when re-prompted, and repeatedly mid-session as servers drop and reconnect between turns.

> **🤖 Agent** — treat a missing MCP server as *not yet connected* rather than absent: retry on a later turn before routing around it, and don't tell the user a capability is unavailable on the strength of one turn.

## A repo's own plugins never load

A repo-adopted plugin — one a repository enables through `enabledPlugins` in its `.claude/settings.json` — **does not load in a web session**, even though the settings themselves are read.
Two mechanisms cause this, and neither can be fixed from inside the session.

**No marketplace is configured at session start** (last verified 2026-08-01, Claude Code v2.1.220).
`claude plugin marketplace list` reports none and `claude plugin list` reports nothing installed, with `SKIP_PLUGIN_MARKETPLACE=true` set in the session environment.
A repo's `extraKnownMarketplaces` declaration is not acted on, so its plugins have no source to install from.
That flag cannot be turned off: setting it empty in the environment's variables leaves it reading `true`, while a canary variable added alongside arrives intact.

**Even with a marketplace configured, project-scope plugins load one launch too late.**
They are installed during one launch of Claude Code but only become available from the *next* one, and a web session gets exactly one launch.
`claude plugin list` will report them installed and **enabled** in a session where their skills were never loaded — check your own available skills instead of trusting it.

Neither mechanism depends on how many repositories the session started with; see the preceding section for what repo count does and doesn't affect.

> **🤖 Agent** — when a repo's adopted conventions matter to the work, read them from the repo's files rather than expecting the plugin to be loaded.

## User-scope plugins arrive through the environment's setup script

Plugins enabled at user scope on the account do **not** reach a web session; only account *Skills* do.
What does reach one is whatever the **cloud environment's setup script** installs, because that runs as root before Claude Code launches — typically `claude plugin marketplace add <owner>/<repo>` followed by `claude plugin install <name>@<marketplace> --scope user`.
Which plugins a given environment installs is a property of that environment, so look to its own record rather than assuming.

Because the environment's filesystem is snapshotted and reused, the versions a session gets can lag their source by up to about a week; editing the setup script forces a rebuild.

> **🤖 Agent** — if an expected user-scope plugin is missing or stale, say that the environment's setup script is where it is fixed, rather than installing it into the container by hand where the fix dies with the session.

## Environment variables and secrets

Set them through the session's **Edit environment** control (the kebab menu `⋮` in the top-right of the session → **Edit environment**), not by `export`-ing in a shell — shell state doesn't persist across turns or the container.
This is where an MCP token, a `TF_VAR_*`, or any other secret the session needs should live.

Only the user can edit that form, so an agent's part is to **propose** the variable and say what it's for, never to assume one exists.
Which variables a given environment already sets is a property of that environment, not of Claude Code Web — read them from the system prompt, or from a companion skill that records them.
