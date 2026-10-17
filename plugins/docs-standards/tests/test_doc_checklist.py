#!/usr/bin/env python3
"""Unit tests for scripts/doc-checklist.sh.

Run from the plugin root: python3 -m unittest discover -s tests
No dependencies beyond the standard library; the script is POSIX sh.

The script is a Stop hook, so the harness parses its stdout and surfaces nothing
if that parse fails. These cases pin what `references/stop-hook.md` asks an
editor to preserve — stdout that is JSON carrying a single `systemMessage`, and
a file the shell will execute — and go two steps further, to the command
`hooks.json` registers and the seconds it allows. Every one of those fails
silently in production: stdout that will not parse surfaces nothing, a script
that is not executable never fires, and one past its budget is killed
mid-checklist.
"""
import json
import os
import pathlib
import subprocess
import unittest

PLUGIN = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = PLUGIN / "scripts" / "doc-checklist.sh"
HOOKS = PLUGIN / "hooks" / "hooks.json"


def registered_stop_commands():
    """Every path a Stop hook command points at, with a leading
    ${CLAUDE_PLUGIN_ROOT} taken off as the harness does when it substitutes one —
    one of the places it resolves, unlike a reference read from disk."""
    registered = json.loads(HOOKS.read_text(encoding="utf-8"))
    for matcher in registered["hooks"]["Stop"]:
        for hook in matcher["hooks"]:
            if hook["type"] != "command":
                continue
            _, _, tail = hook["command"].rpartition("}")
            yield PLUGIN / (tail or hook["command"]).strip().lstrip('"/')


def registered_budget(default=30):
    """The seconds hooks.json gives the script, so the test holds it to the
    same budget the harness does rather than one of its own."""
    try:
        registered = json.loads(HOOKS.read_text(encoding="utf-8"))
        return registered["hooks"]["Stop"][0]["hooks"][0].get("timeout", default)
    except (OSError, ValueError, KeyError, IndexError):
        return default


class DocChecklistOutputTestCase(unittest.TestCase):
    """What the harness reads off stdout."""

    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.run(
            [str(SCRIPT)], capture_output=True, text=True, encoding="utf-8",
            timeout=registered_budget(),
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

    def test_a_registered_command_resolves_to_the_script(self):
        resolved = [path.resolve() for path in registered_stop_commands()]
        self.assertIn(
            SCRIPT.resolve(), resolved,
            f"no Stop hook resolves to {SCRIPT.name}; hooks.json points at {resolved}",
        )


if __name__ == "__main__":
    unittest.main()
