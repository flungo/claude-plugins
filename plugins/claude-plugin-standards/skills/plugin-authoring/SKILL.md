---
name: plugin-authoring
description: Fabrizio's conventions for authoring Claude Code plugins and the marketplace that carries them. Consult this whenever adding a plugin, adding or renaming a skill, editing a plugin.json or marketplace.json, declaring a dependency, or deciding what to bump a version to. Covers the directory and manifest layout, composing via first-party dependencies and declaring every one you reference, whether a plugin is ambient or on-demand and what may depend on it, filing a fact by what it is a property of, skill naming in single- and multi-skill plugins, keeping cross-references current by basename, the reserved word that makes a skill silently fail to load on claude.ai, YAML frontmatter hazards in SKILL.md, validating and test-installing before committing, and the minor-versus-patch test. The prose inside a plugin follows the instructional-writing style in the writing-styles skill, a declared dependency.
---

# Plugin Authoring

How a plugin in this marketplace is **structured** — its directories, manifests, dependencies, names, and versions.

How its agent-facing **prose** is written is a separate concern, and belongs to the instructional-writing style in the **`writing-styles`** skill, a declared dependency of this plugin.
That style governs every `SKILL.md` and reference file here.
In brief: state the current truth rather than the document's own history, converge on plain fact over time, fix wrong guidance at its source instead of annotating it, and never direct an agent to do what only the user can do.
Read the style itself before writing or revising any skill content.

**These conventions complement repo/context rules, they never supersede them** — where a repo's `CLAUDE.md` or `CONTRIBUTING.md` specifies something different, follow the repo.

## Layout

A plugin is one directory under `plugins/<name>/`, registered in the marketplace's `.claude-plugin/marketplace.json`:

```text
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json              the manifest: name, description, version, dependencies
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md             the skill — frontmatter plus a short router
│       └── references/          the detail SKILL.md points at, one file per area
└── evals/                       dev-time fixtures; never loaded at runtime
```

A plugin ships a script it owns under `scripts/`, and a hook under `hooks/`, beside `skills/`.

## Composition

- **Compose via first-party dependencies.**
  Where a plugin builds on another, list it in the plugin's `dependencies` array (bare string = latest in the same marketplace).
  Installing the dependent auto-installs the dependency.
  **Where a plugin references another, it declares the dependency** — including where a bundle is expected to supply it anyway, since a bundle is a convenience rather than a guarantee and any plugin can be installed on its own.
  Do not depend on third-party marketplaces ([ADR-001](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/001-marketplace-structure.md), [ADR-002](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/002-documentation-and-adr-model.md)).
- **Cite a dependency's skill or reference by name, never by path, and share through a dependency rather than a symlink.**
  Each plugin is copied into its own cache directory at install, so a path reaching outside it does not resolve at runtime.
  The name is the stable address, and a declared dependency guarantees it is installed.
- **Know whether a plugin is ambient or on-demand — it decides what may depend on it.**
  An **ambient** plugin applies its conventions by being enabled: its skill description triggers on ordinary work, so enabling it in a scope imposes it across that scope.
  An **on-demand** plugin applies nothing until something names it, so enabling it imposes nothing.
  This is a property of how the skill is written, not an install scope; the platform has only user, project, and local.
- **An on-demand plugin is scope-agnostic; an ambient one is not.**
  Because enabling an on-demand plugin changes no behaviour, it is safe as a dependency of a user-scope *and* a project-scope plugin.
  That holds only while everything it depends on is also on-demand: a single ambient dependency makes the whole chain ambient and carries its conventions into every scope the dependent reaches.
  An ambient plugin may only be depended on from within its own scope.
- **Never reference a user-scope-only plugin from a project-scope one.**
  A plugin that is never repo-adopted cannot be declared as a dependency by one that is ([ADR-003](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/003-owned-vs-third-party-adoption.md)), and pointing at it anyway leaves a reference that dangles wherever the dependent is enabled.
  This holds however the plugin is written: being scope-*only* is a designation about where a plugin may be adopted at all, so it binds even where being on-demand would otherwise have made the dependency safe.
  Where both need the same rule, put it in an **on-demand** plugin they both depend on and cite it by name.
  Where it cannot be made on-demand, cite the **ADR** that records it (by full URL, since an installed plugin has no `docs/` tree beside it), or state the rule locally.
