#!/usr/bin/env python3
"""Unit tests for scripts/reflow.py.

Run from the plugin root: python3 -m unittest discover -s tests
Requires markdown-it-py (the script's only dependency).

Every assertion here is about *source* shape; the script's own guarantee is that
rendered output never changes, which the `reflowed` helper asserts on every case.
"""
import builtins
import contextlib
import importlib.util
import io
import os
import pathlib
import sys
import tempfile
import types
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "reflow.py"
_spec = importlib.util.spec_from_file_location("reflow", SCRIPT)
reflow = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reflow)


class ReflowTestCase(unittest.TestCase):
    def reflowed(self, src):
        out, changed, rejected = reflow.reflow_text(src)
        # The script's two core promises, asserted on every case rather than by eye.
        self.assertEqual(
            reflow.split_frontmatter(src)[0], reflow.split_frontmatter(out)[0],
            "frontmatter must survive byte-identically",
        )
        self.assertEqual(
            reflow.body_html(src), reflow.body_html(out),
            "rendered HTML changed — the render gate should have prevented this",
        )
        return out, changed, rejected


class TestTopLevelParagraphs(ReflowTestCase):
    def test_splits_two_sentences_onto_two_lines(self):
        out, changed, _ = self.reflowed("One sentence. Two sentences.\n")
        self.assertEqual(out, "One sentence.\nTwo sentences.\n")
        self.assertEqual(changed, 1)

    def test_joins_a_hard_wrapped_single_sentence(self):
        out, _, _ = self.reflowed("A single sentence that was\nhard wrapped here.\n")
        self.assertEqual(out, "A single sentence that was hard wrapped here.\n")

    def test_already_compliant_is_untouched(self):
        src = "One.\nTwo.\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)


class TestListItems(ReflowTestCase):
    def test_dash_item_continuation_aligns_to_content_column(self):
        out, _, _ = self.reflowed("- First here. Second here.\n")
        self.assertEqual(out, "- First here.\n  Second here.\n")

    def test_ordered_marker_width_is_respected(self):
        out, _, _ = self.reflowed("1. First here. Second here.\n")
        self.assertEqual(out, "1. First here.\n   Second here.\n")

    def test_wide_ordered_marker(self):
        out, _, _ = self.reflowed("10. First here. Second here.\n")
        self.assertEqual(out, "10. First here.\n    Second here.\n")

    def test_nested_item_keeps_its_indent(self):
        out, _, _ = self.reflowed("- Outer text.\n  - Inner one. Inner two.\n")
        self.assertEqual(out, "- Outer text.\n  - Inner one.\n    Inner two.\n")

    def test_rewraps_an_already_wrapped_item(self):
        out, _, _ = self.reflowed("- First here.\n  Second here. Third here.\n")
        self.assertEqual(out, "- First here.\n  Second here.\n  Third here.\n")


class TestBlockquotes(ReflowTestCase):
    def test_carries_the_marker(self):
        out, _, _ = self.reflowed("> First here. Second here.\n")
        self.assertEqual(out, "> First here.\n> Second here.\n")

    def test_nested_blockquote(self):
        out, _, _ = self.reflowed("> > First here. Second here.\n")
        self.assertEqual(out, "> > First here.\n> > Second here.\n")

    def test_callout_style_blockquote(self):
        out, _, _ = self.reflowed("> **Note:** first here. Second here.\n")
        self.assertEqual(out, "> **Note:** first here.\n> Second here.\n")


class TestLeftAlone(ReflowTestCase):
    def test_hard_break_block_is_preserved(self):
        src = "**Date:** 2026-01-01  \n**Status:** Accepted. Still accepted.\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_heading_is_not_a_paragraph(self):
        src = "# One. Two.\n\nBody.\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_table_rows_untouched(self):
        src = "| A | B |\n|---|---|\n| One. Two. | Three. Four. |\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_fenced_code_untouched(self):
        src = "```python\nx = 1  # One. Two.\n```\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)


