---
name: writing-styles
description: A library of named prose styles, each a reference file describing how one kind of writing is done. Consult it when a plugin, a repo, or a person names one of its styles — currently instructional-writing, for text a reader acts on as instruction. This skill applies nothing on its own; it holds the styles that other conventions cite by name, so read the style that was named rather than applying one because this skill loaded.
---

# Writing Styles

A library of named prose styles.
Each style is a reference file describing how **one kind of writing** is done, so that a plugin, a repo, or a person can adopt it by naming it.

**This skill applies nothing by being enabled.**
A style takes effect only where something cites it — a consuming plugin's own conventions, a repo's `CLAUDE.md`, or a direct request.
Read the style that was named; do not apply one because this skill happened to load.

Styles govern *what the prose says and how it is maintained*.
How the Markdown itself is written — semantic line breaks, cross-references, heading uniqueness — is a separate concern: these styles are written to compose with `markdown-standards` where a repo has adopted it, and to hold on their own where it has not.

**These conventions complement repo/context rules, they never supersede them** — where a repo's `CLAUDE.md` or `CONTRIBUTING.md` specifies something different, follow the repo.

## The styles

- **instructional-writing** (`references/instructional-writing.md`) — text a reader acts on as instruction, wherever it lives: a `SKILL.md` and the reference files beside it, a Diátaxis reference doc, a runbook, a `CLAUDE.md`.
  Covers stating the current truth rather than the document's own history, converging on plain fact over time, fixing wrong guidance at its source instead of annotating it, and never directing an agent to do what only the user can do.
  Read it before writing or revising any of those, and particularly before revising one because you have just learned something that changes it.

## Adopting a style

A consumer declares `writing-styles` in its `dependencies`, then in its own prose **names the style, says which of its writing that style governs, and summarises it** in a line or two.
It never restates the rules, and never links to a path inside this plugin.

Naming the scope is what stops a style being applied where it was not intended.
This plugin asserts nothing about which of a consumer's documents are instructional; the consumer is the only thing that knows.
