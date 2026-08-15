# Cross-references

Keep links and references accurate and unambiguous.
These rules apply to **any** cross-reference — between docs, to an ADR, to source code, or to another repo.

The Markdown validation CI (where adopted) enforces the **mechanical** half: the link/anchor check fails a PR when a relative link doesn't resolve to a file or an anchor doesn't match a heading; markdownlint flags link *style* (bare URLs, empty links, same-file fragment validity); and the daily external-URL sweep raises an issue for dead external links.
The rules below cover both how to fix those failures — always fix the link or its target, never suppress the check — and the **semantic** hygiene the tools can't verify: that link text is unambiguous and correctly qualified.

## General rules — apply to every reference

- **Never reference a bare identifier.**
  `002` alone is ambiguous — write `ADR 002`.
  The same holds for any target: name what it is (a section, a file like `compose.yml`, a function) so the link text stands on its own.
  Never use "here" or "this" as link text.
- **Keep a prefix label in the link text for a single reference; factor it out for a list.**
  One reference keeps the label inside — `[ADR 002](…)`, `[compose.yml](…)`.
  For a list, where the label can't sit inside each link, write it once and link the identifiers: `ADR [002](…), [005](…), and [007](…)`.
- **Same-repo context is implied; cross-repo must be explicit.**
  A plain reference means this repo.
  Anything elsewhere is qualified with its project/repo name and linked to its full URL — e.g. `[<Project> ADR 009](https://github.com/<owner>/<repo>/blob/main/docs/decisions/009-….md)`.
- **Anchors:** put enough context in the link text to disambiguate — if the heading name alone is ambiguous in the sentence, include the page too (e.g. `architecture.md § Naming conventions`).
- **Give any heading you cross-reference a unique name.**
  Identical heading text produces order-dependent GitHub anchors (`#symptom`, `#symptom-1`), so a link to a duplicated heading is ambiguous and silently points to the wrong one if a same-named heading is later added before it.
  `MD024: siblings_only` allows repeated subsection names under different parents, and lychee resolves the `-1`/`-2` suffixes, but the anchor check cannot flag that silent redirect — so link targets must be unique.
  (Detail: `prose-conventions.md § Unique cross-referenced headings`.)
- **Prefer relative links within the repo; full GitHub URLs for other repos.**
  When linking to source that can move, name the file/symbol (and pin to a tag or commit where it matters) so the reference survives churn.
- **When you rename or remove a file, heading/anchor, or symbol, search the repo for references and update them** so links don't break — this is what keeps the link/anchor check green.
  Verify links resolve before committing.

## ADRs — a concrete example of the general rules

- **Local ADR, single:** link the "ADR NNN" text with a path **relative to the linking file** — `[ADR 002](002-….md)` from within `docs/decisions/`, `[ADR 002](decisions/002-…)` from a doc directly in `docs/`, `[ADR 002](../decisions/002-…)` from a doc in a `docs/` subdirectory, and `[ADR 002](docs/decisions/002-…)` from a repo-root file (e.g. `CLAUDE.md`).
- **Local ADRs, a list:** `ADR [002](…), [005](…), and [007](…)`.
- **ADR in another repo:** qualify with the repo and link the full text — `[<Project> ADR 009](https://github.com/<owner>/<repo>/blob/main/docs/decisions/009-….md)`; for a list, `<Project> ADR [001](…), [006](…), and [009](…)`.

## Fixing validation failures

The remediation rule for every check is the same: **fix the link or its target — never suppress, ignore-list, or weaken the check to make it pass.**

- **Internal link/anchor failure (blocking PR check):** the relative path or `#anchor` is wrong, or the target moved.
  Fix the link, or restore/rename the target and update every other reference to it.
  A `Cannot find fragment` failure usually means a heading was renamed — update the links, don't delete them.
- **markdownlint finding:** fix the content.
  Add a rule override to `.markdownlint-cli2.jsonc` only when the rule is genuinely wrong for the repo, with an inline justification comment; overrides are per-repo decisions, kept to a justified minimum.
  One case is not the repo's call: a rule firing on content that was already there and previously passed means a linter bump introduced it, so follow [`new-lint-rules.md`](new-lint-rules.md) before overriding anything.
- **External-sweep issue (the auto-updated `markdown-links` issue):** verify each flagged URL.
  If the resource moved, update the link (prefer a stable or pinned URL); if it's genuinely gone, remove or replace it.
  Add a URL to `.lycheeignore` only when it legitimately 403/404s while unauthenticated (a 404 can be an existence-hiding response) — never to silence a truly dead link.
  `.lycheeignore` entries are repo-specific: curate them from that repo's own token-enabled runs, never copy another repo's entries.
