# Google Drive connector — verified behaviours

How this connector actually behaves, where knowing it changes what you do.
Not only surprises — some entries are simply the mechanism, recorded so it is not re-derived.
Each entry states the behaviour, how it was established, and a `**Do:**` line.

Verified against the live connector on **2026-08-29**, from a Claude Code Web session.

> **Verify:** these are properties of Anthropic's Google Drive connector, not of the Google Drive API, and its tool surface can change without notice.
> An undated or stale entry is a hint to re-probe, not a fact to rely on.

## Trashing a folder is recursive

Trashing a folder trashes everything beneath it.

Established by control experiment: a file trashed directly disappeared from `title contains` search while an untouched control remained, proving **search excludes trashed files**.
A child whose parent folder was then trashed — the child itself never touched — also disappeared from that search, and `get_file_metadata` on it returned *"Requested entity was not found"*.

**Do:** trash the top of the subtree and stop.

A descendant of a trashed folder reports *"Requested entity was not found"* from `get_file_metadata` and *"The caller does not have permission"* from `trash_file`.
Both mean **already trashed**.
Neither is a permissions problem, and neither should be retried or worked around.

## Search is eventually consistent

The search index lags writes.

A newly created file was absent from a `title contains` search that a `parentId =` query, issued at the same moment, returned it from.
The same lag can leave a just-trashed file briefly visible.

**Do:** never treat a `title contains` result as proof of absence for anything recently changed.
To confirm a write, query `parentId = '<folder>'` or fetch the id directly.

This is also why a convention document you have just created may not be discoverable yet — re-run discovery by parent, not by title.

## `title contains` is a case-insensitive substring match

`title contains 'AGENTS'` matches a file whose title merely *contains* that run of letters — a guidance PDF ending in `…LandlordsAgents.pdf` matched.

No prefix or exact-match operator is available.

**Do:** post-filter results on the title after the query returns.

## Folders match title queries too

A folder whose own title contains a search term is returned as a result, indistinguishable from a document without checking `mimeType`.
A test folder named `…-conventions-test` came back as though it were a convention document.

**Do:** add `mimeType != 'application/vnd.google-apps.folder'` to any title search meant to find documents.

## `fileSize` is stale at creation

A freshly created document reports `fileSize` of `1` in the creation response, and its real size on the next query.

**Do:** ignore it.
It is not evidence of a truncated write; read the file back if you need certainty.

## Binary uploads corrupt silently

`create_file` accepts only inline base64 and truncates binary content without raising an error.
Text uploads are unaffected — `textContent` with `text/plain` converts to a Google Doc intact.

**Do:** never upload binary through the connector.
Have the user add those files directly.

## One parent, and roots have none

`get_file_metadata` returns a **single** `parentId`, for folders as well as files.
Drive's API can model multiple parents; this connector surfaces one, so treat ancestry as a linear chain.

A root returns **no `parentId` field at all** — both My Drive (titled `My Drive`, reporting its concrete id rather than the `'root'` alias) and a shared-with-me root (carrying `sharedWithMeTime` and an `owner` that is not the user).

A chain can cross an ownership boundary partway up, from the user's own folders into another account's, before terminating at that shared root.
