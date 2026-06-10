import os
from groq import Groq
from retrieve import retrieve
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def build_prompt(query, chunks):
    context = "\n\n".join(
        [f"[Source: {c['source']}]\n{c['text']}" for c in chunks]
    )
    return f"""You are a helpful assistant for students looking for information about professors and courses.

Answer the question using ONLY the information provided in the documents below.
Do not use any outside knowledge or make assumptions beyond what is written.
If the documents do not contain enough information to answer the question, respond with exactly:
"I don't have enough information on that."

Always end your answer by listing which documents you used, like this:
Sources: prof_smith_reviews.txt, prof_jones_reviews.txt

Documents:
{context}

Question: {query}

Answer:"""

def ask(query):
    chunks = retrieve(query, k=5)
    prompt = build_prompt(query, chunks)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    answer = response.choices[0].message.content
    sources = list(set(c["source"] for c in chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks
    }

if __name__ == "__main__":
    test_question = "Which professor has the most helpful office hours?"
    print(f"Question: {test_question}\n")
    result = ask(test_question)
    print("Answer:")
    print(result["answer"])
    print("\nRetrieved from:")
    for s in result["sources"]:
        print(f"  • {s}")