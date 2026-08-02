# Running the Markdown checks locally

Both checks the CI runs are runnable locally, and both are worth running before pushing — a lint or link finding costs a CI round-trip to discover otherwise.

```bash
npx markdownlint-cli2@<version> '**/*.md'                      # style; must be 0 issues
lychee --offline --include-fragments --no-progress '**/*.md'   # internal links + anchors
```

If a local run reports findings in files you do not recognise — vendored dependencies, a provider's own `README.md` — check the repo's `ignores`.
markdownlint does not read `.gitignore`, so a gitignored build or provider directory is still linted locally even though CI never sees it.
A Terraform repo needs `**/.terraform/**` ignored for exactly this reason; see `adopt-markdown-ci.md`.

## Get the linter version from a CI run, never from a note

`<version>` above is not a constant, and **no repo should record one as if it were**.

The reusable `markdown-lint.yml` tracks `markdownlint-cli2-action` by **major tag**, so the linter version floats underneath it: a Dependabot bump moves it with no change in any consumer.
It has already moved from `@v19` (markdownlint-cli2 0.17.2 / markdownlint 0.37.4) to `@v24` (0.23.1 / 0.41.1) that way.

The failure mode this creates is worse than not pinning at all:

- **Too old** and you get a clean local pass against a linter CI no longer runs — a *false* pass, which is how `MD060` reached the fleet unannounced and failed tables that had been clean for months.
- **Too new** and you chase findings CI never reports.

So read the version off the first line of the `markdown-lint` job's log in any recent run of the repo, and use that.
If a repo's `CLAUDE.md` names a version, treat it as a datestamped observation rather than a pin — and if it reads as a pin, fix it.

When a bump does introduce a rule nobody chose, `new-lint-rules.md` is the procedure.

## Installing lychee

`lychee` has no npm or pip package.
In a locked-down sandbox its release tarballs are commonly proxy-blocked, so install from source:

```bash
cargo install lychee --locked
```

`--locked` matters: without it, cargo resolves fresh dependency versions and the build is materially more likely to fail.

**Start it in the background, early.**
It builds from source and takes minutes, so kick it off as soon as a session looks like it will touch Markdown — not at the point you want to run the check, where the whole build lands on the critical path as dead waiting time.

```bash
cargo install lychee --locked   # in the background; check back before the link check
```

`markdownlint-cli2` needs no equivalent — `npx` fetches it in seconds, so it can wait until it is wanted.

## What cannot be validated locally

**Only the offline link check is meaningful locally.** It is deterministic and needs no network, so a local pass is a real pass.

**The external URL sweep is not.** It is `workflow_dispatch`-only, needs `LYCHEE_GITHUB_TOKEN` to reach private repos, and depends on the runner's egress — which is not a sandbox's.
Verify it in GitHub by dispatching the workflow, never locally.
Curating `.lycheeignore` from a local or tokenless run records token artifacts as if they were dead links; see `cross-references.md`.
