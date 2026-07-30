# Plan: flungo-plugins marketplace build-out

**Status:** Complete — structure decided (ADR-001, ADR-002); the split (#1), the repo bootstrap + `git-conventions` dogfood (#2), `docs-standards` (#4, step 4), `claude-code-web` (#5, step 5), `upstream-research` (#6, step 6), `terraform-standards` (#7, step 7), `terraform-provider-standards` (#8, step 8), `scaffolding` (#10, step 9), `markdown-standards` (#14, step 11), and this repo's own CI (#12, step 10) have merged.
Every step is done; retirement (deleting this plan) follows in a second PR once every load-bearing fact is confirmed persisted.

Turns the single seed plugin into the full personal marketplace: a set of always-on personal plugins plus a growing set of repo-adopted standards plugins, with this repo dogfooding the conventions it encodes.
The structure and its rationale live in the ADRs; this plan tracks the sequencing and is **retired (deleted) when complete** — do not reference it from permanent docs.

## Target structure

Derived from a read-only mining of the sibling repos (`terraform-github`, `terraform-grafana-cloud`, `authentik.flungo.net`, `stalwart.flungo.net`, `terraform-provider-stalwart`) — what recurs across ≥2 repos becomes a shared plugin; what's unique stays in that repo's `CLAUDE.md`.

**Personal — user scope** (installed + enabled in the claude.ai account, always on):

| Plugin | Holds |
|---|---|
| `git-conventions` | Standing git/PR hygiene (branch management, Conventional Commits, linear history, squash-vs-rebase, no fixup commits, force-push policy). Personal (always-on) **and** adopted at project scope in repos Fabrizio owns, so every contributor to them follows it. |
| `contributor-workflow` | Named review/workflow commands (currently `/ready-to-merge`). Depends on `git-conventions`. |
| `claude-code-web` | Working preferences for Claude Code Web — incl. MCP-first-for-GitHub and "no `gh` CLI", the multi-repo caveat, `add_repo`/proxy limits, and the "sandbox can't run X → push and iterate on CI" pattern. |
| `upstream-research` | How to research and verify third-party/upstream components — read their site/repo, cite provenance, distrust training data and stale/archived/secondary sources. |
| `scaffolding` | Setting up a new repo or adopting a toolchain — points Claude to the reusable workflows in `flungo/github-workflows` and the right standards plugins. Distinguishes repos Fabrizio owns (his namespace, not a fork) from third-party repos: in owned repos it encourages repo-level adoption of `git-conventions` and the relevant project-scope standards plugins. |

**Repo-adopted — project scope** (declared per repo in `.claude/settings.json`):

| Plugin | Holds |
|---|---|
| `docs-standards` | Diátaxis docs model, Nygard ADRs, plan lifecycle, index maintenance, staleness discipline, the `> **🤖 Agent**` and `> **Verify:**` callouts, and the stop-hook doc checklist. (Semantic line breaks moved to `markdown-standards` — ADR-004; an `incidents/` doc kind and the "Hard constraints" device are deferred — see dispositions.) |
| `terraform-standards` | HCL consumer conventions — one-`.tf`-per-concern, sensitive-as-variables + placeholders, `import {}` adoption, provider pinning + committed lock, resource-name-mirrors-object, durations-as-arithmetic (when writing raw seconds). |
| `markdown-standards` | Markdown authoring conventions paired with the `github-workflows` Markdown CI — the `## Cross-references` rules, semantic line breaks (`MD013`), unique cross-referenced headings (`MD024`), adjacent blockquotes (`MD028`), fix-the-target remediation, and the `/adopt-markdown-ci` onboarding command. Extracted from the `github-workflows` docs per [its issue #3](https://github.com/flungo/github-workflows/issues/3). Project scope only — enabling it is the opt-in. Added after the original mining — see ADR-004. |
| `terraform-provider-standards` | Go provider conventions **common to any provider** — Plugin Framework, `tfplugindocs` generated docs, MPL-2.0 + copyright headers, and adopting the shared `flungo/github-workflows` provider CI (golangci-lint v2, GoReleaser dual-registry release). Single-provider specifics (backend, client, auth model, container acceptance harness, coverage ratchet) stay in that provider's own `CLAUDE.md` until a second provider proves them reusable. |

**Not in the marketplace:** reusable CI (markdownlint, lychee, `terraform` plan/apply) lives in `flungo/github-workflows` and is referenced by `scaffolding` (ADR-001).

## Single-example dispositions (confirmed with Fabrizio)

Conventions that appeared in only one repo but were judged worth extracting, and where they land:

- `> **🤖 Agent**` callout → `docs-standards`. The distinct `> **Verify:**`
  callout (flagging uncertainty that can't be checked without live access) is
  also desirable and belongs alongside it, not as a replacement.
- `incidents/` doc kind → **open / deferred**: decide after researching
  incident-writeup best practices. The numbered "Hard constraints" device is
  undecided and decoupled from this — not bundled into the `incidents/`
  decision.
- Semantic line breaks (one sentence per line) → `docs-standards`.
  *Superseded by ADR-004: they ship in `markdown-standards`, which `docs-standards` depends on.*
- markdownlint override philosophy (minimum justified overrides; re-enable a
  rule by fixing findings one rule per commit) → `docs-standards` guidance; the
  config itself ships with the reusable workflow.
- MPL-2.0 + copyright headers → `terraform-provider-standards` (provider-specific).
- Source-verification rigour → its own `upstream-research` plugin.

## Steps

- [x] **1. Split the seed plugin** — `code-review-workflow` → `git-conventions` +
  `contributor-workflow` (dependency), update `marketplace.json` + `README`.
  *Merged: #1.*
- [x] **2. Bootstrap repo conventions** — `CLAUDE.md`, `docs/` structure,
  ADR-001/002, this plan. *Merged: #2.*
- [x] **3. Dogfood `git-conventions`** — adopt it in this repo via
  `.claude/settings.json` (project-scope `enabledPlugins` +
  `extraKnownMarketplaces` pointing at this repo), mirroring the
  `terraform-grafana-cloud` pattern. *Merged: #2.*
- [x] **4. `docs-standards` plugin** — the most-reused new authoring; encodes
  the Nygard ADR template and the docs model this repo now demonstrates. Adopt
  it in this repo once it lands. *Merged: #4.*
- [x] **5. `claude-code-web` plugin** — seed from the web-quirk corpus in the
  sibling `CLAUDE.md`s; enable at user scope. Fold in the Web-egress details
  from the Stalwart adoption notes (see Notes). *Merged: #5.*
- [x] **6. `upstream-research` plugin.** *Merged: #6.*
- [x] **7. `terraform-standards` plugin.** *Merged: #7.*
- [x] **8. `terraform-provider-standards` plugin.** *Merged: #8.*
- [x] **9. `scaffolding` plugin** — references `flungo/github-workflows`. Bake
  the Stalwart markdown-validation adoption pitfalls (see Notes) into the
  reusable workflow / scaffolding guidance so adopters don't re-hit them.
  *Merged: #10.* The pitfalls already live in `github-workflows`'
  `adopting-markdown-workflows.md`, which the plugin points at; owned-vs-third-party
  formalised in ADR-003.
- [x] **10. Repo CI** — adopt the markdownlint + lychee reusable workflows from
  `github-workflows`, plus a `claude plugin validate` check on PRs so the
  marketplace can't break; this is itself dogfooding steps 4 and 9. Follow the
  Stalwart markdown-validation adoption notes (see Notes) — or, now that step 11
  exists, run `/adopt-markdown-ci`. *Merged: #12.* Worked through by hand from
  the `github-workflows` runbook before step 11 landed; the outcome matches
  `/adopt-markdown-ci`'s checklist, with the conventions left to
  `markdown-standards` rather than restated in `CLAUDE.md`.
- [x] **11. `markdown-standards` plugin** — extract the Claude-facing
  Markdown-validation conventions inlined in the `github-workflows` docs
  ([its issue #3](https://github.com/flungo/github-workflows/issues/3)) into a
  repo-adopted plugin (cross-references, lint-paired prose conventions,
  `/adopt-markdown-ci`), per ADR-004; the paired
  [github-workflows PR 19](https://github.com/flungo/github-workflows/pull/19)
  makes its docs reference the plugin instead of inlining. Dogfooded here via
  `.claude/settings.json`; `docs-standards` depends on it. *Merged: #14.*

> **🤖 Agent** — author one plugin per PR (draft), validate with
> `claude plugin validate` and a test-install before pushing, and confirm each
> new plugin's disposition against the table above rather than inventing scope.

## Notes

- **Owned vs third-party repos:** in a repo Fabrizio owns (his namespace, not a
  fork), `git-conventions` and the relevant project-scope standards plugins are
  adopted at repo level so every contributor follows them; a third-party repo
  gets only his personal user-scope plugins. The `scaffolding` plugin encodes
  this distinction — formalized in [ADR-003](../decisions/003-owned-vs-third-party-adoption.md) (#9).
- **External input — Stalwart markdown-validation adoption notes**
  ([flungo/stalwart.flungo.net#53](https://github.com/flungo/stalwart.flungo.net/pull/53),
  recorded in that repo's `docs/plans/markdown-validation.md`): pitfalls from
  adopting markdownlint + lychee CI from a Claude Code Web session. Informs
  step 10 (pin markdownlint-cli2 `0.17.2` and preserve the pin in `CLAUDE.md`;
  `cargo install lychee`; point npm/pip/cargo at the proxy CA bundle; provision
  `LYCHEE_GITHUB_TOKEN` before curating `.lycheeignore`; verify Phase 3
  pre-merge via `workflow_dispatch`), step 9 (the `github-workflows` reusable
  workflow should bake these in so adopters don't re-hit them), and step 5 (its
  Web-egress details enrich the `claude-code-web` corpus). Contribute any new
  gaps back to that plan, per its adoption-note norm.
- **claude.ai UI:** the "Add marketplace" flow threw a transient service
  disruption during initial setup; the CLI install path is verified working, so
  any recurrence is claude.ai-side, not a repo defect.
