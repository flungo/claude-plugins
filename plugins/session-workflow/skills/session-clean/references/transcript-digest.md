# Transcript digest

A sweep reads the session from its transcript on disk, not from the conversation left in context.

## Why the context window is not the session

Claude Code appends each turn to a JSONL transcript and never rewrites the file.
Compaction appends a boundary marker and a summary, and continues in a context window that no longer holds the turns before it.
Those turns are still in the transcript.

A sweep that reviews "the conversation" therefore reviews whatever compaction left behind, and the threads most at risk are exactly the ones it drops: an option raised early and never settled, a "we'll come back to this" from two hours ago, a question the user answered in passing.
A summary preserves the shape of that work and loses the loose ends, which are the whole subject of the sweep.

Reading the transcript is also the cheaper option.
Tool calls, tool results, and injected context make up almost all of the file's bulk and none of them are the conversation, so a transcript of several hundred kilobytes digests to a few thousand characters.

## Where the transcript is

`~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the session's working directory with every non-alphanumeric character replaced by `-`, and `~/.claude` is `$CLAUDE_CONFIG_DIR` wherever that is set.
A session's own transcript is the file being appended to as it runs, so it is the most recently modified one there.

A claude.ai chat session has no transcript file and no filesystem to hold one.
There the sweep reads the conversation in context, because that is all there is, and the same compaction caveat applies with no remedy available.

## Run the digest

This plugin ships [`transcript-digest.py`](../../../scripts/transcript-digest.py), which needs only Python 3.
Resolve that path against the path this file was read from, then bind it once:

```bash
DIGEST=<../../../scripts/transcript-digest.py, resolved against this file>
python3 "$DIGEST" --stats
```

Run with `--stats` first.
It prints the line census and, crucially, every compaction boundary with the token count behind it — which tells you whether the conversation in context is the session or a fraction of it.

Then take the conversation itself:

```bash
python3 "$DIGEST"                          # prompts, replies, decisions, boundaries
python3 "$DIGEST" --output <scratch path>  # where a long session would flood the reply
```

With no arguments it resolves its own transcript from the working directory.
Point it elsewhere with `--transcript PATH` or `--session-id ID`, and see what it found with `--list`.

## What the digest carries

Included by default, in transcript order:

- **`USER`** — each prompt, with `<system-reminder>` blocks stripped out.
- **`ASSISTANT`** — each visible reply, without thinking blocks.
- **`USER DECISION`** — the answers to a question the agent put through the question tool, as question and chosen option.
  These are choices the user made that appear nowhere in the reply text.
- **`USER INTERVENTION`** — a tool call the user denied or interrupted, with whatever they typed alongside it.
  A denial carrying "not that, park it" is a deferral the sweep must catch.
- **`COMPACTION`** — each boundary, its trigger, and the token count it discarded.
- **`COMPACTION SUMMARY`** — the summary compaction injected in place of what it dropped.

Left out: tool calls, tool results, injected context and attachments, subagent turns, thinking blocks, and synthetic turns.

## Read it for the sweep

Work the digest the way step 1 of the procedure describes, with two things the digest tells you that the conversation cannot.

**A boundary marks where the context window forgot.**
Threads opened before a boundary and never mentioned after it are the highest-yield region of the whole file: nothing later in the session could have reminded anyone they were open.
Read those stretches even when the rest of the sweep is going quickly.

**The compaction summary is a pointer, not a record.**
It was written to keep the work moving, not to preserve loose ends, so never treat a thread's absence from it as evidence the thread was resolved.
The turns it replaced are a few lines further up the same digest — check there.

## Feed a bad filter back into the plugin

A sweep is the only place the digest's accuracy can be judged.
You hold the digest and what is still in context at the same time, so you can see where the filter was wrong; no later reader of either can.

Two findings are worth acting on:

- **Noise it kept** — a kind of line that is not conversation and recurs across sessions, such as a hook's output or a harness notice arriving as an ordinary turn.
- **Signal it dropped** — something you know happened that the digest does not carry at any flag.

A flag is not a defect.
Where `--include-tools` or `--include-sidechains` recovers what was missing, the digest was right and the sweep needed more of it; only what no flag recovers, and noise that survives the defaults, is a change to the script.

Confirm it against the transcript first.
Find the line in the JSONL and read its `type`, its keys, and where its text sits: that shape is what a fix keys on, and it is also what separates a one-off from the recurring pattern worth filtering.

Then raise it with the user rather than acting on it — in a sweep, as its own item in the step 5 proposal.
Neither command that reads this file writes anything on its own.
Say what the filter did, the record shape behind it, and the change you would make.
On a yes it becomes a pull request against `flungo/claude-plugins`, carrying the script change, a case in `tests/test_transcript_digest.py`, and any line of this reference the change makes wrong.
A session working in another repository needs that one available to it before it can open one.

**Describe the shape, not the content.**
That repository is public and a transcript line carries the session's own text, so a proposal names the record type and the keys involved and leaves the conversation out.
Where a sample is needed, construct one rather than pasting a real line — the **`connector-conventions`** plugin, a declared dependency, carries the judgement in its `data-boundaries` skill.

## When the digest is not enough

- **`--include-tools`** adds one line per tool call.
  Use it to settle whether something was *done* or only discussed, which is the distinction step 0 turns on: a plan described in a reply and never applied leaves no edit in the trace.
- **`--include-sidechains`** adds subagent turns, for a session where a subagent did work the parent only summarised.
- **`--include-thinking`** adds the agent's reasoning, which occasionally holds an assumption that never reached a reply.
- **`--max-chars N`** clips each body, for a session too long to read whole.

Where a single turn needs checking in full, read that region of the JSONL directly rather than widening the digest.

## Without the script

Where the plugin is not installed — a repository checkout, or another machine — this produces the same core view:

```bash
jq -r 'select(.isSidechain != true)
  | if .type == "system" and ((.subtype // "") | test("compact")) then "\n===== COMPACTION =====\n"
    elif .type == "user" or .type == "assistant" then
      ((.message.content) as $c
       | (if ($c | type) == "string" then $c
          else ($c | map(select(.type == "text") | .text) | join("\n")) end)) as $t
      | if ($t | length) == 0 then empty else "\n## \(.type | ascii_upcase) — \(.timestamp)\n\($t)" end
    else empty end' <transcript.jsonl>
```

It omits the decisions and interventions the script recovers from tool results, and keeps the injected context the script strips, so prefer the script wherever it is available.
