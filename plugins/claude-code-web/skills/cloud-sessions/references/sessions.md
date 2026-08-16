# Sessions — the container lifecycle and repo scoping

A web session runs in an isolated VM scoped to a fixed set of repositories.
Two things about it bite if you forget them: the VM restarts constantly, and project config only loads under the right conditions.

## The VM reboots around every turn; its disk persists

**The VM boots afresh around each turn**, and is reclaimed for good after inactivity or when the session ends.
*Observed 2026-08-04 across two consecutive turns of one session — `uptime -s` reported `06:13:04` and then `06:24:22`, each roughly thirty seconds before that turn's first command ran, with `/proc/uptime` agreeing; and 2026-08-02, a container reporting 20 seconds of uptime hours into a session.*

A reboot destroys **processes, not files**.
The root filesystem is a persistent block device — `/` on `/dev/vda`, ext4 — that carries across it, so a commit, a working tree, an installed package, and a scratchpad file are all still there next turn.
*Verified 2026-08-04: a commit and its `git reflog` written the previous day, and plugin-cache writes made minutes before a reboot, all survived intact.*
What does not survive is anything that was only *running* — background jobs, started daemons, shell state, exported variables — and `/root/.ccr/` is rewritten at each boot when the proxy CA bundle and credentials are re-injected.

Repositories are cloned fresh when the session starts, and **committing and pushing is still what makes work safe**: the disk lasts only as long as the session itself, and reopening an expired one provisions a new VM.
Writable disk is a fixed per-session allowance, so a "no space left on device" is the allowance being spent, not a broken machine; delete build artifacts, caches, or stale clones to free space (deletes still succeed while writes fail).

An environment change reaches a session at a boot rather than being pushed into a running container, which is why one can appear part-way through a conversation.

> **Verify:** the disk was seen to persist across turn-to-turn reboots within one session, not across a true *environment expiry* — the reclamation after which reopening the session provisions a fresh VM.
> Assume the disk is gone at that boundary until someone tests it.

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
  The check runs before any access check, so a third-party repo fails with exactly this error rather than an auth error — and a session that already holds repositories, which is every session, therefore can't discover what a genuine no-access failure looks like.
  Don't report a cross-tier message as "no access".
- **One identity spans the owners.**
  In a two-owner session, `git` reached both and the GitHub MCP resolved to a single account — it behaves as one credential, not one per owner.
- **When you can't attach a repo you only need to read**, use `WebFetch` against `github.com` / `raw.githubusercontent.com` (see `egress-and-tooling.md`); otherwise the fix is a new session with it as an initial source, which is the user's to make.
- **Treat `list_repos` totals as indicative.**
  Repeat runs returned different totals and different `has_more` values, and a repository listed there may not appear in the session-creation picker.
- **`/add-dir` is not available in web sessions**, so you can't attach a local directory after start that way.

## Project config in a multi-repo session

A multi-repo session **does** load project-scoped configuration from `.claude/settings.json`, including `enabledPlugins`.

*Verified 2026-08-02 in two sessions started with two repositories each — one with both under a single owner, one spanning two owners.
Both loaded the project plugins of the repository that declared them; the repositories that loaded nothing had no `.claude/settings.json` at all.*

