# Building out a fresh repo

For a **new owned repo** (verify ownership first — see `owned-vs-third-party.md`), bring it to the standards **from the start**, so nothing has to be retrospectively aligned later.

The repo itself is often created and configured through the `terraform-github` helper repo (see `helper-repos.md`), not by hand.

## Onboard, in order

1. **Adopt the core plugins** — commit `.claude/settings.json` enabling `git-conventions` and `docs-standards`, plus the standards plugin(s) for the repo's type (`terraform-standards` / `terraform-provider-standards`), with `extraKnownMarketplaces` pointing at `flungo/claude-plugins`. These are on before any real content lands, so the content is written to standard the first time.
2. **Write an initial `CLAUDE.md`** — repo purpose, structure, "Active work", and "Key decisions", **pointing at** the standards plugins and the `github-workflows` CI contract rather than restating them (`docs-standards` owns the doc conventions; the shared-CI reference owns the CI contract).
3. **Create the `docs/` skeleton** — per `docs-standards` (its Diátaxis model and per-directory indexes; don't restate it here), plus the founding **ADR-001** recording why the repo exists and its core structural choices.
4. **Seed a build-out plan** — a `docs/plans/` plan following `docs-standards`' plan lifecycle, tracking the onboarding to completion. Start from the generic build-out checklist below and **extend it with the repo's own goals**, and retire it once complete per that lifecycle.
5. **Adopt the shared CI** — the `github-workflows` family for the repo's type plus `flungo-workflows` (`helper-repos.md`). Some jobs have a **prerequisite stub** — e.g. the Terraform workflow needs minimal Terraform/backend config, and the provider test workflow a minimal provider — so land that stub in the same step (see below).

## The generic build-out checklist (extend per repo)

Every fresh owned repo's plan starts from roughly this, then grows repo-specific steps:

- [ ] `.claude/settings.json` — core + type-specific standards plugins enabled.
- [ ] `CLAUDE.md` — purpose, structure, active work, key decisions, pointers to standards + CI contract.
- [ ] `docs/` Diátaxis skeleton + indexes + founding ADR-001.
- [ ] Shared CI adopted for the repo type + `flungo-workflows`; repo-specific config (`.tf`, `.markdownlint-cli2.jsonc`, `.goreleaser.yml`, …) added where the family needs it.
- [ ] First real content stubbed (see below).
- [ ] *(repo-specific goals appended here)*

## Stub content together with the plugin that governs it

Introduce a part of the repo **and** adopt the plugin relevant to it in the same move, so the stub is already to standard:

- The first docs → written to `docs-standards` from the first line, not reformatted later.
- Adding the first Terraform config → the `terraform-standards` conventions apply to it as it's written (not fixed up afterwards).
- Standing up a provider's first resource → `terraform-provider-standards` shapes its layout, docs, and tests from the first file.

The point is that no part of the repo is ever written "to be aligned later" — the governing plugin is on before its content exists.
