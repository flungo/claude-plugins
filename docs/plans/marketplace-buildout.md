# Plan: flungo-plugins marketplace build-out

**Status:** In progress — structure decided (ADR-001, ADR-002); the split (#1), the repo bootstrap + `git-conventions` dogfood (#2), and `docs-standards` (#4, step 4) have merged; the remaining plugins are authored one PR at a time.

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
| `docs-standards` | Diátaxis docs model, Nygard ADRs, plan lifecycle, index maintenance, staleness discipline, the `> **🤖 Agent**` and `> **Verify:**` callouts, semantic line breaks, and the stop-hook doc checklist. (An `incidents/` doc kind and the "Hard constraints" device are deferred — see dispositions.) |
| `terraform-standards` | HCL consumer conventions — one-`.tf`-per-concern, sensitive-as-variables + placeholders, `import {}` adoption, provider pinning + committed lock, resource-name-mirrors-object, durations-as-arithmetic (when writing raw seconds). |
| `terraform-provider-standards` | Go provider conventions — Plugin Framework, `tfplugindocs` generated docs, GoReleaser dual-registry release, golangci-lint v2, coverage ratchet, container acceptance tests, MPL-2.0 + copyright headers. |

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
- markdownlint override philosophy (minimum justified overrides; re-enable a
  rule by fixing findings one rule per commit) → `docs-standards` guidance; the
  config itself ships with the reusable workflow.
- MPL-2.0 + copyright headers → `terraform-provider-standards` (provider-specific).
- Source-verification rigour → its own `upstream-research` plugin.

## Steps

- [x] **1. Split the seed plugin** — `code-review-workflow` → `git-conventions`
  + `contributor-workflow` (dependency), update `marketplace.json` + `README`.
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
- [ ] **5. `claude-code-web` plugin** — seed from the web-quirk corpus in the
  sibling `CLAUDE.md`s; enable at user scope.
- [ ] **6. `upstream-research` plugin.**
- [ ] **7. `terraform-standards` plugin.**
- [ ] **8. `terraform-provider-standards` plugin.**
- [ ] **9. `scaffolding` plugin** — references `flungo/github-workflows`.
- [ ] **10. Repo CI** — adopt the markdownlint + lychee reusable workflows from
  `github-workflows`, plus a `claude plugin validate` check on PRs so the
  marketplace can't break; this is itself dogfooding steps 4 and 9.

> **🤖 Agent** — author one plugin per PR (draft), validate with
> `claude plugin validate` and a test-install before pushing, and confirm each
> new plugin's disposition against the table above rather than inventing scope.

## Notes

- **Owned vs third-party repos:** in a repo Fabrizio owns (his namespace, not a
  fork), `git-conventions` and the relevant project-scope standards plugins are
  adopted at repo level so every contributor follows them; a third-party repo
  gets only his personal user-scope plugins. The `scaffolding` plugin encodes
  this distinction — to be formalized in an ADR when that plugin is designed.
- **claude.ai UI:** the "Add marketplace" flow threw a transient service
  disruption during initial setup; the CLI install path is verified working, so
  any recurrence is claude.ai-side, not a repo defect.
