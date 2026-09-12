from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ---------------- PATHS ----------------

BASE_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = BASE_DIR / "knowledge"
CHROMA_DIR = BASE_DIR / "chroma_db"


# ---------------- LOAD DOCUMENTS ----------------

documents = []

for file_path in KNOWLEDGE_DIR.glob("*.txt"):

    text = file_path.read_text(
        encoding="utf-8"
    )

    documents.append(
        Document(
            page_content=text,
            metadata={
                "source": file_path.name
            }
        )
    )


print(f"Loaded {len(documents)} documents.")


# ---------------- TEXT SPLITTING ----------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks.")


# ---------------- EMBEDDINGS ----------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ---------------- CHROMA VECTOR DATABASE ----------------

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(CHROMA_DIR),
    collection_name="travel_knowledge"
)


print("Documents stored in ChromaDB successfully.")
print(f"ChromaDB location: {CHROMA_DIR}")