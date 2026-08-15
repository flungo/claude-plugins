# Egress and tooling

The web sandbox routes all outbound traffic through an agent proxy and blocks some hosts and binaries outright.
These are the ones that cost time the first time.

## The egress proxy and its CA bundle

All outbound HTTPS goes through a pre-configured agent proxy, which terminates TLS with its own CA.
The CA bundle lives at `/root/.ccr/ca-bundle.crt`.

- **Point package managers at the bundle**, or TLS verification fails: `NODE_EXTRA_CA_CERTS`, `PIP_CERT`, and `CARGO_HTTP_CAINFO` all set to `/root/.ccr/ca-bundle.crt`.
- **Package registries are allow-listed** — `registry.npmjs.org`, `pypi.org`, and the crates index are reachable, so `npm`, `pip`, and `cargo` all work once the CA bundle is set.
- **Never disable TLS verification or unset `HTTPS_PROXY`** to get around a failure.
  If a tool fails TLS verification or gets a `403`/`405`/`407` from the proxy, check `curl -sS "$HTTPS_PROXY/__agentproxy/status"` and `/root/.ccr/README.md` for the per-tool fix.

## The network allowlist is the user's to extend

What the proxy allows is a **user-controlled allowlist**, not a fixed wall.
If a host you need is blocked and there's a **durable, repeated benefit** to reaching it (not a one-off), you can **ask the user to add it to the allowlist** instead of only working around it or offloading to CI.

Two things to weigh before asking:

- The allowlist lives in the **environment** (see `sessions.md`), so anything added is added for **every** future session using it — only propose hosts that are fine to have globally, and confirm before the user adds them.
- A genuine one-off is better offloaded to CI or read via `raw.githubusercontent.com`; reserve an allowlist request for access that recurs and is worth making permanent.

Which hosts a given environment already allows is **not** recorded in this plugin — it varies per environment.
Take it from the system prompt, from a companion skill that records that environment, or by probing.

## GitHub access

*Last verified 2026-07-24: `api.github.com` → `403`, `raw.githubusercontent.com` → `200`, CA bundle present at the path above.
Re-probed 2026-07-29 for the download shapes: `/releases/download/…` → `200` (a real 9 MB asset), while `/archive/refs/tags/…` and `codeload.github.com` → `403`.*

- **Use the GitHub MCP (`mcp__github__*`) for anything API-shaped** — PRs, issues, review threads, checks, workflow runs and dispatch.
  There is no `gh` CLI in web sessions, and `api.github.com` returns `403` through the proxy.
- **`git` over `github.com` works** for repositories in the session's scope (clone, fetch, push).
- **Read public files with `WebFetch` against `raw.githubusercontent.com`** (`https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`) — this works unauthenticated, even for repositories outside the session's scope.
- **Source archives for an out-of-scope repo are blocked; published release assets are not**.
  `github.com/<owner>/<repo>/archive/…` and `codeload.github.com/…` return a `403` with an `"access not enabled"` JSON body, so repository *source* must come from `raw.githubusercontent.com` (or `add_repo` + clone).
  A **release asset** under `github.com/<owner>/<repo>/releases/download/…` does download, which is how a published binary or a Terraform provider zip can be fetched directly.

## Terraform

*Last verified 2026-07-29, in an environment whose allowlist had been extended with `registry.terraform.io`: `releases.hashicorp.com` → `200`, `registry.terraform.io` → `200`, `checkpoint-api.hashicorp.com` → `403`; a full `terraform init` in a real repo installed a provider and wrote a lockfile.*

There is no `terraform` binary in the image, but a web session can run `fmt`, `init`, and `validate` — worth doing before pushing, since it catches syntax and type errors without spending a CI round-trip.

```bash
S=<scratchpad>                    # a writable temp dir, never the repo
# Subshell, so the zip and the binary land in $S and the cwd stays at the repo root —
# `curl -O` and `unzip` both write to the *current* directory, not to $S.
( cd "$S" \
  && curl -sSLO https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip \
  && unzip -q -o terraform_1.9.8_linux_amd64.zip )

export CHECKPOINT_DISABLE=1       # see below
$S/terraform fmt -check -recursive
cd <root-module>
$S/terraform init -backend=false  # no backend credentials needed
$S/terraform validate
```

- **`init` needs `registry.terraform.io`**, which is not in the default allowlist — so it resolves and installs providers only in an environment whose allowlist has been extended with it.
  That extension is a worked example of the allowlist section above: the benefit recurs across every Terraform repo, which is what makes it worth making permanent rather than working around.
  If `init` fails to resolve a provider, ask for the host rather than assuming Terraform can't run here.
- **`checkpoint-api.hashicorp.com` is not in the default allowlist** and returns `403`.
  It is only HashiCorp's optional version-check ping and nothing fails without it, so set `CHECKPOINT_DISABLE=1` to keep the error out of the output.
- **`-backend=false` skips backend initialisation**, so `init` needs no state-backend token.
  A *remote* backend's credentials are usually a CI secret the session doesn't hold.
- **`plan` is generally not possible** — it needs both the backend credentials and the provider's own credentials.
  Leave `plan` to CI and treat the PR-posted plan as the authority; see `ci-iteration.md`.
- **Afterwards, delete `.terraform/`** (large, and gitignored by the standard Terraform `.gitignore`) but **keep `.terraform.lock.hcl`, which is committed** — if `init` changed it, that is a real change to review and commit, not an artifact to discard.
  Generating that lockfile is a repo-level convention; see the `terraform-standards` plugin.

## `sleep` is blocked

The harness blocks `sleep`.
To wait, block on a backgrounded command or a Monitor loop that watches for the condition — never a foreground `sleep`.
A Monitor loop only covers conditions *this container* can observe, though — a CI run is not one of them, since the script would need a `gh` CLI the session doesn't have (see `ci-iteration.md`).
