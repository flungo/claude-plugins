## What's here

- **`owners/nova/`** — thin root module: cloud backend → `github-nova`
  workspace in the `terraform-github` project, the `github` provider, and
  the sensitive `github_token` variable.
- **`owners/nova/repositories.tf`** — `import {}` + `github_repository.authentik_nova_dev`,
  reconciled to the live repo from the CI-posted plan (0 changes).
- **`.github/workflows/terraform.yml`** — plan on PR (posted as a comment),
  scoped to `owners/nova` for now.
- **Runbooks:** `onboarding-an-owner.md`, `github-provider-token-rotation.md`.
- **Reference:** `secrets.md`.
- **Conventions (`CLAUDE.md`):** resource names mirror the repo name
  (`.`→`_`); standard-first module-deviation policy.
