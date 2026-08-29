# ADR-007: Conventions for working through connectors, as one plugin with a skill per connector

- **Date:** 2026-08-29
- **Status:** Accepted

## Context

Claude reaches content through connectors — Google Drive, Notion, and others — on surfaces where there is no repository and therefore no `CLAUDE.md`.
Nothing in those stores is loaded automatically.

A Google Drive folder can hold a hand-written document stating how its files are named, dated and filed, and an agent will never read it unless told to go looking.
One such document exists as a proof of concept, written by hand and expected to be used more widely once something reads it; it opens by noting that nothing loads it automatically.
The practice is therefore new rather than established — this decision is about making it worth adopting, not about serving an existing corpus.

Either way the conventions end up restated each session — the problem this marketplace exists to solve, in a place none of its plugins reach.

Two questions had to be settled before building anything.

**How wide is a plugin here?**
One plugin per connector (`google-drive-conventions`, `notion-conventions`, …), or one plugin whose skills cover the connectors?
Plugin names are install identifiers, so a later regrouping is breaking.

**Where does the owner's own configuration go?**
[ADR-005](005-generic-plugins-and-personal-configuration.md) keeps generalisable guidance and Fabrizio's applied configuration in separate plugins, which would imply a companion plugin recording his Drive layout.

## Decision

**Ship one plugin, `connector-conventions`, carrying one skill per connector** — initially `google-drive`.
The skill takes the name of the connector it covers, since that is the axis that varies within the plugin; the plugin name already supplies "conventions", and `connector-conventions:drive-conventions` would say it twice.

[ADR-001](001-marketplace-structure.md) splits plugins by enablement boundary rather than topic, and between connectors there is no such boundary.
"Honour the conventions stored in my connected content" is a single decision; nobody wants it on for Drive and off for Notion.
A skill whose connector is absent never triggers, because the tools it names are not in the session, so an unused skill costs one description line and nothing else.
Splitting per connector would create plugins that are never independently enabled — the outcome ADR-001 exists to avoid.

The name is the domain, not the first slice, per the repo's naming rule — a second connector becomes a second skill, not a rename.

**The plugin covers connector *usage* conventions too, not only the ones a store carries.**
The trash-reporting rule is the proof — it is a rule about using the connector well, with nothing to do with convention discovery, and it has to live somewhere.
`connector-conventions` reads correctly for both halves.
Within a connector, aspects are split by **reference file** rather than by skill, because every skill for one connector would trigger on the same tools and so buy nothing but description overhead.
Those files take the same names in every connector skill — `convention-discovery.md`, `convention-authoring.md`, and `behaviours.md` — so a reader who knows one connector knows where to look in the next.
`behaviours.md` is named for what it holds rather than for surprise, since much of it is simply the mechanism recorded once so it is not re-derived.
A rule that genuinely spans connectors becomes its own cross-cutting skill — the first is `data-boundaries`, for information crossing between sources.

**No companion configuration plugin.**
ADR-005's split is already satisfied, because the conventions live *in Drive*.
The plugin carries the mechanism — how to find the documents and how to order them — and the user's actual rules stay in the folders they govern, authored and edited in place.
That is strictly better than a plugin recording them, since the rules sit beside the files they describe and need no release to change.

**Semantics**, verified against the live connector before being written down.
A document governs its own folder and everything beneath it; where two conflict, the deeper wins; discovery runs once per session and is cached per folder; and one document per folder, so there is never an undefined precedence between peers.

## Consequences

### Positive

- The gap closes without asking the user to move anything — the documents they have already written start being read.
- A convention travels with the folder, so it applies to every session on every surface with the connector, and to files added later.
- Adding a connector is additive — a skill in an existing plugin, no new install, no change to what anyone has enabled.
- The connector's real behaviour is recorded from probing rather than assumption, including the failure modes that make a naive implementation wrong.

### Negative — trade-offs

- Discovery costs one metadata call per folder level before the first write, and the walk cannot be batched.
- Nothing enforces this — a session without the skill, or on a surface without the connector, still ignores the documents entirely.
- The conventions are only as current as the folder's document, and nothing detects staleness.
- Depth-based precedence is a convention of this plugin, not a property of Drive, so it holds only where an agent applies it.

## Related

- [ADR-001](001-marketplace-structure.md) — split by enablement boundary, which decides the plugin's width.
- [ADR-005](005-generic-plugins-and-personal-configuration.md) — generic versus applied configuration, satisfied here by the documents living in Drive.
