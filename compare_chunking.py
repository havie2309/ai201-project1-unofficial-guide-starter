import gradio as gr
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv
import os
import json

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "unofficial_guide"

model = SentenceTransformer(MODEL_NAME)
client_db = chromadb.PersistentClient(path="./chroma_db")
collection = client_db.get_collection(COLLECTION_NAME)
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load all chunks for BM25
with open("chunks.json", "r", encoding="utf-8") as f:
    all_chunks = json.load(f)

bm25_corpus = [c["text"].lower().split() for c in all_chunks]
bm25 = BM25Okapi(bm25_corpus)

PROFESSORS = [
    "All Professors",
    "prof_andrea_hall_reviews.txt",
    "prof_charles_curtsinger_reviews.txt",
    "prof_collin_nolte_reviews.txt",
    "prof_cora_jakubiak_reviews.txt",
    "prof_jenny_kenkel_reviews.txt",
    "prof_jonathan_wells_reviews.txt",
    "prof_nicole_eikmeier_reviews.txt",
    "prof_sam_rebelsky_reviews.txt",
    "prof_shonda_kuiper_reviews.txt",
    "prof_stef_toraba_reviews.txt",
]

def retrieve_semantic(query, k=5, professor_filter=None):
    query_embedding = model.encode([query]).tolist()
    kwargs = dict(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    if professor_filter and professor_filter != "All Professors":
        kwargs["where"] = {"source": {"$eq": professor_filter}}
    results = collection.query(**kwargs)
    return [
        {"text": results["documents"][0][i],
         "source": results["metadatas"][0][i]["source"],
         "distance": results["distances"][0][i]}
        for i in range(len(results["documents"][0]))
    ]

def retrieve_hybrid(query, k=5, professor_filter=None):
    # BM25 scores
    tokenized = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized)

    # Semantic scores
    query_embedding = model.encode([query]).tolist()
    sem_results = collection.query(
        query_embeddings=query_embedding,
        n_results=len(all_chunks),
        include=["documents", "metadatas", "distances"]
    )

    # Build semantic ranking
    sem_ranking = {
        sem_results["metadatas"][0][i]["source"] + "__" + str(i): i
        for i in range(len(sem_results["documents"][0]))
    }

    # RRF fusion
    rrf_scores = {}
    for rank, (doc, meta, dist) in enumerate(zip(
        sem_results["documents"][0],
        sem_results["metadatas"][0],
        sem_results["distances"][0]
    )):
        key = meta["source"] + "__" + doc[:30]
        rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (60 + rank)
        rrf_scores[key] += bm25_scores[rank] / (1 + bm25_scores[rank])

    # Sort and filter
    sorted_keys = sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
    chunks = []
    for rank, (doc, meta, dist) in enumerate(zip(
        sem_results["documents"][0],
        sem_results["metadatas"][0],
        sem_results["distances"][0]
    )):
        if professor_filter and professor_filter != "All Professors":
            if meta["source"] != professor_filter:
                continue
        chunks.append({"text": doc, "source": meta["source"], "distance": dist})
        if len(chunks) >= k:
            break

    return chunks

def build_prompt(query, chunks, history):
    context = "\n\n".join(
        [f"[Source: {c['source']}]\n{c['text']}" for c in chunks]
    )
    messages = history.copy()
    messages.append({
        "role": "user",
        "content": f"""You are a helpful assistant for students looking for information about professors and courses.
Answer the question using ONLY the information provided in the documents below.
Do not use any outside knowledge or make assumptions beyond what is written.
If the documents do not contain enough information to answer, say exactly:
"I don't have enough information on that."
Always end your answer by listing which documents you used:
Sources: filename.txt, filename.txt

Documents:
{context}

Question: {query}

Answer:"""
    })
    return messages

def handle_query(question, professor_filter, use_hybrid, chat_history, history_state):
    if not question.strip():
        return "", "", chat_history, history_state

    # Retrieve
    if use_hybrid:
        chunks = retrieve_hybrid(question, k=5, professor_filter=professor_filter)
    else:
        chunks = retrieve_semantic(question, k=5, professor_filter=professor_filter)

    # Build messages with memory
    messages = build_prompt(question, chunks, history_state)

    # Generate
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500
    )
    answer = response.choices[0].message.content
    sources = "\n".join(f"• {s}" for s in set(c["source"] for c in chunks))

    # Update history
    new_history_state = history_state + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer}
    ]

    # Update chat display
    chat_history = chat_history + [(question, answer)]

    return "", sources, chat_history, new_history_state

def clear_chat():
    return [], []

css = """
    #title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.2em;
    }
    #subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1em;
        margin-bottom: 1.5em;
    }
    #ask-btn {
        background-color: #2c3e50 !important;
        color: white !important;
        font-size: 1em !important;
        border-radius: 8px !important;
    }
    #clear-btn {
        background-color: #e74c3c !important;
        color: white !important;
        border-radius: 8px !important;
    }
"""

with gr.Blocks(title="The Unofficial Guide", css=css) as demo:
    history_state = gr.State([])

    gr.Markdown("<div id='title'>The Unofficial Guide</div>")
    gr.Markdown("<div id='subtitle'>Ask questions about Grinnell College professors — answers drawn from real student reviews.</div>")

    with gr.Row():
        professor_filter = gr.Dropdown(
            choices=PROFESSORS,
            value="All Professors",
            label="Filter by professor"
        )
        use_hybrid = gr.Checkbox(
            label="Use Hybrid Search (BM25 + Semantic)",
            value=False
        )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which professor has the most helpful office hours?"
    )

    btn = gr.Button("Ask", elem_id="ask-btn")

    gr.Markdown("### Example questions:")
    with gr.Row():
        ex1 = gr.Button("Which professor has the most helpful office hours?")
        ex2 = gr.Button("Which professors are good for beginners in CS?")
        ex3 = gr.Button("What do students say about Collin Nolte's teaching style?")
        ex4 = gr.Button("Which professor focuses most on real-world applications?")

    chatbot = gr.Chatbot(label="Conversation", height=400)
    sources_box = gr.Textbox(label="Retrieved from", lines=4)
    clear_btn = gr.Button("Clear conversation", elem_id="clear-btn")

    btn.click(
        handle_query,
        inputs=[inp, professor_filter, use_hybrid, chatbot, history_state],
        outputs=[inp, sources_box, chatbot, history_state]
    )
    inp.submit(
        handle_query,
        inputs=[inp, professor_filter, use_hybrid, chatbot, history_state],
        outputs=[inp, sources_box, chatbot, history_state]
    )
    clear_btn.click(clear_chat, outputs=[chatbot, history_state])

    ex1.click(lambda: "Which professor has the most helpful office hours?", outputs=inp)
    ex2.click(lambda: "Which professors are good for beginners in CS?", outputs=inp)
    ex3.click(lambda: "What do students say about Collin Nolte's teaching style?", outputs=inp)
    ex4.click(lambda: "Which professor focuses most on real-world applications?", outputs=inp)

demo.launch()