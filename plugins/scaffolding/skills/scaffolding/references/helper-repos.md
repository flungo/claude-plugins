# Helper repos

Some of Fabrizio's work is achieved by pulling in a **helper repo** — a shared/infrastructure repo you don't normally have in a session, but `add_repo` when a task needs it, then **remove once the work is merged and validated**.
(`add_repo` mechanics and the "added for as long as required" discipline live in `claude-code-web`; this file is about *which* helper repos exist and *what* each is for.)

| Helper repo | For |
|---|---|
| [`flungo/github-workflows`](https://github.com/flungo/github-workflows) | The shared reusable CI. Adopt a workflow family into a repo, or create/extend a shared workflow. |
| [`flungo/claude-plugins`](https://github.com/flungo/claude-plugins) | These plugins. PR here to fix or extend a convention when a plugin rule is wrong (see `extending-a-repo.md`). |
| [`flungo/terraform-github`](https://github.com/flungo/terraform-github) | Creates new repos and manages existing repos' settings as Terraform. `add_repo`, open a PR, remove once merged. |

## github-workflows

### Adopting the shared CI

Adopt a family by **calling and pinning** its reusable workflow.
The full caller stem is always:

```yaml
uses: flungo/github-workflows/.github/workflows/<workflow>.yml@v1
```

`@v1` is a moving *branch* (not a tag) that fast-forwards on every merge there, so fixes reach the fleet automatically.

| Repo type | Workflow(s) — `flungo/github-workflows/.github/workflows/…@v1` | Adoption runbook (`docs/runbooks/`) |
|---|---|---|
| Terraform **config** repo | `terraform.yml`, opt-in `terraform-drift.yml` | `adopting-terraform-workflows.md` |
| Terraform **provider** repo | `terraform-provider-test.yml`, `terraform-provider-docs.yml`, `terraform-provider-release.yml` | `adopting-terraform-provider-workflows.md` |
| **Any** repo with Markdown | `markdown-lint.yml`, `markdown-links.yml` | `adopting-markdown-workflows.md` |
| **Every** repo | `version-check.yml` | `adopting-version-check.md` |

**Follow the runbook — it is the source of truth** for each caller's inputs, secrets, required `permissions:` block, and gotchas.
Don't paraphrase it here; open it (`add_repo` `github-workflows` if needed).

> **🤖 Agent** — read the current major to pin (`@v1` today) from `github-workflows` itself; a future breaking change cuts a new major and freezes the old, so don't assume `v1` is still current.

### Don't over-share — repo-specific stays in the repo

A shared workflow is justified only when there are **two clear consumers**, or a **clear repeat pattern** (a project *type* the fleet will have more of).
Otherwise the logic stays **defined in the repo**.
Don't reflexively promote one repo's CI to `github-workflows` — a single-consumer "shared" workflow is just indirection.

### Creating, extending, or adapting a shared workflow

When the work genuinely warrants a shared change: `add_repo` `github-workflows` and open a PR there.
To test it end-to-end against the consuming repo **before** it merges:

1. In the dependent (consumer) PR, **temporarily pin** the caller to the workflow's feature branch — `…/<workflow>.yml@<feature-branch>` instead of `@v1`.
2. Treat the consumer PR as **blocked on** the `github-workflows` PR being merged and released (its `@v1` advanced).
3. Once released, **revert the pin back to `@v1`** in the consumer PR before merging the main work.
4. Remove the `github-workflows` helper repo once both PRs are merged and it's no longer needed.

## terraform-github — repos as Terraform

New repositories, and existing repositories' settings, are managed as Terraform in `flungo/terraform-github`.
To create a repo or change its settings: `add_repo` `flungo/terraform-github`, open a PR adding/altering the repo's Terraform, and remove the helper repo once it's merged.