- **File a fact by what it is a property of, not by where you found it.**
  A connector's behaviour — what a tool returns, mangles, or omits — belongs to the connector's own plugin, so it loads wherever that connector is used; which tools exist at all belongs to the surface plugin; platform behaviour an agent reasons about away from any tool stays with the domain plugin that owns the subject ([ADR-008](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/008-connector-behaviour-belongs-to-the-connector.md)).
  A connector skill never tells a session to prefer its connector over some other tool — that is the environment's call, and the skill is consulted once the agent is already using it.
- **Keep generalisable guidance separate from the author's own configuration.**
  A plugin whose content would hold for any reader stays that way; the concrete settings *the author* has applied — an environment's allowlist, its variables, its setup — live in a companion plugin that depends on it, so neither is diluted by the other ([ADR-005](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/005-generic-plugins-and-personal-configuration.md)).

## Naming

- **A skill's `name` must not contain `claude`.**
  claude.ai's marketplace ingestion rejects it outright — `plugin_upload_skill_upload_name_reserved_words`, *"Skill name in SKILL.md cannot contain the reserved word 'claude'"* — so the skill silently never loads on that surface.
  Nothing local catches this: `claude plugin validate` passes, and Claude Code loads the skill normally, so the only signal is the marketplace's `sync_errors` after a sync.
  The restriction binds **skills only**, on the evidence of a plugin whose name carries the word syncing while its own skill was rejected, so a plugin may keep such a name while its skill is named for what it governs.
  Prefer a skill name that describes the domain without naming the product.
- **A single-skill plugin names its skill after itself**, so a mismatch is a signal that something forced it — the reserved word above being the usual cause.
  A **multi-skill** plugin names each skill for the axis that varies within it instead, the plugin name supplying the rest: a `connector-conventions` plugin carries `google-drive`, not `drive-conventions`, which would say "conventions" twice in `<plugin>:<skill>`.
- **Name for the domain, not the initial slice** — plugin names are install identifiers, so a rename is breaking.
  A name that fits only the first skill will sit wrong as soon as a second arrives.

## Keeping cross-references current

A skill or reference is cited by **basename** — `cloud-sessions`, `instructional-writing` — never by path, so the basename is what a search can find.
Use that same basename everywhere the file is referred to, in other plugins and in a repo's own docs, or the search stops working.

- **After editing a skill or a reference**, search the repo for its basename and read each hit.
  A summary elsewhere that paraphrases what you just changed is the thing most likely to have gone stale.
- **After renaming one**, search for the old basename and replace each genuine reference to it.
  Leave anything that legitimately names the old thing, such as an ADR recording the rename.

## `SKILL.md` frontmatter

- **The frontmatter is YAML** — keep `name` and `description` on single lines, and **avoid a colon followed by a space (`:` + space) inside an unquoted value**, which parses as a mapping and silently drops the frontmatter.
- The `description` is what drives skill triggering; write it for that.
  For an on-demand plugin, write it to trigger on *being named* rather than on the work itself, and say in it that the skill applies nothing on its own.

## Before committing

- **Validate:** `claude plugin validate .` for the marketplace and `claude plugin validate plugins/<name>` for each plugin.
- **Test-install from the local path** and confirm the skill loads and any dependency resolves.

A local-path install skips any symlink whose target lies outside the plugin's own directory, while the same symlink is dereferenced and copied for a plugin installed from the marketplace's git source.
Content shared that way is therefore present in production and absent under test, which is why sharing runs through a dependency here.

## Versions

Bump the version when a plugin's behaviour or footprint changes, and update the matching `marketplace.json` entry in the same commit.
These are content plugins pulled from a repo rather than immutable releases, so the version is a human signal rather than a resolver input — keep it cheap.

- **Minor** for anything a consumer would notice: a skill or command added or removed, a new dependency or hook, a *newly* shipped script, or a convention change that alters what an agent does.
- **Patch** for wording that clarifies without changing a rule, and for fixing a shipped script so that it finally does what it already claimed to — the offering is the same, it just works now.
- **Major** for a break — a rename, a removed command, or a reversal that invalidates a repo's existing `.claude/settings.json`.

The test between minor and patch is whether what the plugin offers has changed, not how big the diff was.
