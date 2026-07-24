# Project layout

## Framework — terraform-plugin-framework, protocol v6

Build on HashiCorp's **`terraform-plugin-framework`**, not the legacy `terraform-plugin-sdk/v2`.
Serve the provider over **protocol v6** (`terraform-registry-manifest.json` declares `"protocol_versions": ["6.0"]`) from a root `main.go` that calls `providerserver.Serve` with the registry address `registry.terraform.io/<namespace>/<name>` and a `version` injected at build time via ldflags.

> **🤖 Agent** — read the pinned framework and companion library versions (`terraform-plugin-framework`, `-framework-validators`, `-plugin-go`, `-plugin-testing`) from the provider's `go.mod` each time; they move over time, so don't assume a version.

## Package layout

- `internal/provider/` — the provider plus every resource and data source. One file per resource, `<name>_resource.go` with a colocated `<name>_resource_test.go`; data sources are `<name>_data_source.go`.
- `main.go` at the repo root; the provider constructor is `provider.New(version)`.

Resources and data sources are **registered explicitly** in the provider's `Resources()` / `DataSources()` slices — each `New<Name>Resource` listed by hand, not discovered.

## Resource names mirror the API object

A resource type name mirrors the upstream API object it manages, one-to-one — `<provider>_widget` for the API's `Widget`.
The Go file, the resource type, and the API object share the same name, so any one is predictable from the others.

## Module path and registry coordinates

- Module path: `github.com/<namespace>/terraform-provider-<name>`.
- Registry address: `registry.terraform.io/<namespace>/<name>` (namespace `flungo`).

## Licensing — MPL-2.0, per-file header on every source file

The provider is licensed **MPL-2.0** (`LICENSE` at the root).
**Every** source file opens with the SPDX header — Go files use `//`, YAML/shell/Make files the `#` form:

```go
// Copyright (c) Fabrizio Lungo
// SPDX-License-Identifier: MPL-2.0
```

There is no automated header check (no `copywrite`, no `addlicense`) — the header is maintained by hand, so add it to every new file yourself.
