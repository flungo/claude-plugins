---
name: terraform-standards
description: Fabrizio's conventions for writing and maintaining a Terraform/HCL configuration repository (a consumer of providers, not a provider itself). Consult this whenever adding or changing .tf files, naming resources, handling secrets in config, pinning a provider, or bringing an existing cloud resource under Terraform management. Repo-adopted (project scope) — a repo enables it in its .claude/settings.json; it complements, and defers to, that repo's own CLAUDE.md.
---

# Terraform Standards

Conventions for a Terraform/HCL repo that *consumes* providers to manage real infrastructure — as opposed to a repo that *builds* a provider (see `terraform-provider-standards`).
They keep configuration readable, diffs honest, and the adoption of existing resources safe.

These are repo-adopted defaults: a repo turns them on in its `.claude/settings.json`, and they **complement its own `CLAUDE.md`, never supersede it** — where the repo specifies something different (a structural choice, a naming exception), follow the repo.

This plugin covers *how HCL is written*, not *how the repo is structured*: whether a repo uses a single flat root module or shared modules with a directory per environment is a per-repo decision its own `CLAUDE.md` makes.

## The reference files

- **`references/conventions.md`** — the standing rules: how `.tf` files are organised (by concern or by subject), resource names that mirror the real object, sensitive values as variables, durations as arithmetic, and pinned providers with a committed lock.
- **`references/import-and-move-blocks.md`** — adopting a resource (`import {}`) and renaming or relocating one (`moved {}`) with config-driven blocks that a follow-up PR removes after apply.
