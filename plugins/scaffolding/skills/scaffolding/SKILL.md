---
name: scaffolding
description: Fabrizio's guide for setting up, building out, and extending repos across his fleet. Use it when creating a repo, wiring up CI, bringing an existing repo up to standard, or deciding which of his conventions a repo should take on. The gate is ownership — a repo he owns (verified, not just in his namespace) adopts his conventions and standards plugins; a fork or third-party repo gets nothing adopted without his explicit consent. It routes to the shared CI in flungo/github-workflows and the helper repos (github-workflows, claude-plugins, terraform-github) you add_repo as needed. Personal (user scope) — always on for his account.
---

# Scaffolding

How to set up, build out, and extend repos the way Fabrizio's fleet does — and how to behave in repos he doesn't own.

## Start at the gate — is the repo his?

**The first thing this plugin does is determine ownership**, because everything else depends on it — and namespace alone doesn't settle it (he forks third-party repos into his namespace to contribute).
See `references/owned-vs-third-party.md`.

- **Owned** (his, verified not a fork) → adopt his conventions at repo level.
- **Third-party** (a fork, or someone else's project) → this plugin does **nothing** proactive: adopt nothing into the repo, work within its own conventions, and adopt his plugins or CI only with his **explicit consent**.

## In an owned repo

- **Building out a fresh repo** → bring it to standard *from the start* (core plugins, initial `CLAUDE.md`, Diátaxis docs + a build-out plan, content stubbed together with the plugin that governs it).
  See `references/building-out-a-repo.md`.
- **Extending an existing repo** → spot conventions it hasn't adopted (or restates locally) and *suggest* them as a non-blocking prerequisite or follow-up, without derailing the current task.
  See `references/extending-a-repo.md`.

## The helper repos

Shared/infrastructure repos you `add_repo` when a task needs them and remove once merged — `github-workflows` (shared CI), `claude-plugins` (these plugins), `terraform-github` (repos-as-Terraform).
Which is which, how to adopt the shared CI, when *not* to promote something to a shared workflow, and the feature-branch pin-and-revert dance for changing one: `references/helper-repos.md`.

This plugin is personal (user scope) — always on when Fabrizio works, in any repo — which is why it also governs behaviour in repos he doesn't own.