class TestSentenceSplitting(ReflowTestCase):
    def test_abbreviations_do_not_split(self):
        for abbr in ("e.g.", "i.e.", "etc.", "vs.", "Dr."):
            with self.subTest(abbr=abbr):
                self.assertEqual(
                    reflow.split_sentences(f"Text {abbr} more text here."),
                    [f"Text {abbr} more text here."],
                )

    def test_inline_code_containing_sentence_end_does_not_split(self):
        self.assertEqual(
            reflow.split_sentences("Use `a. b` inline here."),
            ["Use `a. b` inline here."],
        )

    def test_ellipsis_does_not_split(self):
        self.assertEqual(
            reflow.split_sentences("Wait... then continue here."),
            ["Wait... then continue here."],
        )

    def test_sentence_ending_inside_markup_is_a_sentence_end(self):
        """The terminator sits before the closing "**", not after it.

        Missing this is invisible in both directions — see the round-trip case
        in TestIdempotence.
        """
        for text, expected in (
            ("**Bold lead-in.** Next one.", ["**Bold lead-in.**", "Next one."]),
            ("*Emphasis.* Next one.", ["*Emphasis.*", "Next one."]),
            ('He said "stop." Then left.', ['He said "stop."', "Then left."]),
            ("A point (parenthesised.) Next one.", ["A point (parenthesised.)", "Next one."]),
            ("_Underscored.__ Next one.", ["_Underscored.__", "Next one."]),
            ("He said “stop.” Then left.", ["He said “stop.”", "Then left."]),
            ("Il dit «arrête.» Puis partit.", ["Il dit «arrête.»", "Puis partit."]),
        ):
            with self.subTest(text=text):
                self.assertEqual(reflow.split_sentences(text), expected)

    def test_markup_run_at_end_of_text_is_not_a_split(self):
        self.assertEqual(reflow.split_sentences("**Only one.**"), ["**Only one.**"])

    def test_abbreviation_guard_still_applies_before_markup(self):
        self.assertEqual(
            reflow.split_sentences("Tools e.g. *make* and more here."),
            ["Tools e.g. *make* and more here."],
        )

    def test_question_and_exclamation_split(self):
        self.assertEqual(
            reflow.split_sentences("Really? Yes! Fine."),
            ["Really?", "Yes!", "Fine."],
        )


class TestRenderGate(ReflowTestCase):
    def test_gate_rejects_a_change_that_would_alter_rendering(self):
        """Split onto its own line, "# ..." becomes an ATX heading.

        An ATX heading may interrupt a paragraph, so the render would change —
        the gate must reject it and leave the paragraph exactly as found,
        without leaving any of the candidate behind.
        """
        src = "Some text here. # Looks like a heading\n"
        out, changed, rejected = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual((changed, rejected), (0, 1))

    def test_blockquote_marker_would_also_interrupt(self):
        src = "Some text here. > looks like a quote\n"
        out, changed, rejected = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual((changed, rejected), (0, 1))

    def test_empty_ordered_marker_is_safe_to_split(self):
        """A bare "1." cannot interrupt a paragraph, so this one is accepted.

        Guards the gate against being needlessly conservative: CommonMark only
        lets an ordered list interrupt a paragraph when it starts at 1 *and* is
        non-empty, so the split here is render-neutral.
        """
        out, changed, rejected = self.reflowed("See step one. 1. is the first item.\n")
        self.assertEqual(out, "See step one.\n1.\nis the first item.\n")
        self.assertEqual((changed, rejected), (1, 0))

    def test_one_rejected_block_does_not_forfeit_the_rest_of_the_file(self):
        """Per-block gating: the good paragraph still reflows."""
        src = "Some text here. # Looks like a heading\n\nGood one. Good two.\n"
        out, changed, rejected = self.reflowed(src)
        self.assertEqual(
            out,
            "Some text here. # Looks like a heading\n"   # rejected, byte-identical
            "\n"
            "Good one.\nGood two.\n",                    # accepted
        )
        self.assertEqual((changed, rejected), (1, 1))


