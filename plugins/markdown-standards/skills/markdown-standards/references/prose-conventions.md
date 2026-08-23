# Prose conventions paired with the markdownlint defaults

The standard `.markdownlint-cli2.jsonc` in every adopting repo sets `MD013: false`, `MD024: { siblings_only: true }` and `MD060: { style: "compact" }`, and keeps `MD028` at its default (enabled).
Each of those rule choices is half of a pair: the machine-checkable rule, plus a human convention the tool can't enforce.
This file is the human half.
Apply these conventions in any of Fabrizio's repos, whether or not the repo has adopted the lint CI.

This file is also the **register of positions taken**: a rule with an entry here has been considered and either accepted or rejected.
It is not a list of every enabled rule — most of markdownlint's defaults need no position, and no entry means none was ever needed.
When a linter bump enables a rule nobody chose and it fires on unchanged content, see [`new-lint-rules.md`](new-lint-rules.md).
Keep each entry to the convention itself; why it was adopted belongs in the commit that adopted it.

## Semantic line breaks (`MD013` disabled)

Write prose **one sentence per source line**.
Markdown renders consecutive lines as one paragraph, so this is a pure source-level convention — but it gives sentence-scoped diffs and review comments, and no paragraph-wide reflow churn when one sentence changes.

- A sentence lives on a single line however long it runs — that's why `MD013` (line-length) is disabled rather than left to fight the convention.
  A hard wrap column and one-sentence-per-line are mutually exclusive, and the sentence is the meaningful unit, so the wrap limit goes.
  Never "fix" a long line by hard-wrapping it.
