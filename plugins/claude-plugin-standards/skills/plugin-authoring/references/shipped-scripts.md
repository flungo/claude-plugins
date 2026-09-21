# Pointing at a script the plugin ships

`CLAUDE_PLUGIN_ROOT` resolves wherever the harness injects or executes the text itself — skill and agent content, and hook, MCP and LSP configuration.
It resolves in neither of the two places an agent runs a command from: it is absent from the environment of anything run through the Bash tool, and a reference file is read from disk unsubstituted, like any other file.

- **`SKILL.md` names the runnable path** — `${CLAUDE_PLUGIN_ROOT}/scripts/<basename>` — so the agent is handed an absolute path to the version actually running.
  A plugin shipping several scripts may instead declare the root once, as `CLAUDE_PLUGIN_ROOT: ${CLAUDE_PLUGIN_ROOT}`, in the body and never the frontmatter, where a colon followed by a space parses as a mapping.
- **A reference locates the script by a path relative to itself** — `../../../scripts/<basename>` from `skills/<skill>/references/`, resolved against the path the reference was read from rather than the working directory.
  Give it as a link, with the basename as link text: `[<basename>](../../../scripts/<basename>)`.
  The repository's link check then validates the same path the agent resolves at runtime.
- **A command binds that path once** — `NAME=<the relative path, resolved against this file>` — and uses `"$NAME"` after it.
  The angle brackets are the reader's to replace and are not shell syntax, so a command left unsubstituted is a syntax error and nothing runs.
- **No command carries a shell placeholder**, the platform's or one the plugin invents: an unset name expands to the empty string without error, leaving a path under `/` and no sign that anything went wrong.
- **Nothing searches the plugin cache**, which holds a directory per installed version.

[ADR-010](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/010-locating-a-shipped-script.md) records the decision and what it rules out.

## Writing the rule down

A `SKILL.md` cannot display the placeholder.
The substitution is a global replace over the whole file with no escape, so every occurrence becomes a path, including one written to explain it.
Prose needing the literal belongs in a reference, which is read from disk untouched.
