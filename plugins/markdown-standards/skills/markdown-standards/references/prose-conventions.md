# Prose conventions paired with the markdownlint defaults

The standard `.markdownlint-cli2.jsonc` in every adopting repo sets `MD013: false` and `MD024: { siblings_only: true }`, and keeps `MD028` at its default (enabled).
Each of those rule choices is half of a pair: the machine-checkable rule, plus a human convention the tool can't enforce.
This file is the human half.
Apply these conventions in any of Fabrizio's repos, whether or not the repo has adopted the lint CI.

## Semantic line breaks (`MD013` disabled)

Write prose **one sentence per source line**.
Markdown renders consecutive lines as one paragraph, so this is a pure source-level convention — but it gives sentence-scoped diffs and review comments, and no paragraph-wide reflow churn when one sentence changes.

- A sentence lives on a single line however long it runs — that's why `MD013` (line-length) is disabled rather than left to fight the convention.
  A hard wrap column and one-sentence-per-line are mutually exclusive, and the sentence is the meaningful unit, so the wrap limit goes.
  Never "fix" a long line by hard-wrapping it.
- Nothing enforces one-sentence-per-line mechanically (Prettier declined it — cross-language sentence detection is too hard; markdownlint has no reflow rule) — it is convention, applied when writing and editing.
- ("Semantic line breaks" / "ventilated prose" — see <https://sembr.org/> — has no universal consensus; adopted for the diff and review benefits.)

**Scope — apply it wherever the rendered output is unchanged.** That is the whole test, and it reaches further than top-level paragraphs:

- **Top-level prose paragraphs** — always.
- **List items and blockquote paragraphs** — yes.
  A sentence per line renders identically there too, and the diff benefit is the same.
  The source is fiddlier, because each continuation line must carry the list item's indent or the blockquote's `>` prefix; that is a reason to take care, not a reason to exempt them.
- **Headings, tables, and code blocks** — no.
  A line break there changes the render, or the content.
- **Hard-break blocks** — preserve them.
  Lines ending in two spaces or a backslash (e.g. a `**Date:**` / `**Status:**` metadata block) render a `<br>` that carries meaning, so reflowing them *would* change the output.

**Migrating an existing repo.** Because the convention is render-neutral, a migration can be **gated on render-equivalence**: reflow the source, render both versions to normalised HTML, and keep the change only where the HTML is byte-identical.
This plugin ships [`reflow.py`](../../../scripts/reflow.py), which implements exactly that — never do a blind unwrap instead.
It covers everything the rule covers: top-level paragraphs, list items at any nesting level and marker width, and blockquotes including nested ones, carrying each continuation line's indent or `>` prefix, and leaving hard-break blocks alone.
At runtime the script is at `${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py`; run it from the target repo's root:

```sh
pip install markdown-it-py
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py"            # dry run — sample diffs + per-file gate result
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py" --apply    # write the render-verified reflow in place
```

It is a one-time best-effort migration pass, not repo CI.
The gate is applied **per block against the whole file**: a paragraph's reflow is kept only if the entire file still renders identically with it changed, so an awkward paragraph costs only itself rather than forfeiting the file.
Anything it reports as left behind is deliberate — reflow those by hand or leave them.

Pass `--exclude GLOB` (repeatable) for anything the repo exempts from its Markdown conventions — eval fixtures, vendored docs, generated output.
Mirror whatever the repo's `.markdownlint-cli2.jsonc` already ignores, so the two agree on what counts as the repo's own prose.
Patterns match the whole repo-relative path with `*` crossing directory separators, so `--exclude 'plugins/*/evals/*'` reaches any depth.

**It is a migration tool, not the rule.** The rule is the convention above; the script only automates the mechanical majority of a first pass.
It breaks on sentence boundaries alone, because that is what can be done safely without judgement.
A human or an agent writing prose applies the convention with judgement — see [sembr.org](https://sembr.org/) — and may legitimately break where the script would not.
Do not treat the script's output as the target shape, and do not reach for it when writing new prose.

> **🤖 Agent** — write new prose one sentence per line from the start, in list items and blockquotes as well as top-level paragraphs; don't hard-wrap and leave it for a later reflow pass.

## Unique cross-referenced headings (`MD024` `siblings_only`)

`siblings_only` lets docs repeat subsection names under different parents (e.g. `Context` / `Decision` / `Consequences` across ADRs) while still blocking duplicates under the same parent.
That leaves one narrow gap, which convention closes:

**Give any heading you cross-reference a unique name; repeat heading text only where it is not a link target.**

The gap it closes: identical heading text produces order-dependent GitHub anchors (`#symptom`, `#symptom-1`).
lychee replicates that suffixing and flags a dangling fragment, but it is existence-only — if someone later inserts a same-named heading *before* the linked one, the old anchor still resolves and now **silently points at the wrong heading**.
No tool flags that redirect:

| Case | Link outcome | Caught by |
|---|---|---|
| New duplicate is a **sibling** (same parent) | — | `MD024` `siblings_only` blocks it |
| Non-sibling, added **after** the linked heading | still correct | no breakage |
| Non-sibling, added **before** the linked heading | silently redirects to the new heading | **neither** — only the unique-name convention |
| Heading renamed / removed / typo'd | dangles | lychee (`Cannot find fragment`) |

## Adjacent blockquotes (`MD028` enabled)

Two blockquotes separated by only a blank line are two *separate* blockquotes in CommonMark/GFM (the blank line ends the first), but the split is parser-ambiguous, so `MD028` flags it.
Fix to match intent:

- **One blockquote intended:** put `>` on the blank line so it is a single quote.
- **Two distinct blockquotes intended:** prefer a connecting sentence between them where one flows naturally; otherwise separate them with an invisible `<!-- -->` comment.
  Never manufacture filler text just to avoid the comment.
- **Never collapse distinct notes into one blockquote just to silence the rule.**
