---
name: upstream-research
description: Fabrizio's method for researching and verifying facts about third-party and upstream components — a library, API, tool, provider, or service the project depends on. Consult this whenever you need to confirm how an external component actually behaves — its config options, API shape, wire format, an env var name, a version-specific change, or a bug — instead of relying on memory. The rule is to go to the authoritative source (the project's own repository and official docs), distrust training data, web-search summaries, and generated docs, and record where each fact came from. Personal, always-on; complements a repo's own CLAUDE.md.
---

# Upstream Research

How Fabrizio wants facts about **third-party and upstream components** established: by going to the authoritative source, not by trusting recall.
Training data is frozen and often wrong on specifics; blog posts and web-search summaries are worse; even a project's *generated* docs can lie.
The cost of a wrong upstream fact is high — it gets baked into config or code and surfaces as a runtime failure much later.

Apply this whenever you're confirming how an external component behaves — a config option, an API or wire detail, an env var name, a version-specific change, a bug — whether or not a named command was invoked.
These are personal defaults that **complement repo/context rules, never supersede them**.

## The two reference files

- **`references/finding-sources.md`** — what counts as authoritative and how to read it (clone the source, fetch raw files, pin to a ref, navigate from the docs root), and how to record provenance so the next reader can re-check.
- **`references/what-to-distrust.md`** — the sources that mislead (training data, third-party posts and web-search summaries, generated docs, and archived or renamed predecessor repos), with the tell for each.
