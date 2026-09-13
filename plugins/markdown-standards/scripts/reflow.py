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
    python3 reflow.py                    # dry-run: sample diffs + per-file result
    python3 reflow.py --apply            # write the render-verified reflow in place
    python3 reflow.py --apply docs/a.md  # only these paths (a file, glob or directory)

Run from the repo root. Given no paths it globs '**/*.md', reaching into dot
directories so '.github/' is covered — the same reach as the markdown-sembr
check, so a migration leaves a tree that check accepts. The repo's
markdownlint-cli2 `ignores` are read and skipped too (see collect_files).
"""
import argparse, re, json, os, glob as globlib, difflib
from fnmatch import fnmatch
from pathlib import Path
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark").enable("table")

# Abbreviations after which ". " is NOT a sentence end. Over/under-breaking here
# is style-only — the render gate guarantees correctness either way.
ABBR = re.compile(
    r"(?:^|[\s(\[\"'/])(?:e\.g|i\.e|etc|vs|cf|a\.k\.a|approx|resp|viz|Fig|Dr|Mr|Mrs|Ms|Ph\.D|Inc|Ltd|Jr|Sr)\.$",
    re.I,
)

# Closing markup allowed between a sentence's terminator and the space after
# it. "**Bold lead-in.** Next sentence." ends a sentence at the "**", not at
# the "." — and a terminator this misses is invisible in BOTH directions: the
# line is never split there, and the lead-in is not recognised as a sentence
# when joining, so a pair of lines already broken correctly gets collapsed.
# Kept in step with the CLOSERS set in the markdown-sembr check, so the two
# agree on where a sentence ends: anything this misses that the check catches
# is residue the reflow leaves behind for someone to fix by hand.
CLOSING_MARKUP = ")]}\"'’”»*_~"

HARD_BREAK = re.compile(r"(  +|\\)$")
BLOCKQUOTE = re.compile(r"^((?:\s*>)+\s?)")
LIST_MARKER = re.compile(r"^(\s*)([-*+]|\d+[.)])(\s+)")
# Leading YAML frontmatter: "---" opening the file, lines of metadata (lazily,
# so the FIRST closing delimiter wins), then "---" or "..." on its own line.
# No capturing groups — the whole match is the region, taken as group(0).
FRONTMATTER = re.compile(
    r"\A(?:[ \t]*\r?\n)*"                    # tolerate blank lines above it
    r"---[ \t]*\r?\n"                        # opening delimiter, exactly three
    r"(?:.*\r?\n)*?"                         # metadata, lazily
    r"(?:---|\.\.\.)[ \t]*(?:\r?\n|\Z)"      # first closing delimiter wins
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
        if not in_code and c in ".?!":
            end = i + 1                                          # past any "**", ")", ...
            while end < n and text[end] in CLOSING_MARKUP:
                end += 1
            if end >= n or text[end] != " ":                     # not a sentence end
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
    # Windows line endings: normalise for the whole pass and restore on the way
    # out. Left in place, the "\r" defeats every end-of-line pattern here — the
    # frontmatter delimiters stop matching, hard breaks stop being detected, and
    # a joined paragraph comes back with its endings stripped, leaving one file
    # holding both kinds. Only done for a uniformly-CRLF file; a mixed one keeps
    # what it has rather than being rewritten wholesale.
    crlf = "\r\n" in src and "\n" not in src.replace("\r\n", "")
    if crlf:
        src = src.replace("\r\n", "\n")
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
    out = frontmatter + "\n".join(lines)
    return (out.replace("\n", "\r\n") if crlf else out), changed, rejected


# --- file selection -----------------------------------------------------------

ALWAYS_IGNORED = (".git", "node_modules")

# markdownlint-cli2 config files that can carry `ignores`, in its own precedence
# order. The `.markdownlint.*` family holds only the `config` object, so there is
# nothing in one of those to read.
MARKDOWNLINT_CONFIGS = (
    ".markdownlint-cli2.jsonc",
    ".markdownlint-cli2.yaml",
    ".markdownlint-cli2.cjs",
    ".markdownlint-cli2.mjs",
)


def strip_jsonc(text):
    """Remove comments and trailing commas so `json` can parse a JSONC file.

    Scanned rather than regexed because a "//" inside a string literal is data,
    not a comment — the rule paths and URLs in a real config are full of them.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == '"':                                        # copy a string whole
            out.append(ch)
            i += 1
            while i < n:
                out.append(text[i])
                if text[i] == "\\":
                    i += 1
                    if i < n:
                        out.append(text[i])
                elif text[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        if text.startswith("//", i):
            i = text.find("\n", i)
            if i == -1:
                break
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        out.append(ch)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))       # trailing commas


