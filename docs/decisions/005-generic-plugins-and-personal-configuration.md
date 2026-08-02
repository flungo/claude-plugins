# ADR-005: Generalisable guidance and applied configuration ship as separate plugins

- **Date:** 2026-08-02
- **Status:** Accepted

## Context

`claude-code-web` began as one plugin covering everything about working in Claude Code Web, and its content came from two different places.

Most of it is **true for anyone** using the web environment — the egress proxy and its CA bundle, GitHub reached through the MCP rather than `gh`, the ephemeral container, repo scoping and `add_repo`, project config in a multi-repo session, delegating unrunnable steps to CI.
A smaller part is **true only of Fabrizio's environment** — which hosts he added to its network allowlist, which environment variables it sets, whether it has a setup script.
The two had begun to interleave: the Terraform section asserted that `registry.terraform.io` "is allow-listed", which is a fact about his allowlist stated as if it were a platform guarantee.

That interleaving costs in both directions.
A reader in a different environment is told something reachable that isn't, and stops probing.
A session in *his* environment, meanwhile, still has to rediscover what is configured, because the settings form isn't fully described anywhere the agent can read — and when he changes it, there is no obvious home for the change, so it decays into tribal knowledge.
The environment's own settings are also only editable by him, so an agent's role is always to *propose*, never to apply — a distinction the merged text needs to make plainly.

The marketplace's existing split ([ADR-001](001-marketplace-structure.md)) is by **enablement boundary**, and by that test both halves are the same: user scope, always on.
So the enablement rule alone does not separate them.

## Decision

Split them anyway, on a second axis: **a plugin's content is either generalisable or owner-specific, never both.**

- `claude-code-web` is written to hold for **any** Claude Code Web user in
  **any** environment. It describes the allowlist as user-controlled and
  extensible without claiming what any particular one contains, and points at
  the system prompt or a companion skill for those specifics.
- `personal-cloud-environment` records **Fabrizio's applied environment** — its
  name, extra allowed domains and why each is there, environment variable names
  and their purpose, and its (absent) setup script — and declares
  `claude-code-web` as a dependency, so installing it brings the generic
  guidance with it.
- The owner-specific plugin also carries the **round-trip rule**: an agent that
  wants the environment changed opens a PR against `flungo/claude-plugins`
  proposing the entry, and Fabrizio applies the change as he merges; when he
  says he has changed the environment, persisting it back into that skill is due
  in the same session.

Variable values are recorded as an **expectation**, not as a source of truth: a session can read the live value for itself, so what the record adds is what the value *should* be, making a divergence visible instead of silent.
**Secret values are never recorded** — this repo is public, and they belong solely in the environment's settings form.

## Consequences

### Positive

- `claude-code-web` becomes shareable — usable by, or upstreamable to, someone
  who is not Fabrizio, without carrying his hosts and credentials' names.
- A session gets a straight answer about what is configured before it starts
  probing or working around a limit, and knows a proposal isn't live until the
  PR is merged.
- Environment changes have a definite home, so the record and the live
  environment stay in step instead of drifting.

### Negative — trade-offs

- Two plugins to keep aligned: a finding has to be routed to the right one, and
  a rule about *where* things go is another rule to follow. Both skills state
  the routing to make the wrong choice self-correcting.
- The record is only as good as the reporting. Nothing verifies it against the
  live environment, so it can drift silently — hence the dated
  "recorded" marker and the round-trip rule.
- Generalising the text lost some usefully concrete phrasing (Terraform's
  registry host is now conditional rather than stated), which reads as weaker
  guidance to anyone who doesn't also have the companion plugin installed.
