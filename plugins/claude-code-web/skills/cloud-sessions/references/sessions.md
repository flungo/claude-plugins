# Sessions — ephemeral containers and repo scoping

A web session is a fresh, isolated, throwaway container scoped to a fixed set of repositories.
Two consequences bite if you forget them: nothing on disk survives, and project config only loads under the right conditions.

## The container is ephemeral

Repositories are cloned fresh when the container starts, and the container is reclaimed after inactivity or when the session ends.
Anything worth keeping must be **committed and pushed** — a local commit that is never pushed is lost with the container.
Writable disk is a fixed per-session allowance, so a "no space left on device" is the allowance being spent, not a broken machine; delete build artifacts, caches, or stale clones to free space (deletes still succeed while writes fail).

## One shared environment

The *container* is per-session and ephemeral, but the *environment* it runs in — the network allowlist, environment variables and secrets, and any setup — is a **single environment that Fabrizio shares across all his sessions**, regardless of repo or context.
So anything added to it persists into **every future session**, not just this one.

> **🤖 Agent** — treat environment changes as global and lasting: only propose adding something (an allowlist entry, an environment variable, a tool) that's appropriate to share across all of Fabrizio's sessions, and confirm with him before it's added.

## Repo scoping and `add_repo`

The session is scoped to specific repositories (for Fabrizio, `flungo/*`).

- **Add another in-scope repo with `add_repo`**, then clone it.
- **`add_repo` cannot add a repo from a different owner** once the session already holds repos from another owner — cross-owner adds are rejected with "cross-tier adds are not supported in v1".
  For an out-of-owner *public* repo you only need to read, use `WebFetch` against `github.com` / `raw.githubusercontent.com` instead (see `egress-and-tooling.md`).
- **`/add-dir` is not available in web sessions**, so you can't attach a local directory after start that way.

## The multi-repo config-loading caveat

When a web session is started with **more than one repository**, project-scoped configuration from `.claude/settings.json` (including `enabledPlugins`) and `.mcp.json` is **not loaded from any repository**.
This is a known limitation ([anthropics/claude-code#4938](https://github.com/anthropics/claude-code/issues/4938)).
*(Sourced from sibling-repo notes; not re-verified here — re-check the issue for current status.)*

Which repositories a session starts with is the **human's choice at session creation** — the agent can't change it mid-session (`/add-dir` isn't available, and `add_repo` doesn't re-trigger project-config loading).

> **🤖 Agent** — you can't fix this from inside the session, so make the user aware of the impact: if a repo's plugins or MCP servers aren't loading, it's likely because the session was started with more than one repo — tell them, and that a fresh session scoped to just that repo would load them.

## Environment variables and secrets

Set them through the session's **Edit environment** control (the kebab menu `⋮` in the top-right of the session → **Edit environment**), not by `export`-ing in a shell — shell state doesn't persist across turns or the container.
This is where an MCP token, a `TF_VAR_*`, or any other secret the session needs should live.
