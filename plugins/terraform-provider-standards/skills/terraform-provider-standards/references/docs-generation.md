# Generated docs — tfplugindocs

Registry documentation is **generated** with HashiCorp's `terraform-plugin-docs` (`tfplugindocs`), never hand-written.

## How it's wired

- `tfplugindocs` is pinned as a **`go.mod` tool dependency** so its version travels with the module — add it with `go get -tool github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs` (Go 1.24+).
  Older repos may instead pin it through a `//go:build tools` `tools.go` blank import; either works, as long as `go run github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs` resolves.
- **Inputs** live in `templates/` and `examples/`: `templates/index.md.tmpl` for the provider overview (a hand-written intro plus `{{ .SchemaMarkdown }}`), `examples/resources/<name>/resource.tf` and `import.sh` per resource, and `examples/data-sources/<name>/data-source.tf` per data source.
- **Output** is the committed `docs/` tree (`docs/index.md`, `docs/resources/*.md`, `docs/data-sources/*.md`).
- Regenerating locally by hand is a convenience; CI does not depend on it (the shared workflows run `tfplugindocs generate` directly from the module).

## Never hand-edit generated docs

Files under `docs/resources/` and `docs/data-sources/` are regenerated on every run.
Edit the `templates/` and `examples/` inputs and regenerate — never the output files.

## CI keeps docs honest, via the shared workflows

Docs generation is part of the `flungo/github-workflows` provider CI family (see `ci-and-release.md`), split by design so a contributor needs no local Terraform:

- `terraform-provider-docs.yml` runs on **non-default branches**, regenerates the docs, and **commits them back** to the branch.
- The `docs` job in `terraform-provider-test.yml` runs the same generation on the default branch and **fails on drift** (a `git diff` against the committed `docs/`), catching anything that slipped through.

Both derive the provider name from the repo name and use the `tfplugindocs` version pinned in `go.mod`.
A provider without generated docs sets `check-docs: false` on the test workflow.
