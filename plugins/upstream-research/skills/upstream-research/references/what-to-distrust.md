# What to distrust

These sources feel authoritative and aren't.
Treat each as a lead to confirm against the real source (`finding-sources.md`), not as a fact.

## Training data

Your own recall of an external component is **frozen at the training cutoff and often wrong on specifics** — exact option names, defaults, wire formats, and anything that changed in a recent version.
Use it to know *where to look*, never as the final answer for a specific value.

## Third-party posts and web-search summaries

Blog posts, Q&A answers, and search-result summaries are secondhand and frequently wrong on details.
A real example from this workspace: a web-search summary gave the env var `PROXY_HOPS` when the actual name is `TRUSTED_PROXY_DEPTH` — a wrong value that would have failed silently.
When a lead comes from one of these, confirm the specific against the source before using it.

## Generated docs

A project's **auto-generated** reference docs can be wrong or misleading even though they're "official".
Example: a provider's generated `curl` snippets pointed at `/api` when the real JMAP endpoint is `/jmap`, and its generated object docs described the wrong shapes.
Verify a generated-doc claim against the schema or handler in the source, not the rendered page.

## Archived, renamed, or predecessor repos

Before trusting a repo, confirm it's the **current, authoritative** one.
A predecessor repo can look right but be stale — a different framework, different storage keys, a different auth flow — and anything sourced from it will mislead.
Example: `stalwartlabs/webadmin` is the archived predecessor to `webui`; sourcing behaviour from it is a trap.
Check the repo isn't archived, isn't a fork, and is the one the project currently points to.
