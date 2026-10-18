#!/usr/bin/env python3
"""Unit tests for scripts/synced-dependencies.py.

Run from the plugin root: python3 -m unittest discover -s tests
No dependencies beyond the standard library.

The script is a SessionStart hook, so it fails silently in production: stdout
that will not parse surfaces nothing, and a wrong copy of a re-synced plugin
reports a gap that is not there or misses one that is. These cases build synced
folders shaped like the ones Claude Code writes and pin what the hook reports
for each, that a resumed session is told about a gap once rather than on every
container restart, plus the command hooks.json registers and the seconds it
allows.
"""
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = PLUGIN / "scripts" / "synced-dependencies.py"
HOOKS = PLUGIN / "hooks" / "hooks.json"


def registered_hook():
    registered = json.loads(HOOKS.read_text(encoding="utf-8"))
    return registered["hooks"]["SessionStart"][0]["hooks"][0]


def write_plugin(bucket, directory, name, dependencies=()):
    manifest = bucket / directory / ".claude-plugin"
    manifest.mkdir(parents=True)
    (manifest / "plugin.json").write_text(
        json.dumps({"name": name, "version": "1.0.0", "dependencies": list(dependencies)}),
        encoding="utf-8",
    )


def write_manifest(bucket, entries, stale=()):
    (bucket / "manifest.json").write_text(
        json.dumps({"lastUpdated": 0, "plugins": entries, "staleDirs": list(stale)}),
        encoding="utf-8",
    )


class SyncedFolderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / "synced"
        self.bucket = self.root / "org_account"
        self.bucket.mkdir(parents=True)
        (self.root / ".bucket-org_account").touch()

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, root=None, session=None, data=None):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
        if data:
            env["CLAUDE_PLUGIN_DATA"] = str(data)
        proc = subprocess.run(
            [str(SCRIPT), str(root or self.root)], capture_output=True, text=True,
            encoding="utf-8", timeout=registered_hook().get("timeout", 60), env=env,
            input=json.dumps({"session_id": session, "source": "resume"}) if session else "",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def report(self, root=None, **hook):
        stdout = self.run_hook(root, **hook)
        self.assertTrue(stdout.strip(), "expected a report, got no output")
        return json.loads(stdout)


class SilentTestCase(SyncedFolderTestCase):
    """Nothing to report prints nothing, so a session pays nothing for it."""

    def test_no_synced_folder(self):
        self.assertEqual(self.run_hook(self.root / "absent"), "")

    def test_empty_bucket(self):
        self.assertEqual(self.run_hook(), "")

    def test_complete_set(self):
        write_plugin(self.bucket, "bundle", "bundle", ["leaf"])
        write_plugin(self.bucket, "leaf", "leaf")
        write_manifest(self.bucket, [{"name": "bundle"}, {"name": "leaf"}])
        self.assertEqual(self.run_hook(), "")

    def test_unreadable_manifest(self):
        (self.bucket / "manifest.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(self.run_hook(), "")


class ReportTestCase(SyncedFolderTestCase):
    """A gap is reported to both the user and the agent."""

    def setUp(self):
        super().setUp()
        write_plugin(self.bucket, "bundle", "bundle", ["leaf", "absent-one"])
        write_plugin(self.bucket, "workflow", "workflow", ["absent-two", "absent-one"])
        write_plugin(self.bucket, "leaf", "leaf")
        write_manifest(self.bucket, [{"name": "bundle"}, {"name": "workflow"}, {"name": "leaf"}])
        self.output = self.report()

    def test_shape(self):
        self.assertEqual(set(self.output), {"systemMessage", "hookSpecificOutput"})
        specific = self.output["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "SessionStart")
        self.assertIsInstance(specific["additionalContext"], str)

    def test_names_each_gap_and_its_dependents(self):
        for text in (self.output["systemMessage"], self.output["hookSpecificOutput"]["additionalContext"]):
            self.assertIn("absent-one (needed by bundle, workflow)", text)
            self.assertIn("absent-two (needed by workflow)", text)
            self.assertNotIn("leaf (", text)


class DependencyFormsTestCase(SyncedFolderTestCase):
    def test_marketplace_qualified_and_object_forms(self):
        write_plugin(self.bucket, "bundle", "bundle",
                     ["leaf@some-marketplace", {"name": "absent"}, 7])
        write_plugin(self.bucket, "leaf", "leaf")
        write_manifest(self.bucket, [{"name": "bundle"}, {"name": "leaf"}])
        message = self.report()["systemMessage"]
        self.assertIn("absent (needed by bundle)", message)
        self.assertNotIn("leaf (", message)


class GenerationTestCase(SyncedFolderTestCase):
    """A re-synced plugin sits beside its old copy; only the current one counts."""

    def test_generation_selects_the_suffixed_copy(self):
        write_plugin(self.bucket, "workflow", "workflow")
        write_plugin(self.bucket, "workflow~g2", "workflow", ["absent"])
        write_manifest(self.bucket, [{"name": "workflow", "generation": 2}])
        self.assertIn("absent (needed by workflow)", self.report()["systemMessage"])

    def test_no_generation_selects_the_bare_copy(self):
        write_plugin(self.bucket, "workflow", "workflow")
        write_plugin(self.bucket, "workflow~g2", "workflow", ["absent"])
        write_manifest(self.bucket, [{"name": "workflow"}], stale=["workflow~g2"])
        self.assertEqual(self.run_hook(), "")

    def test_missing_named_copy_falls_back_past_stale_ones(self):
        write_plugin(self.bucket, "workflow", "workflow", ["absent"])
        write_plugin(self.bucket, "workflow~g2", "workflow")
        write_manifest(self.bucket, [{"name": "workflow", "generation": 3}], stale=["workflow~g2"])
        self.assertIn("absent (needed by workflow)", self.report()["systemMessage"])


class OncePerSessionTestCase(SyncedFolderTestCase):
    """A container restart resumes the session; the reminder should not repeat."""

    def setUp(self):
        super().setUp()
        self.data = pathlib.Path(self.tmp.name) / "data"
        write_plugin(self.bucket, "bundle", "bundle", ["absent"])
        write_manifest(self.bucket, [{"name": "bundle"}])

    def test_repeats_only_for_a_new_session(self):
        self.report(session="one", data=self.data)
        self.assertEqual(self.run_hook(session="one", data=self.data), "")
        self.report(session="two", data=self.data)

    def test_repeats_when_the_gap_changes(self):
        self.report(session="one", data=self.data)
        write_plugin(self.bucket, "other", "other", ["also-absent"])
        write_manifest(self.bucket, [{"name": "bundle"}, {"name": "other"}])
        self.assertIn("also-absent", self.report(session="one", data=self.data)["systemMessage"])

    def test_reports_every_time_without_state(self):
        self.report(session="one")
        self.report(session="one")
        self.report(data=self.data)
        self.report(data=self.data)


class RegistrationTestCase(unittest.TestCase):
    """What hooks.json hands the harness."""

    def test_command_points_at_the_script(self):
        command = registered_hook()["command"]
        _, _, tail = command.rpartition("}")
        self.assertEqual(PLUGIN / tail.strip().lstrip('"/'), SCRIPT)

    def test_script_is_executable(self):
        self.assertTrue(SCRIPT.stat().st_mode & 0o111)

    def test_fires_on_startup_and_resume(self):
        matcher = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]["SessionStart"][0]["matcher"]
        self.assertEqual(set(matcher.split("|")), {"startup", "resume"})


if __name__ == "__main__":
    unittest.main()
