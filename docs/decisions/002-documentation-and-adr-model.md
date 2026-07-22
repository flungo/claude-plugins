# ADR-002: Documentation model — Diátaxis docs, Nygard ADRs, self-encoded

- **Date:** 2026-07-22
- **Status:** Accepted

## Context

This repository should dogfood the documentation conventions the marketplace
itself will encode (in the future `docs-standards` plugin), the same way the
sibling repos (`terraform-github`, `terraform-grafana-cloud`,
`authentik.flungo.net`, `stalwart.flungo.net`) already do. Two specifics were
open:

1. **ADR format.** Across the sibling repos two divergent forms are in use:
   Format A (`# ADR-NNN: Title` + Date, Status, Context, Decision,
   Consequences — used by the Terraform repos) and Format B (`# NNN — Title` +
   a `Status:` line, no fixed Consequences — used by the deployment repos).
2. **Build vs depend.** Claude Code plugins support dependencies (semver,
   auto-install, cross-marketplace with an allowlist), so a `docs-standards`
   plugin *could* depend on a third-party ADR plugin (`adr-kit`,
   `zircote/adr`, `claude-plugin-adr`) instead of encoding ADR mechanics
   itself.

## Decision

**Adopt the Diátaxis split** used by the sibling repos: `docs/decisions/`
(ADRs), `docs/plans/` (one-time procedures, retired when complete),
`docs/runbooks/` (repeatable how-tos), `docs/reference/` (information-oriented
lookup) — each with a `README.md` index kept current in the same commit as any
change, and the two-PR plan retirement lifecycle.

**Standardize ADRs on the Nygard format (Format A).** Research confirmed Format
A is essentially Michael Nygard's original — the industry-default lightest form
that still records Status + Context + Decision + Consequences and supports
supersession chains. Format B is the same format with Consequences dropped, so
standardizing is mostly retiring Format B. Canonical shape:

```
# ADR-NNN: Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-MMM | Deprecated

## Context
## Decision
## Consequences
```

Optional `### Positive` / `### Negative — trade-offs` subsections under
Consequences are allowed but not required (so records aren't padded with empty
sections). Supersession is recorded in the Status line plus a note on the newer
ADR; ADRs are numbered sequentially and never deleted or renumbered.

**Self-encode the ADR + docs conventions** in the `docs-standards` plugin; do
**not** depend on a third-party ADR plugin. The community ADR plugins are
governance-heavy and none are first-party; depending would couple the
marketplace to an external repo's release cadence and git-tag versioning for
what amounts to a few lines of template. (`npryce/adr-tools` remains useful as a
local CLI for scaffolding + supersession, but only as a tool, never as a plugin
dependency.)

## Consequences

**Positive**

- One canonical ADR form across all repos; adopting it here is deleting
  Format B, not inventing anything new.
- No external dependency for core documentation mechanics; the marketplace
  stays self-contained.
- The repo's own `docs/` becomes the reference implementation of
  `docs-standards` before that plugin is authored.

**Negative — trade-offs**

- The sibling repos' existing Format-B ADRs are left as-is; converging them is
  out of scope here and would be follow-up work in those repos.
- Re-encoding rather than depending means the ADR template is maintained in
  `docs-standards` rather than pulled from an upstream — a deliberate trade of
  reuse for independence.
