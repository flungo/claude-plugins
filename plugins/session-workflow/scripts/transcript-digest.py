#!/usr/bin/env python3
"""Print the user/agent conversation from a Claude Code session transcript.

The transcript JSONL is append-only, so it still holds every turn the context
window dropped at a compaction boundary. This filters it down to what a sweep
of the session needs -- the prompts, the visible replies, and the decisions the
user made through the question tool -- and leaves out tool calls, tool results,
and injected context.

Run with no arguments inside the session being swept; it resolves its own
transcript from the working directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>\s*", re.DOTALL)

# A denied or interrupted tool call is where a user's "no, not that" ends up.
# The surrounding text is theirs, so the whole result is worth surfacing.
INTERVENTION_RE = re.compile(
    r"\[Request interrupted by user"
    r"|The user doesn't want to take this action"
    r"|The user doesn't want to proceed with this tool use",
    re.IGNORECASE,
)


def projects_root() -> Path:
    """The directory Claude Code keeps per-project transcripts in."""
    config = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config) if config else Path.home() / ".claude"
    return base / "projects"


def slug(path: str) -> str:
    """Claude Code's project-directory name: every non-alphanumeric becomes '-'."""
    return re.sub(r"[^a-zA-Z0-9]", "-", path)


def candidates(root: Path, cwd: str, session_id: str | None) -> list[Path]:
    """Transcripts that could belong to this session, most recently written first.

    A session's own transcript is the one being appended to as this runs, so
    mtime order puts it first. Directory names are matched against the working
    directory and each of its ancestors, because a session started in a
    subdirectory files its transcript under that subdirectory's slug.
    """
    if not root.is_dir():
        return []
    if session_id:
        return sorted(root.glob(f"*/{session_id}.jsonl"))

    wanted = {slug(str(p)) for p in [Path(cwd), *Path(cwd).parents]}
    preferred = [d for d in root.iterdir() if d.is_dir() and d.name in wanted]
    for group in (preferred, [d for d in root.iterdir() if d.is_dir()]):
        files = [f for d in group for f in d.glob("*.jsonl")]
        if files:
            return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
    return []


def blocks(content) -> list[dict]:
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def text_of(content) -> str:
    """The human-readable text of a message, dropping tool and image blocks."""
    if isinstance(content, str):
        return content
    parts = [b.get("text", "") for b in blocks(content) if b.get("type") == "text"]
    return "\n".join(p for p in parts if p)


def thinking_of(content) -> str:
    parts = [b.get("thinking", "") for b in blocks(content) if b.get("type") == "thinking"]
    return "\n".join(p for p in parts if p)


def tool_result_text(content) -> str:
    out = []
    for block in blocks(content):
        if block.get("type") != "tool_result":
            continue
        inner = block.get("content")
        if isinstance(inner, str):
            out.append(inner)
        else:
            out.append(text_of(inner))
    return "\n".join(p for p in out if p)


def tool_lines(content, width: int = 160) -> list[str]:
    """One compact line per tool call: the name and the start of its input."""
    lines = []
    for block in blocks(content):
        if block.get("type") != "tool_use":
            continue
        args = json.dumps(block.get("input", {}), ensure_ascii=False)
        if len(args) > width:
            args = args[:width].rstrip() + "…"
        lines.append(f"    → {block.get('name', '?')} {args}")
    return lines


def clip(text: str, limit: int) -> str:
    if limit and len(text) > limit:
        return text[:limit].rstrip() + f"\n… [clipped, {len(text) - limit} more characters]"
    return text


def stamp(record: dict) -> str:
    return (record.get("timestamp") or "")[:19].replace("T", " ")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--transcript", help="path to a transcript JSONL, instead of resolving one")
    ap.add_argument("--session-id", help="resolve the transcript by session id")
    ap.add_argument("--cwd", default=os.getcwd(), help="project directory to resolve from")
    ap.add_argument("--list", action="store_true", help="list the transcripts found and exit")
    ap.add_argument("--stats", action="store_true", help="print the header only and exit")
    ap.add_argument("--include-thinking", action="store_true", help="include the agent's thinking")
    ap.add_argument("--include-tools", action="store_true", help="include one line per tool call")
    ap.add_argument("--include-sidechains", action="store_true", help="include subagent turns")
    ap.add_argument("--include-meta", action="store_true", help="include synthetic and hook turns")
    ap.add_argument("--keep-reminders", action="store_true", help="keep <system-reminder> blocks")
    ap.add_argument("--no-decisions", action="store_true", help="omit question answers and denials")
    ap.add_argument("--max-chars", type=int, default=0, metavar="N",
                    help="clip each body to N characters (0 = whole)")
    ap.add_argument("--output", help="write to this file instead of stdout")
    return ap.parse_args(argv)


