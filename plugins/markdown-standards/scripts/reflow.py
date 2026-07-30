#!/usr/bin/env python3
"""Reflow Markdown prose to semantic line breaks (one sentence per line).

Best-effort migration tool for adopting semantic line breaks in a repo's existing
docs — a one-time pass, never repo CI. Ships with the markdown-standards plugin;
the convention it implements is in
skills/markdown-standards/references/prose-conventions.md. It rewrites only
source whitespace, never rendered output:
every change is gated on render-equivalence (normalised HTML byte-identical
before and after), and anything that would render differently is left untouched.

Scope — everywhere the rendered output is unchanged:
  - TOP-LEVEL prose paragraphs;
  - LIST ITEM paragraphs, at any nesting level and marker width, with
    continuation lines indented to the item's content column;
  - BLOCKQUOTE paragraphs, including nested ones, with the "> " prefix carried;
  - PRESERVING hard-break blocks (trailing "  " / "\\" — e.g. **Date:** metadata),
    whose <br> carries meaning.
Headings, tables and fenced code are never touched: they are not paragraphs, so
the parser never hands them over.

The render gate is applied PER BLOCK against the WHOLE FILE: a block's reflow is
kept only if the entire file still renders identically with that block changed,
accumulated across blocks. One awkward paragraph therefore costs only itself
rather than forfeiting the file.

Usage:
    pip install markdown-it-py
    python3 reflow.py                          # dry-run: sample diffs + per-file result
    python3 reflow.py --apply                  # write the render-verified reflow in place
    python3 reflow.py --exclude 'evals/**'     # hold files out (repeatable)

Run from the repo root (globs '**/*.md', excluding node_modules). Pass
--exclude for anything the repo exempts from its Markdown conventions — eval
fixtures, vendored docs, generated output — mirroring whatever the repo's
.markdownlint-cli2.jsonc already ignores.
"""
import sys, re, glob, difflib, fnmatch
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark").enable("table")

# Abbreviations after which ". " is NOT a sentence end. Over/under-breaking here
# is style-only — the render gate guarantees correctness either way.
ABBR = re.compile(
    r"(?:^|[\s(\[\"'/])(?:e\.g|i\.e|etc|vs|cf|a\.k\.a|approx|resp|viz|Fig|Dr|Mr|Mrs|Ms|Ph\.D|Inc|Ltd|Jr|Sr)\.$",
    re.I,
)

# Closing markup that may sit between a sentence terminator and the space after
# it. Backtick is deliberately absent: it would fight the code-span toggle.
CLOSERS = "*_)]}\"'’”»"

HARD_BREAK = re.compile(r"(  +|\\)$")
BLOCKQUOTE = re.compile(r"^((?:\s*>)+\s?)")
LIST_MARKER = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")


def split_sentences(text):
    sents, start, i, n = [], 0, 0, len(text)
    in_code = False
    while i < n:
        c = text[i]
        if c == "`":
            in_code = not in_code
            i += 1
            continue
        if not in_code and c in ".?!":
            # A terminator may be followed by closing markup before the space —
            # "**Lead-in.** Next" and "(aside.) Next" both end a sentence.
            end = i + 1
            while end < n and text[end] in CLOSERS:
                end += 1
            if end >= n or text[end] != " ":
                i += 1
                continue
            if c == "." and i >= 1 and text[i - 1] == ".":       # ellipsis
                i += 1
                continue
            prefix = text[start:i + 1]
            if c == "." and ABBR.search(prefix):                 # abbreviation
                i += 1
                continue
            sent = text[start:end].strip()
            if sent:
                sents.append(sent)
            start = end + 1
            i = start
            continue
        i += 1
    tail = text[start:].strip()
    if tail:
        sents.append(tail)
    return sents


def norm_html(s):
    return re.sub(r"\s+", " ", md.render(s)).strip()


def split_prefix(line):
    """Split a source line into its structural prefix and its prose content.

    The prefix is any blockquote markers, then either a list marker or plain
    indentation — i.e. everything that positions the text rather than being it.
    """
    m = BLOCKQUOTE.match(line)
    bq = m.group(1) if m else ""
    rest = line[len(bq):]
    m2 = LIST_MARKER.match(rest)
    if m2:
        return bq + m2.group(0), rest[len(m2.group(0)):]
    indent = len(rest) - len(rest.lstrip())
    return bq + rest[:indent], rest[indent:]


