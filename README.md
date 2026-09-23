# The Unofficial Guide

Qhelani Moyo — corpus: `advice_threads`

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

This is a question-answering system over `advice_threads`, a corpus of 23
student forum threads where someone asks a practical question about university
life — laptops for CS courses, pass/fail deadlines, laundry timing, parking
permits, roommate conflicts — and three to five other students reply with vote
counts attached. You ask it a question in plain English and it answers from
those threads only, naming the file it used.

It handles specific questions with a findable answer: "how much RAM do I need
for CS courses", "how late can I declare pass/fail", "when is laundry least
busy". Because the replies in a thread routinely disagree with each other, the
answers surface both sides rather than picking one, and they report what
students said rather than stating it as official policy — the corpus is
opinion, not the registrar.

Anything the threads don't cover gets refused instead of guessed at. A
relevance gate checks the retrieved chunks before the model is called at all,
so an off-topic question costs nothing and comes back as "I don't have enough
information about that."

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

**Question:** How much RAM do I need in a laptop for CS courses?

**Answer:**

```
$ python app.py --corpus advice_threads ask "How much RAM do I need in a laptop for CS courses?"

  (best distance 0.161, cutoff 0.6)

Based on `thread_laptop_specs.txt`, students state that 16GB of RAM is the recommended amount worth paying for, with one reply noting that an 8GB machine was fine for two years until struggling on the final project.

Sources retrieved: thread_first_gen.txt, thread_laptop_specs.txt, thread_pass_fail.txt

1 model calls this session, 680 tokens (630 in, 50 out)
```

And the same system refusing something it doesn't cover, before any model call:

```
$ python app.py --corpus advice_threads ask "What is the capital of Mongolia?"

  (best distance 0.893, cutoff 0.6)

I don't have enough information about that.

0 model calls this session
```

**My relevance cutoff:** 0.6 — unchanged from the starter, kept deliberately
after measuring. `TOP_K` also stays at 5.

| Question | In corpus? | Best distance |
|---|---|---|
| How much RAM do I need in a laptop for CS courses? | yes | 0.161 |
| When is laundry least busy in the dorms? | yes | 0.232 |
| How late can I declare a course pass/fail? | yes | 0.296 |
| Does it matter if I buy an older edition of the textbook? | yes | 0.342 |
| How much printing credit do students get? | yes | 0.396 |
| What is the recommended dosage of ibuprofen for a headache? | no | 0.808 |
| How do I write a for loop in Rust? | no | 0.835 |
| Who won the 1994 World Cup? | no | 0.893 |
| What is the capital of Mongolia? | no | 0.894 |
| How do I change the oil in a diesel engine? | no | 0.896 |

The two groups are 0.161–0.396 and 0.808–0.896, so the gap is 0.41 wide and its
midpoint is 0.602. The starter's 0.6 is already sitting almost exactly in the
middle of it, so there was nothing to gain by moving it.

**The gap is wider than it is real, though.** The five OUT_OF_SCOPE questions
are from a different world entirely, so of course they score badly. I ran six
harder ones — things a student would plausibly ask this system that the corpus
simply doesn't contain:

| Near-miss question | Best distance | Passes the 0.6 gate? |
|---|---|---|
| What are the library's opening hours? | 0.471 | yes |
| How many credits do I need to graduate? | 0.489 | yes |
| What is the tuition payment deadline? | 0.570 | yes |
| How do I appeal a parking ticket? | 0.614 | no |
| Who is the dean of the engineering school? | 0.698 | no |
| What is the wifi password on campus? | 0.715 | no |

These land *inside* the gap, and three of them clear the gate. That's the real
decision, and both directions cost something:

- I could drop the cutoff to about **0.43** — between my worst real question
  (0.396) and my closest near-miss (0.471). On this sample that scores
  perfectly: all five real questions pass, all six near-misses refuse. But the
  margin is 0.035 on each side. A real question worded slightly differently
  lands on the wrong side of it, and refusing a question I have the answer to
  is the failure I care about most.
- At **0.6** the margin above my worst real question is 0.2, which survives
  rewording, and the three near-misses that get through go to the second layer
  instead.

I checked that the second layer actually holds rather than assuming it, by
sending all three through:

- *"How many credits do I need to graduate?"* → "I don't have enough
  information to answer how many credits you need to graduate."
- *"What is the tuition payment deadline?"* → "I don't have enough information
  to answer this question."
