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

*Last verified 2026-10-17, through both `curl` and `gh api`: REST for an in-scope repository → `200`; `/graphql`, `search/issues`, and an out-of-scope repository → `403`; `GET …/pulls/<n>/ccr/review_threads` → `200`; `POST …/ccr/ready_for_review` → `{"draft":false}`; `POST …/ccr/comments/<id>/resolve` → `"resolved":true`; a job's log download → refused at its blob-storage redirect; `raw.githubusercontent.com` → `200`; CA bundle present at the path above.
Re-probed 2026-07-29 for the download shapes: `/releases/download/…` → `200` (a real 9 MB asset), while `/archive/refs/tags/…` and `codeload.github.com` → `403`.*

- **The proxy serves GitHub's REST API for the repositories in the session's scope, and attaches the credential itself.**
  `curl https://api.github.com/repos/<owner>/<repo>/…` needs no token, and the image's `gh` — GitHub's own CLI — works the same way through `gh api repos/<owner>/<repo>/…`.
  Everything else is refused with a `403` whose body names the alternative: GraphQL, any path not under `repos/<owner>/<repo>/` (such as `search/issues`), and a repository outside the session's scope.
- **Most `gh` subcommands fail here, because they run on GraphQL.**
  `gh pr view`, `gh pr list`, `gh pr checks` and `gh issue list` all get the GraphQL `403`, while REST-backed ones such as `gh run list` and `gh run view` work.
  Translate a procedure written around `gh` into `gh api` calls on REST paths, or into the GitHub MCP; a field that exists only in GraphQL, such as `reviewDecision`, cannot be read here at all.
- **Job logs are out of reach on REST, though the endpoint is in scope.**
  `…/actions/jobs/<id>/logs` redirects to a `*.blob.core.windows.net` host that the proxy refuses, so read a job's log through the GitHub MCP's `get_job_logs` instead.
- **The proxy adds REST routes for what GraphQL would otherwise be needed for**, under `api.github.com/repos/<owner>/<repo>/pulls/<n>/ccr/`: `GET review_threads` returns each thread's `resolved` and `outdated` state with its comment IDs, `POST ready_for_review` takes a draft out of draft, and `POST comments/<comment_id>/resolve` resolves the thread that comment belongs to, taking the ID of any comment in it.
  The GraphQL `403` body names the rest — `POST comments/<comment_id>/unresolve`, `PUT` or `DELETE auto_merge`, and `POST convert_to_draft`.
  > **Verify:** `unresolve`, `auto_merge` and `convert_to_draft` are known from the `403` body alone; none has been exercised.
- **The GitHub MCP (`mcp__github__*`) reaches the same repositories**, and is the route that needs no translation.
- **How that connector then behaves is `connector-conventions:github`'s subject, not this plugin's** — most importantly that the text it returns for issues and pull requests is sanitised and lossy, so a description that reads as mangled or truncated must never be "fixed" on the strength of that read.
  Those properties belong to the MCP server and hold wherever it is used; only the fact that it is one of the routes belongs here.
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
  How to generate that lockfile is the repo's own convention, so follow its `CLAUDE.md`.

## `sleep` is blocked

The harness blocks `sleep`.
To wait, block on a backgrounded command or a Monitor loop that watches for the condition — never a foreground `sleep`.
A Monitor loop can watch a CI run as well, by polling the REST check-runs path with `gh api` (see `ci-iteration.md`).
