# ADR-009: Authoring conventions ship as plugins, with shared styles cited on demand

- **Date:** 2026-08-13
- **Status:** Accepted

## Context

The plugins here are almost entirely agent-facing prose, so how that prose is written is the product, not packaging around it.
Review of that prose kept returning the same findings, across plugins and across sessions:

- a statement framed against what the file used to say, rather than as what is true — "the restart boundary is more frequent than 'after inactivity' suggests", "this contradicts the older report … which this plugin previously carried second-hand";
- a note explaining that guidance elsewhere in the document is now wrong, with that guidance left standing;
- an `> **🤖 Agent** — …` callout ordering an action only the user can take, such as editing a cloud environment's settings form.

Each was caught in review and fixed in the pull request that raised it.
Nothing carried the rule forward, so the next session reproduced it: the conventions existed only as feedback, which is exactly the condition [ADR-001](001-marketplace-structure.md) created this marketplace to end for Fabrizio's other conventions.

The same rules govern a Diátaxis reference doc under `docs/reference/`, which `docs-standards` governs, so any home for them has two consumers rather than one.

`CLAUDE.md` separately held a "Plugin authoring conventions" section covering *structure* — manifest layout, dependency composition, the version-bump policy, the reserved-word trap in skill names — reaching only sessions working in this repository with that file in context.

## Decision

**Three plugins, composed through `dependencies`.**

- **`writing-styles`** owns the prose conventions, one reference file per style.
  The first is `references/instructional-writing.md`, the style for text a reader acts on as instruction.
- **`claude-plugin-standards`** owns plugin *structure*, in a `plugin-authoring` skill, and depends on `writing-styles` and `markdown-standards`.
- **`docs-standards`** depends on `writing-styles` too, alongside its existing `markdown-standards` dependency.

This repository adopts all three through [`.claude/settings.json`](../../.claude/settings.json).

**`writing-styles` is on-demand, and that is what makes it shareable.**
A plugin is *ambient* when its skill description triggers on ordinary work, so enabling it applies its conventions across that scope; it is *on-demand* when nothing happens until something names it.
`writing-styles` is written to be the second: its description says it applies nothing on its own, and each consumer names the style and says which of its writing that style governs.
An on-demand plugin is therefore scope-agnostic — safe as a dependency of a user-scope plugin and a project-scope one alike, because enabling it changes no behaviour.
That property is not an install scope: the platform has only user, project and local, and no way to mark a plugin dependency-only.
It is a property of how the skill is written, and it survives only while every dependency the plugin declares is also on-demand, since one ambient dependency carries its conventions into every scope the dependent reaches.

**So `writing-styles` declares no dependencies.**
An earlier shape had it depend on `markdown-standards`, which is ambient: that would have made the whole chain ambient and pushed Markdown conventions into any scope a consumer reached.
The styles are written to compose with `markdown-standards` where a repo has adopted it and to hold on their own where it has not.
`claude-plugin-standards` declares `markdown-standards` directly instead, which is sound because both are ambient and project scope.

**A style is a reference file inside one skill, not a skill each.**
Only one style exists, so a skill per style would be structure built for a population of one, and it would put a second always-on description in every session for no gain.
`markdown-standards` is the shape to copy: one skill, several reference files, each read when its area is in play.

**Consumers cite the style by name and never restate it.**
A plugin is copied into its own cache directory at install, so a path reaching outside it does not resolve at runtime — the skill name is the only stable address, and a declared dependency guarantees it is installed.
`docs-standards` therefore carries a short summary of the style and a pointer to it, in place of the rules themselves.

**A shared plugin, not a shared file.**
Claude Code does dereference a symlink whose target sits elsewhere in the same marketplace, copying the content into each consumer's cache, which would let one file serve several plugins.
Two properties rule it out.
Symlinks outside a plugin's own directory are skipped for a local-path install, which is how an in-flight branch is tested here, so the shared content would be present in production and absent under test.
`claude plugin validate` also does not follow symlinks, so the `plugin-validate` workflow would stop checking the shared file.
A dependency has neither problem and needs no new mechanism.

**`writing-styles` is separately installable, and that is not a defect.**
There is no dependency-only plugin: no manifest field marks a plugin hidden or not-directly-installable, and none of the three install scopes is that either.
Nothing is lost — a repository wanting the prose conventions without either the docs structure or the plugin-authoring rules is a legitimate adopter, and under [ADR-001](001-marketplace-structure.md) that separate enablement boundary is what earns a plugin its own identity.

**`claude-plugin-standards` is project scope**, like the other `*-standards` plugins, because it is ambient.
These are house-style rules rather than correctness rules — a plugin written to different conventions is not a worse plugin — so adoption is a repository's deliberate choice, not something it earns by happening to author plugins.
That is what rules out user scope for it, which would apply a personal house style wherever Fabrizio worked, including repositories that are not his.
[ADR-003](003-owned-vs-third-party-adoption.md) already forbids adopting anything there, and a house style is not something to impose on a repository that is not his whatever the mechanism permits.

`writing-styles` carries no such constraint, being on-demand: it is adopted at project scope here because its consumers are, and a future user-scope consumer could depend on it without imposing anything.

**Names.**
`claude-plugin-standards` is named for the domain rather than the first slice, per the rule it now carries itself; `skill-standards` would have fitted only its initial content.
Its skill is `plugin-authoring` because a skill name may not contain "claude" — claude.ai's ingestion rejects it — the same constraint that makes `claude-code-web` ship `cloud-sessions`.
`writing-styles` is plural because the plugin is the home for styles as a category, with room for a second.

**The structural conventions move out of `CLAUDE.md` into `claude-plugin-standards`.**
Without them that plugin would hold nothing but a dependency edge.
That includes the rules [ADR-007](007-connector-carried-conventions.md) and [ADR-008](008-connector-behaviour-belongs-to-the-connector.md) added there — declaring every dependency you reference, filing a fact by what it is a property of, and naming skills in a multi-skill plugin — since each holds for any marketplace rather than only this one.
`CLAUDE.md` keeps what is specific to *this marketplace*: bundle reachability, which plugins are user-scope-only, where each kind of fact goes among the plugins that exist here, and the two skills deliberately not named after their plugin.
It summarises the rest.

## Consequences

### Positive

- The instructional-writing rules are stated once and cited by both consumers, so a change lands in one place.
- The conventions load automatically in any repository that adopts the plugins, instead of being rediscovered through review comments each time.
- Review of plugin prose gets a citable standard, so a finding can point at a rule rather than restating it.
- `writing-styles` gives a second style somewhere to go without disturbing either consumer.
- `CLAUDE.md` shrinks to what only this repository knows, and the conventions it used to hold now reach contributors through the plugin rather than through that file being read.

### Negative — trade-offs

- Three plugins where the first sketch had one, and three dependency edges to keep accurate.
- Ambient-versus-on-demand is a distinction an author now has to hold, and nothing mechanical enforces it: a description rewritten to trigger on ordinary work turns an on-demand plugin ambient without any error being raised.
- Adopting `docs-standards` now pulls in two plugins rather than one.
  That is the intended composition, as `docs-standards` → `markdown-standards` already was ([ADR-004](004-markdown-standards-plugin.md)), but a repository wanting only the docs structure can no longer get it alone.
- `writing-styles` can be installed directly by someone expecting a fuller catalogue than one style.
- The rules are drawn from review findings on this marketplace's own plugins, so they are evidenced rather than exhaustive.
  Further conventions are expected to arrive the same way, by being caught in review first.
