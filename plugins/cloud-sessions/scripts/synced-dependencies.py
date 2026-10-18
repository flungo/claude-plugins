#!/usr/bin/env python3
"""Report dependencies that claude.ai chat lacks, read from the synced folder.

Claude Code syncs the plugins installed for claude.ai chat into
~/.claude/plugins/synced/<bucket>/, one directory per plugin plus a
manifest.json naming the set. Chat does not resolve a plugin's dependencies but
Claude Code does, so a synced plugin whose dependency chat lacks loads
disabled. The synced folder is the one place a session can see chat's set, so
this compares each synced plugin's declared dependencies against it.

Run as a SessionStart hook: it prints nothing when chat's set is complete or
there is no synced folder, and otherwise one JSON object carrying a
systemMessage for the user and additionalContext for the agent. A cloud
session's container restarts around most turns and resumes the session each
time, so it reports a given gap once per session, recording what it reported
under the plugin's data directory; with no session id or data directory to go
on, it reports every time. It reads the synced folder as the last sync left it
and never writes there. Pass a directory to check one other than the session's
own.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def synced_root() -> Path:
    """The directory Claude Code syncs chat's plugins into."""
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config) if config else Path.home() / ".claude"
    return base / "plugins" / "synced"


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def plugin_dir(bucket: Path, entry: dict, stale: set[str]) -> Path | None:
    """The directory holding a plugin's current copy.

    A re-synced plugin is written beside the old copy rather than over it, and
    the manifest's `generation` says which one is current: none for the bare
    name, N for `<name>~gN`. Failing that, take the newest copy not listed as
    stale.
    """
    name = entry["name"]
    generation = entry.get("generation")
    named = bucket / (f"{name}~g{generation}" if generation else name)
    if (named / ".claude-plugin" / "plugin.json").is_file():
        return named
    candidates = [
        path
        for path in [bucket / name, *bucket.glob(f"{name}~g*")]
        if path.name not in stale and (path / ".claude-plugin" / "plugin.json").is_file()
    ]
    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def dependency_name(dependency) -> str | None:
    """A dependency's plugin name, whether given as `name`, `name@marketplace`,
    or an object carrying `name`."""
    if isinstance(dependency, str):
        return dependency.split("@", 1)[0] or None
    if isinstance(dependency, dict) and isinstance(dependency.get("name"), str):
        return dependency["name"]
    return None


def missing_dependencies(root: Path) -> dict[str, list[str]]:
    """Each dependency absent from chat's set, mapped to the synced plugins
    that declare it."""
    missing: dict[str, set[str]] = {}
    for bucket in sorted(root.iterdir()) if root.is_dir() else []:
        if bucket.name.startswith(".") or not bucket.is_dir():
            continue
        manifest = read_json(bucket / "manifest.json")
        if not isinstance(manifest, dict):
            continue
        entries = [
            entry
            for entry in manifest.get("plugins") or []
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        ]
        installed = {entry["name"] for entry in entries}
        stale = set(manifest.get("staleDirs") or [])
        for entry in entries:
            directory = plugin_dir(bucket, entry, stale)
            if directory is None:
                continue
            declared = read_json(directory / ".claude-plugin" / "plugin.json")
            if not isinstance(declared, dict):
                continue
            for dependency in declared.get("dependencies") or []:
                name = dependency_name(dependency)
                if name and name not in installed:
                    missing.setdefault(name, set()).add(entry["name"])
    return {name: sorted(needed_by) for name, needed_by in sorted(missing.items())}


KEPT_SESSIONS = 50


def already_reported(missing: dict[str, list[str]]) -> bool:
    """Whether this session was already told about exactly this gap, recording
    it as told if not."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data:  # not run as a hook, so there is no hook input to read
        return False
    try:
        session = json.load(sys.stdin).get("session_id") if not sys.stdin.isatty() else None
    except (OSError, ValueError, AttributeError):
        session = None
    if not isinstance(session, str):
        return False
    state_file = Path(data) / "synced-dependencies.json"
    state = read_json(state_file)
    state = state if isinstance(state, dict) else {}
    if state.get(session) == missing:
        return True
    state.pop(session, None)
    state[session] = missing
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        kept = dict(list(state.items())[-KEPT_SESSIONS:])
        state_file.write_text(json.dumps(kept), encoding="utf-8")
    except OSError:
        pass
    return False


def report(missing: dict[str, list[str]]) -> dict:
    gaps = "; ".join(
        f"{name} (needed by {', '.join(needed_by)})" for name, needed_by in missing.items()
    )
    return {
        "systemMessage": f"claude.ai chat is missing dependencies of plugins installed there: {gaps}. "
        "Install them in claude.ai, or their dependents load disabled wherever the sync is all that brings them.",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"The plugins synced from claude.ai chat declare dependencies chat does not have: {gaps}. "
            "Synced copies of those dependents load disabled unless a local install supplies them. "
            "Only the user can install plugins in claude.ai, so tell them once, in a line, which to install there.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("synced_dir", nargs="?", type=Path, default=None,
                        help="the synced-plugins folder to read (default: this session's)")
    args = parser.parse_args(argv)
    try:
        missing = missing_dependencies(args.synced_dir or synced_root())
    except OSError:
        return 0
    if missing and not already_reported(missing):
        json.dump(report(missing), sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
