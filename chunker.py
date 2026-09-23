"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# Every document in advice_threads is a question line followed by reply blocks
# that look exactly like this. Nothing else in the corpus starts with "---".
REPLY_MARKER = re.compile(r"^--- reply \d+ \(\d+ votes\) ---$", re.M)

# One reply is the unit. A reply shorter than this gets the next one glued on,
# so no chunk goes out as a bare fragment like "Counterpoint, I sold mine."
# Reply bodies here run 68-195 characters with a median of 117, so 120 leaves
# most replies standing alone and merges only the genuinely short ones. Raising
# it to 180 collapsed every three-reply thread back into a single chunk.
MIN_CHUNK_CHARS = 120

# Nothing here comes close to this. It only stops the trailing-reply merge
# below from building one oversized chunk on a longer thread.
MAX_CHUNK_CHARS = 600


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _split_thread(text: str) -> list[str] | None:
    """
    Cut one thread into chunks at reply boundaries.

    Returns None if the document isn't thread-shaped, so the caller can fall
    back to something generic.

    The thread question goes on the front of every chunk. Replies lean on it
    constantly — "Doesn't roll over between semesters" only means anything if
    you know the thread asked about the printing quota — and repeating one
    short line is cheaper than carrying a character overlap that would drag in
    half of whoever replied before.
    """
    markers = list(REPLY_MARKER.finditer(text))
    if not markers:
        return None

    title = text[: markers[0].start()].strip()

    blocks: list[str] = []
    for i, marker in enumerate(markers):
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        body = text[marker.end() : end].strip()
        if body:
            # Keep the vote count. It's the corpus's own signal for which
            # answers people agreed with, and it costs one line to carry.
            blocks.append(f"{marker.group(0)}\n{body}")

    if not blocks:
        return None

    # Pack replies into groups, closing a group once it's substantial enough
    # to stand on its own.
    groups: list[list[str]] = []
    current: list[str] = []
    for block in blocks:
        current.append(block)
        if sum(len(b) for b in current) >= MIN_CHUNK_CHARS:
            groups.append(current)
            current = []

    if current:
        # A leftover short reply joins the previous chunk rather than going out
        # alone — unless that would make the previous chunk oversized.
        tail_len = sum(len(b) for b in current)
        if groups and sum(len(b) for b in groups[-1]) + tail_len <= MAX_CHUNK_CHARS:
            groups[-1].extend(current)
        else:
            groups.append(current)

    return [f"{title}\n\n" + "\n\n".join(group) for group in groups]


def _split_paragraphs(text: str) -> list[str]:
    """Generic fallback: pack whole paragraphs up to MAX_CHUNK_CHARS."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    pieces: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > MAX_CHUNK_CHARS:
            pieces.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        pieces.append(current)

    return pieces


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents at reply boundaries, one reply per chunk.

    Written for `advice_threads`, where every document is a question followed
    by three to five replies and each reply is one person making one claim.
    The starter's 800-character window was wrong for this corpus in both
    directions at once: it never split a thread into its separate arguments,
    and its 650-character stride sliced a duplicate tail off the four longest
    documents — including a 2-character chunk.

    Splitting on replies keeps whole opinions intact and lets retrieval surface
    the reply that answers the question instead of a thread where the useful
    sentence is a quarter of the text. Threads disagree with themselves a lot,
    so several short chunks from one thread beat one blob averaging them out.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        pieces = _split_thread(doc.text) or _split_paragraphs(doc.text)
        for index, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
