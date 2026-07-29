---
name: claude-code-web
description: Fabrizio's working preferences and hard constraints for Claude Code Web (the browser and cloud environment at claude.ai/code, as opposed to the local CLI). Consult this whenever a session runs in that environment and something behaves differently from local — outbound network going through the egress proxy, GitHub access, installing tools, adding or scoping repositories, setting environment variables or secrets, or a command that can't run in the sandbox and should be delegated to CI. Personal, always-on preferences; they complement a repo's own CLAUDE.md rather than overriding it.
---

# Claude Code Web

How Fabrizio wants a session to behave when it runs in **Claude Code Web** — the managed, cloud-hosted environment at `claude.ai/code`, rather than the local CLI.
The sandbox is real: outbound traffic is proxied, some tools and hosts are blocked, the container is ephemeral, and the session is scoped to specific repositories.
Work *with* those constraints rather than rediscovering them each time.

Apply these whenever you're in a web session, whether or not a named command was invoked.
They are personal defaults that **complement repo/context rules, never supersede them** — check the repo's own `CLAUDE.md`/`CONTRIBUTING.md` first, and where it differs, follow the repo.

## These constraints change — verify, and defer to the environment's own description

The sandbox's limits are set by Anthropic and by the **network policy chosen for the environment**, so they vary between environments and change over time.
Treat everything here as *last-known behaviour, not a permanent guarantee*: before spending effort working around a constraint, probe whether it still holds (the references give reproducers), and don't assume a documented block is universal — a different environment's policy may not have it.

The harness's own description of the environment in the **system prompt** (the "remote execution environment" / network-policy section it gives the session) is authoritative and **supersedes this plugin**.
Where the two conflict, follow the system prompt and open a PR against `flungo/claude-plugins` to correct the plugin.

Claims that were checked carry a **last-verified date**; an undated or stale claim is a hint to re-probe, not a fact to rely on.

## Record and contribute what you learn

When you hit a fresh, reusable gotcha about the web environment, record it where the next session will find it:

- **Specific to the current repo** → that repo's `CLAUDE.md` (or its relevant plan).
- **A general Claude Code Web behaviour**, independent of the repo → back into *this* plugin.
  You may ask the user to `add_repo flungo/claude-plugins` so you can open a PR updating the relevant reference, with a reproducer and a last-verified date.

## The reference files

- **`references/egress-and-tooling.md`** — the egress proxy and its CA bundle, which registries and GitHub hosts work, why GitHub goes through the MCP rather than `gh`, how to run Terraform in a session, and why `sleep` is blocked.
  Read it before installing a tool, fetching a URL, hitting the GitHub API, or running Terraform.
- **`references/sessions.md`** — the session shape: ephemeral container, repo scoping and `add_repo`, the multi-repo config-loading caveat, and setting environment variables or secrets.
  Read it before adding a repo, relying on project config, or setting an env var.
- **`references/ci-iteration.md`** — the pattern for anything the sandbox can't run: push the branch and iterate against CI, provision tokens first, and probe whether a restriction has lifted.
  Read it when a build, container, or toolchain won't run locally.