[anthropics/claude-code#4938](https://github.com/anthropics/claude-code/issues/4938) reports the opposite — a multi-repo session loading project config from no repository at all.
Check the issue for its current status if a session ever behaves that way; the observation above is what the environment did when tested.

Two related behaviours are **still untested** — don't assume either way:

- whether `.mcp.json` loads on the same terms as `.claude/settings.json` (only `enabledPlugins` was observed);
- whether a repository attached mid-session with `add_repo` gets its project config loaded, since the ones attached during that test carried none.

> **🤖 Agent** — when a repo's plugins aren't loading, check that the repo actually declares them before blaming the session's shape.
> If a fresh session does turn out to be the fix, say so — the starting repositories are the user's choice at creation and can't be changed from inside (`/add-dir` isn't available).

## MCP servers can be unavailable at first

A session can come up with its MCP servers reported as disconnected, and have them connect on a later turn — observed 2026-08-02 on a fresh session whose servers were all missing on the first turn and present when re-prompted, and repeatedly mid-session as servers drop and reconnect between turns.

> **🤖 Agent** — treat a missing MCP server as *not yet connected* rather than absent: retry on a later turn before routing around it, and don't tell the user a capability is unavailable on the strength of one turn.

## The system prompt can withhold subagents

A web session's system prompt may carry tool restrictions the local CLI's does not — observed 2026-08-04: *"Do not call the AgentTool unless the user requested it"*, and the same for workflows and deep research.
Whether it appears varies: it comes from the harness, and a session can also be created with an appended system prompt, so read your own rather than assuming either way.

Note what it gates on.
The instruction conditions delegation on the user having asked; it does not forbid subagents outright.
Its target is a fan-out nobody asked for, in an environment where the user cannot watch the tokens being spent.

That leaves the question of what counts as asking, which is not this plugin's to answer — a skill whose documented procedure dispatches subagents is the place that decides how its own steps read against such an instruction, and one may state outright that invoking it is itself the request.

> **🤖 Agent** — before following a procedure step that delegates, check your own system prompt for a restriction like this.
> Where one applies and the skill doesn't say otherwise, do the work in the main loop and say so in your report, rather than dispatching anyway or silently dropping the step.

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

Because the environment's filesystem is snapshotted and reused, the versions a session gets can lag their source — see § Plugin versions lag the marketplace for why, by how much, and what a session can do about it.

> **🤖 Agent** — a plugin that is missing entirely, rather than stale, is fixed by adding it to the environment's setup script, which only the user can edit.
> Ask for that change; installing it by hand reaches only the session you are in.

## Plugin versions lag the marketplace

The lag is a consequence of [environment caching](https://code.claude.com/docs/en/cloud-environments#environment-caching), which Anthropic documents: the setup script runs the *first* time a session starts in an environment, the filesystem is then snapshotted, and later sessions start from that snapshot and **skip the setup script entirely**.
The script runs again only when the setup script or the allowed-hosts list changes, or when the cache expires after roughly seven days.
Resuming an existing session never re-runs it.

So the plugin versions in a session are whatever the marketplace held **when the snapshot was built**, which can be a week old — and every session in that environment gets the same stale set, not just long-running ones.

**Read the snapshot's age rather than guessing it.**
`claude plugin install` records the provenance of each install in `/root/.claude/plugins/installed_plugins.json`, and the snapshot preserves it:

```json
"installedAt": "2026-08-02T17:54:19.097Z",
"gitCommitSha": "7f27c55738fb5c39705ee15e9f6dec3256b3f9a9"
```

A single `installedAt` shared by every plugin, to within a second or two, is the setup script's run — the snapshot build time.
`gitCommitSha` pins the exact marketplace commit it was built from, which beats a timestamp when you want to know precisely what you have.
*Observed 2026-08-04: a session reporting `2026-08-02T17:54:19Z` for all ten plugins, three of them behind the marketplace by then.*

## A session can update its own plugins for the next turn

The disk persists across turn boundaries but the Claude Code process does not, so an update applied now takes effect **on the next turn**, when the boot starts a new process that reads the updated config.
Update as soon as you find a plugin stale; the session gets the new version for every turn after this one.

```bash
claude plugin marketplace update <marketplace>              # refresh the manifest first
claude plugin update <plugin>@<marketplace>                 # user scope (the default)
claude plugin update <plugin>@<marketplace> --scope project # project-scoped plugins
```

- **`--scope` must match how the plugin was installed.**
  A project-scoped plugin fails at the default scope with `Plugin "<name>" is not installed at scope user`; check `claude plugin list`, which prints each plugin's scope.
- **Ignore "Restart to apply changes."**
  A web session has no way to restart Claude Code, and does not need one — the next turn's boot does it.
- **Compare against the marketplace to find what is stale**: the `version` fields in `installed_plugins.json` against the marketplace's own manifest, which you can read from the repo if it is attached or over `raw.githubusercontent.com` if it isn't.

**Confirm which version the running process actually holds** — the cache keeps old versions alongside new ones, so its contents prove nothing on their own.
Each version directory under `~/.claude/plugins/cache/<marketplace>/<plugin>/` carries an `.in_use` directory naming the PIDs holding it, and a superseded version gets an `.orphaned_at` file:

```text
session-workflow/0.1.0/   in_use=[]           ORPHANED
session-workflow/0.2.0/   in_use=[506 6908]
```

Match those PIDs against the live `claude` process (`ps -eo pid,lstart,args | grep claude`) and you know what is loaded, without invoking a skill to find out.
*Verified 2026-08-04: `claude plugin update` wrote `.orphaned_at` on the superseded versions immediately, and after the next turn's boot the new `claude` PID held `.in_use` on the new ones.*

> **🤖 Agent** — an in-session update reaches nothing beyond this session's remaining turns, and the snapshot it came from refreshes only when the environment's setup script or allowed-hosts list changes, or when the cache expires.
> Those are the user's to trigger, so report the update you made and leave the snapshot as a separate request.

## Prefer the setup script over per-session installs

Work done in the setup script is captured in the snapshot, so it costs nothing on later sessions — a toolchain installed or a container image pulled there is simply on disk when the session starts.
A `SessionStart` hook, by contrast, runs on every session and every resume, so the same install is paid for repeatedly.

So anything slow and cacheable belongs in the setup script, and hooks are for what genuinely must run each time.
The script must exit zero or the session fails to start, and should finish within roughly five minutes for the cache to build.

> **🤖 Agent** — propose setup-script content to the user with what it would save; the environment settings form is theirs to edit, so an install you run in the session is a stopgap for this session, never the fix.
> How they want that proposed is environment-specific — a companion skill recording the environment you are in may set out the route.

## Environment variables and secrets

Set them through the session's **Edit environment** control (the kebab menu `⋮` in the top-right of the session → **Edit environment**), not by `export`-ing in a shell — shell state doesn't persist across turns or the container.
This is where an MCP token, a `TF_VAR_*`, or any other secret the session needs should live.

Only the user can edit that form, so an agent's part is to **propose** the variable and say what it's for, never to assume one exists.
Which variables a given environment already sets is a property of that environment, not of Claude Code Web — read them from the system prompt, or from a companion skill that records them.
