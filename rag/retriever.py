from pathlib import Path

from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

_embeddings = None
_vectorstore = None


def get_vectorstore():
    global _embeddings, _vectorstore

    if _vectorstore is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        _vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=_embeddings,
            collection_name="travel_knowledge"
        )

    return _vectorstore


@tool
def retrieve_travel_info(query: str) -> str:
    """
    Retrieve relevant travel information from the TripGenie
    knowledge base.

    Use this tool for questions about:
    - best time to visit
    - travel tips
    - popular places
    - activities
    - transportation
    - destination information
    """

    vectorstore = get_vectorstore()

    results = vectorstore.similarity_search(
        query,
        k=3
    )

    if not results:
        return "No relevant travel information found."

    formatted_results = []

    for i, doc in enumerate(results, start=1):
        source = doc.metadata.get("source", "unknown")

        formatted_results.append(
            f"Result {i} (Source: {source}):\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(formatted_results)