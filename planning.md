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

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
