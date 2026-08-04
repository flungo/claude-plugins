# ADR-006: Plugin delivery differs per surface — a cloud-environment setup script carries user-scope plugins

- **Date:** 2026-08-01
- **Status:** Accepted

## Context

[ADR-001](001-marketplace-structure.md) rests on a dual-surface premise: one repo of plugins usable from both Claude Code and claude.ai, kept in sync by pulling from this repo rather than by re-uploading files by hand.
The local Claude Code half works.
The other half was assumed to be a single mechanism — add this repo as a marketplace in the claude.ai UI — and the README documented that flow as though it were proven.
It is not: the flow crashes, and issue [#21](https://github.com/flungo/claude-plugins/issues/21) was opened to establish what actually works per surface.

A Claude Code Web session was used to probe the behaviour directly, on 2026-08-01 with Claude Code v2.1.220.
Five things were established, and the load behaviours were later confirmed once the delivery mechanism was in place.

**Cloud sessions start with no plugins at all.**
At session start `claude plugin marketplace list` reports no marketplaces and `claude plugin list` reports none installed, with `SKIP_PLUGIN_MARKETPLACE=true` set in the session environment.
This repo's own `.claude/settings.json` declaration of `extraKnownMarketplaces` and three `enabledPlugins` had no effect, and those plugins' skills were absent from the session.
That contradicts the [cloud environments reference](https://code.claude.com/docs/en/cloud-environments), whose "What carries over from your setup" table claims plugins declared in a repo's `.claude/settings.json` are installed at session start.

**Installing inside the container works.**
`claude plugin marketplace add flungo/claude-plugins` followed by `claude plugin install <name>@flungo-plugins --scope user` succeeds, and all five user-scope plugins then load from any working directory, not only from a repo that declares them.

**Project-scope plugins load one launch too late.**
Once the marketplace is known, a repo's declared plugins are installed during a launch but only *load* from the following launch.
A cloud session gets exactly one launch, so a repo-adopted plugin never loads in one.
This is a distinct failure from the multi-repo caveat already recorded in the `claude-code-web` plugin, and it applies to single-repo sessions too.
`SKIP_PLUGIN_MARKETPLACE=true` was the obvious suspect, but it cannot be turned off: setting it empty in the environment's variables leaves it reading `true` in the session, while a canary variable added alongside arrives intact — so the platform sets it after copying yours, and no amount of configuration reaches it.
The behaviour is therefore a property of cloud sessions rather than something to work around.

**Both load behaviours were then confirmed end to end** in an independent session started against a cloud environment carrying the setup script, on 2026-08-01.
All five user-scope plugins loaded, namespaced as `<plugin>:<skill>`, from the snapshot alone.
`docs-standards` and `markdown-standards` — enabled by this repo's own `.claude/settings.json` — were reported by `claude plugin list` as installed, project scope, **enabled**, while their skills were absent from that session entirely.
`SKIP_PLUGIN_MARKETPLACE=true` was still set, which establishes that the flag does not suppress plugin *loading*: plugins already on disk when Claude Code launches are picked up regardless.
The same session showed the `code-review-workflow` account skill loaded alongside the `contributor-workflow` plugin, which is the duplication [#25](https://github.com/flungo/claude-plugins/issues/25) has to sequence around.

**claude.ai account Skills already reach both surfaces.**
Skills authored on the account are synced into the session's `~/.claude/skills/` and load in every cloud session as well as in chat.
They are the only artefact that spans both surfaces today.
There is no public API for them — programmatic management is an open feature request ([anthropics/claude-code#39929](https://github.com/anthropics/claude-code/issues/39929)) — so keeping them current means re-uploading by hand, which is the exact loop ADR-001 exists to avoid.

**Plugins installed on claude.ai do not reach cloud sessions.**
Skills and plugins are independent transports, and only the first crosses.
Tested directly once the marketplace was usable: with two plugins installed from the account marketplace and the setup script removed, a fresh session on an unrelated repo had **no** marketplaces, **no** plugins, and no `~/.claude/plugins/` directory at all, while the account's own Skills arrived normally in `~/.claude/skills/`.
The control is what makes this conclusive — the removed script used to install *five* plugins, so a reused snapshot would have shown five and a genuine propagation two; it showed zero, and every file in `~/.claude` was stamped seconds after boot.
This matches the [cloud environments reference](https://code.claude.com/docs/en/cloud-environments), whose "What carries over from your setup" table allows account skills and excludes user-scope plugins.
The setup script is therefore load-bearing rather than a convenience: without it a cloud session has none of these conventions.

**The claude.ai failure is a client-side crash, not a refusal.**
A HAR capture of the Add-marketplace attempt (2026-08-01) shows `POST /marketplaces/create-account-marketplace` returning **200** with `sync_status: "success"`, `already_connected: true`, and `last_synced_sha` tracking this repo's `main`.
The server accepts the marketplace and syncs it; `auto_sync_on_push` is on and working.
What fails is the browser: React error #185, "Maximum update depth exceeded" — an infinite render loop — caught by a fatal error boundary, with the in-flight plugin-list requests dying as `net::ERR_ABORTED` (all their time in `blocked`, zero `wait`, so cancelled client-side before reaching the network).
Further captures narrow it to the account's own marketplace records, not to this repo.
The account holds **two records for this repository**, created 88 ms apart in a double-submit that was never de-duplicated, and — critically — carrying an **identical `name`**, `claude-plugins`, while differing by `id`.
Instrumenting `fetch` in the page shows the true order: the tab issues exactly one `account-list-plugins` call, React error #185 fires roughly 120 ms later, the error boundary follows ~26 ms after that, and only then does the request abort with `AbortError: signal is aborted without reason`.
The request never receives a response at all.
A network panel reports that as a 503, which is why an earlier reading treated it as a server failure; re-issuing the identical request by hand returns **200 twelve times out of twelve**.
The crash causes the failed request, not the other way round.
The behaviour is deterministic — five reproductions out of five, including in a fresh tab — and the app only ever fetches one of the two records, never reaching the second.

Two rows distinct by `id` but identical by `name`, of which only one is ever loaded, is the signature of a list keyed or de-duplicated on `name`: the entries collapse onto one key, the resolved row flips on each render, and each flip schedules another update until the depth guard trips.
That last step is inference from minified code rather than proof, but it fits every observation.
Anthropic's own `knowledge-work-plugins` marketplace answers the equivalent `list-plugins` call with a 200 in the same session, so neither the endpoint family nor the account's plan is the fault.
This disproves the working hypothesis on [#21](https://github.com/flungo/claude-plugins/issues/21) that personal accounts may not support marketplaces at all.

An intermediate reading blamed an MCP transport mismatch, because a `405 Method Not Allowed` on a legacy SSE handshake to `/v1/toolbox/shttp/mcp/<id>` sat directly above the React error in one console capture.
A **baseline capture of an ordinary page load, with no crash**, settles it: those same 405s fire every time, one per MCP server, each immediately followed by successful `POST`s to the identical URL.
The client probes the legacy transport, is told the endpoint is `POST`-only, falls back, and works.
It is routine negotiation noise present in the healthy case, so the MCP reading is withdrawn entirely.

**claude.ai rejects a skill whose name contains `claude`.**
The same sync recorded `plugin_upload_skill_upload_name_reserved_words`: *"Skill `skills/claude-code-web`: Skill name in SKILL.md cannot contain the reserved word 'claude'."*
`claude-code-web` was the only plugin here that tripped it, and its skill was renamed in response — after which the marketplace re-synced with `sync_errors` null.
This is a platform constraint on the marketplace itself, and no amount of UI fixing removes it.
It is also demonstrably **not** the cause of the crash: a capture taken once the sync was clean reproduces it unchanged.

**Cloud environments run a setup script.**
It runs as root before Claude Code launches, and the resulting filesystem is snapshotted and reused by later sessions.
One environment serves every cloud surface: the web, `claude --cloud`, the mobile and Desktop apps, routines, and Claude Tag.

So "make the plugins available" is not one problem with one answer.
The cloud-session surfaces and the chat surfaces have different delivery mechanisms, and only one of them currently works.

## Decision

**Deliver user-scope plugins to cloud sessions with a setup script on the cloud environment.**
The script adds this marketplace and installs each user-scope plugin at user scope.
Because one environment serves every cloud surface and the script is repo-independent, this covers every Claude Code Web session in every repo, not only repos that adopt the marketplace.
The script is configuration held outside this repo, so the README carries its text verbatim as the authoritative copy.

**Name one bundle in the script rather than enumerating plugins.**
`personal-cloud-environment` records the environment as applied, and what that environment carries is part of describing it — so it depends on `claude-code-web` and on `personal-defaults`, a dependency-only bundle of the surface-independent set with no skills and no measurable context cost.
Installing that single plugin resolves all seven, so adding a plugin later is a change to this repo rather than an edit to configuration held in the environment where nothing can review or validate it.

**Keep the claude.ai personal-plugin marketplace as the intended chat mechanism.**
It is the only channel that would keep chat in sync by pulling rather than re-uploading, and the [help centre](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) documents it for chat on the web, the Desktop Chat tab, and Cowork with no stated plan gate.
The blocker was a front-end crash on a marketplace the backend had already accepted, so the response was to report it with the captures rather than design around it — filed upstream as [anthropics/claude-code#83139](https://github.com/anthropics/claude-code/issues/83139).

**That blocker is now cleared, and clearing it confirmed the diagnosis.**
Deleting one of the two same-named records resolved both symptoms at once: the Personal tab renders, all nine plugins list, the previously unreachable per-marketplace menu is reachable, and **Add marketplace** opens cleanly.
Nothing server-side changed — both endpoints had been answering 200 throughout — so removing one of two records sharing a `name` was sufficient on its own.
Independent corroboration turned up in the shipped bundle: the auto-sync-enable path resolves its target with `marketplaces.find(m => m.name === name)`, a name-keyed lookup that would misbehave under duplicates in exactly the same way.
That moves the mechanism from inference to a demonstrated instance.

**Chat is now covered, tested end to end.**
With `claude-code-web` and `scaffolding` installed from the account marketplace, a fresh conversation lists both as `scaffolding:scaffolding` and `claude-code-web:cloud-sessions`, invokes them, and — the part that decides whether this is real — **reads their `references/` files**, quoting a heading from `references/sessions.md` on request.
Nearly all the substance in these plugins lives in those references; had they not survived ingestion, chat would have got a signpost pointing at nothing.
It also vindicates the skill rename: without it `claude-code-web`'s skill would still be rejected, and only `scaffolding` would have arrived.
ADR-001's dual-surface premise therefore holds in full for the first time, by three different mechanisms rather than one.

The sync message `9 plugins found, 1 loaded with 1 warning` reads as though only one plugin was ingested, which would have made the marketplace far more broken here than the crash alone suggests.
It doesn't mean that: querying `account-list-plugins` directly returns **all nine**, so the count refers to the one plugin carrying a warning, not to how many loaded.
The wording is misleading rather than the ingestion being broken.

**Do not adopt hand-uploaded account Skills as the standing mechanism.**
Each user-scope plugin here is a single skill with no hooks, commands, or MCP servers, so the mapping is trivial and the stopgap is available if chat stays broken.
Reach for it only as an explicitly dated, explicitly temporary measure.

**Leave repo-adopted plugins at project scope, absent in cloud sessions.**
Promoting them to user scope would make them always-on everywhere and collapse the enablement-scope split that ADR-001 is built on.
Repos that adopt them continue to summarise their rules in their own `CLAUDE.md`, which is part of the clone and therefore always present.

## Consequences

### Positive

- Every cloud session, in every repo, starts with the user-scope set loaded — seven plugins, at a measured cost of roughly 1,250 always-on tokens per session, of which the two bundles contribute nothing.
- No re-upload step, so ADR-001's dual-surface premise survives for the surfaces it now covers.
- The approval-gate misalignment parked on [#21](https://github.com/flungo/claude-plugins/issues/21) becomes testable, because `contributor-workflow` now loads in the sessions where the workflow runs.
- Chat gets a scope of its own rather than an inherited one: because it installs per plugin, it can carry the skills that make sense in a chat window and leave behind the ones that only make sense over a checkout.

### Negative — trade-offs

- The setup script is the one piece of this system not version-controlled here; the README copy can drift from the environment's actual script, and nothing detects that.
- Installed versions are frozen into the environment snapshot, so they can lag this repo by up to the cache lifetime of roughly seven days.
  Editing the setup script forces a rebuild.
- Chat is a third enablement decision to maintain, not a free consequence of the other two: these plugins are written for repo work, so what belongs there has to be chosen deliberately rather than mirrored from user scope.
- A repo's adopted conventions still do not load in cloud sessions, which keeps the pressure on each repo's `CLAUDE.md` to restate them.

**Settled 2026-08-04: the snapshot does carry them, and no added marker was needed.**
`claude plugin install` already records an `installedAt` timestamp and the marketplace `gitCommitSha` per plugin in `/root/.claude/plugins/installed_plugins.json`, and the snapshot preserves both.
A session running on 2026-08-04 reported `installedAt: 2026-08-02T17:54:19Z` for every plugin — two days before that session existed, so a cache hit rather than the run that installed them, which is exactly what the proposed marker was meant to demonstrate.
It also quantifies the lag above: those were the versions current at the snapshot build, and three had fallen behind by then.
The mechanics, and what a session can do about a stale plugin, are recorded in the `cloud-sessions` skill.
