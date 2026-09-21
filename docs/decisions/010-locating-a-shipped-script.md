# ADR-010: A shipped script is located from the file that names it

- **Date:** 2026-09-21
- **Status:** Accepted

## Context

`${CLAUDE_PLUGIN_ROOT}` is the documented way a plugin refers to its own files.
[Claude Code's plugins reference](https://code.claude.com/docs/en/plugins-reference) resolves it in skill and agent content, in hook and monitor commands, and in MCP and LSP server configuration, and exports it to hook processes and to MCP and LSP subprocesses.
It states that the variables "aren't present in the environment of commands Claude runs through the Bash tool, in the main session or in a subagent".

A reference file is neither of those things.
It is opened from disk at the moment an agent needs it, so nothing substitutes the placeholder inside it, and no shell expands it either.

`markdown-standards` therefore shipped instructions that could not work.
Its `SKILL.md` named `${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py` and resolved to a real path, while `references/prose-conventions.md` gave the same string in four commands an agent was told to run.
What runs is `python3 "/scripts/reflow.py"`, which fails on a path nobody wrote.

Two ways of keeping a placeholder in references were weighed.

**Declaring the value in `SKILL.md` and leaving the agent to substitute it.**
A session holds one plugin root per installed plugin version — 17 of them when this was measured — and a reference file names nowhere in its text the plugin it belongs to.
Associating a placeholder with the right value among many then rests on which `SKILL.md` was in context when the file was opened, which is what compaction removes.

**Declaring a uniquely named variable per skill**, such as `SESSION_WORKFLOW_CLAUDE_PLUGIN_ROOT`, and using that in references.
The name disambiguates, and the prefix survives the harness substitution, whose regex requires `${` immediately before `CLAUDE_PLUGIN_ROOT`.
It still binds only while the declaring `SKILL.md` is in context, and it keeps the shape that caused the defect: `${NAME}` in a shell command is a real expansion, and an unset variable expands to the empty string silently, producing `/scripts/reflow.py` again.

## Decision

**A reference locates a script the plugin ships by a path relative to itself** — `../../../scripts/<basename>` from `skills/<skill>/references/` — resolved against the path the reference was read from rather than the working directory.
It is given as a link, with the basename as link text, so the link check sees it.

**`SKILL.md` names the runnable path with `${CLAUDE_PLUGIN_ROOT}`**, which resolves there.
A plugin shipping several scripts may declare the root once instead, as `CLAUDE_PLUGIN_ROOT: ${CLAUDE_PLUGIN_ROOT}` in the body, never the frontmatter, where a colon followed by a space parses as a mapping.

**No reference carries a placeholder inside a command**, the platform's or an invented one.
A command binds the resolved path once, as `NAME=<the relative path, resolved against this file>`, and uses `"$NAME"` after it.
Angle brackets are not shell syntax, so a command left unsubstituted is a syntax error and nothing runs, where an unset `${NAME}` expands to the empty string and runs against `/`.

**Nothing resolves a script by searching the plugin cache**, which holds a directory per installed version.

The rule itself lives in `claude-plugin-standards`, in `references/shipped-scripts.md` rather than in that plugin's `SKILL.md`, because the substitution is a global replace with no escape: a `SKILL.md` cannot display the placeholder at all.

## Consequences

### Positive

- A reference is self-contained.
  The agent resolves the path against the file it has just opened, so nothing depends on `SKILL.md` still being in context.
- It cannot name a different plugin's root, whatever else the session holds.
- Nothing in the command is a shell expansion, so there is no silent substitution of the empty string.
- **CI validates the runtime path.**
  A repository checkout and an installed plugin share the same layout below the plugin root, so `../../../scripts/<basename>` resolves to the same file in both, and the `markdown-links / internal` check fails the pull request rather than the session.
- It was already the idiom here: both `markdown-standards` references link `[reflow.py](../../../scripts/reflow.py)`.

### Negative — trade-offs

- The depth is structural.
  Moving a reference to a different level changes the path, and only the link check catches it — so the path belongs in a link, where that check can see it, rather than in prose alone.
- The agent has to anchor on the file it read rather than on the working directory, which each reference states where it gives the path.
