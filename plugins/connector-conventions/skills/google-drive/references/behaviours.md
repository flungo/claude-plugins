# Google Drive connector — verified behaviours

How this connector actually behaves, where knowing it changes what you do.
Not only surprises — some entries are simply the mechanism, recorded so it is not re-derived.
Each entry states the behaviour, how it was established, and a `**Do:**` line.

Verified against the live connector on **2026-08-29**, and extended on **2026-08-31**, from Claude Code Web sessions.

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

## Reading a document loses formatting that exporting keeps

`read_file_content` returns a *natural language representation*, not the document.
Headings and list nesting survive it; several things do not.

A document written with code spans, a blockquote and a table came back with the backticks gone, the `>` marker gone, and the table's header row emptied — its headings pushed into a body row where the bold markers appeared as literal `\*\*Column\*\*`.
Underscores inside identifiers came back backslash-escaped, and doubly so inside the table.

`download_file_content` with `exportMimeType: 'text/markdown'` returned the *same document* byte-faithfully, every one of those constructs intact.
It returns base64, so it must be decoded.

**Do:** read a convention document — anything whose structure carries meaning — with the markdown export.
Keep `read_file_content` for prose you only need the gist of.

**Do not** conclude from a `read_file_content` result that a write lost formatting.
Export before believing it; the loss is usually in the reading, not in the document.

## Markdown creates a faithful Google Doc

`create_file` with `textContent` and `contentMimeType: 'text/markdown'` converts to a Google Doc, preserving headings, bold, italic, code spans, nested and ordered lists, blockquotes, and tables.

Established by exporting the created document straight back to markdown and comparing: only the table's alignment markers changed (`---` became `:----`).

**Do:** use markdown for any document an agent will later read.

## Document content cannot be changed

No tool edits a document's body.
`update_file` takes only `title` and `parentId`; there is no content parameter, and no other tool writes into an existing file.

**Do:** treat every document as write-once.
To change one, create its replacement and trash the original — and read [`convention-authoring.md`](convention-authoring.md) first, because the replacement is visible to discovery before the original is gone.

## A same-title create adds a second document

Creating a file whose title already exists in the folder does **not** overwrite it.

Two documents titled `CONVENTIONS`, with different ids, coexisted in one folder after a second create.
Nothing in either response flagged the collision.

**Do:** trash the original in the same session that creates its replacement.
Between the two calls the folder has two convention documents, which is precisely the ambiguity discovery cannot resolve.

## Moving a file replaces its only parent

`update_file` with a `parentId` **moves** the file; it does not add a location.

A file moved from one folder to another was gone from the source folder's listing immediately, with no warning in the response.

**Do:** before moving anything, consider what still points at it.
A folder that indexed the file develops a hole, and nothing raises an error — the move looks entirely successful from the response alone.

## Shortcuts are opaque, and can only be made by copying

`create_file` cannot make one.
Asked for `application/vnd.google-apps.shortcut` it fails, naming the only types that can be created empty: `document`, `spreadsheet`, `presentation`, `vid`, `folder`, `form`.

`copy_file` on an existing shortcut **does** yield a shortcut, with a title and parent of your choosing.

A shortcut's target is invisible either way.
`get_file_metadata` returns no target field, `read_file_content` returns `{}`, and `download_file_content` is refused outright with *"Download not allowed"*.

> **Verify:** whether a copied shortcut still points at the original's target is not observable through the connector, only in the Drive UI.
> Until that is checked, treat `copy_file` as producing a shortcut of unconfirmed aim.

**Do:** confirm a shortcut's target in the UI rather than inferring it from the connector.
The title is set independently of the target and is not evidence of what it points at.

## Folders have no downloadable content

`download_file_content` on a folder fails with *"The head revision doesn't seem to have any content."*

There is no way to fetch a folder, or resolve the shortcuts inside one, through the connector.
That is a Drive UI capability, and reaching it means handing the action back — see the skill's rule on doing so in one executable pass.
