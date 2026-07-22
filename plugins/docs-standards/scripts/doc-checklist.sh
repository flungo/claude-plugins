#!/usr/bin/env sh
# docs-standards Stop hook: print a documentation-maintenance checklist when a
# session ends. Emits a JSON object with a `systemMessage` field on stdout,
# which Claude Code surfaces to the user. Read-only — it never edits files; it
# only reminds. The checklist backstops the docs-standards conventions (see the
# plugin's references/documentation-model.md); it fires after the turn, so it is
# a safety net, not the place to land tracker updates.
cat <<'JSON'
{"systemMessage": "📋 docs-standards — doc-maintenance checklist before ending the session:\n  1. Decisions — did a structural decision get made or revised? Write/update its ADR (Nygard format) and its docs/decisions/README row, in the same commit.\n  2. Plans — mark completed steps [x]; make plan checkboxes, the docs/plans/README status, and CLAUDE.md \"Active work\" reflect merged work (the PR that completes a step is the one that ticks it).\n  3. Indexes — every docs/ directory README index (decisions, plans, runbooks, reference) is current for anything you touched, in the same commit.\n  4. Staleness — versions, hostnames, and owner/workspace/provider/module/secret names still accurate; open decisions resolved this session are closed; \"Active work\" reflects reality.\n  5. Callouts — agent-directed instructions use > **🤖 Agent** (one action each); uncertainty that can't be checked without live access uses > **Verify:** rather than being left silent."}
JSON
