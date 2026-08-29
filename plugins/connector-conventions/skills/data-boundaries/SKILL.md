---
name: data-boundaries
description: Handling information that crosses between sources — a connector's content, another connector's, and the local repository or working directory. Consult this whenever content read from one source is about to be written into, quoted in, or summarised for another — a commit message, a pull request, an issue, a document in a different connector, or a file in the repo — and whenever deciding how much detail a summary should carry. Covers why a source's audience is not inferable from its content, preferring the general statement over the identifying one, and confirming with the user when the boundary is unclear.
---

# Crossing between sources

A session often has several sources open at once — one or more connectors, and the local repository or working directory.
**Each has its own audience, and they do not match.**

A folder in a connector may be shared with an employer, a client, or a family member.
A repository may be public, or may become public later.
A pull request body, an issue, and a commit message are all published to whoever can see that repository, permanently and often to search engines.

The reader of one source did not consent to being the reader of another.

## The rule

Before content read from one source is written into another — quoted, summarised, or used as an example — decide whether it belongs there.

**If there is any doubt, confirm with the user before writing it.**
The cost of asking is a sentence; the cost of being wrong is not retractable, because anything published may already be cached, indexed, or replicated.

## Prefer the general statement

Most of the time the specific detail is not what the destination needs.

A convention, a rule, a shape of a problem, or a lesson learned is usually the whole value — and it survives being stated without the client name, the file name, the account number, or the verbatim quote.
**Where generalising loses nothing, generalise.**
It needs no permission and raises no question.

Reach for the specific only when it genuinely carries information the general form cannot, and then treat it as a crossing that needs confirming.

Worth generalising by default:

- Names of people, employers, clients, and counterparties.
- File, folder, and document titles from a private store.
- Verbatim quotations from a private document.
- Identifiers — account, reference, and case numbers.
- Anything that would let a reader identify whose data it was.

## You cannot infer audience from content

A document does not say who may read it, and its sensitivity is not proportional to how sensitive it looks.
A mundane filing rule may sit in a folder shared with an employer; a dramatic-sounding note may be entirely the user's own.

So the question is never "does this look sensitive" but **"which source did this come from, and who reads the one I am writing to"**.
When the answer to either half is unknown, that is the doubt that triggers confirming.

## Direction matters

Crossing *into* a wider audience is the risk — a private store into a public repository, one connector into another, anything into a published artifact.

Crossing the other way, into a more private destination, is usually safe, but still carries the source's rules with it.
Content taken from a connector remains subject to that folder's own conventions wherever it lands.

## Secrets never cross

Credentials, keys, and tokens are not a boundary question.
They do not get written into another source at all, in any form, regardless of how private the destination looks.