def markdownlint_pattern(pattern):
    """Translate one markdownlint-cli2 `ignores` glob into this script's dialect.

    globby reads "**/" as ZERO or more directories, so "**/fixtures/**" covers a
    top-level "fixtures/" as well as a nested one. This script spells "at any
    depth" as a bare name instead (see matches_ignore), and its "**/…" requires
    at least one leading directory — so importing a pattern verbatim would leave
    the top-level copy in scope, rewriting the very files the linter skips.
    Stripping the wildcard prefix and the "everything beneath" suffix makes the
    two agree; the markdown-sembr check translates the same way (ADR-016).
    """
    result = pattern.strip()
    while result.startswith("**/"):
        result = result[3:]
    while result.endswith("/**"):
        result = result[:-3]
    return result.rstrip("/")


def load_markdownlint_ignores(path=None, root="."):
    """Read `ignores` from a markdownlint-cli2 config: (patterns, source, notes).

    `notes` carries what the caller should be told rather than left to infer from
    a surprising set of rewritten files: a config that cannot be read, or a
    pattern whose meaning may not survive translation. A missing config is not a
    note — most repos have none.
    """
    notes = []
    if path is None:
        for candidate in MARKDOWNLINT_CONFIGS:
            if os.path.isfile(os.path.join(root, candidate)):
                path = os.path.join(root, candidate)
                break
        else:
            return [], None, notes
    elif not os.path.isfile(path):
        return [], None, [f"markdownlint config not found: {path}"]

    name = os.path.basename(path)
    if name.endswith((".cjs", ".mjs")):
        return [], path, [
            f"{path} is JavaScript and cannot be read here — "
            "pass its exclusions with --exclude"
        ]
    try:
        text = Path(path).read_text(encoding="utf-8")
        if name.endswith((".yaml", ".yml")):
            try:
                import yaml
            except ImportError:
                return [], path, [
                    f"{path} needs PyYAML to read — install it, switch to "
                    ".markdownlint-cli2.jsonc, or pass --exclude"
                ]
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(strip_jsonc(text))
    except Exception as error:                               # malformed, unreadable
        return [], path, [f"{path} could not be read ({error}) — ignoring it"]

    raw = data.get("ignores") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return [], path, notes

    patterns = []
    for entry in raw:
        if not isinstance(entry, str) or not entry.strip():
            continue
        if entry.lstrip().startswith("!"):                   # a re-inclusion
            notes.append(f"{path}: ignoring negated pattern {entry!r}")
            continue
        translated = markdownlint_pattern(entry)
        if translated:
            if "*" in translated.replace("**", ""):
                notes.append(
                    f"{path}: {entry!r} has a wildcard inside a path segment, "
                    "which may exclude more here than in markdownlint"
                )
            patterns.append(translated)
    return patterns, path, notes


def matches_ignore(path, pattern):
    """fnmatch, with gitignore's anchoring rule and directory shorthand.

    A pattern naming a directory covers everything beneath it. A pattern
    CONTAINING A SLASH is relative to the repo root, while a bare name matches at
    any depth — so "node_modules" catches every one, top-level included, and
    "docs/generated" catches only the top-level one.
    """
    pattern = pattern.rstrip("/")
    candidates = [pattern, pattern + "/*", pattern + "/**"]
    if "/" not in pattern:
        candidates += ["**/" + pattern, "**/" + pattern + "/*"]
    return any(fnmatch(path, candidate) for candidate in candidates)


