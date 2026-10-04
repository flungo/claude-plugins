# ADR-010: Plugin and skill names avoid Anthropic's reserved words

- **Date:** 2026-10-04
- **Status:** Accepted

## Context

On 2026-10-04 the `plugin-validate` workflow failed on `main` for a commit whose identical content had passed on its pull request five days earlier.
The workflow installs the `claude` CLI unpinned, and between the two runs it moved to 2.1.289, which rejects a plugin name that "passes as one of Anthropic's own": one starting `claude-`, `anthropic-`, `anthropics-`, or `cc-plugin-`, one that is `claude`, `anthropic`, `anthropics`, `claude-code`, or `claude-mods`, or one that puts `official` beside `claude` or `anthropic`.
Two plugins here tripped it, `claude-code-web` and `claude-plugin-standards`, each in its own manifest and again in `marketplace.json` — so the marketplace as a whole failed validation, blocking every pull request that touches a plugin.

Installing either plugin still worked on 2.1.289, so the break was confined to validation; nothing guarantees that stays true.

Until then the only reserved-word rule known here was claude.ai's ingestion rejecting a *skill* name containing `claude`.
`claude plugin validate` does not check that one: on 2.1.289 it parses each skill's frontmatter, failing on YAML it cannot read, but passes a skill named `claude`, and the CLI installs it.
[ADR-006](006-plugin-delivery-per-surface.md) and [ADR-009](009-plugin-authoring-standards.md) record the response: keep the plugin name, and give its skill a different one — `cloud-sessions` and `plugin-authoring`.
The `plugin-authoring` skill went further, stating that the restriction bound skills only, on the evidence of `claude-code-web` syncing while its own skill was rejected.

Pinning the CLI to the last passing version would have turned CI green without changing anything a consumer installs, and would fail again at the first bump: suppressing the check rather than fixing what it found.

## Decision

**Rename both plugins, and keep `claude` and `anthropic` out of plugin and skill names altogether.**

- **`claude-code-web` becomes `cloud-sessions`.**
  Anthropic's documentation calls the subject a *cloud session* — a Claude Code session running on cloud infrastructure — and uses *Claude Code on the web* only for the browser at `claude.ai/code`, one of several surfaces that start one alongside the mobile and Desktop apps, `claude --cloud`, and routines.
  The plugin already covered all of them, so the new name is the accurate one rather than merely the permitted one, and it is the name its skill already had.
- **`claude-plugin-standards` becomes `agent-plugin-standards`, and its skill `plugin-authoring` becomes `agent-plugin-standards`.**
  `plugin-standards` alone reads as unambiguous only inside this repository; another repository sees it in `enabledPlugins`, possibly beside `terraform-provider-standards`, where Terraform providers are plugins too.
  *Agent* covers both surfaces these plugins load on, Claude Code and claude.ai, without naming either.
  With the reserved word gone from the plugin name nothing forces its skill to differ, so the skill takes the plugin's name as a single-skill plugin's does — which also ends its clash with a built-in Claude Code skill also called `plugin-authoring`.
- **The naming rule moves into `agent-plugin-standards`.**
  A plugin name must pass `claude plugin validate`'s reserved-name check, a skill name must not contain `claude`, and both are platform rules that a newer CLI or ingestion can extend — so a name with neither word anywhere in it is the one that stays valid.
  This concerns Anthropic's words only: naming another product where it is the domain, as `terraform-standards` and `google-drive` do, is unaffected.
- **Both renamed plugins go to 1.0.0**, the major bump a rename calls for; `personal-cloud-environment`, whose dependency changes name, takes a minor bump.
- **CI keeps the CLI unpinned.**
  A floating validator surfaces a new platform rule in CI rather than at install time; `CLAUDE.md` records the version last seen, as it does for markdownlint.

## Consequences

### Positive

- Validation passes again, and the marketplace no longer depends on a reading of the reserved-word rules that the platform has already outgrown.
- Every single-skill plugin here now names its skill after itself, so `CLAUDE.md` drops its exception for the two that did not.
- `cloud-sessions` describes what the plugin covers, not just the browser surface it was first written in.

### Negative — trade-offs

- A rename is breaking: an installed `claude-code-web` or `claude-plugin-standards` is left orphaned and has to be uninstalled, and the new name installed, on each local CLI and in claude.ai chat.
- A repository adopting `claude-plugin-standards@flungo-plugins` in its `.claude/settings.json` has to change the entry; this repository was the only one, and its entry changes with the rename.
- The cloud environment's setup script installs neither plugin by name, so it keeps working unchanged and `cloud-sessions` arrives when the environment's snapshot next rebuilds.
  Editing the live copy to match the README's updated comment rebuilds the snapshot at once rather than at its expiry.
- Earlier ADRs keep the old names as written, with dated amendments beneath them.