def continuation_prefix(first_prefix):
    """The prefix a wrapped line needs to stay in the same block.

    Blockquote markers are carried verbatim; a list marker becomes spaces of
    equal width, so continuations align with the item's content column.
    """
    m = BLOCKQUOTE.match(first_prefix)
    bq = m.group(1) if m else ""
    return bq + " " * len(first_prefix[len(bq):])


def reflow_block(block):
    """Reflow one paragraph's source lines, or None to leave it alone."""
    if any(HARD_BREAK.search(l) for l in block):
        return None
    first_prefix, first_content = split_prefix(block[0])
    contents = [first_content] + [split_prefix(l)[1] for l in block[1:]]
    joined = " ".join(c.strip() for c in contents).strip()
    sentences = split_sentences(joined)
    if not sentences:
        return None
    cont = continuation_prefix(first_prefix)
    return [first_prefix + sentences[0]] + [cont + s for s in sentences[1:]]


def paragraph_spans(src):
    """Line spans of every paragraph, at any nesting depth.

    Only paragraphs are returned, so headings, tables and fenced code are never
    candidates. Hidden paragraphs (tight list items) are included — that is
    exactly the list-item text we want to reach.
    """
    return [t.map for t in md.parse(src) if t.type == "paragraph_open" and t.map]


def reflow_text(src):
    """Return (reflowed source, blocks changed, blocks rejected by the gate)."""
    lines = src.split("\n")
    target = norm_html(src)
    changed = rejected = 0
    # Bottom-up, so a rewrite never invalidates an earlier span's indices.
    for a, b in sorted(paragraph_spans(src), reverse=True):
        new_block = reflow_block(lines[a:b])
        if new_block is None or new_block == lines[a:b]:
            continue
        saved = lines[a:b]
        lines[a:b] = new_block
        if norm_html("\n".join(lines)) == target:
            changed += 1
        else:
            # Revert over the block just inserted, not the original span — the
            # replacement is usually longer, so a:b no longer covers it.
            lines[a:a + len(new_block)] = saved
            rejected += 1
    return "\n".join(lines), changed, rejected


def select_files(paths, excludes):
    """Filter discovered paths by the --exclude patterns.

    Patterns are glob-style and matched against the whole repo-relative path,
    with "*" crossing directory separators — so 'plugins/*/evals/*' reaches any
    depth under any plugin's evals directory.
    """
    return sorted(
        p for p in paths
        if "node_modules" not in p.split("/")             # nested *and* top-level
        and not any(fnmatch.fnmatch(p, pat) for pat in excludes)
    )


def parse_args(argv):
    apply_changes = False
    excludes = []
    it = iter(argv)
    for arg in it:
        if arg == "--apply":
            apply_changes = True
        elif arg == "--exclude":
            excludes.append(next(it, ""))
        elif arg.startswith("--exclude="):
            excludes.append(arg.split("=", 1)[1])
        else:
            sys.exit(f"unknown argument: {arg}\n{__doc__}")
    return apply_changes, excludes


def main():
    apply_changes, excludes = parse_args(sys.argv[1:])
    files = select_files(glob.glob("**/*.md", recursive=True), excludes)
    reflowed, unchanged, partial = [], [], []
    shown = 0
    for f in files:
        orig = open(f, encoding="utf-8").read()
        new, changed, rejected = reflow_text(orig)
        if rejected:
            partial.append(f"{f} ({rejected} block(s) left)")
        if new == orig:
            unchanged.append(f)
            continue
        if norm_html(orig) != norm_html(new):                    # belt and braces
            print(f"!! WHOLE-FILE GATE FAILED, skipping: {f}")
            continue
        reflowed.append(f)
        if apply_changes:
            open(f, "w", encoding="utf-8").write(new)
        elif shown < 2:
            shown += 1
            print(f"\n----- SAMPLE DIFF: {f} -----")
            diff = difflib.unified_diff(orig.splitlines(), new.splitlines(), lineterm="", n=1)
            print("\n".join(list(diff)[:60]))
    print(f"\n=== {'APPLIED' if apply_changes else 'DRY-RUN'} ===")
    print(f"reflowed (render-verified): {len(reflowed)}")
    print(f"unchanged: {len(unchanged)}")
    print(f"partially reflowed (gate kept the rest): {len(partial)} -> {partial}")
    if excludes:
        print(f"excluded by pattern: {excludes}")


if __name__ == "__main__":
    main()