class TestFrontmatter(ReflowTestCase):
    """Frontmatter is metadata, not prose, and must come back byte-identical.

    The regression these guard is silent: a CommonMark parser sees the block as
    an ordinary paragraph, so the render gate is satisfied by a rewrite that has
    destroyed the YAML.
    """

    def test_sequence_valued_frontmatter_is_not_joined(self):
        """The closing "---" only ends a *setext heading* when a paragraph runs
        straight into it. Give a key a sequence value and it no longer does, so
        the keys above it become a plain paragraph — and joining them onto one
        line turns two keys into one unparseable string.
        """
        src = (
            "---\n"
            "name: my-command\n"
            "allowed-tools:\n"
            "  - Bash\n"
            "---\n"
            "\n"
            "Body one. Body two.\n"
        )
        out, _, _ = self.reflowed(src)
        self.assertEqual(
            out,
            "---\n"
            "name: my-command\n"
            "allowed-tools:\n"
            "  - Bash\n"
            "---\n"
            "\n"
            "Body one.\nBody two.\n",                    # only the body moved
        )

    def test_sentence_valued_key_is_not_split_across_lines(self):
        src = (
            "---\n"
            "description: A skill. It does things.\n"
            "tags:\n"
            "  - one\n"
            "---\n"
        )
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_setext_style_frontmatter_is_untouched(self):
        """Frontmatter whose last line runs into "---" parses as a heading.

        It survived by accident before frontmatter was split off; assert it now
        survives on purpose.
        """
        src = "---\nname: foo\ndescription: One. Two.\n---\n\nBody.\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_empty_frontmatter(self):
        out, _, _ = self.reflowed("---\n---\n\nBody one. Body two.\n")
        self.assertEqual(out, "---\n---\n\nBody one.\nBody two.\n")

    def test_dot_terminated_frontmatter(self):
        out, _, _ = self.reflowed("---\ntitle: T\n...\n\nBody one. Body two.\n")
        self.assertEqual(out, "---\ntitle: T\n...\n\nBody one.\nBody two.\n")

    def test_body_immediately_after_the_delimiter_still_reflows(self):
        out, changed, _ = self.reflowed("---\ntags:\n  - a\n---\nBody one. Body two.\n")
        self.assertEqual(out, "---\ntags:\n  - a\n---\nBody one.\nBody two.\n")
        self.assertEqual(changed, 1)

    def test_blank_lines_above_the_delimiter_still_count(self):
        """A stray leading newline stops Jekyll seeing frontmatter at all.

        It must not stop *this* from seeing it: the file is already broken, and
        joining its keys would make that irreversible rather than a one-line fix.
        """
        src = "\n---\nname: x\ntags:\n  - a\n---\n\nOne. Two.\n"
        out, _, _ = self.reflowed(src)
        self.assertEqual(out, "\n---\nname: x\ntags:\n  - a\n---\n\nOne.\nTwo.\n")

    def test_crlf_frontmatter_is_recognised_and_endings_are_preserved(self):
        """A "\\r" left in place defeats every end-of-line pattern in the script.

        The delimiters stop matching, so the keys reflow; and the joined lines
        come back stripped of their "\\r", leaving one file holding both kinds.
        """
        src = "---\r\nname: x\r\ntags:\r\n  - a\r\n---\r\n\r\nOne. Two.\r\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, "---\r\nname: x\r\ntags:\r\n  - a\r\n---\r\n\r\nOne.\r\nTwo.\r\n")
        self.assertEqual(changed, 1)

    def test_crlf_body_without_frontmatter_keeps_its_endings(self):
        out, _, _ = self.reflowed("One. Two.\r\n\r\n- Item one. Item two.\r\n")
        self.assertEqual(out, "One.\r\nTwo.\r\n\r\n- Item one.\r\n  Item two.\r\n")


