#!/usr/bin/env python3
"""Unit tests for scripts/doc-checklist.sh.

Run from the plugin root: python3 -m unittest discover -s tests
No dependencies beyond the standard library; the script is POSIX sh.

The script is a Stop hook, so the harness parses its stdout and surfaces nothing
if that parse fails. These cases pin the two properties `references/stop-hook.md`
asks an editor to preserve — stdout that is JSON carrying a single
`systemMessage`, and a file the shell will execute — because a hook that breaks
either one fails by staying silent rather than by erroring.
"""
import json
import os
import pathlib
import subprocess
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = PLUGIN / "scripts" / "doc-checklist.sh"
HOOKS = PLUGIN / "hooks" / "hooks.json"


class DocChecklistOutputTestCase(unittest.TestCase):
    """What the harness reads off stdout."""

    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True, timeout=30,
        )

    def test_exits_zero(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr)

    def test_stdout_is_json(self):
        json.loads(self.proc.stdout)

    def test_carries_exactly_one_system_message(self):
        payload = json.loads(self.proc.stdout)
        self.assertEqual(list(payload), ["systemMessage"])

    def test_system_message_is_a_non_empty_string(self):
        payload = json.loads(self.proc.stdout)
        self.assertIsInstance(payload["systemMessage"], str)
        self.assertTrue(payload["systemMessage"].strip())

    def test_writes_nothing_to_stderr(self):
        self.assertEqual(self.proc.stderr, "")


class DocChecklistWiringTestCase(unittest.TestCase):
    """Whether the hook can fire at all."""

    def test_script_is_executable(self):
        self.assertTrue(
            os.access(SCRIPT, os.X_OK),
            f"{SCRIPT.name} is not executable; a Stop hook that is not silently never fires",
        )

    def test_registered_command_resolves_to_the_script(self):
        registered = json.loads(HOOKS.read_text(encoding="utf-8"))
        commands = [
            hook["command"]
            for matcher in registered["hooks"]["Stop"]
            for hook in matcher["hooks"]
            if hook["type"] == "command"
        ]
        self.assertEqual(len(commands), 1, commands)
        # The hook command is the one place ${CLAUDE_PLUGIN_ROOT} is substituted;
        # resolve it against the plugin root the way the harness does.
        relative = commands[0].split("}", 1)[1].lstrip('"/')
        self.assertTrue(
            (PLUGIN / relative).is_file(),
            f"hooks.json registers {relative!r}, which is not a file in the plugin",
        )


if __name__ == "__main__":
    unittest.main()
