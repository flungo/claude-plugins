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
        # The script's core promise, asserted on every case rather than by eye.
        self.assertEqual(
            reflow.norm_html(src), reflow.norm_html(out),
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


class TestIdempotence(ReflowTestCase):
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
