# The Unofficial Guide — Project 1

## Demo Video
[Watch the demo on Loom](https://www.loom.com/share/37a97ceeefc04d4e82462c2c5485100d)

---

## Domain

Student-written professor and course reviews at Grinnell College. This knowledge 
is valuable because official university channels only provide course descriptions 
and faculty bios — they don't tell students whether a professor curves grades, 
what their exams are actually like, how heavy the workload is, or what teaching 
style to expect. Students share this information informally through Rate My 
Professors and word of mouth, making it hard to search or summarize across 
multiple professors at once.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Professor reviews | documents/prof_andrea_hall_reviews.txt |
| 2 | Rate My Professors | Professor reviews | documents/prof_charles_curtsinger_reviews.txt |
| 3 | Rate My Professors | Professor reviews | documents/prof_collin_nolte_reviews.txt |
| 4 | Rate My Professors | Professor reviews | documents/prof_cora_jakubiak_reviews.txt |
| 5 | Rate My Professors | Professor reviews | documents/prof_jenny_kenkel_reviews.txt |
| 6 | Rate My Professors | Professor reviews | documents/prof_jonathan_wells_reviews.txt |
| 7 | Rate My Professors | Professor reviews | documents/prof_nicole_eikmeier_reviews.txt |
| 8 | Rate My Professors | Professor reviews | documents/prof_sam_rebelsky_reviews.txt |
| 9 | Rate My Professors | Professor reviews | documents/prof_shonda_kuiper_reviews.txt |
| 10 | Rate My Professors | Professor reviews | documents/prof_stef_toraba_reviews.txt |

---

## Chunking Strategy

**Chunk size:** 250 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Each review is 4–6 sentences long. 
Using 250-character chunks with sentence-boundary splitting means each chunk 
captures 2–3 complete sentences — enough context to be meaningful on its own 
without merging multiple reviews together. The 50-character overlap ensures 
that key facts near chunk boundaries appear in at least one complete chunk. 
We use sentence-boundary splitting (regex on punctuation) rather than hard 
character cuts so chunks never end mid-word or mid-sentence.

**Final chunk count:** 135 chunks across 10 documents

---

## Sample Chunks

**Chunk 1** (prof_andrea_hall_reviews.txt, chunk #0)

**Chunk 2** (prof_andrea_hall_reviews.txt, chunk #1)

**Chunk 3** (prof_collin_nolte_reviews.txt, chunk #0)

**Chunk 4** (prof_sam_rebelsky_reviews.txt, chunk #2)

**Chunk 5** (prof_jonathan_wells_reviews.txt, chunk #3)

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, 
no API key required, no rate limits)

**Production tradeoff reflection:** For a real deployment I would consider 
OpenAI's text-embedding-3-small — it has higher accuracy on short 
opinion-style text and a longer context window (8191 tokens vs 256 tokens 
for all-MiniLM-L6-v2), but comes with per-token API costs and rate limits. 
I would also evaluate multilingual support if the system needed to serve 
non-English reviews. For latency-sensitive production systems, a locally 
hosted model avoids API round-trip time entirely. all-MiniLM-L6-v2 is the 
right choice here because it runs locally with no cost, no rate limits, and 
performs well on short sentence-level similarity — which matches the 
structure of professor reviews.

---

## Grounded Generation

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:** The prompt instructs 
the model to end every answer by listing which documents it used in the 
format "Sources: filename.txt, filename.txt". Additionally, the Gradio 
interface displays a separate "Retrieved from" box that programmatically 
lists all source filenames from the retrieved chunks, independent of what 
the LLM writes — so attribution is guaranteed even if the model omits it.

---

## Query Interface

**Input field:** A text box labeled "Your question" with a placeholder 
example. Users can also click any of 4 example question buttons which 
auto-fill the input box.

**Output fields:** Two text boxes — "Answer" (the LLM-generated response 
with inline source citation) and "Retrieved from" (programmatic list of 
source filenames).

**Sample interaction transcript:**

Query: What do students commonly say about Collin Nolte's teaching style?

Answer: Students describe Professor Collin Nolte as knowledgeable and 
passionate about physics. His lectures focus on building a strong conceptual 
understanding before moving into calculations.
Sources: prof_collin_nolte_reviews.txt

Retrieved from:
- prof_cora_jakubiak_reviews.txt
- prof_jonathan_wells_reviews.txt
- prof_sam_rebelsky_reviews.txt
- prof_collin_nolte_reviews.txt
- prof_andrea_hall_reviews.txt

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor is most frequently described as having helpful office hours? | Sam Rebelsky receives strongest mentions, followed by Wells, Eikmeier, Kuiper | Listed Andrea Hall, Sam Rebelsky, Cora Jakubiak, Jonathan Wells, Nicole Eikmeier as all having helpful office hours but declined to pick one | Relevant | Partially accurate |
| 2 | Which professors are recommended for students new to their subject area? | Nicole Eikmeier and Sam Rebelsky recommended for CS beginners | Returned Cora Jakubiak and Stef Toraba as recommended for new students | Partially relevant | Partially accurate |
| 3 | Which professor's course is most focused on real-world applications? | Andrea Hall and Shonda Kuiper receive strongest mentions | Correctly identified Shonda Kuiper, Jonathan Wells, and Andrea Hall | Relevant | Accurate |
| 4 | What do students commonly say about Collin Nolte's teaching style? | Organized, patient, focused on conceptual understanding | Correctly described as knowledgeable, passionate, focused on conceptual understanding before calculations | Relevant | Accurate |
| 5 | Which professor receives the most comments about a supportive learning environment? | Cora Jakubiak and Sam Rebelsky most frequently described this way | Returned Jenny Kenkel, Cora Jakubiak, and Sam Rebelsky — named Jenny Kenkel as top based on appearing in two documents | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Which professor is most frequently described as 
having helpful office hours?" (Question 1)

**What the system returned:** The system listed five professors as all having 
helpful office hours but explicitly refused to identify which one receives 
the most mentions, stating the reviews are "generally positive and similar 
for all of them."

**Root cause (tied to a specific pipeline stage):** This is a retrieval 
failure caused by the comparison nature of the query. The retrieval stage 
returns only 5 chunks (top-k=5), and because all professor reviews use 
similar language around office hours ("welcoming," "helpful," "approachable"), 
the embedding similarity scores are close together. No single chunk contains 
enough information to compare frequency across professors — the LLM correctly 
declines to rank what it cannot determine from the retrieved context alone.

**What you would change to fix it:** Increase top-k to 10–15 so the LLM 
receives chunks from more professors simultaneously. Alternatively, add 
metadata filtering so the system can retrieve the top chunk per professor 
and compare them side by side, rather than retrieving the 5 globally most 
similar chunks which may cluster around 2–3 professors.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking 
strategy section in planning.md before touching any code forced a decision 
about chunk size upfront. When the initial 400-character fixed-split produced 
chunks cut mid-word (e.g., "the pra" / "licy discussions"), the spec gave a 
clear target to fix toward — sentence-boundary splitting that preserves 
complete thoughts. Without the spec, it would have been easy to skip chunk 
inspection entirely and only discover the problem during retrieval.

**One way your implementation diverged from the spec, and why:** The spec 
specified 400-character chunks with 80-character overlap. During Milestone 3, 
the chunk count came out to only 71 — too few for reliable retrieval. The 
chunk size was reduced to 250 characters with 50-character overlap to produce 
135 chunks. This divergence was necessary because the actual documents turned 
out to be shorter than anticipated — each review averages 4–5 sentences 
rather than the longer paragraphs assumed during planning.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md 
specifying 400-character chunks with 80-character overlap, plus the pipeline 
diagram showing the five stages.
- *What it produced:* A complete ingest.py with load_documents(), 
clean_text(), and chunk_text() functions using fixed character splitting.
- *What I changed or overrode:* The fixed character split was cutting chunks 
mid-word and mid-sentence. I asked Claude to rewrite chunk_text() to split 
on sentence boundaries using regex instead. I also changed the chunk size 
from 400 to 250 after seeing the total chunk count was only 71 — too few 
for reliable retrieval.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md 
specifying all-MiniLM-L6-v2 and ChromaDB, plus the grounding requirement 
that answers must come only from retrieved documents with source attribution.
- *What it produced:* Complete embed.py, retrieve.py, query.py, and app.py 
files wiring all stages together with a Gradio interface.
- *What I changed or overrode:* The initial Gradio UI used a basic layout 
with no example questions and an emoji in the title. I directed Claude to 
redesign the UI with a cleaner dark-button style, remove the emoji, add 4 
clickable example question buttons, and stack the answer and sources 
vertically instead of side by side.