---
name: google-drive
description: Working rules for Google Drive through the connector, and the convention documents a Drive folder can carry. Consult this whenever acting on a file or folder in Google Drive — reading, searching, renaming, moving, filing, de-duplicating, trashing, or uploading — so that any CONVENTIONS document governing that folder or one of its parents is applied first, and so that trashing, stale search results, and silent upload corruption are handled correctly. Covers the hard rules that always hold, and indexes the references carrying the discovery algorithm, the connector's verified behaviours, and how to write a convention document.
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
Re-run it when the user asks, and after you create or edit a convention document.

Documents named `AGENTS` or `CLAUDE`, or carrying a descriptive tail, are recognised and applied the same way.
When you meet one, or find more than one in a single folder, offer to normalise it — rename to plain `CONVENTIONS`, and combine multiples into one document with a section each.
Offer only; never rename, merge, or trash a convention document unasked.

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
