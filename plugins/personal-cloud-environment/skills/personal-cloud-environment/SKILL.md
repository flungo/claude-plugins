---
name: personal-cloud-environment
description: The manually-applied configuration of Fabrizio's own Claude Code Web environment — its name, network allowlist, environment variables, and setup script — layered on top of the platform defaults. Consult this in a web session to know what is actually reachable or set before probing or working around it, whenever an allowlist or environment-variable change is proposed, and whenever Fabrizio says he has changed the environment, so the change is persisted back here. Companion to the environment-agnostic cloud-sessions skill.
---

# The personal Claude Code Web environment

`cloud-sessions` (in the `claude-code-web` plugin) describes how Claude Code Web behaves for **anyone**.
This skill records what **Fabrizio has manually applied** on top of those defaults for his own environment, so a session can tell his choices apart from the platform's.

Two things follow from that split:

- **Nothing here is a platform guarantee.**
  Every entry below exists because he added it, and it can be changed or removed at any time.
- **The harness's system prompt still wins.**
  If it describes the environment differently, follow it and correct this skill (see § Keeping this record in step).

*Recorded 2026-08-02, from Fabrizio's description of the environment's settings form; the variable values were confirmed the same day against a live session.
A variable added mid-session was visible to a later turn of that session, but that says nothing about propagation into a running container — the container is replaced across idle periods (see `sessions.md` in `cloud-sessions`), so the value most likely arrived at a fresh start.*

## Environment "Cloud"

| Setting | Value |
| --- | --- |
| Name | Cloud |
| Network access | Custom |
| Default allowed domains included | Yes |
| Extra allowed domains | Listed below |
| Setup script | Installs the user-scope plugins — see below |

