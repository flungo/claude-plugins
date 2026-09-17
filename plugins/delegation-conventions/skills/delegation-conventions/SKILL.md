---
name: delegation-conventions
description: Fabrizio's conventions for handing work to another agent or session — currently which model it should run on. Consult this whenever starting a session from the one you are in, creating a Routine, or dispatching a subagent, and whenever any of those offers a model to choose. Always-on personal preferences; they complement a repo's own CLAUDE.md rather than overriding it.
---

# Delegation

How work is handed to something that will carry it out elsewhere — a session started from this one, a Routine that fires later, or a subagent dispatched within a turn.

These are defaults that **complement repo/context rules, never supersede them** — check the repo's own `CLAUDE.md`/`CONTRIBUTING.md` first, and where it differs, follow the repo.

## Choosing a model

**Where the model can be chosen, choose it rather than letting it be inherited.**
A tool that takes a model argument falls back to the calling session's when it is omitted, which makes the model an accident of where the work happened to start instead of a judgement about the work being handed over.

**Prefer Opus, at its latest version.**
It is the default for delegated work and the right answer wherever neither case below clearly applies.

- **Sonnet** suits a task that is simple *and* fully specified — the thinking is already done, and what remains is to carry out instructions that are all present in the prompt.
  Both halves have to hold: a short task still wants Opus where it has to work out what to do.
- **Fable** suits open-ended work that needs a great deal of design, but the bar it has to clear over Opus is a high one, and where that bar sits is not settled.
  So it is never yours to choose: put the case to the user — what it is about this task that Fable would serve better — and let them decide between Fable and Opus.
  Opus stands unless they say otherwise.

**Name the model by the identifier the surface offers, which is usually a short name such as `opus`.**
A short name keeps pointing at the current release, where a full versioned identifier remembered from elsewhere dates quietly.
Where a tool documents the set it accepts, read it from there rather than from memory.
