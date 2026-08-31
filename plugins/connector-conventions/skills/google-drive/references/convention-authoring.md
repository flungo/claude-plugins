# Writing a convention document

How to write the document itself, so an agent finding it can act on it.

## Placement and naming

Put the document **in the folder whose rules it states**.
Placement is what defines scope — it governs its own folder and everything beneath it, and nothing outside.

Title it exactly **`CONVENTIONS`**.

`AGENTS` and `CLAUDE` are recognised as equivalents when discovering, so documents written for those ecosystems are found.
A descriptive tail (`CONVENTIONS - Filing Rules`) is also *recognised*, because such documents exist, but **do not create one** — a tail names a topic, and naming a topic invites a second document for the next topic, which the one-document rule below rules out.

**One document per folder.**
Splitting a folder's rules across several documents produces competing rule sets with no defined precedence between them.
A second topic is a second section, not a second file.

### Normalising what discovery finds

Documents under the recognised alternatives still show up in discovery, so they are read and applied either way — but they are worth tidying when you meet one.

On finding a document named `AGENTS`, `CLAUDE`, or `CONVENTIONS` with a descriptive tail, **offer to rename it** to plain `CONVENTIONS`.
On finding **more than one** in a folder, offer to **combine them into a single document**, each former file becoming an H1 section, and trash the others once merged.
Where the merged rules overlap or conflict, put the conflict to the user rather than silently picking one.

Offer the restructure too where a document's shape fights the format — rules buried in prose, or topics that never start at H1.

Always propose and let the user decide; never rename, merge, or trash a convention document unasked.
The document is the user's, and renaming it changes what a folder appears to declare.

Push each rule as **deep** as it is true.
A rule at the top of a tree binds everything beneath it, so one that only holds for a single subfolder belongs in that subfolder — where it will also win, being deeper.

## Structure

Top-level topics are `#` H1 sections, one per topic, with nothing above the first heading except a sentence saying what the folder holds.

Nest freely below that.
H2 and deeper are for structure *within* a topic — cases, exceptions, worked examples — and are encouraged where a topic has real internal shape.
The rule is only that a **topic** starts at H1, so that the document reads as a flat list of rules with their detail tucked underneath.

Prefer headings, lists and prose to tables.
The document survives being written and exported intact, but an agent reading it the lossy way loses a table's header row entirely ([`behaviours.md`](behaviours.md)) — and a rule read out of a headerless table is a rule read wrong.

Name each heading for the **decision it settles**, since that is what an agent scans to find the rule bearing on what it is doing.
`Which date to use` earns its place; `Notes on dates` does not.

> **🤖 Agent** — when writing a document, take its headings from the folder's actual rules.
> Never copy the headings from an example, and never carry a rule from one folder's document into another's.

## Writing rules an agent can follow

- **State the rule, then the reason.**
  The rule is what gets applied; the reason is what lets an agent extend it to a case you did not anticipate.
- **Give the failure mode.**
  Naming the specific misreading a rule prevents is worth more than restating the rule.
- **Say what is deliberate.**
  Anything that looks like a mistake gets tidied up by someone unless the document says it is intentional, and why.
- **Give a check, where one exists.**
  A rule with a test attached — a relationship that should hold, a range a value should fall in — is verifiable rather than merely stated.
- **Record open questions as open.**
  An item nobody could resolve, a decision not yet made — say so, rather than leaving an agent to infer a rule from an inconsistency.

Prefer the imperative.
*"Preserve duplicate markers"* is unambiguous in a way that *"duplicate markers are generally preserved"* is not.

## Changing a document means replacing it

The connector cannot edit a document's body ([`behaviours.md`](behaviours.md)).
There is no append, no edit, no overwrite — the only way to change a convention document is to write a new one carrying the full revised text, then trash the old one.

So a change is **create then trash**, and the order matters:

1. **Read the current document first**, with the markdown export rather than `read_file_content`, which drops code spans and blockquotes and mangles tables.
   The replacement has to carry every rule the original held; anything not read is a rule silently dropped.
2. **Create the replacement**, with the full text, in the same folder.
3. **Trash the original**, reporting it as the skill requires for anything trashed.

Between steps 2 and 3 the folder holds **two** convention documents, and a same-title create does not overwrite the first — it adds a second with its own id.
Discovery finding two documents in one folder cannot tell which is current.
Close that window in the same session; never leave it open across one.

If the trash cannot be completed, say so explicitly rather than leaving the pair in place — a folder with two convention documents is worse than one with a stale document, because the stale one is at least unambiguous.

Because replacing is this expensive, prefer a document whose rules can absorb a new case without a rewrite.

## Keeping it true

The document is read *before* the folder is touched, so a stale rule is applied with the same confidence as a current one.

- Replace it in the same session in which a rule changes, by the create-and-trash sequence above.
- Say when it was last updated.
- When a session establishes a rule that previously existed only in someone's head, offer to write it in.
  That is how the document accumulates.

## What does not belong

- **Secrets and personal data.**
  Anything an agent may read, treat as read — no credentials, keys, account numbers, or anything you would not want quoted back in another context.
- **Rules for other folders.**
  Put those in those folders, where their scope is correct.
- **A file inventory.**
  It goes stale immediately, and the folder listing is authoritative.
  Describe the rules; let the listing describe the contents.