class TestFrontmatterVersusThematicBreaks(ReflowTestCase):
    """Only a closed "---" opening the file is frontmatter; everything else is a
    thematic break (or a setext underline) and belongs to the parser."""

    def test_unterminated_delimiter_is_a_thematic_break_not_frontmatter(self):
        out, _, _ = self.reflowed("---\n\nBody one. Body two.\n")
        self.assertEqual(out, "---\n\nBody one.\nBody two.\n")
        self.assertEqual(reflow.split_frontmatter("---\n\nBody one.\n"), ("", "---\n\nBody one.\n"))

    def test_thematic_break_below_the_first_line_is_not_frontmatter(self):
        src = "Intro one. Intro two.\n\n---\n\nkey: value\n\n---\n"
        out, _, _ = self.reflowed(src)
        self.assertEqual(out, "Intro one.\nIntro two.\n\n---\n\nkey: value\n\n---\n")

    def test_setext_underline_at_the_top_is_not_frontmatter(self):
        out, _, _ = self.reflowed("Title\n---\n\nBody one. Body two.\n")
        self.assertEqual(out, "Title\n---\n\nBody one.\nBody two.\n")

    def test_other_thematic_break_spellings_never_open_frontmatter(self):
        for rule in ("----", "- - -", "***", "___", "  ---"):
            with self.subTest(rule=rule):
                self.assertEqual(
                    reflow.split_frontmatter(f"{rule}\nname: x\n{rule}\n")[0], "",
                )

    def test_the_first_closing_delimiter_wins(self):
        """The metadata quantifier is lazy, so a "---" in the body cannot be
        mistaken for the close and swallow the prose between the two."""
        src = "---\ntags:\n  - a\n---\n\nOne. Two.\n\n---\n\nThree. Four.\n"
        out, changed, _ = self.reflowed(src)
        self.assertEqual(reflow.split_frontmatter(src)[0], "---\ntags:\n  - a\n---\n")
        self.assertEqual(out, "---\ntags:\n  - a\n---\n\nOne.\nTwo.\n\n---\n\nThree.\nFour.\n")
        self.assertEqual(changed, 2)   # both body paragraphs, neither delimiter

    def test_a_dashed_value_is_not_mistaken_for_a_delimiter(self):
        src = "---\nsummary: a --- b\ntags:\n  - a\n---\n\nOne. Two.\n"
        self.assertEqual(reflow.split_frontmatter(src)[0], "---\nsummary: a --- b\ntags:\n  - a\n---\n")

    def test_trailing_whitespace_on_a_delimiter_is_tolerated(self):
        src = "---  \nname: x\ntags:\n  - a\n---\t\n\nOne. Two.\n"
        self.assertEqual(reflow.split_frontmatter(src)[0], "---  \nname: x\ntags:\n  - a\n---\t\n")

    def test_a_document_opening_with_a_thematic_break_reads_as_frontmatter(self):
        """The one case position cannot settle — pinned as a decision, not an
        accident. Every frontmatter reader resolves it the same way, and the
        cost is a skipped reflow rather than destroyed YAML.
        """
        src = "---\n\nSome text. More text.\n\n---\n\nTail one. Tail two.\n"
        out, _, _ = self.reflowed(src)
        self.assertEqual(
            out,
            "---\n\nSome text. More text.\n\n---\n"   # read as frontmatter, skipped
            "\nTail one.\nTail two.\n",               # the body below it reflows
        )

    def test_no_capturing_groups_so_the_whole_match_is_the_region(self):
        m = reflow.FRONTMATTER.match("---\nname: x\ntags:\n  - a\n---\nBody.\n")
        self.assertEqual(m.re.groups, 0)
        self.assertEqual(m.group(0), "---\nname: x\ntags:\n  - a\n---\n")


class TestIdempotence(ReflowTestCase):
    def test_a_correctly_broken_bold_lead_in_is_not_collapsed(self):
        """The regression that made the reflow actively harmful.

        Blind to the terminator inside "**", it read the pair as one sentence
        hard-wrapped over two lines and joined them — undoing a break that was
        already right, on a repo already following the convention.
        """
        src = (
            "**Only when a rule fires on content that was already there.**\n"
            "That is the signature of a rule nobody chose.\n"
        )
        out, changed, _ = self.reflowed(src)
        self.assertEqual(out, src)
        self.assertEqual(changed, 0)

    def test_a_bold_lead_in_sharing_a_line_is_split(self):
        out, _, _ = self.reflowed("**Bold lead-in.** Next sentence.\n")
        self.assertEqual(out, "**Bold lead-in.**\nNext sentence.\n")

    def test_second_pass_is_a_no_op(self):
        src = (
            "Top one. Top two.\n\n"
            "- Item one. Item two.\n\n"
            "> Quote one. Quote two.\n"
        )
        once, _, _ = self.reflowed(src)
        twice, changed, _ = self.reflowed(once)
        self.assertEqual(once, twice)
        self.assertEqual(changed, 0)


