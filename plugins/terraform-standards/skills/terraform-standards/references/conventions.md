# HCL conventions

## Organising `.tf` files — by concern or by subject

Split configuration across files so a reader can find a resource by guessing the filename, and keep the split consistent within a repo.

The plumbing is always its own file, grouped by concern: `providers.tf`, `terraform.tf` (version + backend), `variables.tf`, `outputs.tf`.

For the managed resources, two groupings are both valid — pick per repo (its `CLAUDE.md` decides):

- **By resource type / concern** — `repositories.tf`, `dns.tf`, `secrets.tf`: all resources of one kind together.
  Best when resources are largely cross-cutting or singletons, or when a concern (all DNS, all IAM) is the natural unit to reason about.
- **By subject / entity** — `terraform-github.tf`, `claude-plugins.tf`: everything that defines one subject (a repo, and its branch protection, secrets, webhooks, …) in a single file named for that subject.
  Best when the config is many similar composite entities that each span several resource types and you reason about them one at a time — you open one file and see a subject's *entire* definition.

Rule of thumb: when one subject's definition is spread across several resource types, prefer by-subject; when you have many instances of a few types with little per-entity composition, prefer by-concern.

## Resource names mirror the real object

A resource's local name matches the real object's name (the repository, team, domain, secret, …), with any character not valid in a Terraform identifier replaced by `_`.
Terraform identifiers allow letters, digits, `_`, and `-` and must start with a letter or `_`; `.` is the usual offender.

- `authentik.flungo.net` → `github_repository.authentik_flungo_net`
- `claude-mcp` → `grafana_service_account.claude_mcp`

The local name is then predictable from the object, and the object from the local name.

## Sensitive values are variables, never literals

Every secret — a token, password, private key, or API key — is a variable declared `sensitive = true`, never hard-coded in `.tf`.
Give a sensitive variable no default that bakes in a value, and prefer no default at all where an empty value could do damage, so a missing value fails fast rather than applying a blank.
In docs and examples, write a **placeholder** (e.g. `<github-token>`) and note where the real value lives (an Actions secret, a secrets manager, an env var) — never the value itself.

## Durations as arithmetic

Write a raw-seconds duration as arithmetic so it reads: `30 * 86400 # 30 days`, not `2592000`.
This applies when the field takes raw seconds; a provider field that accepts a friendly string (`"90d"`, `"5m"`) takes the string as-is.

## Pin the provider, commit the lock

Pin each provider in the `terraform` block (e.g. `version = "~> 6.0"`) and set `required_version`, and **commit `.terraform.lock.hcl`** so every run — local, CI, or another machine — resolves the same provider builds.
A constraint alone is not a pin: without the lockfile every CI run silently takes the newest version that satisfies it, so a provider release can change a plan with no change to the config.

The lockfile belongs to each **root module** — a repo with several (one per environment or owner) commits one in each.

### Lock every platform in play

A lockfile records a hash per provider *package*, so a platform with no recorded hash fails the next `init` with a checksum error rather than falling back.
Generate it with the platforms that actually run the config — CI plus whatever the humans use — rather than letting whichever machine ran `init` first decide:

```bash
cd <root-module>
terraform providers lock \
  -platform=linux_amd64 -platform=linux_arm64 \
  -platform=darwin_amd64 -platform=darwin_arm64
```

Bumping a provider is then a **deliberate, reviewable commit of its own**: regenerate the lock, and let the PR's plan show what the new version changes.
CI must never update the lockfile — a run that quietly rewrites it defeats the point.

> If the environment can't run `init` at all (no binary, a blocked registry), fix *that* first — an un-committed lockfile is usually a symptom of it, not a decision.
> For Claude Code Web specifically, the `claude-code-web` plugin's `egress-and-tooling.md` has the working recipe.
