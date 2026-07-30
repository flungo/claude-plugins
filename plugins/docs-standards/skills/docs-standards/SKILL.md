---
name: docs-standards
description: Fabrizio's documentation conventions for a repository's docs/ tree. Consult this whenever writing or maintaining docs in one of his repos — adding or changing an ADR, plan, runbook, or reference doc; updating a README index; recording an architectural decision; retiring a completed plan; or scanning for stale docs at session end. Covers the Diátaxis directory split (decisions, plans, runbooks, reference), the Nygard ADR format, the ephemeral two-PR plan lifecycle, keeping every README index current in the same commit, the agent-directed and verify callouts, and a session-end doc-maintenance checklist. Relies on the markdown-standards skill for how the Markdown itself is written. Complements the repo's own CLAUDE.md rather than overriding it.
---

# Documentation Standards

Fabrizio's standing conventions for how a repository's `docs/` tree is
organised and maintained. Documentation is a first-class deliverable — stale
docs are actively harmful, because they mislead future sessions into
re-deriving settled decisions or acting on wrong assumptions. Apply these any
time you write or touch documentation in one of his repos, whether or not a
named command was invoked.

**These conventions complement repo/context rules, they never supersede
them.** Always check for a `CLAUDE.md`, `CONTRIBUTING.md`, or similar guidance
in the repo first; where the repo specifies something different, follow the
repo. These conventions only fill the gaps the repo doesn't cover.

This skill governs how a `docs/` tree is **organised and maintained**; how the
Markdown itself is **written** — semantic line breaks, cross-references and
link hygiene, heading uniqueness — belongs to the **`markdown-standards`**
skill, a declared dependency of this plugin. Read it for any prose or link
you write, in `docs/` or anywhere else in the repo.

## The reference files

Read the relevant reference before doing the work — each is the authoritative
detail for its area:

- **`references/documentation-model.md`** — the core model: the Diátaxis
  directory split (`decisions/`, `plans/`, `runbooks/`, `reference/`), what
  belongs in each, keeping every `README.md` index current in the same commit,
  the ephemeral two-PR plan lifecycle, the end-of-session staleness scan, and
  the two callout devices. Read it before adding or moving any doc, or at
  session end.
- **`references/adr-template.md`** — the canonical Nygard ADR format (the exact
  heading shape, the `Date` and `Status` metadata, the `Context` / `Decision`
  / `Consequences` sections), sequential numbering, and supersession. Read it
  before writing or changing an ADR.
- **`references/stop-hook.md`** — the session-end doc-maintenance checklist:
  the `Stop` hook this plugin ships, and the equivalent `.claude/settings.json`
  snippet for a repo that wants it without adopting the plugin.

## When to reach for this

- Recording an architectural decision → write an ADR
  (`references/adr-template.md`) and update the decisions index.
- Starting, advancing, completing, or retiring a one-time procedure → the plan
  lifecycle in `references/documentation-model.md`.
- Writing a repeatable how-to → a runbook; writing a lookup doc → a reference.
- Touching anything under `docs/` → refresh the directory's `README.md` index
  in the same commit.
- Ending a session → run the staleness scan and the doc-maintenance checklist.

## Session-end checklist

This plugin ships a `Stop` hook that prints a doc-maintenance checklist when a
session ends (see `references/stop-hook.md`). The checklist is a backstop, not
the mechanism — land tracker updates (plan checkboxes, an "Active work" table,
ADR statuses) in the same PR that earns them, not after the fact from the hook.
