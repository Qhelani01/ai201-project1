# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** 4 of 5 and not 5 of 5 because my chunks are one reply
each, so a thread's answer is spread across several small chunks rather than
sitting in one big one. My printing question is the one I expect to be hard —
`thread_printing.txt` is the shortest document in the corpus with only two
replies, so there are just two chunks in the whole store that could possibly
contain the answer, and if neither ranks it has nothing to fall back on. The
other four questions each have three or more replies on topic.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** All five and not four because this is the one thing the
system should never get wrong for my corpus. These are anonymous student
opinions, not policy, so an answer without a filename is worthless — the reader
can't tell whether they're being told what the registrar says or what one
person with nine votes reckons. It's also the cheapest criterion to hit: the
filename is stamped on every excerpt in the prompt, the grounding instruction
asks for it explicitly, and a refusal doesn't need one. If this drops below
five, something is wrong with the prompt rather than with retrieval.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** The two groups didn't overlap at all when I set the cutoff
— in-corpus questions scored 0.161–0.396 and the five `OUT_OF_SCOPE` ones
scored 0.808–0.896, so 0.6 sits in a gap 0.41 wide. On that evidence 5 of 5
looks safe and 4 of 5 looks too easy.

I'm keeping it at 4 of 5 anyway, because the gap is an artefact of how easy
those five questions are. They're from a different world entirely — the capital
of Mongolia, the 1994 World Cup — so of course nothing in a student forum comes
near them. Questions a student would plausibly ask that my corpus doesn't cover
score 0.471–0.715 and land inside the gap. If I swap any of the five for a
harder near-miss later, or if re-chunking shifts the distances, the margin is
much thinner than 0.41 suggests. 4 of 5 is the honest target for a gate I know
is only comfortable against easy misses.

---

## 4. Sampled chunks carry the context needed to read them

At least 4 of 5 chunks sampled with `python app.py chunks -n 5` contain both
the `THREAD:` question they belong to and at least one complete reply, with no
sentence cut off at either end.

**Why this target:** A reply in this corpus is unreadable without the question
it answers. "Doesn't roll over between semesters" is a real chunk of text that
means nothing on its own — you have to know the thread asked about the printing
quota. So "the right size" here isn't a character count, it's whether the
thread question travelled with the reply. That's countable by eye on five
samples.

The second half of it is a guard against what the starter's chunker did to this
corpus: cutting on a fixed 800-character window with a 650-character stride
sliced a duplicate tail off the four longest documents and produced a
**2-character chunk**. Any chunk ending mid-sentence means the splitter is
cutting on position instead of structure, and one of those in five samples is
enough to tell me that.

4 of 5 rather than 5 of 5 because the sampler spreads its picks across the
corpus and I'd rather leave room for one document that doesn't follow the reply
format than discover I'd written a target that punishes me for sampling
honestly.



---

## 5. Answers stay inside their sources

For at least 4 of my 5 test questions, every factual claim in the answer
appears in one of the retrieved chunks, and the answer is no more than 50 words
longer than the chunk it was drawn from.

**Why this target:** This is the one I actually care about, because the failure
it catches is the one I can't spot by reading. A wrong answer about laundry
timing is obvious. An answer that is *mostly* from my documents with one
confident extra sentence from the model's training data looks exactly like a
good answer, and my corpus makes that easy to do — these are questions about
university life, which the model has plenty of generic opinions about, so it
can pad a thin retrieval with plausible-sounding filler and still name a real
filename.

The 50-word cap is the countable half. My chunks are one reply, around 40 words
each, and a faithful two-or-three-sentence answer to one of them has nowhere to
get much longer from. An answer that runs well past its source is either
merging several replies, which is fine and I'll see that in the citation, or
inventing, which isn't. The length is what makes me go and look.

Note that this is stricter than criterion 2. Naming a source only proves a file
was cited; it doesn't prove the sentence came from it. This criterion is about
attribution being *correct* rather than merely present.

4 of 5 because judging "every factual claim appears in a chunk" means reading
the answer against the chunks by hand, and on a borderline one — a hedge, or a
rephrasing that adds an implication the reply didn't quite make — I don't trust
myself to score it the same way twice.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
