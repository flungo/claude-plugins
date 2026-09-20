#!/usr/bin/env python3
"""Unit tests for scripts/transcript-digest.py.

Run from the plugin root: python3 -m unittest discover -s tests
No dependencies beyond the standard library, as the script itself has none.

The suite's central case is the one the digest exists for: turns written before a
compaction boundary still reach the output, because the transcript keeps what the
context window drops.
"""
import importlib.util
import io
import json
import os
import pathlib
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "transcript-digest.py"
_spec = importlib.util.spec_from_file_location("transcript_digest", SCRIPT)
digest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(digest)


def user(text, **extra):
    return {"type": "user", "sessionId": "s", "cwd": "/proj",
            "timestamp": "2026-01-01T00:00:00.000Z",
            "message": {"role": "user", "content": text}, **extra}


def assistant(blocks, **extra):
    return {"type": "assistant", "sessionId": "s",
            "timestamp": "2026-01-01T00:00:01.000Z",
            "message": {"role": "assistant", "content": blocks}, **extra}


def boundary(trigger="auto", pre=123456):
    return {"type": "system", "subtype": "compact_boundary", "sessionId": "s",
            "timestamp": "2026-01-01T00:00:02.000Z",
            "compactMetadata": {"trigger": trigger, "preTokens": pre}}


class DigestTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def transcript(self, rows, name="t.jsonl"):
        path = self.tmp / name
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(row if isinstance(row, str) else json.dumps(row))
                fh.write("\n")
        return path

    def render(self, rows, *flags):
        path = self.transcript(rows)
        args = digest.parse_args(["--transcript", str(path), *flags])
        return digest.render(path, args)


class TestCompaction(DigestTestCase):
    def test_turns_before_a_boundary_survive(self):
        out = self.render([
            user("Add retry to the uploader."),
            assistant([{"type": "text", "text": "We can revisit the jitter later."}]),
            boundary(),
            user("carry on"),
        ])
        # The whole point: the pre-compaction deferral is still here.
        self.assertIn("We can revisit the jitter later.", out)
        self.assertIn("Add retry to the uploader.", out)

    def test_boundary_reports_trigger_and_token_count(self):
        out = self.render([boundary(trigger="manual", pre=98765)])
        self.assertIn("manual", out)
        self.assertIn("98765", out)
        self.assertIn("COMPACTION", out)

    def test_header_counts_boundaries_and_warns(self):
        out = self.render([boundary(), assistant([{"type": "text", "text": "hi"}]), boundary()])
        self.assertIn("Compaction : 2", out)
        self.assertIn("dropped from the", out)

    def test_header_says_none_without_a_boundary(self):
        out = self.render([user("hello")])
        self.assertIn("Compaction : none", out)

    def test_compaction_summary_is_labelled(self):
        out = self.render([user("Summary of the work so far.", isCompactSummary=True)])
        self.assertIn("COMPACTION SUMMARY", out)
        self.assertIn("Summary of the work so far.", out)

    def test_microcompact_boundary_is_recognised(self):
        rows = [{"type": "system", "subtype": "microcompact_boundary", "sessionId": "s",
                 "timestamp": "2026-01-01T00:00:02.000Z"}]
        self.assertIn("COMPACTION", self.render(rows))


