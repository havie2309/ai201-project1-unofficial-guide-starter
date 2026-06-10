# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

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

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Reviews for Prof. Andrea Hall | documents/prof_andrea_hall_reviews.txt |
| 2 | Rate My Professors | Reviews for Prof. Charles Curtsinger | documents/prof_charles_curtsinger_reviews.txt |
| 3 | Rate My Professors | Reviews for Prof. Collin Nolte | documents/prof_collin_nolte_reviews.txt |
| 4 | Rate My Professors | Reviews for Prof. Cora Jakubiak | documents/prof_cora_jakubiak_reviews.txt |
| 5 | Rate My Professors | Reviews for Prof. Jenny Kenkel | documents/prof_jenny_kenkel_reviews.txt |
| 6 | Rate My Professors | Reviews for Prof. Jonathan Wells | documents/prof_jonathan_wells_reviews.txt |
| 7 | Rate My Professors | Reviews for Prof. Nicole Eikmeier | documents/prof_nicole_eikmeier_reviews.txt |
| 8 | Rate My Professors | Reviews for Prof. Sam Rebelsky | documents/prof_sam_rebelsky_reviews.txt |
| 9 | Rate My Professors | Reviews for Prof. Shonda Kuiper | documents/prof_shonda_kuiper_reviews.txt |
| 10 | Rate My Professors | Reviews for Prof. Stef Toraba | documents/prof_stef_toraba_reviews.txt |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Reasoning:** Each review is 4–6 sentences long, typically 200–400 characters. 
Using 400-character chunks means each chunk captures roughly one complete review, 
preserving the full opinion in a single retrievable unit. Overlap of 80 characters 
ensures that if a key fact (like exam style or grading) falls near a chunk boundary, 
it appears in at least one complete chunk. Chunks smaller than 200 characters would 
split individual reviews into fragments with no standalone meaning; chunks larger 
than 600 characters would merge multiple reviews together, diluting the semantic 
signal for retrieval.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, 
no API key required)

**Top-k:** 5

**Production tradeoff reflection:** For a real deployment I would consider 
OpenAI's text-embedding-3-small — it has higher accuracy on short opinion-style 
text and a longer context window, but comes with per-token API costs and rate 
limits. I would also evaluate multilingual support if the system needed to serve 
non-English reviews. all-MiniLM-L6-v2 is the right choice here because it runs 
locally with no cost, no rate limits, and performs well on short sentence-level 
similarity — which matches the structure of professor reviews.

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which professor is most frequently described as having helpful office hours? | Sam Rebelsky receives the strongest and most detailed mentions for helpful office hours, followed by Jonathan Wells, Nicole Eikmeier, and Shonda Kuiper |
| 2 | Which professors are recommended for students who are new to their subject area? | Nicole Eikmeier and Sam Rebelsky are frequently recommended for beginners in computer science, with reviews emphasizing supportive teaching and approachable explanations |
| 3 | Which professor's course is most focused on real-world applications? | Andrea Hall and Shonda Kuiper receive the strongest mentions for connecting course material to real-world examples, with Jenny Kenkel also frequently described this way |
| 4 | What do students commonly say about Collin Nolte's teaching style? | Students describe Collin Nolte as organized, patient, and focused on building conceptual understanding through step-by-step explanations and problem solving |
| 5 | Which professor receives the most comments about creating a supportive learning environment? | Cora Jakubiak and Sam Rebelsky are most frequently described as creating supportive, welcoming, and collaborative classroom environments |

---

## Anticipated Challenges

1. Several reviews across different professors use very similar language 
(e.g., "supportive environment," "clear explanations," "fair grading"). 
This could cause retrieval to return chunks from the wrong professor when 
a query asks about a specific person — the embedding similarity may be 
high even though the source is irrelevant.

2. Some questions ask the system to compare across multiple professors 
(e.g., "which professor is most..."). A single retrieved chunk won't 
contain enough information to answer a comparison question — the system 
would need chunks from multiple files simultaneously, which may dilute 
or confuse the generated response.

---

## Architecture

```
[.txt files in /documents]
         ↓
Document Ingestion
(Python / open() + os.listdir())
         ↓
Cleaning
(remove extra whitespace, normalize text)
         ↓
Chunking
(400 char chunks, 80 char overlap)
         ↓
Embedding
(sentence-transformers / all-MiniLM-L6-v2)
         ↓
Vector Store
(ChromaDB — stored locally in /chroma_db)
         ↓
Retrieval
(semantic search, top-5 chunks)
         ↓
Generation
(Groq API / llama-3.3-70b-versatile)
         ↓
Response with Source Attribution
(Gradio UI at localhost:7860)
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude my Chunking Strategy section and Documents section and ask 
it to implement ingest.py — specifically the load_documents(), clean_text(), 
and chunk_text() functions using 400-character chunks with 80-character overlap. 
I will verify the output by printing 5 sample chunks and checking they each 
contain one complete review.

**Milestone 4 — Embedding and retrieval:**
I will give Claude my Retrieval Approach section and architecture diagram and 
ask it to implement embed.py and retrieve.py using all-MiniLM-L6-v2 and 
ChromaDB. I will verify by running 3 test queries and checking that returned 
chunks are visibly relevant and have distance scores below 0.5.

**Milestone 5 — Generation and interface:**
I will give Claude my grounding requirement and ask it to implement query.py 
with a prompt that instructs the LLM to answer only from retrieved context, 
and app.py with a Gradio interface showing the answer and source files. I will 
verify grounding by asking a question my documents don't cover and confirming 
the system refuses to answer.
