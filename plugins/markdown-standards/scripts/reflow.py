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
the parser never hands them over. YAML frontmatter is not Markdown at all and is
split off before parsing (see split_frontmatter).

The render gate is applied PER BLOCK against the WHOLE FILE: a block's reflow is
kept only if the entire file still renders identically with that block changed,
accumulated across blocks. One awkward paragraph therefore costs only itself
rather than forfeiting the file.

Usage:
    pip install markdown-it-py
    python3 reflow.py            # dry-run: sample diffs + per-file result
    python3 reflow.py --apply    # write the render-verified reflow in place

Run from the repo root (globs '**/*.md', excluding node_modules).
"""
import sys, re, glob, difflib
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark").enable("table")

# Abbreviations after which ". " is NOT a sentence end. Over/under-breaking here
# is style-only — the render gate guarantees correctness either way.
ABBR = re.compile(
    r"(?:^|[\s(\[\"'/])(?:e\.g|i\.e|etc|vs|cf|a\.k\.a|approx|resp|viz|Fig|Dr|Mr|Mrs|Ms|Ph\.D|Inc|Ltd|Jr|Sr)\.$",
    re.I,
)

HARD_BREAK = re.compile(r"(  +|\\)$")
BLOCKQUOTE = re.compile(r"^((?:\s*>)+\s?)")
LIST_MARKER = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")
# Leading YAML frontmatter: "---" opening the file, lines of metadata (lazily,
# so the FIRST closing delimiter wins), then "---" or "..." on its own line.
# No capturing groups — the whole match is the region, taken as group(0).
FRONTMATTER = re.compile(
    r"\A(?:[ \t]*\n)*"                       # tolerate blank lines above it
    r"---[ \t]*\n"                           # opening delimiter, exactly three
    r"(?:.*\n)*?"                            # metadata, lazily
    r"(?:---|\.\.\.)[ \t]*(?:\n|\Z)"         # first closing delimiter wins
)


def split_sentences(text):
    sents, start, i, n = [], 0, 0, len(text)
    in_code = False
    while i < n:
        c = text[i]
        if c == "`":
            in_code = not in_code
            i += 1
            continue
        if not in_code and c in ".?!" and i + 1 < n and text[i + 1] == " ":
            if c == "." and i >= 1 and text[i - 1] == ".":       # ellipsis
                i += 1
                continue
            prefix = text[start:i + 1]
            if c == "." and ABBR.search(prefix):                 # abbreviation
                i += 1
                continue
            sent = prefix.strip()
            if sent:
                sents.append(sent)
            start = i + 2
            i = start
            continue
        i += 1
    tail = text[start:].strip()
    if tail:
        sents.append(tail)
    return sents


def norm_html(s):
    return re.sub(r"\s+", " ", md.render(s)).strip()


def split_frontmatter(src):
    """Split leading YAML frontmatter off the Markdown body: (frontmatter, body).

    Frontmatter is metadata, not Markdown, and a CommonMark parser has no notion
    of it: the delimiters read as a thematic break or a setext underline and the
    key lines read as prose. That makes a frontmatter block a paragraph like any
    other, and reflowing it rewrites YAML — "name: a" and "tags:" joined onto one
    line, or a "description:" value split across two — while the render gate sees
    nothing wrong, because the mangled keys render to the same <p> as before.

    So it never reaches the parser. Anything a frontmatter-aware consumer would
    treat as frontmatter is carried through byte-identically, and the body after
    it reflows as usual.

    Telling it from a thematic break is positional, exactly as Jekyll, Hugo and
    every other frontmatter reader do it: only a "---" opening the FILE can open
    frontmatter, it must be exactly three dashes, and it must be closed. A "---"
    anywhere below, an unterminated one, a setext underline, and the other
    thematic-break spellings ("- - -", "***", "___") are all left to the parser.
    The one ambiguity the position rule cannot settle is a document that opens
    with a genuine thematic break and has another "---" further down; that reads
    as frontmatter here, as it does everywhere else. Deliberately so: guessing
    wrong that way skips a reflow, guessing wrong the other way destroys YAML.
    """
    m = FRONTMATTER.match(src)
    return (m.group(0), src[m.end():]) if m else ("", src)


def body_html(src):
    """Normalised render of everything the script may rewrite."""
    return norm_html(split_frontmatter(src)[1])


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
    frontmatter, src = split_frontmatter(src)
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
    return frontmatter + "\n".join(lines), changed, rejected


def main():
    apply_changes = "--apply" in sys.argv
    files = sorted(f for f in glob.glob("**/*.md", recursive=True) if "/node_modules/" not in f)
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
        if body_html(orig) != body_html(new):                    # belt and braces
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


if __name__ == "__main__":
    main()