@contextlib.contextmanager
def temp_repo(files):
    """A throwaway repo root, `files` mapping relative path to content.

    The script reports what it inherits and what it skips on stdout, which is
    the point of it — captured here so a test run stays readable.
    """
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as root:
        for name, content in files.items():
            path = pathlib.Path(root) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        os.chdir(root)
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                yield out
        finally:
            os.chdir(cwd)


class TestMarkdownlintPattern(unittest.TestCase):
    """globby's dialect translated into this script's — see ADR-016."""

    def test_zero_or_more_directories_becomes_a_bare_name(self):
        # The load-bearing case: taken verbatim, "**/" would need at least one
        # leading directory here and leave a top-level fixtures/ being rewritten.
        self.assertEqual(reflow.markdownlint_pattern("**/fixtures/**"), "fixtures")

    def test_each_affix_is_optional(self):
        self.assertEqual(reflow.markdownlint_pattern("fixtures/**"), "fixtures")
        self.assertEqual(reflow.markdownlint_pattern("**/fixtures"), "fixtures")
        self.assertEqual(reflow.markdownlint_pattern("fixtures/"), "fixtures")
        self.assertEqual(reflow.markdownlint_pattern("vendor"), "vendor")

    def test_an_anchored_path_keeps_its_directories(self):
        self.assertEqual(
            reflow.markdownlint_pattern("docs/generated/**"), "docs/generated"
        )


class TestStripJsonc(unittest.TestCase):
    def test_line_and_block_comments_go(self):
        self.assertEqual(
            reflow.strip_jsonc('{ // why\n"a": 1, /* and */ "b": 2 }'),
            '{ \n"a": 1,  "b": 2 }',
        )

    def test_a_double_slash_inside_a_string_is_data(self):
        """The reason this is scanned rather than regexed — a real config is
        full of URLs, and truncating one silently loses the key after it."""
        text = '{ "ignores": ["https://example.com/x"], "b": 1 }'
        self.assertEqual(reflow.strip_jsonc(text), text)

    def test_trailing_commas_are_removed(self):
        self.assertEqual(reflow.strip_jsonc('{ "a": [1, 2, ], }'), '{ "a": [1, 2 ] }')


class TestLoadMarkdownlintIgnores(unittest.TestCase):
    def test_reads_ignores_through_the_comments(self):
        with temp_repo({".markdownlint-cli2.jsonc": (
            '{\n  // fixtures are reproduced verbatim\n'
            '  "ignores": ["**/fixtures/**", "vendor/**"],\n}\n'
        )}):
            patterns, source, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, ["fixtures", "vendor"])
        self.assertTrue(source.endswith(".markdownlint-cli2.jsonc"))
        self.assertEqual(notes, [])

    def test_no_config_is_silent(self):
        """Most repos have none; saying so every run would be noise."""
        with temp_repo({"README.md": "x\n"}):
            self.assertEqual(reflow.load_markdownlint_ignores(), ([], None, []))

    def test_a_config_named_but_absent_is_reported(self):
        with temp_repo({"README.md": "x\n"}):
            patterns, _, notes = reflow.load_markdownlint_ignores("nope.jsonc")
        self.assertEqual(patterns, [])
        self.assertIn("not found", notes[0])

    def test_a_javascript_config_is_reported_rather_than_passed_over(self):
        with temp_repo({".markdownlint-cli2.cjs": "module.exports = {}\n"}):
            patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, [])
        self.assertIn("--exclude", notes[0])

    def test_a_malformed_config_is_reported_rather_than_read_as_empty(self):
        with temp_repo({".markdownlint-cli2.jsonc": "{ not json at all\n"}):
            patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, [])
        self.assertIn("could not be read", notes[0])

    def test_a_negated_pattern_is_skipped_and_flagged(self):
        with temp_repo({".markdownlint-cli2.jsonc":
                        '{"ignores": ["fixtures/**", "!fixtures/README.md"]}'}):
            patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, ["fixtures"])
        self.assertIn("negated", notes[0])

    def test_a_wildcard_inside_a_segment_is_applied_but_flagged(self):
        with temp_repo({".markdownlint-cli2.jsonc":
                        '{"ignores": ["plugins/*/evals/**"]}'}):
            patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, ["plugins/*/evals"])
        self.assertIn("wildcard", notes[0])