- *"What are the library's opening hours?"* → answered "one reply mentions that
  the library is open until 2am (thread_sleep_schedule.txt). The documents do
  not provide information on when the library opens." That's a real line in
  that file, so it's grounded, and it says what it doesn't know.

Zero fabrications across the three. So I kept 0.6 and let the prompt handle the
near ones, which is the division of labour the gate was designed around — it
catches the clear misses, the prompt catches the near ones.

**Top-k stayed at 5.** The chunk containing the expected answer came back at
rank 1 for all five questions, so raising it buys nothing. Lowering it would
cost the corroborating and dissenting replies that are the point of this
corpus: reply-level chunks mean a three-reply thread is three retrievals, and
cutting to k=3 would throw away the disagreement. The loosely-related chunks
that come back for the narrower questions (the printing thread has only two
replies, so 4 of its 5 results score above 0.6) did not corrupt any answer.

**I tightened the grounding instruction.** The starter's version got the
citation right but the framing wrong for this corpus — it answered "You need
16GB of RAM for CS courses" as if it were policy, when it is three students
with vote counts who partly disagree. I added four rules: report what students
said rather than asserting it, give both sides when replies disagree, say
plainly what the documents don't cover when they only answer part of a
question, and keep the existing filename citation. Same question now returns
"students state that 16GB is the recommended amount worth paying for, with one
reply noting that an 8GB machine was fine for two years until the final
project" — same fact, honest about what kind of claim it is.

All five in-corpus questions return an answer containing the phrase in
`expects`, and all five OUT_OF_SCOPE questions are refused by the gate without
reaching the model.

## How I Used AI

I used Claude heavily on this project, including to write most of the chunker
and the write-ups. The two moments below are the ones where what came back was
wrong or incomplete and had to change.

**1. The merge floor in the chunker was wrong, and the numbers caught it.**

I asked Claude to replace the starter's fixed-width chunker with one that cuts
at reply boundaries, since every document in `advice_threads` is a `THREAD:`
question followed by `--- reply N (X votes) ---` blocks. What came back did
that correctly and also added something I hadn't asked for: a minimum chunk
length of 180 characters, so that a very short reply gets the next one glued on
instead of going out as a fragment. The reasoning was sound — the starter's
chunker produced a 2-character chunk on this corpus, so guarding against
fragments is a real concern.

It was the wrong number. Checking the output showed 34 chunks from 23
documents, with 14 chunks holding three replies and **12 of the 23 documents
coming back as a single whole-document chunk** — which is the starter's
behaviour with extra steps, and defeats the entire reason for splitting on
replies. The cause was that reply bodies here have a median of 117 characters,
so a 180-character floor almost never lets one stand alone. I had it sweep the
value: at 120 the corpus gives 67 chunks, mostly one reply each, with only the
8 genuinely short replies merged. The lesson was that the argument for the
guard was fine and the number attached to it was picked without looking at the
corpus.

**2. It called the distance gap clean when it wasn't.**

For the relevance cutoff I asked what the five in-corpus questions and the five
`OUT_OF_SCOPE` questions scored. The answer was that in-corpus ran 0.161–0.396
and out-of-scope ran 0.808–0.896, a gap 0.41 wide whose midpoint is 0.602, so
the starter's 0.6 was already correct and nothing needed changing.

That conclusion was right about the number and wrong about the confidence. The
five `OUT_OF_SCOPE` questions are things like the capital of Mongolia and the
1994 World Cup — a different world entirely, so a wide gap is guaranteed by how
easy they are and says very little. The test that matters is a question a
student would actually ask this system that the corpus happens not to contain.
Six of those — library opening hours, credits to graduate, tuition deadline,
parking ticket appeals, the engineering dean, the wifi password — score
0.471–0.715, which is *inside* the gap, and three of them clear the 0.6 gate.

That changed the write-up from "0.6 is obviously right" to a documented
trade-off, and it changed what I checked. Rather than assume the grounding
instruction catches what the gate lets through, I sent all three through the
model: two refused outright and the third answered from a real line in
`thread_sleep_schedule.txt` and stated what the documents didn't cover. Zero
fabrications, which is the evidence for keeping 0.6 instead of tightening to
0.43 and risking refusals on real questions.

A third thing worth recording: Claude also caught that `questions.py` was
broken — the five dicts had the question text as the key with an empty value
instead of `{"question": ..., "expects": ...}`, which would have raised
`KeyError` in `run_eval.py` next unit — and that the questions were about
`campus_life` topics while my corpus is `advice_threads`.

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