def resolve(args: argparse.Namespace) -> tuple[Path | None, list[Path]]:
    if args.transcript:
        path = Path(args.transcript)
        return (path if path.is_file() else None), [path]
    found = candidates(projects_root(), args.cwd, args.session_id)
    return (found[0] if found else None), found


def render(path: Path, args: argparse.Namespace) -> str:
    counts: dict[str, int] = {}
    boundaries: list[str] = []
    entries: list[str] = []
    sidechain_lines = unreadable = 0
    first_stamp = last_stamp = session_id = project = ""

    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                unreadable += 1
                continue

            kind = rec.get("type", "?")
            counts[kind] = counts.get(kind, 0) + 1
            session_id = session_id or rec.get("sessionId", "")
            project = project or rec.get("cwd", "")
            if rec.get("timestamp"):
                first_stamp = first_stamp or rec["timestamp"]
                last_stamp = rec["timestamp"]

            if rec.get("isSidechain"):
                sidechain_lines += 1
                if not args.include_sidechains:
                    continue

            if kind == "system" and "compact" in str(rec.get("subtype", "")):
                meta = rec.get("compactMetadata") or {}
                label = (f"{rec.get('subtype')} ({meta.get('trigger', 'unknown trigger')}, "
                         f"{meta.get('preTokens', '?')} tokens before)")
                boundaries.append(f"{stamp(rec)} {label}")
                entries.append(f"\n===== COMPACTION: {label} — {stamp(rec)} =====\n")
                continue

            if kind == "summary" and rec.get("summary"):
                entries.append(f"\n----- STORED SUMMARY -----\n{rec['summary']}\n")
                continue

            if kind not in ("user", "assistant"):
                continue

            message = rec.get("message") or {}
            content = message.get("content")
            body = text_of(content)
            tags: list[str] = ["sidechain"] if rec.get("isSidechain") else []

            if kind == "user":
                result = rec.get("toolUseResult")
                if not args.no_decisions:
                    answers = result.get("answers") if isinstance(result, dict) else None
                    if isinstance(answers, dict) and answers:
                        chosen = "\n".join(f"- {q}\n  → {a}" for q, a in answers.items())
                        entries.append(f"\n## USER DECISION — {stamp(rec)}\n{chosen}\n")
                        continue
                    refused = tool_result_text(content)
                    if refused and INTERVENTION_RE.search(refused):
                        entries.append(
                            f"\n## USER INTERVENTION — {stamp(rec)}\n"
                            f"{clip(refused.strip(), 600)}\n"
                        )
                        continue
                if rec.get("isCompactSummary"):
                    tags.append("COMPACTION SUMMARY")
                elif rec.get("isMeta"):
                    if not args.include_meta:
                        continue
                    tags.append("meta")
                if not args.keep_reminders:
                    body = REMINDER_RE.sub("", body)
            else:
                if rec.get("isApiErrorMessage"):
                    tags.append("api error")
                if args.include_thinking:
                    thought = thinking_of(content)
                    if thought:
                        body = f"[thinking]\n{thought}\n[/thinking]\n{body}".strip()

            extras = tool_lines(content) if args.include_tools else []
            body = body.strip()
            if not body and not extras:
                continue

            label = kind.upper() + (f" [{', '.join(tags)}]" if tags else "")
            block = f"\n## {label} — {stamp(rec)}\n"
            if body:
                block += clip(body, args.max_chars) + "\n"
            if extras:
                block += "\n".join(extras) + "\n"
            entries.append(block)

    header = [
        "# Session transcript digest",
        f"Transcript : {path}",
        f"Session    : {session_id or 'unknown'}",
        f"Project    : {project or args.cwd}",
        f"Span       : {first_stamp or '?'} → {last_stamp or '?'}",
        f"Lines      : {' | '.join(f'{k}: {v}' for k, v in sorted(counts.items())) or 'none'}",
        f"Sidechain  : {sidechain_lines} line(s) "
        + ("included" if args.include_sidechains else "excluded"),
        f"Compaction : {len(boundaries) or 'none'}"
        + "".join(f"\n             - {b}" for b in boundaries),
    ]
    if unreadable:
        header.append(f"Unreadable : {unreadable} line(s) skipped")
    if boundaries:
        header.append(
            "\nEverything above each boundary is in this file but was dropped from the\n"
            "context window. Sweep this digest, not the conversation still in context."
        )

    out = "\n".join(header) + "\n"
    if not args.stats:
        out += "\n" + "".join(entries)
    return out


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path, found = resolve(args)
    if path is None:
        where = args.transcript or f"{projects_root()} for {args.cwd}"
        print(
            f"No transcript found at {where}.\n"
            "A claude.ai chat session has no transcript file; sweep the conversation directly.",
            file=sys.stderr,
        )
        return 1

    if args.list:
        for f in found:
            when = dt.datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")
            print(f"{when}\t{f.stat().st_size:>9} bytes\t{f}")
        return 0

    out = render(path, args)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Wrote {len(out)} characters to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