def expand(pattern):
    """Every Markdown file one command-line path or glob names.

    A directory is taken as everything Markdown beneath it, so "reflow.py docs"
    means what it looks like rather than matching nothing. An absolute pattern
    goes through `glob`, because pathlib refuses one outright.
    """
    if os.path.isdir(pattern):
        pattern = os.path.join(pattern.rstrip("/\\"), "**", "*.md")
    if os.path.isfile(pattern):
        return {os.path.relpath(pattern).replace(os.sep, "/")}
    matches = (
        globlib.glob(pattern, recursive=True)
        if os.path.isabs(pattern)
        else Path(".").glob(pattern)
    )
    return {
        os.path.relpath(m).replace(os.sep, "/") for m in matches if os.path.isfile(m)
    }


def collect_files(patterns, ignores):
    """Sort what the patterns name: (to reflow, ignored, matching nothing).

    The second and third are returned rather than dropped so the caller can say
    which of the paths it was given went nowhere, and why. A path that produces
    no work and no explanation is the failure this whole option set exists to
    remove — it reads as a file the reflow had nothing to do to.

    `pathlib` rather than `glob` so that "**/*.md" reaches documentation under a
    dot directory — ".github/" most of all, which the markdown-sembr check scans
    and a migration must therefore cover. Every hidden directory is then in
    scope, which is why ".git" is ignored unconditionally.

    Pre-canned data — a fixture, a sample input, a recorded response — is out of
    scope for the prose conventions ENTIRELY, not merely exempt from CI, so this
    script has to skip whatever the repo's linter skips. Its `ignores` are read
    for that rather than restated here, which is how the exclusion stays declared
    once: the markdown-sembr check reads the same key (ADR-016), so all three
    cover the same tree and no pair of them can drift apart.
    """
    paths, unmatched = set(), []
    for pattern in patterns:
        found = expand(pattern)
        if not found:
            unmatched.append(pattern)
        paths |= found
    ignores = list(ignores) + list(ALWAYS_IGNORED)
    ignored = {p for p in paths if any(matches_ignore(p, i) for i in ignores)}
    return sorted(paths - ignored), sorted(ignored), unmatched


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="reflow.py",
        description="Reflow Markdown prose to one sentence per source line.",
    )
    parser.add_argument("paths", nargs="*", help="files or globs (default: **/*.md)")
    parser.add_argument("--apply", action="store_true", help="write the changes")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                        help="path to skip, beyond the linter's; repeatable")
    parser.add_argument("--markdownlint-config", metavar="PATH",
                        help="markdownlint-cli2 config to inherit `ignores` from "
                             "(default: whichever one is in the repo root)")
    parser.add_argument("--no-markdownlint-config", dest="markdownlint_config",
                        action="store_const", const=False,
                        help="do not inherit `ignores` from a markdownlint-cli2 config")
    args = parser.parse_args(argv)

    apply_changes = args.apply
    ignores = list(args.exclude)
    if args.markdownlint_config is not False:
        inherited, source, notes = load_markdownlint_ignores(args.markdownlint_config)
        for note in notes:
            print(f"reflow: {note}")
        if inherited:
            print(f"reflow: inheriting {len(inherited)} ignore(s) from {source}")
            ignores += inherited

    files, ignored, unmatched = collect_files(args.paths or ["**/*.md"], ignores)
    # Every way a path can produce no work is said out loud. Skipping an excluded
    # one is right — pre-canned data is out of scope by hand too — but in silence
    # it reads as a file the reflow had nothing to do to, as does a typo.
    named = {os.path.relpath(p).replace(os.sep, "/") for p in args.paths}
    for f in sorted(named & set(ignored)):
        print(f"reflow: skipping {f} — excluded (pass --no-markdownlint-config "
              f"or drop --exclude to reflow it anyway)")
    for pattern in unmatched:
        print(f"reflow: no Markdown files matched {pattern!r}")

    reflowed, unchanged, partial = [], [], []
    shown = 0
    for f in files:
        # newline="" throughout: without it Python's universal-newline handling
        # hands us a CRLF file as LF and writes it back as LF, rewriting every
        # line ending in a file we may not have changed a word of.
        with open(f, encoding="utf-8", newline="") as handle:
            orig = handle.read()
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
            with open(f, "w", encoding="utf-8", newline="") as handle:
                handle.write(new)
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