class TestYamlConfig(unittest.TestCase):
    """The two PyYAML scenarios, both mocked — the result must not depend on
    what happens to be installed where the tests run."""

    CONFIG = {".markdownlint-cli2.yaml": "ignores:\n  - '**/fixtures/**'\n"}

    def test_yaml_config_is_read_when_pyyaml_is_available(self):
        fake = types.ModuleType("yaml")
        fake.safe_load = lambda text: {"ignores": ["**/fixtures/**"]}
        with temp_repo(self.CONFIG), mock.patch.dict(sys.modules, {"yaml": fake}):
            patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, ["fixtures"])
        self.assertEqual(notes, [])

    def test_missing_pyyaml_says_so_rather_than_reading_the_config_as_empty(self):
        real_import = builtins.__import__

        def no_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("no module named yaml")
            return real_import(name, *args, **kwargs)

        with temp_repo(self.CONFIG), mock.patch.dict(sys.modules, {}, clear=False):
            sys.modules.pop("yaml", None)
            with mock.patch.object(builtins, "__import__", no_yaml):
                patterns, _, notes = reflow.load_markdownlint_ignores()
        self.assertEqual(patterns, [])
        self.assertIn("PyYAML", notes[0])


class TestMatchesIgnore(unittest.TestCase):
    def test_a_bare_name_matches_at_every_depth_including_the_top(self):
        self.assertTrue(reflow.matches_ignore("node_modules/a/R.md", "node_modules"))
        self.assertTrue(reflow.matches_ignore("x/node_modules/a/R.md", "node_modules"))

    def test_a_pattern_with_a_slash_is_anchored_to_the_repo_root(self):
        self.assertTrue(reflow.matches_ignore("docs/generated/a.md", "docs/generated"))
        self.assertFalse(reflow.matches_ignore("x/docs/generated/a.md", "docs/generated"))

    def test_an_unrelated_path_is_not_matched(self):
        self.assertFalse(reflow.matches_ignore("docs/a.md", "fixtures"))


