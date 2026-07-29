# Session-End Doc-Maintenance Checklist

A repository that adopts these documentation conventions wants a nudge, at the end of every session, to check that the docs were kept current.
This plugin ships that nudge as a `Stop` hook so an adopting repo gets it for free — no per-repo configuration.

## What it does

When a session ends, the hook prints a short checklist (via a `systemMessage`) covering the maintenance the conventions require:

1. **Decisions** — a structural decision made or revised gets its ADR and its
   `docs/decisions/README` row, in the same commit.
2. **Plans** — completed steps ticked `[x]`; plan checkboxes, the
   `docs/plans/README` status, and `CLAUDE.md` "Active work" reflect merged
   work (the PR that completes a step is the one that ticks it).
3. **Indexes** — every `docs/` directory README index is current for anything
   touched, in the same commit.
4. **Staleness** — versions, hostnames, and owner/workspace/provider/module/
   secret names still accurate; resolved open decisions closed; "Active work"
   reflects reality.
5. **Callouts** — agent-directed instructions use `> **🤖 Agent**`;
   live-unverifiable uncertainty uses `> **Verify:**`.

Item 2 deliberately restates the "plan checkboxes / Active work reflect merged work" rule, so this hook backstops the in-repo status-tracker reconciliation that the `/ready-to-merge` command performs.

**It is a backstop, not the mechanism.** The hook fires *after* the turn, which is too late to land a tracker update in the PR that earned it.
Do the tracker updates as you go (per `references/documentation-model.md`); the checklist only catches what slipped.

## How it's shipped (plugin-native)

Claude Code plugins provide hooks from a `hooks/hooks.json` file at the plugin root, so the checklist ships **with the plugin** rather than being copied into each repo's settings:

```text
plugins/docs-standards/
  hooks/hooks.json          # registers the Stop hook
  scripts/doc-checklist.sh  # prints the checklist JSON
```

`hooks/hooks.json` registers a `Stop` hook that runs the bundled script, located via the `${CLAUDE_PLUGIN_ROOT}` substitution so the path resolves wherever the plugin is installed:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/doc-checklist.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

The script emits `{"systemMessage": "…"}` on stdout; Claude Code surfaces the message at session end.
Because it is plugin-native, any repo that enables `docs-standards` at project scope inherits the checklist automatically — the preferred distribution.

> **🤖 Agent** — if you change the checklist, edit `scripts/doc-checklist.sh`,
> keep its stdout valid JSON with a single `systemMessage` field, and keep the
> script executable (`chmod +x`); hooks that aren't executable silently don't
> fire.

## Fallback — settings.json snippet (no plugin adoption)

A repo that wants the checklist **without** adopting the plugin can add an equivalent `Stop` hook to its `.claude/settings.json` directly.
This is the pattern the sibling repos used before the plugin existed:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"systemMessage\": \"📋 Doc maintenance checklist — review before ending session:\\n  1. docs/decisions/ — structural decision made? Write/update its ADR and README row\\n  2. docs/plans/*.md — mark completed steps [x]; plan checkboxes and CLAUDE.md \\\"Active work\\\" reflect merged work\\n  3. docs/ README indexes current for anything touched\\n  4. Staleness — versions/names accurate; resolved open decisions closed\"}'",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Prefer the plugin: adopting `docs-standards` at project scope brings the maintained checklist along, so it stays in sync with the conventions instead of drifting as an inline copy in each repo.
