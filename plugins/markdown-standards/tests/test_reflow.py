#!/usr/bin/env python3
"""Unit tests for scripts/reflow.py.

Run from the plugin root: python3 -m unittest discover -s tests
Requires markdown-it-py (the script's only dependency).

Every assertion here is about *source* shape; the script's own guarantee is that
rendered output never changes, which the `reflowed` helper asserts on every case.
"""
import importlib.util
import pathlib
import unittest

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


if __name__ == "__main__":
    unittest.main()
