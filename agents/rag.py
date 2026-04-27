"""
RAG Agent: Embeds and retrieves relevant chunks using ChromaDB.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from utils.state import AgentState
import uuid
import re


def slugify(text: str) -> str:
    # Replace invalid chars with dash instead of underscore
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text)

    # Remove leading/trailing dashes
    text = text.strip('-')

    # Ensure valid length
    return text[:50] if text else "default-collection"


def chunk_text(text: str, size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), size - overlap):
        chunks.append(text[i:i + size])
    return chunks


def rag_node(state: AgentState) -> AgentState:
    print("🔹 Running RAG Node...")

    client = chromadb.Client()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    collection_name = slugify(state["topic"])

    try:
        try:
            client.delete_collection(collection_name)
        except:
            pass

        collection = client.create_collection(collection_name)

        all_chunks = []
        metadatas = []

        for item in state["search_results"]:
            chunks = chunk_text(item["content"])
            for chunk in chunks:
                all_chunks.append(chunk)
                metadatas.append({"url": item["url"]})

        embeddings = model.encode(all_chunks).tolist()

        collection.add(
            documents=all_chunks,
            embeddings=embeddings,
            ids=[str(uuid.uuid4()) for _ in all_chunks],
            metadatas=metadatas
        )

        retrieved = []
        sources = set()

        for question in state["sub_questions"]:
            query_embedding = model.encode([question]).tolist()

            res = collection.query(
                query_embeddings=query_embedding,
                n_results=3
            )

            for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
                retrieved.append(doc)
                sources.add(meta["url"])

        state["retrieved_chunks"] = retrieved
        state["sources"] = list(sources)

    except Exception as e:
        raise Exception(f"RAG Error: {str(e)}")

    return state