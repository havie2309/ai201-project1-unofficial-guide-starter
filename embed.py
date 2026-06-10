import json
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "unofficial_guide"

def embed_and_store(chunks):
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Setting up ChromaDB...")
    client = chromadb.PersistentClient(path="./chroma_db")

    # Delete old collection if re-running
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  Deleted old collection")
    except:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    ids = [f"{c['source']}__chunk{c['chunk_index']}" for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    print(f"Embedding {len(texts)} chunks — this may take a minute...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    print(f"\nStored {len(texts)} chunks in ChromaDB successfully.")

if __name__ == "__main__":
    with open("chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    embed_and_store(chunks)