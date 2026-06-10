import os
import re
import json

DOCUMENTS_DIR = "documents"
CHUNK_SIZE = 250
OVERLAP = 50

def load_documents(directory):
    docs = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            docs.append({"source": filename, "text": text})
            print(f"  Loaded: {filename}")
    return docs

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # collapse all whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # remove non-ASCII characters
    text = text.strip()
    return text

def chunk_text(text, source, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    # Split into sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    chunk_index = 0

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += " " + sentence
        else:
            if len(current_chunk.strip()) > 20:
                chunks.append({
                    "text": current_chunk.strip(),
                    "source": source,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
            # Start new chunk with overlap from end of previous
            current_chunk = current_chunk[-overlap:] + " " + sentence

    # Don't forget the last chunk
    if len(current_chunk.strip()) > 20:
        chunks.append({
            "text": current_chunk.strip(),
            "source": source,
            "chunk_index": chunk_index
        })

    return chunks

def run_pipeline():
    print("Loading documents...")
    docs = load_documents(DOCUMENTS_DIR)
    print(f"  Total documents loaded: {len(docs)}\n")

    all_chunks = []
    for doc in docs:
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned, doc["source"])
        all_chunks.extend(chunks)
        print(f"  {doc['source']} → {len(chunks)} chunks")

    print(f"\n  TOTAL CHUNKS: {len(all_chunks)}")

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print("  Saved to chunks.json\n")
    return all_chunks

if __name__ == "__main__":
    chunks = run_pipeline()
    print("--- 5 Sample Chunks ---\n")
    for c in chunks[:5]:
        print(f"[Source: {c['source']} | Chunk #{c['chunk_index']}]")
        print(c['text'])
        print("-" * 50)