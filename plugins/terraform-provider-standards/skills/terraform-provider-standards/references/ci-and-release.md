# CI and release — adopt the shared provider workflows

A provider's CI is boilerplate for the HashiCorp scaffold (build, lint, test, docs, release), so it is **not** written per repo.
It is adopted from the shared **`flungo/github-workflows`** reusable workflows, pinned to `@v2` — a moving *branch* (not a tag) that advances on every merge to that repo's `main`, so consumers pick up fixes automatically.
The authoritative contract, inputs, and secrets live there (`docs/reference/terraform-provider-workflow.md` and the provider adoption runbook); **point to it rather than restating it** — this file captures only what a provider author needs to keep in mind.

## What the consumer calls, and what it keeps

Three reusable workflows cover the scaffold; the consumer keeps its own acceptance-test job:

| Concern | Where it lives |
| --- | --- |
| build + vet, gofmt + golangci-lint, unit tests, docs-in-sync check | `terraform-provider-test.yml@v2` |
| regenerate + commit Registry docs on a branch | `terraform-provider-docs.yml@v2` |
| GoReleaser signed publish on a `v*` tag | `terraform-provider-release.yml@v2` |
| **acceptance tests** (provider-specific) | **the consumer's own `testacc` job** |

A reusable workflow composes at the **job** level, so the consumer's `test.yml` mixes the shared `ci:` caller with its own `testacc:` job in the same file — no forking.
That `testacc:` job runs the provider's acceptance tests (`terraform-plugin-testing`, gated on `TF_ACC=1`) against its own backend, so it stays with the consumer rather than being adopted from the shared CI.
The provider name is derived from the repo name (the `terraform-provider-` prefix stripped), so most callers pass no inputs at all.
Grant `contents: write` on the caller side for the docs-commit and release callers — a reusable workflow's own `permissions:` only cap the token.

## Also adopt `flungo-workflows`

Every provider consumer should call the credential-free `flungo-workflows.yml@v2` too — its `version-check` job raises an issue against the repo itself if a future major bump ever leaves it pinning a now-frozen `@vN`.

## golangci-lint — a v2 config needs the v2 tool

The `.golangci.yml` is **v2 format**, so the lint job must run golangci-lint **v2.x** — the shared test workflow's `golangci-lint-version` input defaults to a pinned v2 release.
The durable rule: a v2 config requires the v2 tool, because the older `golangci-lint-action@v6` installs v1.x and fails to parse it.

> **🤖 Agent** — when the specific golangci-lint version matters, read the current default from the shared workflow in `github-workflows` each time rather than assuming a pinned value; it drifts as that repo updates.

## Release & signing, at a glance

The release the shared workflow runs is GoReleaser (`release --clean`) on a `v*` tag (or a `workflow_dispatch` that creates the tag), publishing a GitHub release that the **Terraform Registry** ingests and the **OpenTofu Registry** polls for.
Signing is **conditional**: with the `GPG_PRIVATE_KEY` / `PASSPHRASE` secrets the checksums are GPG-signed; without them the build passes `--skip=sign` and produces an unsigned release fit only for early testing, which neither registry accepts.
The `.goreleaser.yml` that drives it stays in the provider repo.
