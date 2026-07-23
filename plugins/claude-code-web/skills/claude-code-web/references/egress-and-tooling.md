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
If a host you need is blocked and there's a **durable, repeated benefit** to reaching it (not a one-off), you can **ask Fabrizio to add it to the allowlist** instead of only working around it or offloading to CI.

Two things to weigh before asking:

- The allowlist lives in the **single shared environment** (see `sessions.md`), so anything added is added for **all** his future sessions — only propose hosts that are fine to have globally, and confirm before he adds them.
- A genuine one-off is better offloaded to CI or read via `raw.githubusercontent.com`; reserve an allowlist request for access that recurs and is worth making permanent.

## GitHub access

*Last verified 2026-07-24: `api.github.com` → `403`, `raw.githubusercontent.com` → `200`, CA bundle present at the path above.*

- **Use the GitHub MCP (`mcp__github__*`) for anything API-shaped** — PRs, issues, review threads, checks, workflow runs and dispatch.
  There is no `gh` CLI in web sessions, and `api.github.com` returns `403` through the proxy.
- **`git` over `github.com` works** for repositories in the session's scope (clone, fetch, push).
- **Read public files with `WebFetch` against `raw.githubusercontent.com`** (`https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`) — this works unauthenticated, even for repositories outside the session's scope.
- **Don't `curl` a `github.com` release or download URL for an out-of-scope repo** — the proxy returns an "access not enabled" JSON body instead of the file.
  Use the `raw.githubusercontent.com` + `WebFetch` path instead.

## `sleep` is blocked

The harness blocks `sleep`.
To wait, block on a backgrounded command or a Monitor loop that watches for the condition — never a foreground `sleep`.
