# CI iteration — offloading what the sandbox can't (or shouldn't) run

Some work is better pushed to CI than run in the session — a step the environment's network policy blocks, a toolchain that can't be installed, a build slow enough to waste the session on, or a step that **needs repo-specific secrets**.
That last reason is easy to underrate: Claude Code Web has no secrets management, and an environment shared across sessions (see `sessions.md`) can't hold per-repo, correctly-scoped, rotated secrets without a real maintenance burden — whereas CI already needs and maintains exactly those secrets, scoped to the repo.
So a task that depends on a repo's secrets belongs in CI, not the session.
The pattern is the same each time: **push the branch and iterate against CI**, reading the job logs, instead of fighting the sandbox.

But first — **don't assume something is blocked.
Verify.**
What's reachable is set by the environment's network policy (see the SKILL's note on volatility), so it varies between environments and changes over time.

## What's actually restricted — check, don't assume

*Last verified 2026-07-24, in this environment; a different environment's policy may differ.*

- **Docker works — but the daemon isn't running by default; you start it.**
  `docker`/`dockerd` are installed (Engine 29.x), but there's no daemon socket until you launch `dockerd` yourself (needs root; `sudo` is available).
  Start it with the agent proxy in its environment so image pulls route through the proxy — then pull and run work.
  Verified 2026-07-24 by pulling and running `alpine:3.20` (`echo` from inside the container, exit 0):

  ```sh
  sudo -n env HTTP_PROXY="$HTTPS_PROXY" HTTPS_PROXY="$HTTPS_PROXY" NO_PROXY=localhost,127.0.0.1 dockerd >/tmp/dockerd.log 2>&1 &
  until docker info >/dev/null 2>&1; do :; done   # wait for the socket (no sleep in the sandbox)
  docker run --rm alpine:3.20 echo ok
  ```

  So container-based work runs here once the daemon is up.
  A more restrictive environment policy could still block registry egress — if a pull fails after the daemon is up, that's the policy, not a universal rule.
- **`api.github.com` returns `403`; `raw.githubusercontent.com` returns `200`.**
  Use the GitHub MCP for API work and `WebFetch` on `raw.githubusercontent.com` for public files (see `egress-and-tooling.md`).
- **Installing a toolchain** depends on how it ships: a registry-installable tool (npm/pip/cargo) works once the CA bundle is set; a binary that only ships as a blocked `github.com` release download does not.
- **Long compiles** (e.g. `cargo install lychee`, a few minutes) work but are slow — background them, or move them to CI.

Reproduce the network checks:

```sh
curl -sS -m 20 -o /dev/null -w '%{http_code}\n' https://registry-1.docker.io/v2/   # 401 = reachable (needs auth)
curl -sS -m 20 -o /dev/null -w '%{http_code}\n' https://api.github.com/            # 403 = blocked here
```

If a host is genuinely blocked but you'll need it repeatedly, extending the **user-controlled allowlist** is an option too — see `egress-and-tooling.md` — not only offloading to CI.

## The pattern — push and iterate on CI

When a step genuinely can't run here, or is heavy enough to be worth offloading:

- **Push to the feature branch and read the CI job log**, iterating there.
  Trigger a run through the GitHub MCP (`actions_run_trigger`); `workflow_dispatch` with an explicit `ref` works on a feature branch *before* the workflow exists on the default branch.
- **Provision required tokens/secrets before a verification run**, or its findings are noise.
  (A tokenless lychee dispatch, for instance, floods the auto-issue with false `404`s on private cross-repo links — token artifacts, not dead links.)
- **Watch the run through the GitHub MCP, not a Monitor script.**
  The Monitor tool's polling examples all shell out to a `gh` CLI that a web session doesn't have, and `api.github.com` is blocked through the proxy, so a watch script can't observe check status at all — it will sit silent rather than fail loudly.
  Instead background a timer and re-check `pull_request_read` with `get_check_runs` on a later turn.
  Foreground `sleep` is blocked, so the timer itself has to be a backgrounded loop (see `egress-and-tooling.md`).

## Probe, don't assume

> **🤖 Agent** — before treating a restriction as real, probe it: a bare `curl -sS -D- -o /dev/null <host>` that returns any HTTP status (even `401`/`403`/`400`) proves the host is reachable; only a proxy denial (a `403` with an `x-deny-reason` or "access not enabled" body, or a refused connection) is an actual block.