class TestConversationFilter(DigestTestCase):
    def test_prompt_and_reply_are_kept(self):
        out = self.render([user("the ask"), assistant([{"type": "text", "text": "the reply"}])])
        self.assertIn("## USER", out)
        self.assertIn("the ask", out)
        self.assertIn("## ASSISTANT", out)
        self.assertIn("the reply", out)

    def test_tool_calls_and_results_are_dropped(self):
        out = self.render([
            assistant([{"type": "tool_use", "name": "Bash", "input": {"command": "ls /secret"}}]),
            user([{"type": "tool_result", "content": "total 0"}], toolUseResult={"stdout": "total 0"}),
        ])
        self.assertNotIn("ls /secret", out)
        self.assertNotIn("total 0", out)

    def test_include_tools_adds_one_line_per_call(self):
        out = self.render(
            [assistant([{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}])],
            "--include-tools",
        )
        self.assertIn("→ Bash", out)
        self.assertIn('"command": "ls"', out)

    def test_thinking_is_excluded_by_default_and_included_on_request(self):
        rows = [assistant([{"type": "thinking", "thinking": "private reasoning"},
                           {"type": "text", "text": "public"}])]
        self.assertNotIn("private reasoning", self.render(rows))
        self.assertIn("private reasoning", self.render(rows, "--include-thinking"))

    def test_system_reminders_are_stripped_by_default(self):
        rows = [user("real words <system-reminder>injected</system-reminder> more")]
        self.assertNotIn("injected", self.render(rows))
        self.assertIn("real words", self.render(rows))
        self.assertIn("injected", self.render(rows, "--keep-reminders"))

    def test_a_turn_that_is_only_a_reminder_disappears(self):
        out = self.render([user("<system-reminder>nothing else</system-reminder>")])
        self.assertNotIn("## USER", out)

    def test_meta_turns_are_excluded_by_default(self):
        rows = [user("<command-name>/compact</command-name>", isMeta=True)]
        self.assertNotIn("command-name", self.render(rows))
        self.assertIn("meta", self.render(rows, "--include-meta"))

    def test_sidechains_are_excluded_by_default_and_labelled_when_included(self):
        rows = [assistant([{"type": "text", "text": "subagent chatter"}], isSidechain=True)]
        out = self.render(rows)
        self.assertNotIn("subagent chatter", out)
        self.assertIn("1 line(s) excluded", out)
        included = self.render(rows, "--include-sidechains")
        self.assertIn("subagent chatter", included)
        self.assertIn("[sidechain]", included)

    def test_api_error_replies_are_flagged(self):
        rows = [assistant([{"type": "text", "text": "overloaded"}], isApiErrorMessage=True)]
        self.assertIn("api error", self.render(rows))

    def test_string_content_and_block_content_both_work(self):
        out = self.render([user("plain string"),
                           user([{"type": "text", "text": "block form"}])])
        self.assertIn("plain string", out)
        self.assertIn("block form", out)


class TestUserIntent(DigestTestCase):
    def test_question_answers_become_a_decision_entry(self):
        rows = [user([{"type": "tool_result", "content": "answered"}],
                     toolUseResult={"questions": [], "answers": {"Ship now?": "Wait for review"}})]
        out = self.render(rows)
        self.assertIn("USER DECISION", out)
        self.assertIn("Ship now?", out)
        self.assertIn("Wait for review", out)

    def test_decisions_can_be_turned_off(self):
        rows = [user([{"type": "tool_result", "content": "answered"}],
                     toolUseResult={"answers": {"Ship now?": "Wait"}})]
        self.assertNotIn("USER DECISION", self.render(rows, "--no-decisions"))

    def test_a_denied_tool_call_surfaces_with_the_users_words(self):
        rows = [user([{"type": "tool_result", "content":
                       "The user doesn't want to take this action right now. "
                       "Feedback: don't touch prod, park it."}])]
        out = self.render(rows)
        self.assertIn("USER INTERVENTION", out)
        self.assertIn("park it", out)

    def test_an_interrupted_call_surfaces(self):
        rows = [user([{"type": "tool_result", "content": "[Request interrupted by user]"}])]
        self.assertIn("USER INTERVENTION", self.render(rows))

    def test_an_ordinary_tool_result_is_not_an_intervention(self):
        rows = [user([{"type": "tool_result", "content": "build succeeded"}])]
        out = self.render(rows)
        self.assertNotIn("USER INTERVENTION", out)
        self.assertNotIn("build succeeded", out)


class TestHeaderAndRobustness(DigestTestCase):
    def test_header_carries_session_project_and_census(self):
        out = self.render([user("hi")])
        self.assertIn("Session    : s", out)
        self.assertIn("Project    : /proj", out)
        self.assertIn("user: 1", out)

    def test_malformed_lines_are_counted_not_fatal(self):
        out = self.render([user("before"), "{ not json", user("after")])
        self.assertIn("Unreadable : 1 line(s) skipped", out)
        self.assertIn("before", out)
        self.assertIn("after", out)

    def test_blank_lines_are_ignored(self):
        path = self.transcript([user("kept")])
        path.write_text(path.read_text() + "\n\n", encoding="utf-8")
        args = digest.parse_args(["--transcript", str(path)])
        self.assertIn("kept", digest.render(path, args))

    def test_stats_prints_the_header_without_bodies(self):
        out = self.render([user("body text here")], "--stats")
        self.assertIn("# Session transcript digest", out)
        self.assertNotIn("body text here", out)

    def test_max_chars_clips_a_long_body(self):
        out = self.render([user("x" * 500)], "--max-chars", "50")
        self.assertIn("clipped, 450 more characters", out)

    def test_max_chars_zero_keeps_the_whole_body(self):
        out = self.render([user("y" * 300)])
        self.assertIn("y" * 300, out)


