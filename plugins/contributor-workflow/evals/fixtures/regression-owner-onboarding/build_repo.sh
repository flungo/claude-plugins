#!/usr/bin/env bash
# Builds the sanitized regression fixture: a Terraform repo managing GitHub
# resources, with the same messy-but-well-titled commit pattern that a real
# session once approved as "clean" (see notes.md). Names are fictional.
# Usage: ./build_repo.sh [target-dir]   (default: ./terraform-github-nova)
set -euo pipefail
TARGET="${1:-terraform-github-nova}"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.email "agent@example.invalid"
git config user.name "Fixture Agent"

mkdir -p owners/nova docs .github/workflows
cat > README.md <<'EOF'
# terraform-github

Terraform-managed GitHub resources across personal and org accounts.
EOF
git add -A
git commit -q -m "chore: seed repo" --date="2026-04-01T09:00:00"

git checkout -q -b feature/nova-owner-onboarding

# b288063-equivalent
cat > owners/nova/main.tf <<'EOF'
terraform {
  cloud {
    organization = "acme-oss"
    workspaces { name = "github-nova" }
  }
}

provider "github" {
  token = var.github_token
}

variable "github_token" {
  sensitive = true
}
EOF
git add -A
git commit -q -m "feat: add owners/nova skeleton for the personal account" --date="2026-04-01T10:00:00"

# c9d16d2-equivalent: anti-pattern, bundles CI with an unrelated resource.
cat > .github/workflows/terraform.yml <<'EOF'
name: terraform
on: [pull_request, push]
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: terraform plan
EOF
cat > owners/nova/repositories.tf <<'EOF'
import {
  to = github_repository.authentik_nova_dev
  id = "authentik.nova.dev"
}

resource "github_repository" "authentik_nova_dev" {
  name = "authentik.nova.dev"
}
EOF
git add -A
git commit -q -m "ci: add plan-on-PR Terraform workflow and first-pass authentik resource" --date="2026-04-01T14:00:00"

# b13f26a-equivalent: a fixup of commit 1, should end up folded into it.
cat > owners/nova/main.tf <<'EOF'
terraform {
  cloud {
    organization = "acme-oss"
    workspaces {
      name    = "github-nova"
      project = "terraform-github"
    }
  }
}

provider "github" {
  token = var.github_token
}

variable "github_token" {
  sensitive = true
}
EOF
git add -A
git commit -q -m "fix: place the github-nova workspace in the terraform-github project" --date="2026-04-01T15:00:00"

# 291e3e4-equivalent: anti-pattern, bundles two unrelated docs.
cat > docs/github-provider-token-rotation.md <<'EOF'
# Rotating the GitHub Provider Token

1. Generate a new fine-grained PAT.
2. Update the `github_token` variable in Terraform Cloud.
3. Revoke the old token.
EOF
cat > docs/secrets.md <<'EOF'
# Secrets

| Name | Where | Notes |
|---|---|---|
| github_token | Terraform Cloud variable | fine-grained PAT |
EOF
git add -A
git commit -q -m "docs: add GitHub provider token rotation runbook and secrets table" --date="2026-04-02T09:00:00"

# b1f4bb1-equivalent: a fixup of commit 2's resource, should fold into it.
cat > owners/nova/repositories.tf <<'EOF'
import {
  to = github_repository.authentik_nova_dev
  id = "authentik.nova.dev"
}

resource "github_repository" "authentik_nova_dev" {
  name        = "authentik.nova.dev"
  description = "SSO for the nova homelab"
  visibility  = "private"
}
EOF
git add -A
git commit -q -m "fix: reconcile authentik config to the live repo for a clean import" --date="2026-04-02T11:00:00"

# 3afe0be-equivalent: the main anti-pattern — three unrelated things bundled
# into one commit (a runbook, a doc relocation, and unrelated conventions).
cat > docs/onboarding-an-owner.md <<'EOF'
# Onboarding a New Owner

1. Create `owners/<name>/` from the `owners/nova` skeleton.
2. Set the Terraform Cloud workspace name and project.
3. Open a PR; CI will post a plan comment.
EOF
cat > docs/index.md <<'EOF'
- [Onboarding a New Owner](onboarding-an-owner.md)
- [Secrets](secrets.md)
EOF
cat > CLAUDE.md <<'EOF'
# Conventions

- Resource names mirror the repo name, with `.` replaced by `_`.
- Prefer the standard module shape; deviations must be justified in a
  comment above the deviating block.
EOF
git add -A
git commit -q -m "docs: relocate secrets to reference; add owner-onboarding runbook; naming + deviation conventions" --date="2026-04-02T16:00:00"

# 2b79934-equivalent: a trailing fixup that should fold into the runbook
# commit above rather than standing alone.
cat > docs/onboarding-an-owner.md <<'EOF'
# Onboarding a New Owner

1. Create `owners/<name>/` from the `owners/nova` skeleton.
2. Set the Terraform Cloud workspace name and project (see ADR-002).
3. Open a PR; CI will post a plan comment before you merge.
4. After merge, confirm the apply succeeded in Terraform Cloud.
EOF
git add -A
git commit -q -m "docs: refine owner-onboarding runbook per review" --date="2026-04-03T09:00:00"

echo "--- log ---"
git log --oneline
