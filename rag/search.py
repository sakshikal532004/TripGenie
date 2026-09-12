from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


vectorstore = Chroma(
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings,
    collection_name="travel_knowledge"
)


query = input("Ask a travel question: ")

results = vectorstore.similarity_search(
    query,
    k=3
)


print("\n--- Relevant Information ---\n")

for i, doc in enumerate(results, start=1):
    print(f"Result {i}")
    print(f"Source: {doc.metadata.get('source')}")
    print(doc.page_content)
    print("-" * 50)