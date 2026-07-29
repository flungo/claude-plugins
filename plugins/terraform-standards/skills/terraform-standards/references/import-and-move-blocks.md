# Import and move blocks — transient, never persisted

Bringing an existing resource under management, and renaming or relocating one in state, are both done with **config-driven blocks** (Terraform ≥ 1.5) — `import {}` and `moved {}` — so the operation is reviewable in the diff, not run as an imperative `terraform import` / `terraform state mv` command.

Both kinds of block are **transient**: once applied they are dead code, and a follow-up PR removes them.
The committed config never carries a stale `import {}` or `moved {}` block.

## Importing an existing resource

Any resource that already exists in the real system must be imported before Terraform manages it, or an apply tries to create a duplicate (or fails).

1. **Write the resource and its `import {}` block together**, in the same `.tf` file, in one PR:

   ```hcl
   import {
     to = github_repository.authentik_flungo_net
     id = "authentik.flungo.net"
   }
   ```

2. **The plan should be import-only** — `N to import, 0 to add, 0 to change, 0 to destroy` — when adopting a resource *as it is*. A change here means the config doesn't match the live object, and an apply would mutate live infrastructure: reconcile the config first.

   **Exception — importing into a standardising module.** When you import into a module that deliberately enforces a standard and doesn't expose inputs to match the resource's current (drifted) state, the plan *will* show changes — those changes are the resource being brought to the standard, which is the point. Review that the plan contains **only** that intended standardisation (nothing destructive or surprising) and proceed. A clean import into matching config followed by a move into the module doesn't help — `moved` only renames an address, it never changes attributes — so it's pure overhead.
3. **Merge → apply** brings the resource into state.
4. **A follow-up PR removes the `import {}` blocks.**

## Moving or renaming a resource

When you rename a resource, move it into or out of a module, or otherwise change its address, use a `moved {}` block so Terraform updates state rather than destroying and recreating:

```hcl
moved {
  from = github_repository.old_name
  to   = github_repository.new_name
}
```

A `moved` block changes only the state address, never attributes, so its plan should be the move plus `0 to add, 0 to change, 0 to destroy`.
Merge → apply, then a **follow-up PR removes the block.**

> **🤖 Agent** — treat `import {}` and `moved {}` as scaffolding: they land in the PR that does the import or move, and a follow-up PR removes them once applied. Never let an import PR's plan show a change beyond the imports themselves *unless* it's the intended standardisation of importing into an opinionated module (see the exception above).
