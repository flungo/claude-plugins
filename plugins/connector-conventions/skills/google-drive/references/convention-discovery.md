# Finding a folder's convention documents

The algorithm for discovering which convention documents govern a Drive file, and in what order they apply.

Connector quirks this depends on are in [`behaviours.md`](behaviours.md); this file assumes them.

## The algorithm

Given a target file or folder:

1. **Build the ancestor chain.**
   Call `get_file_metadata` on the target, take its `parentId`, call `get_file_metadata` on that, and repeat.
   Stop when a folder returns no `parentId` — that is a root.
   The walk is sequential, since each parent is only known once its child has been fetched.
   Cap it at 15 hops as a loop guard.

2. **Discover in one query.**
   Do not query per folder.
   `OR` every ancestor id into a single `search_files` call, and exclude folders:

   ```text
   (parentId = 'ID1' or parentId = 'ID2' or parentId = 'ID3') and
   (title contains 'CONVENTIONS' or title contains 'AGENTS' or title contains 'CLAUDE') and
   mimeType != 'application/vnd.google-apps.folder'
   ```

   Pass `excludeContentSnippets: true` — snippets are not needed and dominate the response size.

3. **Filter by title.**
   `title contains` is a substring match, so discard anything whose title does not *start with* one of the three keywords.

4. **Read each survivor** with `read_file_content`, which renders a Google Doc as text with `#` heading markers, so an authored structure survives.

5. **Order by depth, deepest last.**
   Each result carries the `parentId` it was found under; map that back to the chain to get its depth.
   Apply outermost-first so the deepest document is applied last and wins.

## Cost

For a chain of depth *d* with *n* documents found — *d* sequential `get_file_metadata` calls, **one** `search_files` call, and *n* `read_file_content` calls.

Only the metadata walk is sequential, and it cannot be batched.
Chains in practice are shallow; the hop cap bounds a pathological case, not an expected one.

## Caching

Cache **per folder id**, never as one merged blob.

A session often touches more than one subtree, and a document loaded for one must not leak into work under another.
Keying by folder lets the applicable set be recomputed per target from documents already read.

For a second target, walk its chain — the metadata calls are cheap — then reuse any cached document and read only the folders not yet seen.

## More than one match in a folder

A folder should hold **at most one** convention document.

If several match, apply the one whose title matches a keyword most exactly, and tell the user the others are being ignored.
Competing rule sets in a single folder have no defined precedence between them, which is the ambiguity the depth ordering exists to remove.

## When nothing is found

Say so once, rather than silently proceeding — the absence is information, especially where the user expected a document to exist.

Bear in mind that a document created moments ago may not be indexed yet ([`behaviours.md`](behaviours.md)), so confirm by parent rather than by title before reporting that a folder has none.
