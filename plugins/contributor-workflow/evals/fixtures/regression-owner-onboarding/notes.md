# Provenance

This fixture reproduces a real regression: an agent ran `/ready-to-merge` on an actual PR and judged the commit history "clean" based on the commit *titles* alone, without checking whether the underlying diffs actually matched one logical change per commit.
They didn't — several commits bundled multiple unrelated changes together.

Names, domains, and org identifiers here are fictional and do not correspond to the original repo, person, or infrastructure.
The commit sequence, message pattern, and the specific ways the history was messy are preserved, because that's what the fixture is testing.

One simplification: the original PR also included a third runbook (`importing-repositories.md`) as its own commit in the corrected history.
This fixture omits it for brevity — it doesn't add a new failure pattern beyond what's already covered here.

## What was wrong with the original history

1. `ci: add plan-on-PR Terraform workflow and first-pass authentik resource` bundles an unrelated CI change with a Terraform resource.
2. `fix: place the github-nova workspace in the terraform-github project` is a fixup of the very first commit and should never have stood alone.
3. `docs: add GitHub provider token rotation runbook and secrets table` bundles two distinct docs (a runbook and a reference table).
4. `fix: reconcile authentik config to the live repo for a clean import` is a fixup of the resource added in commit 2.
5. `docs: relocate secrets to reference; add owner-onboarding runbook; naming + deviation conventions` is the worst offender — three unrelated things in one commit.
6. `docs: refine owner-onboarding runbook per review` is a trailing fixup of commit 5's runbook and should fold into it.

## Target clean history (6 commits)

1. `feat: add owners/nova skeleton for the personal account` — commit 1, with commit 3's workspace-placement fix folded in.
2. `ci: add plan-on-PR Terraform workflow` — commit 2's CI half only.
3. `feat: adopt authentik.nova.dev into Terraform` — commit 2's resource half, with commit 5's fixup folded in, bundling the naming + deviation conventions from commit 6 (they became relevant here).
4. `docs: add owner-onboarding runbook` — commit 6's runbook, with commit 7's "refine per review" folded in, including its own `docs/index.md` row.
5. `docs: add GitHub provider token rotation runbook` — split out of commit 4, including its own `docs/index.md` row.
6. `docs: add secrets reference and point CLAUDE.md/onboarding doc to it` — split out of commit 4, including its own `docs/index.md` row.

See `evals.json` for the assertions checked against whatever structure the agent under test actually produces.
