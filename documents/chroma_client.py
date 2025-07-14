# 📦 ChromaDB Client Setup & Utilities

from __future__ import annotations

import logging
from typing import Any, Dict, List, Union

import chromadb
from chromadb.utils import embedding_functions

# 🛠️ Logger Setup (for ChromaDB interactions)
logger = logging.getLogger(__name__)


# 💾 Persistent ChromaDB Client
client = chromadb.PersistentClient(path="./chroma_db")  # Data stored in /chroma_db folder


# 🧠 Embedding Function (using SentenceTransformers)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


# 📚 Documents Collection Setup (created if missing)
collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_func
)


# 📥 Store Document in ChromaDB
def store_document_in_chromadb(doc_id: str, text: str, document_type: str, entities: Dict[str, List[str]]) -> None:
    """
    📝 Store document embedding and metadata in ChromaDB.
    
    Args:
        doc_id (str): Unique document identifier.
        text (str): Full document text.
        document_type (str): Type/category of document (e.g., invoice, email).
        entities (dict): Extracted entities to store as metadata.

    Notes:
        - Metadata must consist of flat primitive values.
        - Lists in entities are converted to comma-separated strings.
    """
    try:
        # 🛠️ Flatten entity values (convert lists to strings)
        flat_entities = {
            key: ", ".join(value) if isinstance(value, list) else str(value)
            for key, value in entities.items()
        }

        metadata = {
            "document_type": document_type,
            **flat_entities
        }

        logger.info(f"📥 Storing document {doc_id} in ChromaDB (type: {document_type})")
        collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        logger.info(f"✅ Document {doc_id} stored successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to store document {doc_id} in ChromaDB: {e}", exc_info=True)


# 🔍 Query Similar Documents
def query_similar_documents(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    🔎 Search for similar documents using embedding similarity.

    Args:
        query_text (str): Query text to search for.
        top_k (int): Number of similar documents to retrieve.

    Returns:
        dict: Query results (document IDs, distances, etc.)
    """
    try:
        logger.info(f"🔍 Querying ChromaDB for top {top_k} similar documents.")
        results = collection.query(query_texts=[query_text], n_results=top_k)
        logger.info("✅ Query completed successfully.")
        return results

    except Exception as e:
        logger.error(f"❌ Error querying ChromaDB: {e}", exc_info=True)
        return {}
