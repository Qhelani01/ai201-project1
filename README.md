# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

## Chunking Strategy

**Chunk size:** one reply, with a 120-character floor and a 600-character cap
(produces 157–385 characters in practice, 220 on average)
**Overlap:** none — the thread's question line is prepended to every chunk instead

I split on structure, not on a character count. Every document in
`advice_threads` is a `THREAD:` question followed by three to five
`--- reply N (X votes) ---` blocks, and that markup is completely consistent
across all 23 files, so a reply is a natural unit to cut on.

Two things I noticed reading the documents made me pick this:

**Each reply is one person making one claim, and the replies disagree with each
other.** In the bike thread, reply 1 says it's worth it, reply 2 sold theirs
because road salt destroys a drivetrain, reply 3 splits the difference. Keeping
those in one chunk averages three positions into one blob that matches any
question about bikes a little and none of them well. Separate chunks let
retrieval surface the position that actually answers the question.

**Replies lean on the question and never restate it.** "Doesn't roll over
between semesters" is meaningless unless you know the thread asked about the
printing quota. That's why the title is prepended to every chunk. It also does
the job overlap normally does — carrying context across a cut — for about 40
characters, instead of dragging in half of whoever replied before. So overlap
is zero.

**What the starter was doing:** 26 chunks from 23 documents, averaging 487
characters. The 800-character window never split a thread into its separate
arguments, and the 650-character stride sliced a duplicate tail off the four
longest documents — one of which came out as a **2-character chunk**. So it was
wrong in both directions at once: too coarse for the corpus, and generating
fragments anyway. Mine gives 67 chunks with a shortest of 157 characters.

**I changed my mind on one number.** I set the merge floor at 180 characters
first, reasoning that a lone 68-character reply like "Counterpoint, I sold
mine" is too thin to retrieve on. But reply bodies here run 68–195 characters
with a median of 117, so a 180 floor merged almost everything in pairs and
collapsed every three-reply thread straight back into a single whole-document
chunk — 12 of 23 documents came out unsplit, which is the starter's behaviour
with extra steps. Dropping it to 120 leaves most replies standing alone and
merges only the genuinely short ones (8 of 67 chunks hold two replies). All 75
replies survive either way; the floor only decides how they group.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `thread_bike_commute.txt#0` — produced by: `chunker.py::split_documents`

```
THREAD: Is a bike worth it for a 20 minute walk commute?

--- reply 1 (14 votes) ---
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.
```

Answers "is a bike faster than walking here" and "where do I park it" without
any of the three replies that follow it.

**Chunk 2** — source: `thread_first_year_regret.txt#0` — produced by: `chunker.py::split_documents`

```
THREAD: What do you wish you'd known in first year?

--- reply 1 (41 votes) ---
That the add/drop deadline and the withdrawal deadline are different dates and only one of them is on the calendar everyone reads.
```

One claim, and the thread question is what makes it findable — the reply never
says "first year" itself.

**Chunk 3** — source: `thread_laptop_specs.txt#2` — produced by: `chunker.py::split_documents`

```
THREAD: How much laptop do I actually need for CS courses?

--- reply 3 (12 votes) ---
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.
```

Reply 3 of 3, and it stands alone. Under the starter this was the middle of an
800-character window with two other opinions.

**Chunk 4** — source: `thread_parking.txt#0` — produced by: `chunker.py::split_documents`

```
THREAD: Worth getting a parking permit?

--- reply 1 (15 votes) ---
West lots sell out in about three days in August. East lot never sells out but it's a 12 minute walk, at which point you might as well have parked on the street.
```

Names both lots and the timing. A question about either lot hits this chunk.

**Chunk 5** — source: `thread_roommate_conflict.txt#2` — produced by: `chunker.py::split_documents`

```
THREAD: Roommate situation isn't working. What now?

--- reply 3 (33 votes) ---
Write down specifics before the meeting. 'It's not working' is hard to act on; 'guests four nights a week past 2am' is not.
```

Complete advice plus the example that explains it. The 33 votes travel with it,
which is the corpus's own signal that people agreed.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

**2.**

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