- markdownlint has no rule for this, and Prettier declined one (cross-language sentence detection is too hard) — but it is not unenforced.
  [`markdown-sembr.yml`](https://github.com/flungo/github-workflows/blob/main/.github/workflows/markdown-sembr.yml) in `flungo/github-workflows` gates the one MUST rule: two sentences must not share a source line.
  It is opt-in by adoption, since it is the only Markdown workflow there that imposes a prose style.
  Where a line *could* also have been broken stays a judgement call the check never reports, so the rest remains convention, applied when writing and editing.
- ("Semantic line breaks" / "ventilated prose" — see <https://sembr.org/> — has no universal consensus; adopted for the diff and review benefits.)

**Scope — apply it wherever the rendered output is unchanged.**
That is the whole test, and it reaches further than top-level paragraphs:

- **Top-level prose paragraphs** — always.
- **List items and blockquote paragraphs** — yes.
  A sentence per line renders identically there too, and the diff benefit is the same.
  The source is fiddlier, because each continuation line must carry the list item's indent or the blockquote's `>` prefix; that is a reason to take care, not a reason to exempt them.
- **Headings, tables, and code blocks** — no.
  A line break there changes the render, or the content.
- **Hard-break blocks** — leave them alone, but read one as a smell rather than a pattern to copy.
  Lines ending in two spaces or a backslash render a `<br>`, so rewrapping them changes the output and the reflow refuses to touch them.
  That is a rule about not breaking a document, not an endorsement: a run of `**Key:** value` lines held together by trailing whitespace is a list that has not admitted it, and the `<br>` is papering over the mismatch between a source that looks like separate lines and a render that is one paragraph.
  Written as a list it renders the way it reads, every item is already on its own line, and the question of where sentences may break never comes up — which is how the ADRs here carry their `Date` and `Status`.
- **Pre-canned data** — out of scope entirely, wherever a repo keeps it.
  A fixture, a sample input, a recorded response: it is reproduced to look like the thing it stands in for, so imposing the house style on it changes the very thing it exists to preserve.
  This is a scope rule rather than a lint exemption — don't reflow one by hand either, and don't read a hard-wrapped one as a defect.
  **Keep such data in a directory the checks can match** — `fixtures/`, `inputs/`, `testdata/`, whatever the repo calls it — rather than scattering it and excluding file by file.
  One directory pattern covers the files that do not exist yet; a list naming files goes stale the moment somebody adds another, and it goes stale silently, as a passing build.
  Exclude that directory rather than a parent that also holds authored prose, so a README explaining the data stays in scope.
  Declare it once, in the repo's markdownlint config: the semantic-line-break check reads `ignores` from there too, so neither check can end up covering a tree the other skips.

**Migrating an existing repo.**
Because the convention is render-neutral, a migration can be **gated on render-equivalence**: reflow the source, render both versions to normalised HTML, and keep the change only where the HTML is byte-identical.
This plugin ships [`reflow.py`](../../../scripts/reflow.py), which implements exactly that — never do a blind unwrap instead.
It covers everything the rule covers: top-level paragraphs, list items at any nesting level and marker width, and blockquotes including nested ones, carrying each continuation line's indent or `>` prefix, and leaving hard-break blocks alone.
Leading YAML frontmatter is split off before any of that and carried through byte-identically — it is metadata, not prose, and the render gate cannot protect it, because a CommonMark parser reads the delimiters as a thematic break and the key lines as an ordinary paragraph, so YAML mangled into one line renders to exactly the same `<p>`.
At runtime the script is at `${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py`; run it from the target repo's root:

```sh
pip install markdown-it-py
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py"            # dry run — sample diffs + per-file gate result
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py" --apply    # write the render-verified reflow in place
```

It is a one-time best-effort migration pass, not repo CI — `markdown-sembr.yml` is the repeatable gate, and the two are meant to be adopted together.
Run the check after the reflow and fix anything it still reports by hand: the script is deliberately conservative, and the gate is the arbiter of done.
The gate is applied **per block against the whole file**: a paragraph's reflow is kept only if the entire file still renders identically with it changed, so an awkward paragraph costs only itself rather than forfeiting the file.
Anything it reports as left behind is deliberate — reflow those by hand or leave them.

> **🤖 Agent** — write new prose one sentence per line from the start, in list items and blockquotes as well as top-level paragraphs; don't hard-wrap and leave it for a later reflow pass.

## Unique cross-referenced headings (`MD024` `siblings_only`)

`siblings_only` lets docs repeat subsection names under different parents (e.g. `Context` / `Decision` / `Consequences` across ADRs) while still blocking duplicates under the same parent.
That leaves one narrow gap, which convention closes:

**Give any heading you cross-reference a unique name; repeat heading text only where it is not a link target.**

The gap it closes: identical heading text produces order-dependent GitHub anchors (`#symptom`, `#symptom-1`).
lychee replicates that suffixing and flags a dangling fragment, but it is existence-only — if someone later inserts a same-named heading *before* the linked one, the old anchor still resolves and now **silently points at the wrong heading**.
No tool flags that redirect:

| Case | Link outcome | Caught by |
| --- | --- | --- |
| New duplicate is a **sibling** (same parent) | — | `MD024` `siblings_only` blocks it |
| Non-sibling, added **after** the linked heading | still correct | no breakage |
| Non-sibling, added **before** the linked heading | silently redirects to the new heading | **neither** — only the unique-name convention |
| Heading renamed / removed / typo'd | dangles | lychee (`Cannot find fragment`) |

## Tables are compact, delimiter rows included (`MD060: { style: "compact" }`)

**One space each side of every pipe — `| --- | --- |`, not `|---|---|` and not columns padded out to a common width.**

Header and body rows get padded naturally; the delimiter row is the one that gets compressed out of habit, leaving the table inconsistent with itself.
`markdownlint-cli2 --fix` rewrites it, so this is worth knowing rather than hand-applying.

**Pin `compact` rather than leaving the default `"consistent"`, which is ambiguous.**
It infers the style per table, and a table no row disambiguates — cells all different widths — infers `"aligned"` instead.

Compact is the choice for the same reason `MD013` is off: **a diff should be the size of the change.**
Under `aligned`, cell width is shared state — every cell is padded to its column's widest, so editing one cell reflows the whitespace of every row in the table and a one-word change arrives as a whole-table diff.
One long cell also taxes every other row with padding forever.
Compact has no such coupling: a cell's source is its own content, so the diff names the row that changed.
That is the table-shaped version of one sentence per line.

Two lesser points fall out the same way: `--fix` produces compact but will not pad to alignment, so an inferred-aligned table becomes hand editing; and aligned tables are unreadable in source once one cell is long, which is most of them here.

## Adjacent blockquotes (`MD028` enabled)

Two blockquotes separated by only a blank line are two *separate* blockquotes in CommonMark/GFM (the blank line ends the first), but the split is parser-ambiguous, so `MD028` flags it.
Fix to match intent:

- **One blockquote intended:** put `>` on the blank line so it is a single quote.
- **Two distinct blockquotes intended:** prefer a connecting sentence between them where one flows naturally; otherwise separate them with an invisible `<!-- -->` comment.
  Never manufacture filler text just to avoid the comment.
- **Never collapse distinct notes into one blockquote just to silence the rule.**
