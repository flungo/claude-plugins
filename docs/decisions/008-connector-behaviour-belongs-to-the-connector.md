# ADR-008: A connector's behaviour belongs to the connector plugin, not to the surface or the workflow that met it

- **Date:** 2026-08-31
- **Status:** Accepted

## Context

[ADR-007](007-connector-carried-conventions.md) created `connector-conventions` and settled its shape.
It did not say what should move *into* it, and facts about connector behaviour had already accumulated elsewhere, filed wherever they were first discovered.

The GitHub MCP was the worked example.
Its read path silently mangles issue and pull request text — tag-shaped tokens deleted, whole bodies truncated after a `<title>` or `<style>` mention — and that had been recorded in `claude-code-web`, because a web session was where it was found.
The same server omits `reviewDecision` from `pull_request_read`, recorded in `contributor-workflow`, because `/ready-to-merge` was the command that needed it.

Both facts are properties of the MCP server.
They hold in the local CLI and in claude.ai chat exactly as they hold in a cloud session.
Filed as they were, each loaded only in the narrow case that discovered it — the mangling rule, whose whole point is *don't rewrite a description because the read looked wrong*, was reachable only in cloud sessions, and silent everywhere else the same trap exists.

Three kinds of fact were being conflated, and only their common mention of "GitHub" made them look alike.

## Decision

**Sort a fact by what it is a property of, not by where it was discovered.**

- **A property of the connector** — what a tool returns, mangles, or omits → the connector's skill in `connector-conventions`.
  It travels with the connector, so it must load wherever the connector is used.
- **A property of the environment** — which tools exist at all, what the network reaches → the surface plugin (`claude-code-web`).
  Tool *choice* is environment business and stays there: in a web session the GitHub MCP is not the preferred option but the only one, since there is no `gh` CLI and `api.github.com` is blocked, and that is a stronger claim than a preference.
- **A property of the platform, reasoned about away from any tool** — how a merge method rewrites commits, why merged commits report as unverified → the domain plugin that owns the subject (`git-conventions`).

A connector skill therefore never tells a session to prefer its connector over another tool; it is consulted once the agent is already using it.
`git-conventions` keeps its GitHub material for the third reason and one more: it is repo-adopted at project scope, so a dependency on a user-scope plugin would violate ADR-003's boundary in every repo that adopts it.

**Where a plugin references another, it declares the dependency** — including where the reference is expected to be satisfied some other way, such as through the `personal-defaults` bundle.
The bundle is a convenience, not a guarantee, and a stated reference with no declared dependency is a dangling one wherever the plugin is installed alone.

**A connector skill carries a convention-discovery half only where the store holds rules that nothing else loads.**
Google Drive needs one because nothing there is read automatically; a repository does not, because its own files already load and the harness understands them.
[ADR-007](007-connector-carried-conventions.md)'s shared reference filenames are therefore a naming convention for the files a connector skill *does* have, not a requirement that every connector have all three.
Nor is the absence worth explaining to an agent in the skill itself: a mechanism invented for one store is not something a reader expects to find in another, so a skill that narrates what it does not have spends attention answering a question nobody asked.

## Consequences

### Positive

- Each fact loads wherever it is true, so the GitHub read-path trap is now reachable in chat and the local CLI, not only in cloud sessions.
- A fact has one home, so a correction lands once and the surrounding plugins keep only their own subject.
- The sorting rule generalises — a second connector's quirks have an obvious destination the first time they are met, rather than being filed wherever they were discovered.

### Negative — trade-offs

- A reader of `claude-code-web` alone no longer sees the GitHub MCP's behaviour inline; they follow a pointer to another plugin.
- Three plugins gain a dependency edge on `connector-conventions`, so the graph is wider even though every one of them already ships together in practice.
- The boundary needs applying by judgement each time.
  "Platform, reasoned about away from the tool" versus "met through the connector" is a real distinction but not always a sharp one — `workflow_dispatch` accepting a ref the workflow is not yet on is GitHub's behaviour, recorded with the connector because that is where an agent meets it.

## Related

- [ADR-007](007-connector-carried-conventions.md) — created the plugin whose boundary this defines.
- [ADR-003](003-owned-vs-third-party-adoption.md) — the user-scope/project-scope split that keeps `git-conventions` from depending on this plugin.
- [ADR-005](005-generic-plugins-and-personal-configuration.md) — the same instinct applied to a different axis, separating generalisable guidance from applied configuration.
