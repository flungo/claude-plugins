---
name: google-drive
description: Working rules for Google Drive through the connector, and the convention documents a Drive folder can carry. Consult this whenever acting on a file or folder in Google Drive — reading, searching, renaming, moving, filing, de-duplicating, trashing, or uploading — so that any CONVENTIONS document governing that folder or one of its parents is applied first, and so that trashing, moving, stale search results, lossy reads, and silent upload corruption are handled correctly. Covers the hard rules that always hold, what the connector cannot do at all — edit a document, create or resolve a shortcut, act on a folder in bulk — and how to hand those actions back, plus an index of the references carrying the discovery algorithm, the connector's verified behaviours, and how to write a convention document.
---

# Google Drive

Google Drive has no equivalent of a repository's `CLAUDE.md`.
Nothing there is loaded automatically, so a folder's rules are invisible unless an agent goes looking.

This skill carries the rules that always hold when working in Drive through the connector.
The mechanics sit in the references indexed at the end — read the one you need rather than all of them.

## Load the governing conventions before you act

A Drive folder may hold a **convention document** — titled `CONVENTIONS`, `AGENTS`, or `CLAUDE` — stating how its contents are named, dated, filed and handled.

Before the first write to any Drive file or folder, and before reading a file whose handling depends on local rules, find the convention documents governing it.
Walk the target's parent chain and look in every ancestor, not just the immediate folder.

Discovery is **once per session**, cached per folder, not once per file.
Re-run it when the user asks, and after you create or replace a convention document.

Documents named `AGENTS` or `CLAUDE`, or carrying a descriptive tail, are recognised and applied the same way.
When you meet one, or find more than one in a single folder, offer to normalise it — rename to plain `CONVENTIONS`, and combine multiples into one document with a section each.
Offer only; never rename, merge, or trash a convention document unasked.

Read a convention document with the markdown export, never with `read_file_content`.
The latter is a *rendering*, and it drops code spans and blockquote markers and strips a table's header row — so a rule can be read as something other than what it says.

→ [`references/convention-discovery.md`](references/convention-discovery.md) for the algorithm and the exact queries.

## Precedence and scope

A convention document governs **its own folder and everything beneath it**, and nothing outside.

Where two documents in one chain answer the same question differently, the **deeper** one wins — it is the more specific statement.
Where they address different things, both apply.
Cache per folder, never as a single merged blob, so one subtree's rules cannot leak into another.

State which convention documents you loaded, and from which folders, the first time they affect what you do.
A rule applied silently is one the user cannot correct.

## Capture conventions the user states

When an instruction **implies a convention exists** — a naming pattern, a filing rule, a date format, a "we always/never…" — treat that as a rule worth keeping, not a one-off.

Work out the **scope** it belongs at, and consider whether it is broader than the immediate case.
A rule stated about one file usually holds for its folder; sometimes for the whole tree above it.
Push it as deep as it is true, and no deeper.

Then offer to record it — creating a convention document at that folder, or appending a section to the one already governing it.
Do not write it silently; propose the scope and the wording, and let the user place it.

→ [`references/convention-authoring.md`](references/convention-authoring.md) for how to write the document.

## Report every file you trash

Trashing is recoverable for 30 days, so what matters is that the user can **reach** the files.

List them **immediately before the trash call**, so that if the harness prompts for approval the file under discussion is one click away, and **again in your closing summary**, so the record is not buried mid-conversation.
Both times as links:

```markdown
- [invoice-2024-09.pdf](https://drive.google.com/open?id=FILE_ID) — `FILE_ID`
```

Filename as the link text, id alongside, `https://drive.google.com/open?id=<id>` as the target — that form still resolves once the file is in the trash.

The list before is **not** a request for permission.
Whether to ask is the ordinary judgement call it would be anyway, governed by the folder's conventions and the scale of the change.

**Trashing a folder trashes everything beneath it.**
Trash the top of the subtree and stop; do not walk into it.
A descendant then reports *"not found"* or *"caller does not have permission"* — both mean *already trashed*, not a failure to work around.

## Documents are write-once

Nothing in the connector edits a document's body — there is no append, no edit, no overwrite.

Changing one means writing a full replacement and trashing the original, and a same-title create does **not** overwrite the first; it leaves two documents with the same name and no way to tell which is current.
Do both halves in the same session, never across one.

→ [`references/convention-authoring.md`](references/convention-authoring.md) for the sequence and its failure mode.

## Moving or renaming can strand a reference

A move replaces a file's only location — it leaves the source folder immediately, and the response looks like an unqualified success either way.
A rename is the same hazard by a different route: a shortcut's title is fixed at creation and does not follow its target, so renaming a file leaves every pointer to it reading the old name.

Neither raises an error, and nothing surfaces the damage later.
So before moving or renaming anything, ask what else points at it.

Where you know of a pointer, **offer to update it in the same step** rather than fixing it afterwards.
A rename and its pointer are one change; splitting them leaves a window where the index is wrong, and an interruption makes that window permanent.

## Hand back what the connector cannot do

The connector cannot create a shortcut from scratch, resolve one, act on a folder in bulk, or upload a binary.
The Drive UI can do all of it, so the honest move is to hand the action back — not to approximate it.

Hand it back in **one executable pass**, so the user acts once instead of assembling the task themselves:

- **Group the items by the folder they are acted on from**, since that is what a person has open.
- **Link that folder**, so it opens in a click.
- **List the exact filenames**, in a form that can be pasted or multi-selected.
- **Say what to do**, once per group.

Then **verify afterwards** rather than assuming it worked, and report anything missed or wrongly included.
A hand-back you never check is a hand-back you cannot claim as done.

## Never treat search as current

Drive's search index is **eventually consistent**.
A file created or trashed moments ago may still be missing from, or present in, a `title contains` result.

So a search that finds nothing is not proof that nothing is there.
When it matters — confirming a write landed, or checking a convention document exists — query `parentId = '<folder>'` or fetch the id directly, which reflect the change immediately.

## Never upload binary content

`create_file` takes only inline base64 and truncates binaries silently, with no error.
Text is safe; PDFs and images are not.
To get binary files into Drive, have the user add them directly.

## References

| Read | When |
| --- | --- |
| [`references/convention-discovery.md`](references/convention-discovery.md) | Finding the convention documents — the parent walk, the batched query, ordering by depth |
| [`references/behaviours.md`](references/behaviours.md) | The connector behaves unexpectedly, or before relying on any tool's result |
| [`references/convention-authoring.md`](references/convention-authoring.md) | Writing or extending a convention document |