"Custom" network access with the [default allowed domains](https://code.claude.com/docs/en/claude-code-on-the-web#default-allowed-domains) still included means the common package-manager hosts work as documented, **plus** the extras below — it is an extension of the default policy, not a replacement for it.
Background on the policy and on what each level permits is in Anthropic's [network access documentation](https://code.claude.com/docs/en/claude-code-on-the-web#network-access) and its [access levels](https://code.claude.com/docs/en/claude-code-on-the-web#access-levels) section.

### Setup script

The script installs Fabrizio's always-on plugins into every cloud session, because plugins enabled at user scope on the account do not reach one — the environment's setup script is the only channel that does.
It is a single install: `personal-cloud-environment` carries `claude-code-web` and the `personal-defaults` bundle through its dependencies, so adding a plugin to the marketplace needs no change here.

The authoritative copy of the script lives in [the `flungo/claude-plugins` README](https://github.com/flungo/claude-plugins#install-in-claude-code-web-and-other-cloud-sessions); this file records only that the environment runs it.
Two consequences worth knowing in a session: the installed versions come from a filesystem snapshot and can lag the repo by up to about a week, and a plugin newly added to the marketplace does not arrive until the script is edited or the cache expires.

> **🤖 Agent** — if a user-scope plugin is missing or stale, tell Fabrizio to edit the setup script, which forces the snapshot to rebuild; installing into the container by hand fixes only the session you are in.

### Extra allowed domains

Kept sorted alphabetically, so an addition has one obvious place to go.
The domains are as applied; the *why* column is inferred from each host's role rather than stated, so treat a reason as a best reading and correct it if it misses the actual intent.

| Domain | Why it is there |
| --- | --- |
| `*.githubusercontent.com` | Public file reads over `raw.githubusercontent.com` and the other `githubusercontent` hosts, without needing repo scope. |
| `flungo.grafana.net` | The Grafana Cloud stack the Grafana MCP server talks to. |
| `oncall-prod-us-central-0.grafana.net` | The OnCall API for that same stack. |
| `pkg-containers.githubusercontent.com` | Blob storage behind GitHub's container registry, so a `ghcr.io` pull can fetch layers. |
| `production.cloudfront.docker.com` | The CDN Docker Hub serves image layers from, so `docker pull` completes once the daemon is up. |
| `registry.terraform.io` | Provider resolution during `terraform init`; added 2026-07-29 at a session's request, and what makes the Terraform workflow in `cloud-sessions` viable here. |

> **Verify:** `pkg-containers.githubusercontent.com` is already covered by the `*.githubusercontent.com` wildcard above it, so it is likely redundant.
> Harmless either way — worth removing only if the list is being tidied, and only after confirming the wildcard does match subdomains in this policy.

### Environment variables

A session can read these values for itself, so the table isn't how it *obtains* one — it is what the value is **expected** to be, which is the part reading can't tell you.
That makes the expectation worth writing down for a non-secret value, because a divergence between it and the live environment is a real signal.
A **secret** value is never worth writing down, in this table or anywhere else in this public repo.

| Variable | Expected value | Why it is set |
| --- | --- | --- |
| `CARGO_HTTP_CAINFO` | `/root/.ccr/ca-bundle.crt` | Points `cargo` at the proxy's CA bundle so crates.io fetches verify. |
| `GRAFANA_MCP_API_KEY` | Never recorded — secret | Credential for the Grafana MCP server. Lives solely in the settings form. |
| `NODE_EXTRA_CA_CERTS` | `/root/.ccr/ca-bundle.crt` | Same CA bundle for Node and npm. |
| `PIP_CERT` | `/root/.ccr/ca-bundle.crt` | Same CA bundle for `pip`, which `cloud-sessions` recommends setting. Added 2026-08-02, in review of the change that created this skill. |

> **🤖 Agent** — if a value differs from the expectation above, use the live value and say so, then offer a PR reconciling the two.
> Silently adapting is what lets the record rot.

## Repository scope

Not part of the environment form, and **not fixed to `flungo/*`**.
Fabrizio installs the Claude GitHub integration **per organisation**, so a session can be started with repositories from any of them, in any combination — including two owners at once.

*Verified 2026-08-02 across four sessions; the mechanics are in `sessions.md` in `cloud-sessions`, and only what is specific to him is repeated here.*

- **`flungo` is a user account, not the boundary.**
  The integration is also installed in the organisations `flungo-ansible`, `flungo-avr`, `flungo-docker`, `flungo-maven`, `flungo-soton`, `flungo-theaigames`, `flungo-vibe`, `bashrc-io`, `plugcraft`, `SystemDocker` and `WorldCretornica` — as seen in `list_repos` that day, and not necessarily exhaustive or current.
- **One credential covers them all.**
  Every session resolved to the single account `flungo`, and reached both owners' repositories in a session started with two.
- **Mixing owners is a decision at session creation.**
  `add_repo` will not introduce an owner the session lacks, so if work spans two of these, they have to be picked up front — the fix afterwards is a new session, which is Fabrizio's to start.

> **Verify:** `WorldCretornica` appeared in `list_repos` but was not spotted in the session-creation picker, so it may be listable without being startable.
> Worth checking before planning work that depends on starting a session there.

## Keeping this record in step

This record is only useful while it matches the live environment, and it can drift in either direction.
Both directions end in a PR against [`flungo/claude-plugins`](https://github.com/flungo/claude-plugins) — use `add_repo` to bring that repo into the session first.

**When a session wants the environment changed** — a blocked host worth allow-listing, a variable worth setting, something worth doing in a setup script — don't just work around it and move on:

1. Confirm the benefit is durable and recurring, not a one-off (a one-off belongs in CI, or on `raw.githubusercontent.com`).
2. Open a PR adding the entry to the table above, saying what it unblocks — the open PR *is* the proposal.
3. Fabrizio applies the change to the environment as he merges that PR, so the merged file and the live environment agree.
   Until then the change isn't live — keep working around the limit for the rest of the session, and don't report it as available.

**When Fabrizio says he has changed the environment** — an added domain, a new variable, a setup script — treat that as a documentation task due in the same session, not something to remember later.
Open the PR that persists it here, so the next session inherits it instead of rediscovering it.

> **🤖 Agent** — never treat an entry as live because you wrote it.
> This file describes applied configuration, and a proposal only becomes that once the PR carrying it is merged and Fabrizio has applied it.

Some findings belong in the *other* plugin instead: if what you learned is true of Claude Code Web for everyone rather than of this environment's settings, put it in `cloud-sessions` and leave this record alone.
