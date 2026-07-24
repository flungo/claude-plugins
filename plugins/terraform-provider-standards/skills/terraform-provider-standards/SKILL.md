---
name: terraform-provider-standards
description: Fabrizio's conventions for building a Terraform provider in Go — the terraform-plugin-framework layout, tfplugindocs-generated docs, MPL-2.0 per-file headers, and adopting the shared flungo/github-workflows provider CI (golangci-lint v2, GoReleaser dual-registry release). Consult it whenever writing or changing a terraform-provider-* repo, whether the provider's resources and data sources, docs generation, tests, CI, or release. Repo-adopted (project scope) — a repo enables it in its .claude/settings.json; it complements, and defers to, that repo's own CLAUDE.md, and pairs with git-conventions and docs-standards.
---

# Terraform Provider Standards

Conventions for a repo that *builds* a Terraform provider in Go — as opposed to one that *consumes* providers to manage real infrastructure (see `terraform-standards`).
They cover how the provider is laid out, documented, licensed, and how its CI and release are adopted from the shared workflows.

These are the conventions that hold for **any** provider in this namespace; anything specific to one provider (its backend, client, auth model, acceptance-test harness) stays in that repo's own `CLAUDE.md`.

These are repo-adopted defaults: a repo turns them on in its `.claude/settings.json`, and they **complement its own `CLAUDE.md`, never supersede it** — where the repo specifies something different, follow the repo.

This plugin is provider-authoring specific.
It does **not** restate the standing git/PR hygiene (branch management, Conventional Commits, linear history, squash-vs-rebase) or the docs discipline (Diátaxis, Nygard ADRs, index maintenance) — those live in `git-conventions` and `docs-standards`, which a provider repo also adopts.

## The reference files

- **`references/project-layout.md`** — the framework choice (terraform-plugin-framework, protocol v6), the `internal/provider` package layout, resource types that mirror the API object, module and registry coordinates, and the MPL-2.0 per-file header.
- **`references/docs-generation.md`** — generating Registry docs with `tfplugindocs` (pinned as a `go.mod` tool dependency) from `templates/` + `examples/`, never hand-editing the committed `docs/` tree, and the shared workflows that regenerate and drift-check them.
- **`references/ci-and-release.md`** — adopting the `flungo/github-workflows` provider CI (test/docs/release, pinned `@v1`) and the version check, keeping the provider's own `testacc` acceptance-test job, why golangci-lint v2 needs the v2 tool (the `@v6` trap), and the GoReleaser dual-registry (Terraform + OpenTofu), conditionally GPG-signed, tag-triggered release.