class TestHelpers(unittest.TestCase):
    def test_slug_replaces_every_non_alphanumeric(self):
        self.assertEqual(digest.slug("/home/user/claude-plugins"), "-home-user-claude-plugins")
        self.assertEqual(digest.slug("/a/b.c_d"), "-a-b-c-d")

    def test_text_of_ignores_non_text_blocks(self):
        content = [{"type": "text", "text": "keep"},
                   {"type": "tool_use", "name": "X", "input": {}},
                   {"type": "image", "source": {}}]
        self.assertEqual(digest.text_of(content), "keep")

    def test_text_of_handles_a_plain_string(self):
        self.assertEqual(digest.text_of("plain"), "plain")

    def test_tool_lines_clips_long_input(self):
        content = [{"type": "tool_use", "name": "Bash", "input": {"command": "z" * 400}}]
        line = digest.tool_lines(content)[0]
        self.assertTrue(line.endswith("…"))
        self.assertLess(len(line), 400)

    def test_clip_is_a_no_op_at_zero(self):
        self.assertEqual(digest.clip("abc", 0), "abc")

    def test_tool_result_text_reads_string_and_block_forms(self):
        self.assertEqual(digest.tool_result_text([{"type": "tool_result", "content": "s"}]), "s")
        nested = [{"type": "tool_result", "content": [{"type": "text", "text": "n"}]}]
        self.assertEqual(digest.tool_result_text(nested), "n")


class TestResolution(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def make(self, dirname, stem, mtime=None):
        d = self.root / dirname
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{stem}.jsonl"
        f.write_text("{}\n", encoding="utf-8")
        if mtime:
            os.utime(f, (mtime, mtime))
        return f

    def test_prefers_the_directory_matching_the_working_directory(self):
        self.make("-a-b", "wanted")
        self.make("-somewhere-else", "other")
        found = digest.candidates(self.root, "/a/b", None)
        self.assertEqual([f.stem for f in found], ["wanted"])

    def test_falls_back_to_an_ancestor_of_the_working_directory(self):
        self.make("-a-b", "wanted")
        found = digest.candidates(self.root, "/a/b/c/d", None)
        self.assertEqual([f.stem for f in found], ["wanted"])

    def test_orders_by_most_recently_written(self):
        self.make("-a-b", "old", mtime=1_000_000)
        self.make("-a-b", "new", mtime=2_000_000)
        found = digest.candidates(self.root, "/a/b", None)
        self.assertEqual([f.stem for f in found], ["new", "old"])

    def test_session_id_selects_across_directories(self):
        self.make("-x", "target")
        self.make("-y", "decoy")
        found = digest.candidates(self.root, "/unrelated", "target")
        self.assertEqual([f.stem for f in found], ["target"])

    def test_falls_back_to_every_directory_when_none_matches(self):
        self.make("-nothing-like-it", "only")
        found = digest.candidates(self.root, "/a/b", None)
        self.assertEqual([f.stem for f in found], ["only"])

    def test_a_missing_root_yields_nothing(self):
        self.assertEqual(digest.candidates(self.root / "absent", "/a/b", None), [])


class TestMain(DigestTestCase):
    def test_missing_transcript_reports_and_exits_nonzero(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = digest.main(["--transcript", str(self.tmp / "absent.jsonl")])
        self.assertEqual(code, 1)
        self.assertIn("claude.ai chat session", err.getvalue())

    def test_output_writes_the_digest_to_a_file(self):
        path = self.transcript([user("written out")])
        target = self.tmp / "digest.md"
        with redirect_stderr(io.StringIO()):
            code = digest.main(["--transcript", str(path), "--output", str(target)])
        self.assertEqual(code, 0)
        self.assertIn("written out", target.read_text(encoding="utf-8"))

    def test_stdout_carries_the_digest_by_default(self):
        path = self.transcript([user("to stdout")])
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(digest.main(["--transcript", str(path)]), 0)
        self.assertIn("to stdout", out.getvalue())

    def test_list_prints_each_candidate(self):
        path = self.transcript([user("x")])
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(digest.main(["--transcript", str(path), "--list"]), 0)
        self.assertIn(str(path), out.getvalue())


if __name__ == "__main__":
    unittest.main()
