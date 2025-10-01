# D:\AI_Project\hand_reader_ai_baba\app\vector_db.py
import os
from typing import List
from dotenv import load_dotenv  # Add this import
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Load environment variables
load_dotenv()  # Add this line

FAISS_DB_PATH = "db/faiss_palmistry"

def build_vector_db(knowledge_file: str = "palmistry_knowledge.md"):
    """
    Build FAISS vector DB from palmistry knowledge base file.
    Run this once or whenever knowledge file updates.
    """
    if not os.path.exists(knowledge_file):
        raise FileNotFoundError(f"Knowledge base file missing: {knowledge_file}")

    # Load file
    loader = TextLoader(knowledge_file)
    documents = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    # Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Create FAISS
    db = FAISS.from_documents(docs, embeddings)

    # Save locally
    os.makedirs("db", exist_ok=True)
    db.save_local(FAISS_DB_PATH)
    print(f"✅ FAISS DB created at {FAISS_DB_PATH}")


def load_vector_db() -> FAISS:
    """Load FAISS DB if exists."""
    if not os.path.exists(FAISS_DB_PATH):
        raise FileNotFoundError("FAISS DB not found. Run build_vector_db() first.")
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(FAISS_DB_PATH, embeddings, allow_dangerous_deserialization=True)


def query_db(queries: List[str], top_k: int = 2) -> List[str]:
    """
    Search FAISS DB with feature labels.
    Returns list of top matching text chunks.
    """
    db = load_vector_db()
    results = []
    for q in queries:
        docs = db.similarity_search(q, k=top_k)
        for d in docs:
            results.append(d.page_content)
    return results