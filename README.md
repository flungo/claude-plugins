# claude-plugins

Personal Claude Code / Claude.ai plugin marketplace. One repo, plugins
usable from both Claude Code and claude.ai, kept in sync by pulling from
this repo rather than by re-uploading files by hand.

## Plugins

- **[code-review-workflow](plugins/code-review-workflow)** — personal
  git/PR workflow commands and standing git conventions. Currently one
  command, `/ready-to-merge` (aliases "Ready to Merge?", "RTM?"); more
  expected over time.

## Install in Claude Code

```
/plugin marketplace add flungo/claude-plugins
/plugin install code-review-workflow@flungo-plugins
```

To pull in updates later:

```
/plugin marketplace update flungo-plugins
```

(Claude Code also refreshes marketplaces in the background periodically;
`update` forces it immediately.)

## Install in claude.ai (web, desktop, Cowork)

1. Open **Customize** in the left sidebar → **Plugins** tab.
2. Under **Personal plugins**, click "+" → **Add marketplace**.
3. Choose **Add from a repository** and paste this repo's URL:
   `https://github.com/flungo/claude-plugins`
4. Claude parses `.claude-plugin/marketplace.json` and lists
   `code-review-workflow` — install it.

To pick up updates after pushing changes here, use the marketplace's
"Update" action in the Plugins tab to pull the latest commit.

## Repo layout

```
.claude-plugin/marketplace.json     — marketplace catalog
plugins/<plugin-name>/
  .claude-plugin/plugin.json        — plugin manifest
  skills/<skill-name>/SKILL.md      — the skill Claude loads
  skills/<skill-name>/references/   — supporting reference docs
  evals/                            — dev-time test fixtures (not loaded at runtime)
```

Adding a new plugin later: create `plugins/<new-plugin>/` following the
same shape, then add an entry to `.claude-plugin/marketplace.json`'s
`plugins` array.

## Conventions

Commits in this repo follow the same git conventions documented in
`plugins/code-review-workflow/skills/code-review-workflow/references/git-conventions.md`
— Conventional Commits, linear history, one logical change per commit.
