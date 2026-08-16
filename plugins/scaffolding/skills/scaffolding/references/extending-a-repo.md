# Extending an existing repo

Working in an already-established **owned** repo (verify ownership first — see `owned-vs-third-party.md`), you'll notice conventions it hasn't adopted yet: a standards plugin it doesn't enable, a shared CI workflow it's missing, or — worse — CI or config it **restates locally** that a shared workflow already provides.

## Suggest adoption without breaking flow

A gap is a **suggestion, not an interruption**.
Don't stop the work the user came to do to force an adoption.

> **🤖 Agent** — when you spot a missing or locally-restated convention, surface it as a suggested **prerequisite or follow-up**, and let the user choose: do it now in this session, defer it, or spin up a new session for it.
> Don't block their current task on it.

When the user opts for a **separate session**, hand them what they need to start it: a ready-to-paste **prompt** describing the adoption, and the **list of repositories** that session should be created with (the target repo, plus any helper repos it will need — e.g. `github-workflows` for a CI adoption; see `helper-repos.md`).

## When a rule contradicts what the user wants

Sometimes a plugin's rule genuinely conflicts with what the user wants in this repo.
That's one of two things — resolve it, don't just override silently:

- **A legitimate repo-specific exception** — the repo really does need to differ.
  Record it in the repo's own `CLAUDE.md` (which overrides the plugins for that repo), so the exception is explicit and future sessions honour it rather than re-flagging it.
- **A misinterpretation or a genuine gap/mistake in the plugin** — the rule is wrong, unclear, or too rigid.
  Fix it at the source: `add_repo` `flungo/claude-plugins` and open a PR that resolves the ambiguity (see `helper-repos.md`), so every repo benefits and the plugins stay the single source of truth.

Deciding which it is is the judgement call; when it's the plugin, prefer fixing the plugin over piling up per-repo exceptions.
