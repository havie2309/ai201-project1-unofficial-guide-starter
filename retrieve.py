import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "unofficial_guide"

model = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(COLLECTION_NAME)

def retrieve(query, k=5):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })
    return chunks

if __name__ == "__main__":
    test_queries = [
        "Which professor has the most helpful office hours?",
        "Which professors are good for beginners in computer science?",
        "Which professor focuses most on real-world applications?"
    ]
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        results = retrieve(query)
        for r in results:
            print(f"  [dist: {r['distance']:.3f}] ({r['source']})")
            print(f"  {r['text'][:150]}...")
            print()