# Instructional writing

The style for text a reader acts on as **instruction** rather than reads as background: a `SKILL.md` and the reference files beside it, a Diátaxis reference doc, a runbook, a `CLAUDE.md`.

A reader acts on what the text says.
They hold no memory of an earlier draft, have no way to adjudicate between two sentences that contradict each other, and — where the reader is an agent — cannot step outside the session to carry out an instruction meant for someone else.
The rules below all follow from that.

## State the current truth, never the document's own history

Write each statement as though the document had always said it.

A reader arriving fresh holds no image of the previous version, so framing a fact against what the file used to say spends their attention on a comparison they cannot make — and dates the text to the moment of its correction rather than to what is true.

- **As history:** "The restart boundary is far more frequent than 'after inactivity' suggests: the VM boots afresh around each turn."
- **As fact:** "The VM boots afresh around each turn."

The same applies to a claim the document once carried and no longer stands behind.
Replace it; do not keep it with a note attached.

- **As history:** "This contradicts the older report that a multi-repo session loads project config from no repository, which this plugin previously carried second-hand and unverified."
- **As fact:** "[The upstream issue] reports the opposite.
  Check it for current status if a session ever behaves that way."

The test is whether a sentence states a fact about **the world** or a fact about **this file's past**.
The second never survives the edit.

That test keeps three things which can look like history but are not:

- **Evidence and dates** — "*Observed 2026-08-04: …*", or a last-verified date.
  These say what is known and how strongly, which a reader needs in order to judge whether to re-probe.
- **Recorded uncertainty** — a `Verify:` callout naming what has not been tested, so the next reader knows where the claim stops.
- **A contrary claim from outside** — an upstream issue reporting different behaviour is a fact about the world, not about this file, and a reader who hits that behaviour needs it.

## Converge on plain fact

None of those three is a resting place.
Verify what is recorded as unverified, settle a contradiction rather than citing it indefinitely, and promote an observation to a statement once it rests on something firmer than observed behaviour.

The qualifier goes when the claim no longer needs it: a fact grounded in documentation or source has earned the right to be stated flatly, without the date it was first noticed or the callout that hedged it.
Leaving the hedge in place after the evidence has firmed up is its own inaccuracy — it tells the reader to re-probe something already settled.

History has two homes, both read deliberately by someone looking for it: the **commit message**, which says what changed and why, and a **decision log** such as an ADR, where the repo keeps one, recording what was decided and what it superseded.
Neither belongs in the instruction itself.

## Fix wrong guidance at its source

When a change makes advice elsewhere in the document wrong, rewrite that advice.
Never add a note beside the new text explaining that the old text is now mistaken.

- **Annotated:** adding "which is the opposite of the usual 'don't fix it in the container' advice", while that advice stands unchanged further up.
- **Fixed:** rewriting the advice further up, and saying nothing about it here.

An annotation leaves both instructions standing, and makes correctness depend on the reader finding the second one.
A reader who opens only the section they need meets the wrong half as readily as the right one, and a reference doc is read in fragments by design.

This is a **scope** rule as much as a style one.
The sentence your change invalidated belongs to your change, even when it sits in a section you were not otherwise touching.

## Never direct an agent to do what only the user can do

Every imperative aimed at an agent has to be executable with the tools a session actually has.
Where the action belongs to the user — editing a cloud environment's settings form, starting a session scoped to different repositories, merging a pull request, changing anything outside the repository — the instruction is to **ask**, and it should say what to ask for.

- **Unexecutable:** "> **🤖 Agent** — edit the environment's setup script, which forces the snapshot to rebuild."
- **A request:** "> **🤖 Agent** — ask the user to add it to the environment's setup script; only they can edit that form."

Read each instruction back and ask whether the agent could carry it out unaided.
Where it could not, writing it as an order buys either a failed attempt or a silent skip.

Where the *route* for asking depends on whose environment or repository it is, the general document says to ask and leaves the route to whichever companion document records those specifics — the split in [ADR-005](https://github.com/flungo/claude-plugins/blob/main/docs/decisions/005-generic-plugins-and-personal-configuration.md).

## Where these bite

Most often when revising a document in the light of something just learned, which is the moment the correction feels vivid and most deserving of explanation.
Reread the result as someone who never saw the previous version: every sentence that only makes sense to a reader who did is one to cut or rewrite.
