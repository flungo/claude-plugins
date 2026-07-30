# `/adopt-markdown-ci` — onboard a repo to the Markdown validation CI

The end-to-end adoption: adds the reusable Markdown workflows from [flungo/github-workflows](https://github.com/flungo/github-workflows) to a repo, brings its Markdown up to the conventions in this plugin, and adopts the plugin at project scope so they travel with the repo.
Run it as the automated alternative to working through that repo's runbook by hand — the runbook's own § Optional section points here for exactly this.

**Target repo:** an explicitly named repo always takes precedence; otherwise the repo of the current session.
If neither is clear, ask.

## Gate — owned repos only

Adoption imposes house style, so it is only for repos **Fabrizio owns, verified — not a fork** (fork flag/parent on GitHub, contributor list, pre-existing adoption of his plugins or shared CI as precedent; when unsure, treat as third-party and adopt nothing).
This is the fleet-wide owned-vs-third-party gate, not something specific to Markdown; it is recorded in [claude-plugins ADR 003](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/003-owned-vs-third-party-adoption.md).
The trap it exists for: forking a third-party project puts it in Fabrizio's namespace, so "is it in his namespace?" is necessary but not sufficient — check the fork flag/parent.

## Division of labour — what comes from where

The workflows and these conventions are **separable**: a repo can adopt the CI without adopting any of this, and `github-workflows` is written that way deliberately.
Keep the split straight when reading the two sources:

| Source | Owns |
|---|---|
| [`adopting-markdown-workflows.md`](https://github.com/flungo/github-workflows/blob/main/docs/runbooks/adopting-markdown-workflows.md) in `github-workflows` | The **mechanical contract**, true for any adopter — caller snippets, the required `permissions:` block, what each per-repo config file is for, `LYCHEE_GITHUB_TOKEN` provisioning and the `token:`-not-`env:` trap, and the tool-version/sandbox pitfalls. |
| **This plugin** | The **opinions** — the lint rule defaults below, the check-then-fix commit discipline, the semantic-line-break reflow, and the authoring conventions in the sibling references. |

Open the runbook for anything in its column rather than working from memory of it, and don't assume the major to pin is still `@v1` — read the current major from `github-workflows` itself.
`add_repo` it if it isn't in the session.

## The lint defaults we choose

Start the repo's `.markdownlint-cli2.jsonc` from these, then add further overrides only with an inline justification:

```jsonc
{
  "config": {
    // Disabled in favour of semantic line breaks (one sentence per source
    // line) — a character ceiling can't reflow and would fight the convention.
    "MD013": false,
    // Allow repeated subsection names under different parents (e.g. Context /
    // Decision / Consequences across ADRs); paired with the unique-heading
    // convention for anything cross-referenced.
    "MD024": { "siblings_only": true }
  }
}
```

`MD028` stays at its default (enabled).
Each of these three is half of a pair whose human half is in `prose-conventions.md` — read it before applying them, and record neither half in the repo's `CLAUDE.md`: the plugin is what carries them (step 5).

## Check-then-fix commit discipline

The rule that matters more than the PR boundary is the **commit** boundary.
For each check introduced:

1. **Introduce the check** (workflow / config) in one commit, with **no fixes**.
2. **Push it and confirm CI shows the expected failure** — this proves the check catches what it should.
   Seeing the red is the point; never fix pre-emptively.
3. **Apply the fixes in a separate, later commit** — always distinct from, and after, the check that surfaced them; never squashed into it.
   A separate commit per logical fix group aids review (e.g. one per reverted markdownlint override).

Work through the checks in this order, each as its own commit pair:

1. **Internal links + anchors** — offline, blocking.
   Confirm it goes red on a genuinely broken link/anchor before fixing.
2. **markdownlint** — expect many findings on a repo adopting it for the first time.
3. **Semantic-line-break reflow** — the render-gated pass below.
4. **External URLs** — verify **in GitHub via `workflow_dispatch`**, not from a sandbox with limited egress, and only after the token exists (the runbook explains why a tokenless dispatch floods the issue with false 404s).

Adopting may be a **single PR**, provided it still contains those distinct commits.

## The reflow pass

Applying semantic line breaks to a repo's *existing* Markdown is a pure source-whitespace change with identical rendered output.
Use this plugin's render-gated [`reflow.py`](../../../scripts/reflow.py) (`${CLAUDE_PLUGIN_ROOT}/scripts/reflow.py`) from the target repo's root — see `prose-conventions.md § Semantic line breaks` for what it does and does not touch.
Land it as its own commit; it is best-effort, and any file it reports as gate-failed is left untouched by design.

## Checklist

0. **Read the runbook's § Adoption pitfalls and sandbox constraints first** — each one costs a session to rediscover.
   Pin the local `markdownlint-cli2` to the version `markdownlint-cli2-action` ships, or you chase findings CI never reports; in a locked-down sandbox install `lychee` with `cargo install --locked` rather than the release tarball; and never curate `.lycheeignore` from a tokenless dispatch, whose cross-repo 404s are token artifacts rather than dead links.
1. **Add the caller workflows**, pinned to the current major: `markdown-lint.yml`, and `markdown-links.yml` with the `permissions:` block its external job needs.
   Also add the (highly recommended) `version-check.yml` caller if the repo lacks it.
2. **Add repo-specific config — regenerate, never copy another repo's:** `.markdownlint-cli2.jsonc` from the defaults above, and a seeded `.lycheeignore` populated from this repo's own token-enabled runs.
3. **Provision `LYCHEE_GITHUB_TOKEN`** per the runbook, **before** curating `.lycheeignore`.
4. **Work through the checks** in the commit discipline and order above, including the reflow pass.
5. **Adopt this plugin at project scope** instead of pasting conventions into `CLAUDE.md`: in the repo's `.claude/settings.json`, add the `flungo-plugins` marketplace to `extraKnownMarketplaces` and enable `markdown-standards@flungo-plugins` in `enabledPlugins`.
   Keep only repo-specific facts in `CLAUDE.md` (e.g. the pinned local markdownlint-cli2 version); if the repo carries an inlined `## Cross-references` block or paired-convention sections from an earlier adoption, remove them in favour of the plugin.
6. **Feature branch, never `main`; land via PR** — follow `git-conventions` and the repo's own `CLAUDE.md`/`CONTRIBUTING.md` where they differ.