class TestCollectFiles(unittest.TestCase):
    def test_a_top_level_node_modules_is_excluded(self):
        """The substring test this replaces ("/node_modules/" not in path) missed
        a top-level one — the usual case when running from a repo root."""
        with temp_repo({"node_modules/pkg/README.md": "x\n", "README.md": "x\n"}):
            files, _, _ = reflow.collect_files(["**/*.md"], [])
        self.assertEqual(files, ["README.md"])

    def test_dot_directories_are_reached(self):
        """The markdown-sembr check scans them, so a migration has to as well."""
        with temp_repo({".github/CONTRIBUTING.md": "x\n", "README.md": "x\n"}):
            files, _, _ = reflow.collect_files(["**/*.md"], [])
        self.assertEqual(files, [".github/CONTRIBUTING.md", "README.md"])

    def test_git_is_always_ignored(self):
        with temp_repo({".git/COMMIT_EDITMSG.md": "x\n", "README.md": "x\n"}):
            files, _, _ = reflow.collect_files(["**/*.md"], [])
        self.assertEqual(files, ["README.md"])

    def test_an_explicit_path_needs_no_glob(self):
        with temp_repo({"docs/a.md": "x\n", "docs/b.md": "x\n"}):
            files, _, _ = reflow.collect_files(["docs/a.md"], [])
        self.assertEqual(files, ["docs/a.md"])

    def test_an_excluded_path_comes_back_as_skipped_rather_than_vanishing(self):
        with temp_repo({"fixtures/a.md": "x\n", "README.md": "x\n"}):
            files, skipped, _ = reflow.collect_files(["**/*.md"], ["fixtures"])
        self.assertEqual(files, ["README.md"])
        self.assertEqual(skipped, ["fixtures/a.md"])

    def test_a_directory_means_the_markdown_beneath_it(self):
        """"reflow.py docs" has to mean what it looks like; matching nothing is
        the silent no-op the reporting elsewhere exists to prevent."""
        with temp_repo({"docs/a.md": "x\n", "docs/sub/b.md": "x\n", "top.md": "x\n"}):
            for named in ("docs", "docs/"):
                with self.subTest(named=named):
                    files, _, unmatched = reflow.collect_files([named], [])
                    self.assertEqual(files, ["docs/a.md", "docs/sub/b.md"])
                    self.assertEqual(unmatched, [])

    def test_an_absolute_glob_is_expanded_rather_than_refused(self):
        """pathlib raises NotImplementedError on a non-relative pattern, so an
        absolute one goes through `glob` instead."""
        with temp_repo({"docs/a.md": "x\n"}) as _:
            root = os.getcwd()
            files, _, unmatched = reflow.collect_files([f"{root}/docs/*.md"], [])
        self.assertEqual(files, ["docs/a.md"])
        self.assertEqual(unmatched, [])

    def test_a_path_matching_nothing_is_reported_not_swallowed(self):
        with temp_repo({"README.md": "x\n"}):
            files, _, unmatched = reflow.collect_files(["docs/nope.md"], [])
        self.assertEqual(files, [])
        self.assertEqual(unmatched, ["docs/nope.md"])


class TestEndToEndFileSelection(unittest.TestCase):
    """What the reported defect was: a repo-wide pass rewriting the fixtures its
    own linter config excludes."""

    REPO = {
        ".markdownlint-cli2.jsonc": '{\n  "ignores": ["**/fixtures/**"]\n}\n',
        "fixtures/recorded.md": "One. Two.\n",
        "docs/guide.md": "One. Two.\n",
    }

    def test_a_repo_wide_apply_leaves_the_linters_exclusions_alone(self):
        with temp_repo(self.REPO):
            reflow.main(["--apply"])
            self.assertEqual(
                pathlib.Path("fixtures/recorded.md").read_text(), "One. Two.\n"
            )
            self.assertEqual(
                pathlib.Path("docs/guide.md").read_text(), "One.\nTwo.\n"
            )

    def test_opting_out_of_the_config_reaches_them_again(self):
        with temp_repo(self.REPO):
            reflow.main(["--apply", "--no-markdownlint-config"])
            self.assertEqual(
                pathlib.Path("fixtures/recorded.md").read_text(), "One.\nTwo.\n"
            )

    def test_a_named_path_is_the_only_one_touched(self):
        with temp_repo(self.REPO):
            reflow.main(["--apply", "docs/guide.md"])
            self.assertEqual(pathlib.Path("docs/guide.md").read_text(), "One.\nTwo.\n")

    def test_dry_run_is_the_default(self):
        with temp_repo(self.REPO):
            reflow.main([])
            self.assertEqual(pathlib.Path("docs/guide.md").read_text(), "One. Two.\n")

    def test_naming_a_path_that_matches_nothing_says_so(self):
        """A typo'd path and an excluded one fail the same way to a reader —
        nothing happened — so neither may be silent."""
        with temp_repo(self.REPO) as out:
            reflow.main(["--apply", "docs/guied.md"])
        self.assertIn("no Markdown files matched 'docs/guied.md'", out.getvalue())

    def test_naming_an_excluded_path_says_why_nothing_happened(self):
        """Skipping it is right; skipping it silently would look like a no-op
        file, and the next move would be to hunt for a bug in the reflow."""
        with temp_repo(self.REPO) as out:
            reflow.main(["--apply", "fixtures/recorded.md"])
            self.assertEqual(
                pathlib.Path("fixtures/recorded.md").read_text(), "One. Two.\n"
            )
        self.assertIn("skipping fixtures/recorded.md", out.getvalue())


if __name__ == "__main__":
    unittest.main()
