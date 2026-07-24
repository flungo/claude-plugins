# Finding and reading authoritative sources

The authoritative source for how a component behaves is, in order:

1. **The component's own source code** — the ground truth: the schema, the handler, the constant.
2. **The project's official docs / website repo** — authoritative for intent and usage, but it can lag the code.
3. **The project's issue tracker and changelog** — for version-specific changes and known bugs.

Everything else (your memory, blog posts, Q&A sites, search summaries) is a *lead* to confirm against one of the above — see `what-to-distrust.md`.

## Reading a source without adding the repo

You usually only need to *read* an upstream repo, not work in it.
In the web sandbox `add_repo` can't add another owner's repo, and `api.github.com` is blocked (see the `claude-code-web` plugin), so:

- **Clone the source shallow** when you need to grep across it: `git clone --depth 1 https://github.com/<owner>/<repo>.git /tmp/<repo>-src`, then read the real files.
- **Fetch a single file** with `WebFetch` on `https://raw.githubusercontent.com/<owner>/<repo>/<ref>/<path>` — unauthenticated, any public repo.
- **List a tree** at `https://github.com/<owner>/<repo>/tree/<ref>/<path>`.

## Pin to a ref, and navigate from the root

- **Pin to the version or commit you depend on** when a fact is version-sensitive — read the file at that tag, not `main`, so the fact matches the version in use.
- **Navigate from the docs root, not a deep link.** Projects reorganise their docs between releases, so deep links to specific pages rot; start at the docs root, walk to the page, and confirm it's for the right version.

## Record where each fact came from

A fact is only as trustworthy as its provenance, and the next reader — or the next session — will want to re-check it.

> **🤖 Agent** — when a non-obvious upstream fact drives a decision, record its source next to where it's used: the repo and path (and ref, if version-sensitive) you verified it against, e.g. a `// VERIFIED against <owner>/<repo> <path>` comment or a citation in the doc.

## Curate the sources in the repo's CLAUDE.md

Finding the authoritative source once and re-finding it every session is waste — and different sessions can land on different, sometimes wrong, sources.
So **in a repo Fabrizio owns, or one that already keeps such a section, maintain a curated "Upstream sources" list in its `CLAUDE.md`**: the authoritative source for each third-party component the repo depends on, plus any traps to avoid.
Every session then starts from the same vetted set instead of re-researching.
In a repo you don't own that has no such section, don't add one — record what you find as per-fact provenance (above) instead.

Template for the section:

```markdown
## Upstream sources

When verifying behaviour, config options, or bugs for the components below,
consult these authoritative sources rather than training data, third-party
posts, or web-search summaries.

| Component | Source | URL |
|---|---|---|
| `<name>` | Source code | <repo URL> |
| `<name>` | Official docs / website | <docs or website-repo URL> |

**Do not use `<repo>`** — <why it misleads: archived, a predecessor, a fork>.
(Only when there is a known trap.)

Pin version-sensitive facts to <the tag/branch the repo depends on>; navigate
docs from the root, since deep links rot.
```

Keep it current: add a component's row when the repo starts depending on it, and add a "Do not use" line the first time a wrong or stale source costs a session.
